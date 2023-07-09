### Patch Namespace `annotation`

```bash
$ kubectl patch namespace checkrestarter -p '{"metadata":{"annotations":{"collectdeployments":"allow"}}}'
```

#### Docker build and PUSH

```bash
$ docker build -t jamalshahverdiev/deployrestarter:1.0.3 .
$ docker push jamalshahverdiev/deployrestarter:1.0.3
```
