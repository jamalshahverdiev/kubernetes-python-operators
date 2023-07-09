from kubernetes import client, config
from os import getenv, path
from datetime import datetime
from kubernetes.client.rest import ApiException
from kubernetes.client import CoreV1Api
from src.variables import Settings

def initialize_kube():
    ENVIRONMENT = getenv('DEV')
    if ENVIRONMENT:
        print("Loading user kube config file")
        home = path.expanduser("~")
        kube_config_path = getenv("KUBE_CONFIG", home+"/.kube/config")
        config.load_kube_config(config_file=kube_config_path)
    else:
        print("Loading In-cluster KUBECONFIG")
        config.load_incluster_config()

def get_unique_nodes_for_deployment_in_namespace(namespace, deployment_name):
    try:
        api_instance = client.AppsV1Api()
        deployment = api_instance.read_namespaced_deployment(deployment_name, namespace)

        # Get the replica count of the deployment
        replica_count = deployment.spec.replicas

        # If the replica count is less than 2, print log and return
        if replica_count < 2:
            print(f'Replica count for {deployment_name} is less than 2. Not continuing.')
            return

        # Fetch all Pods for the given Deployment
        v1 = client.CoreV1Api()
        pods = v1.list_namespaced_pod(namespace, label_selector=f'app={deployment_name}')

        # Get unique nodes that the Pods are running on
        nodes = set([pod.spec.node_name for pod in pods.items])

        return len(nodes)

    except ApiException as e:
        print(f"Exception when calling Kubernetes API: {e}")

def restart_deployment(namespace, deployment_name):
    print(f'Rollout restart deployment `{deployment_name}` in namespace `{namespace}`.')
    apps_v1_api = client.AppsV1Api()
    
    # Get the deployment
    deployment = apps_v1_api.read_namespaced_deployment(deployment_name, namespace)

    # Update the deployment's template metadata with a new annotation
    # This triggers the rollout
    annotations = deployment.spec.template.metadata.annotations
    if annotations and 'kubectl.kubernetes.io/restartedAt' in annotations:
        del annotations['kubectl.kubernetes.io/restartedAt']
    else:
        deployment.spec.template.metadata.annotations = {}
    
    deployment.spec.template.metadata.annotations['kubectl.kubernetes.io/restartedAt'] = datetime.now().isoformat()

    # Apply the updated deployment
    apps_v1_api.patch_namespaced_deployment(deployment_name, namespace, deployment)
    print(f'Deployment `{deployment_name}` in namespace `{namespace}` has been restarted.')

def get_namespaces_with_annotation():
    print('Getting namespaces with annotation.')
    v1 = client.CoreV1Api()
    namespaces = v1.list_namespace().items
    annotated_namespaces = [ns.metadata.name for ns in namespaces if ns.metadata.annotations and ns.metadata.annotations.get(Settings.deploy_annotations) == Settings.deploy_annotations_value]
    print(f'Found {len(annotated_namespaces)} namespaces with annotation: {annotated_namespaces}')
    return annotated_namespaces

def get_deployments_in_namespace(namespace):
    print(f'Getting deployments in namespace `{namespace}`.')
    api_instance = client.AppsV1Api()
    deployments = api_instance.list_namespaced_deployment(namespace).items
    print(f'Found {len(deployments)} deployments in namespace `{namespace}`.')
    return deployments

def get_ready_nodes():
    v1 = CoreV1Api()
    ready_nodes = 0
    for node in v1.list_node().items:
        # Skip the node if it's a master node
        if Settings.label_master_node in node.metadata.labels:
            continue
        for condition in node.status.conditions:
            if condition.type == 'Ready' and condition.status == 'True':
                ready_nodes += 1

    return ready_nodes

def restart_deployments_if_needed():
    
    # Check if there are at least 2 nodes in 'Ready' state
    ready_nodes = get_ready_nodes()
    if ready_nodes < 2:
        print(f'Only {ready_nodes} node(s) in `Ready` state. No action taken.')
        return
    
    # For each namespace with the annotation
    for ns in get_namespaces_with_annotation():
        # Get deployments in the namespace
        for deployment in get_deployments_in_namespace(ns):
            depl_name = deployment.metadata.name
            node_count = get_unique_nodes_for_deployment_in_namespace(ns, depl_name)

            # Restart the deployment if there are fewer than 2 nodes
            if node_count and node_count < 2:
                print(f'Node count is less than 2 for deployment `{depl_name}`. Restarting deployment `{depl_name}`.')
                restart_deployment(ns, depl_name)
            elif node_count:
                print(f'Node count is equal or greater than 2 for `{depl_name}`. No need to restart.')
            else:
                print(f'Could not determine node count for `{depl_name}`. No action taken.')

