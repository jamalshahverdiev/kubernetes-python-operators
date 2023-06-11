from kopf import on, run
from logging import basicConfig, INFO
from src.functions import create_or_update_policy, initialize_kube, get_policy_name
from src.variables import Settings
from kubernetes import client

@on.create(Settings.crd_group_name, Settings.version, Settings.crd_kind_name)
def create_fn(body, spec, meta, namespace, logger, **kwargs):
    return create_or_update_policy(spec, meta, logger, action='create')

@on.update(Settings.crd_group_name, Settings.version, Settings.crd_kind_name)
def update_fn(body, spec, meta, namespace, logger, **kwargs):
    return create_or_update_policy(spec, meta, logger, action='update')


@on.delete(Settings.crd_group_name, Settings.version, Settings.crd_kind_name)
def delete_fn(body, spec, meta, namespace, logger, **kwargs):
    # Print the spec to debug its content
    logger.info(f"Spec content: {spec}")

    # Get policy_name from the spec, if that's how it's structured
    policy_name = get_policy_name(spec)
    
    group = Settings.group
    version = Settings.version
    plural = Settings.plural

    try:
        response = client.CustomObjectsApi().delete_namespaced_custom_object(
            group=group,
            version=version,
            namespace=namespace,
            plural=plural,
            name=policy_name
        )
        logger.info(f"Deleted policy: {policy_name}")
    except Exception as e:
        logger.error(f"Failed to delete policy {policy_name}: {e}")


if __name__ == "__main__":
    basicConfig(level=INFO)
    initialize_kube()
    run()
