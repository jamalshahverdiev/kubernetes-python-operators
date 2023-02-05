from src.functions import main 
from src.variables import api, exclude_namespaces, agent

if __name__ == "__main__":
    print("This is the blackadder version 0.1.5")
    print("Ready to start a havoc in your cluster")
    main(api, exclude_namespaces, agent)
