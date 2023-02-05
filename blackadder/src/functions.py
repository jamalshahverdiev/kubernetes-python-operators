from random import randint
from pykube import all, exceptions, Pod, Deployment, ConfigMap, HTTPClient 
from time import sleep
from requests.exceptions import HTTPError
from lorem import paragraph
from src.variables import api

def list_objects(self, k8s_obj, exclude_namespaces):

    exclude_namespaces = ",".join("metadata.namespace!=" + ns
                                  for ns in exclude_namespaces)
    return list(
        k8s_obj.objects(api).filter(namespace=all,
                                    field_selector=exclude_namespaces
                                    ))

HTTPClient.list_objects = list_objects

def randomly_kill_pods(pods, tolerance, eagerness):
    if len(pods) < tolerance:
        return

    for p in pods:
        if randint(0, 100) < eagerness:
            p.delete()
            print(f"Deleted {p.namespace}/{p.name}",)

def randomly_scale_deployments(deployments, eagerness):
    for d in deployments:
        if randint(0, 100) < eagerness:
            while True:
                try:
                    if d.replicas < 128:
                        d.replicas = min(d.replicas * 2, 128)
                    d.update()
                    print(f"scaled {d.namespace}/{d.name} to {d.replicas}",)
                    break
                except (HTTPError, exceptions.HTTPError):
                    print(
                        f"error scaling {d.namespace}/{d.name} to {d.replicas}",)
                    d.reload()
                    continue

def randomly_write_configmaps(configmaps, eagerness):
    for cm in configmaps:
        print(f"Checking {cm.namespace}/{cm.name}")
        if cm.obj.get("immutable"):
            continue

        if randint(0, 100) < eagerness:
            for k, v in cm.obj["data"].items():
                cm.obj["data"][k] = paragraph()

            print(f"Lorem Impsum in {cm.namespace}/{cm.name}",)

def main(api, exclude_namespaces, agent):
    while True:
        pods = api.list_objects(Pod, exclude_namespaces)
        deployments = api.list_objects(Deployment, exclude_namespaces)
        configmaps = api.list_objects(ConfigMap, exclude_namespaces)

        if agent.config.tantrumMode:
            randomly_kill_pods(pods,
                               agent.config.podTolerance,
                               agent.config.eagerness)

        if agent.config.cancerMode:
            randomly_scale_deployments(deployments,
                                       agent.config.eagerness)

        if agent.config.ipsumMode:
            randomly_write_configmaps(configmaps,
                                      agent.config.eagerness)

        sleep(agent.config.pauseDuration)