from os import getenv, path
from kubernetes import config

def initialize_kube():
    
    ENVIRONMENT = getenv('DEV')
    if ENVIRONMENT:
        print ("Loading user kube config file")
        home = path.expanduser("~")
        kube_config_path = getenv("KUBE_CONFIG", home+"/.kube/config")
        config.load_kube_config(config_file=kube_config_path)
    else:
        print ("Loading In-cluster KUBECONFIG")
        config.load_incluster_config()