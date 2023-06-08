# Get Kyverno Version

```bash
$ kubectl get -n kyverno deployment.apps/kyverno -o=jsonpath='{$.metadata.labels.version}'
```