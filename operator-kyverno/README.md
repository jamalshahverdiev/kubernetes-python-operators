# Steps

### Install `Kyverno`

```bash
$ chart_version=$(helm search repo kyverno/kyverno --versions | grep -v NAME | head -n1 | awk '{ print $2 }')
kyverno/kyverno                 3.0.3           v1.10.2         Kubernetes Native Policy Management               
$ helm show values kyverno/kyverno --version $chart_version > custom-values-$chart_version.yaml
$ helm install kyverno kyverno/kyverno -n kyverno --create-namespace --version $chart_version -f custom-values-$chart_version.yaml
```
### Install Operator

```bash
$ kubectl create ns policy-writer
$ kubectl apply -f k8f/
```
#### Get Kyverno Version

```bash
$ kubectl get -n kyverno deployment.apps/kyverno -o=jsonpath='{$.metadata.labels.version}'
```

#### To test this we can create new ns and check it there

```bash
$ kubectl create ns check-kyverno
$ kubectl apply -f applied-resources/
```