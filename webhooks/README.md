#### Generate certificate

```bash
$ openssl req \
  -newkey rsa:2048 \
  -nodes \
  -keyout server.key \
  -x509 \
  -days 365 \
  -out server.crt \
  -subj "/CN=webhook-service.kubehook.svc" \
  -extensions SAN \
  -config <(cat /etc/ssl/openssl.cnf \
    <(printf "\n[SAN]\nsubjectAltName=DNS:webhook-service.kubehook.svc"))

$ mkdir certs && mv server.crt server.key certs/
$ docker build -t jamalshahverdiev/kubehook:0.0.1 . && docker push jamalshahverdiev/kubehook:0.0.1
```

#### Don't forget to change image version `jamalshahverdiev/kubehook:0.0.1` inside of the `k8s/deployment.yaml` file


#### Get base64 code and add it as `value` to the key `webhooks.clientConfig.caBundle` inside of the `k8s/webhook-configuration.yaml` for validation and mutation endpoints.   

```bash
$ cat certs/server.crt | base64 | tr -d '\n'
$ kubectl describe pod test-pod
```

#### Apply needed manifests 

```bash
$ kubectl apply -f k8s/ns.yaml
$ kubectl apply -f k8s/service.yaml
$ kubectl apply -f k8s/deployment.yaml
$ kubectl apply -f k8s/webhook-configuration.yaml
```

#### To test it we can use these manifests

```bash
$ kubectl apply -f applied-resources/pod.yaml
$ kubectl apply -f applied-resources/deployment.yaml
```

