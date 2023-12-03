from json import load, loads, dumps
from logging import error, info
from os import getenv, path
from kubernetes import config, client
from src.variables import Settings

def initialize_kube():
    ENVIRONMENT = getenv("DEV")
    if ENVIRONMENT:
        print("Loading user kube config file")
        home = path.expanduser("~")
        kube_config_path = getenv("KUBE_CONFIG", home + "/.kube/config")
        config.load_kube_config(config_file=kube_config_path)
    else:
        print("Loading In-cluster KUBECONFIG")
        config.load_incluster_config()

def find_virtual_service(domain, gateway, namespace):
    api = client.CustomObjectsApi()

    try:
        vs_list = api.list_namespaced_custom_object(
            group=Settings.istio_group,
            version=Settings.istio_version,
            namespace=namespace,
            plural=Settings.virtual_service_plural,
        )

        for vs in vs_list.get("items", []):
            if domain in vs["spec"].get("hosts", []) and gateway in vs["spec"].get(
                "gateways", []
            ):
                return vs

    except client.ApiException as e:
        error(f"Error searching for VirtualService in namespace {namespace}: {e}")
        raise

    return None

def update_virtual_service(vs, uriprefix, delegatevs, delegatevsns):
    api = client.CustomObjectsApi()
    name = vs["metadata"]["name"]
    namespace = vs["metadata"]["namespace"]

    new_delegation = {
        "match": [{"uri": {"prefix": uriprefix}}],
        "delegate": {"name": delegatevs, "namespace": delegatevsns},
    }

    if "http" not in vs["spec"]:
        vs["spec"]["http"] = []

    vs["spec"]["http"].append(new_delegation)

    try:
        api.replace_namespaced_custom_object(
            group=Settings.istio_group,
            version=Settings.istio_version,
            namespace=namespace,
            name=name,
            plural=Settings.virtual_service_plural,
            body=vs,
        )
        info(f"Updated VirtualService {name} in namespace {namespace}")
    except client.ApiException as e:
        error(f"Error updating VirtualService {name} in namespace {namespace}: {e}")
        raise

def load_virtual_service_template(
    template_file, domain, gateway, uriprefix, delegatevs, delegatevsns, namespace
):
    with open(template_file, "r") as file:
        vs_json_file = load(file)

    repaired_vs_json_file = loads(
        dumps(vs_json_file)
        .replace("{{ istio_group }}", Settings.istio_group)
        .replace("{{ istio_version }}", Settings.istio_version)
        .replace("{{ domain }}", domain)
        .replace("{{ gateway }}", gateway)
        .replace("{{ uriprefix }}", uriprefix)
        .replace("{{ delegatevs }}", delegatevs)
        .replace("{{ delegatevsns }}", delegatevsns)
        .replace("{{ namespace }}", namespace)
    )

    return repaired_vs_json_file

def create_or_update_virtual_service(name, namespace, spec):
    api = client.CustomObjectsApi()
    resource_exists = False

    try:
        existing_vs = api.get_namespaced_custom_object(
            group=Settings.istio_group,
            version=Settings.istio_version,
            namespace=namespace,
            plural=Settings.virtual_service_plural,
            name=name,
        )
        resource_exists = True
    except client.ApiException as e:
        if e.status != 404:
            error(f"Error checking VirtualService {name} in {namespace}: {e}")
            raise

    try:
        if resource_exists:
            api.replace_namespaced_custom_object(
                group=Settings.istio_group,
                version=Settings.istio_version,
                namespace=namespace,
                name=name,
                plural=Settings.virtual_service_plural,
                body=spec,
            )
            info(f"Updated VirtualService {name} in {namespace}")
        else:
            api.create_namespaced_custom_object(
                group=Settings.istio_group,
                version=Settings.istio_version,
                namespace=namespace,
                plural=Settings.virtual_service_plural,
                body=spec,
            )
            info(f"Created VirtualService {name} in {namespace}")
    except client.ApiException as e:
        error(f"Error creating/updating VirtualService {name} in {namespace}: {e}")
        raise

