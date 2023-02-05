The Blackadder - a chaos engineering operator
=============================================

This a companion repository for the article in
the German Entwickler magazine about writing
Kubernetes Operators with Python.

The Operator's algorithm in pseudo code is:

```
client = connect_to_kubernetes()

# retrieves our agent configuration from the kube-api-server
chaos_agent = client.get_chaos_agent()

while True:
      pods = client.list_pods(exclude_namespaces)
      deployments = client.list_deployments(exclude_namespaces)
      namespaces =   client.list_configmaps(exclude_namespaces)
      
      if chaos_agent.tantrum:
         randomly_kill_pods(pods, chaos_agent.tolerance, chaos_agent.eagerness)

      if chaos_agent.cancer:
         randomly_scale_deployments(deployments, chaos_agent.eagerness)
      
      if chaos_agent.ipsum:
         randomly_write_configmaps(configmaps, chaos_agent.eagerness)

      time.sleep(chaos_agent.pause)
```

**WARNING**

DON'T RUN THIS IN PRODUCTION !!!  
DON'T RUN THIS IN PRODUCTION !!!  
DON'T RUN THIS IN PRODUCTION !!!  

## Why the name?
The name is obvisiouly inspired from the
british comedy [The Blackadder][1].

[1]: https://en.wikipedia.org/wiki/The_Black_Adder
