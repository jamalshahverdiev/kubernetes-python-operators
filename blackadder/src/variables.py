from pykube.config import KubeConfig
from pykube import all, HTTPClient, objects
from munch import munchify

config = KubeConfig.from_env()
api = HTTPClient(config)
ChaosAgent = objects.object_factory(api, "blackadder.io/v1beta1", "ChaosAgent")
# retrieves our agent configuraton from the kube-api-server
agent = list(ChaosAgent.objects(api, namespace=all))[0]
agent.config = munchify(agent.obj["spec"])
exclude_namespaces = agent.config.excludedNamespaces