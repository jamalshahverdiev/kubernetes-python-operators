### Patch Namespace `annotation`

```bash
$ kubectl patch namespace checkrestarter -p '{"metadata":{"annotations":{"collectdeployments":"allow"}}}'
```

#### Docker build and PUSH

```bash
$ docker build -t jamalshahverdiev/deployrestarter:1.0.3 .
$ docker push jamalshahverdiev/deployrestarter:1.0.3
```

#### Drain and uncordon

```bash
$ kubectl drain db1 --ignore-daemonsets --delete-emptydir-data
$ kubectl uncordon db1
```

#### Suspend Cronjobs

```bash
$ kubectl patch cronjobs replica-checker -n replicachecker -p '{"spec" : {"suspend" : true }}'
```

#### Patch namespace `check-kyverno`

```bash
$ kubectl annotate namespace check-kyverno collectdeployments=allow --overwrite
```

#### Watch to the rsources

```bash
$ watch -n1 'for ns in checkrestarter check-kyverno; do kubectl get pods -n $ns -o wide; done'
```