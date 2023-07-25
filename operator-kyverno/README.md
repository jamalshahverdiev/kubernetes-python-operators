# Install operator itself

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