def remove_delegation_from_virtual_service(vs, uriprefix, delegatevs, delegatevsns, logger):
    api = client.CustomObjectsApi()
    name = vs["metadata"]["name"]
    namespace = vs["metadata"]["namespace"]

    vs['spec']['http'] = [http for http in vs['spec'].get('http', []) 
                          if not (http.get('delegate', {}).get('name') == delegatevs and 
                                  http.get('delegate', {}).get('namespace') == delegatevsns and 
                                  http.get('match', [{}])[0].get('uri', {}).get('prefix') == uriprefix)]

    if not vs['spec']['http']:
        try:
            api.delete_namespaced_custom_object(
                group=Settings.istio_group,
                version=Settings.istio_version,
                namespace=namespace,
                plural=Settings.virtual_service_plural,
                name=name,
            )
            logger.info(f"Deleted VirtualService {name} in namespace {namespace} as it no longer contains any delegations")
        except client.ApiException as e:
            error(f"Error deleting VirtualService {name} in namespace {namespace}: {e}")
            raise
    else:
        try:
            api.replace_namespaced_custom_object(
                group=Settings.istio_group,
                version=Settings.istio_version,
                namespace=namespace,
                name=name,
                plural=Settings.virtual_service_plural,
                body=vs,
            )
            logger.info(f"Updated VirtualService {name} in namespace {namespace}")
        except client.ApiException as e:
            error(f"Error updating VirtualService {name} in namespace {namespace}: {e}")
            raise

def create_or_update_sidecar(name, namespace, spec, logger):
    api = client.CustomObjectsApi()
    sidecar_body = {
        "apiVersion": "networking.istio.io/v1beta1",
        "kind": "Sidecar",
        "metadata": {
            "name": name,
            "namespace": namespace,
            "labels": spec.get("labels", {})
        },
        "spec": {
            "egress": [{"hosts": spec.get("egressHosts", [])}],
            "workloadSelector": {"labels": spec.get("selector", {})}
        }
    }

    try:
        api.replace_namespaced_custom_object(
            group="networking.istio.io",
            version="v1beta1",
            namespace=namespace,
            plural="sidecars",
            name=name,
            body=sidecar_body,
        )
        logger.info(f"Updated Sidecar {name} in namespace {namespace}")
    except client.exceptions.ApiException as e:
        if e.status == 404:
            api.create_namespaced_custom_object(
                group="networking.istio.io",
                version="v1beta1",
                namespace=namespace,
                plural="sidecars",
                body=sidecar_body,
            )
            logger.info(f"Created Sidecar {name} in namespace {namespace}")
        else:
            raise

def create_or_update_authorization_policy(name, namespace, spec, logger):
    api = client.CustomObjectsApi()
    auth_policy_body = {
        "apiVersion": "security.istio.io/v1",
        "kind": "AuthorizationPolicy",
        "metadata": {
            "name": name,
            "namespace": namespace,
            "labels": spec.get("labels", {})
        },
        "spec": {
            "action": "ALLOW",
            "rules": [
                {
                    "from": [
                        {
                            "source": {
                                "namespaces": spec.get("policyRules", [{}])[0].get("from", {}).get("source", {}).get("namespaces", [])
                            }
                        }
                    ],
                    "to": [
                        {
                            "operation": {
                                "paths": spec.get("policyRules", [{}])[0].get("to", {}).get("operation", {}).get("paths", []),
                                "ports": spec.get("policyRules", [{}])[0].get("to", {}).get("operation", {}).get("ports", [])
                            }
                        }
                    ]
                }
            ],
            "selector": {"matchLabels": spec.get("selector", {})}
        }
    }

    try:
        api.replace_namespaced_custom_object(
            group="security.istio.io",
            version="v1",
            namespace=namespace,
            plural="authorizationpolicies",
            name=name,
            body=auth_policy_body,
        )
        logger.info(f"Updated AuthorizationPolicy {name} in namespace {namespace}")
    except client.exceptions.ApiException as e:
        if e.status == 404:
            api.create_namespaced_custom_object(
                group="security.istio.io",
                version="v1",
                namespace=namespace,
                plural="authorizationpolicies",
                body=auth_policy_body,
            )
            logger.info(f"Created AuthorizationPolicy {name} in namespace {namespace}")
        else:
            raise

def delete_sidecar(name, namespace, logger):
    api = client.CustomObjectsApi()
    try:
        api.delete_namespaced_custom_object(
            group="networking.istio.io",
            version="v1beta1",
            namespace=namespace,
            plural="sidecars",
            name=name,
        )
        logger.info(f"Deleted Sidecar {name} in namespace {namespace}")
    except client.exceptions.ApiException as e:
        error(f"Error deleting Sidecar {name} in namespace {namespace}: {e}")

def delete_authorization_policy(name, namespace, logger):
    api = client.CustomObjectsApi()
    try:
        api.delete_namespaced_custom_object(
            group="security.istio.io",
            version="v1",
            namespace=namespace,
            plural="authorizationpolicies",
            name=name,
        )
        logger.info(f"Deleted AuthorizationPolicy {name} in namespace {namespace}")
    except client.exceptions.ApiException as e:
        error(f"Error deleting AuthorizationPolicy {name} in namespace {namespace}: {e}")
