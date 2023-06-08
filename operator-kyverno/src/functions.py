from json import load, loads, dumps
from os import getenv, path
from kubernetes import config, client
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

def get_policy_name(spec):
    return 'restart-{}-on-{}-change'.format(spec.get('policymutatekind').lower(), spec.get('policyanalyzekindname').lower())
    
def get_kyverno_version(name, namespace):
    api_instance = client.AppsV1Api()
    deployment = api_instance.read_namespaced_deployment(name, namespace)
    image = deployment.spec.template.spec.containers[0].image
    kyverno_version = image.split(":")[-1]
    
    if kyverno_version.startswith('v'):
        kyverno_version = kyverno_version[1:]
    
    return kyverno_version

def get_kubernetes_version():
    api_instance = client.VersionApi()
    version_info = api_instance.get_code()
    kubernetes_version = version_info.git_version
    
    if kubernetes_version.startswith('v'):
        kubernetes_version = kubernetes_version[1:]
    
    return kubernetes_version
        
def create_or_update_policy(spec, meta, logger, action):
    policyanalyzekindname = spec.get('policyanalyzekindname')
    policymutatekind = spec.get('policymutatekind')
    policymutatename = spec.get('policymutatename')
    
    policy_name = get_policy_name(spec)

    with open('templates/policy-file.json', 'r') as f:
        policy = load(f)
        
    policy = loads(dumps(policy).replace(
    "<<policy_name>>", policy_name
    ).replace(
        "<<namespace>>", meta.get('namespace')
    ).replace(
        "<<policymutatekind>>", policymutatekind
    ).replace(
        "<<policymutatename>>", policymutatename
    ).replace(
        "<<policyanalyzekindname>>", policyanalyzekindname
    ).replace(
        "<<policymutatekind_lower>>", policymutatekind.lower()
    ))
    

    group = Settings.group
    version = Settings.version
    namespace = meta.get('namespace')
    plural = Settings.plural

    # Set dynamic values for annotations    
    policy['metadata']['annotations']['kyverno.io/kyverno-version'] = get_kyverno_version(Settings.kyverno_namespace, Settings.kyverno_namespace)
    policy['metadata']['annotations']['policies.kyverno.io/minversion'] = get_kyverno_version(Settings.kyverno_namespace, Settings.kyverno_namespace)
    policy['metadata']['annotations']['kyverno.io/kubernetes-version'] = get_kubernetes_version()


    if action == 'create':
        response = client.CustomObjectsApi().create_namespaced_custom_object(
            group=group,
            version=version,
            namespace=namespace,
            plural=plural,
            body=policy
        )
    elif action == 'update':
        response = client.CustomObjectsApi().patch_namespaced_custom_object(
            group=group,
            version=version,
            namespace=namespace,
            plural=plural,
            name=policy_name,
            body=policy
        )

    logger.info(f"{action.capitalize()}d policy: {policy_name}")
    return {"policy_name": policy_name}
