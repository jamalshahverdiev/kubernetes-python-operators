from src.functions import restart_deployments_if_needed, initialize_kube

if __name__ == "__main__":
    initialize_kube()
    restart_deployments_if_needed()        