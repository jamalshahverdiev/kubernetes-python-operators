kubectl apply -f k8s/clusterrole.yml
kubectl apply -f k8s/clusterrolebinding.yml
kubectl create namespace chaos-operator
kubectl apply -f k8s/edmund-v1beta1.yml
kubectl apply -f k8s/crd.yml
kubectl patch chaosagents.blackadder.io princeedmund1 --type merge --patch='{"spec": {"excludedNamespaces": ["kube-system", "chaos-operator"]}}'
kubectl create deployment blackadder --image=jamalshahverdiev/blackadder:v0.1.5 --replicas=1 -n chaos-operator
kubectl logs -f -n chaos-operator deployment/blackadder