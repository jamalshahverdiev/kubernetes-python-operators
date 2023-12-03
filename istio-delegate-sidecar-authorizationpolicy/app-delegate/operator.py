from kopf import on, run
from logging import basicConfig, INFO
from src.functions import (
    initialize_kube,
    create_or_update_sidecar,
    create_or_update_authorization_policy,
    create_or_update_virtual_service,
    find_virtual_service,
    update_virtual_service,
    load_virtual_service_template,
    remove_delegation_from_virtual_service,
    delete_sidecar,
    delete_authorization_policy,
)
from src.variables import Settings


@on.create("istio.opso.info", "v1", "delegators")
@on.update("istio.opso.info", "v1", "delegators")
def delegator_handler(spec, name, namespace, logger, **kwargs):
    domain = spec.get("domain")
    gateway = spec.get("gateway")
    uriprefix = spec.get("uriprefix")
    delegatevs = spec.get("delegatevs")
    delegatevsns = spec.get("delegatevsns")

    # Find existing VirtualService
    vs = find_virtual_service(domain, gateway, namespace)
    if vs:
        # Check if the URI prefix exists
        if not any(
            match.get("uri", {}).get("prefix") == uriprefix
            for http in vs["spec"]["http"]
            for match in http["match"]
        ):
            # Update VirtualService to include new delegation
            update_virtual_service(vs, uriprefix, delegatevs, delegatevsns)
            logger.info(
                f"Updated VirtualService {vs['metadata']['name']} in namespace {vs['metadata']['namespace']}"
            )
    else:
        # Construct and create new VirtualService spec
        vs_spec = load_virtual_service_template(
            Settings.template_file,
            domain,
            gateway,
            uriprefix,
            delegatevs,
            delegatevsns,
            namespace,
        )
        create_or_update_virtual_service(
            name=delegatevs, namespace=namespace, spec=vs_spec
        )
        logger.info(f"Created VirtualService {delegatevs} in namespace {namespace}")


@on.delete("istio.opso.info", "v1", "delegators")
def delete_delegator_handler(spec, name, namespace, logger, **kwargs):
    domain = spec.get("domain")
    gateway = spec.get("gateway")
    uriprefix = spec.get("uriprefix")
    delegatevs = spec.get("delegatevs")
    delegatevsns = spec.get("delegatevsns")

    vs = find_virtual_service(domain, gateway, namespace)
    if vs:
        remove_delegation_from_virtual_service(vs, uriprefix, delegatevs, delegatevsns, logger)
        logger.info(
            f"Updated VirtualService {vs['metadata']['name']} in namespace {vs['metadata']['namespace']} after delegator deletion"
        )


@on.create("istio.opso.info", "v1", "istiopolicymanagers")
@on.update("istio.opso.info", "v1", "istiopolicymanagers")
def istio_policy_manager_handler(name, namespace, spec, logger, **kwargs):
    create_or_update_sidecar(name, namespace, spec, logger)
    create_or_update_authorization_policy(name, namespace, spec, logger)
    logger.info(f"IstioPolicyManager {name} in namespace {namespace} processed")

    

@on.delete("istio.opso.info", "v1", "istiopolicymanagers")
def delete_istio_policy_manager_handler(name, namespace, logger, **kwargs):
    delete_sidecar(name, namespace, logger)
    delete_authorization_policy(name, namespace, logger)
    logger.info(f"Deleted Istio resources for {name} in namespace {namespace}")

if __name__ == "__main__":
    basicConfig(level=INFO)
    initialize_kube()
    run()
