# Prerequisites
- Every node has installed Docker and Kubernetes, properly configured (master and worker roles), and properly joined the Kubernetes cluster
- Ensure that the network connectivity is functioning properly within the cluster 

# Deploy pods
## Deploy Flannel CNI plugin
Deploy Flannel CNI plugin pods after the nodes joined the Kubernetes cluster but before any other offloading application pod deployment:

```
kubectl apply -f kube-flannel.yaml
```

The plugin is necessary for networking between pods and services located on different node locations.

## Deploy PostgreSQL database
This database pod contains all the necessary information for the experimental evaluation. This pod has to be deployed before any offloading-site service pod. 
On Kubernetes master node execute the following command:

```
kubectl apply -f database-deploy.yaml
kubectl apply -f database-service.yaml
```

The first command Deployment spec determines which container images will be included in the pod, how many pods will be deployed, and their node location. Service spec defines which pod
deployments will be included under the same service. Service is nothing more than an abstraction of the underlying application (pod) to the end-user. 
The aforementioned YAML file contains both specs. 

## Deploy offloading application and service
On Kubernetes master node execute the following command:

```
kubectl apply -f off-site-deploy.yaml
```

This YAML file contains both deployment and service specs for all included offloading applications (cloud, edge database server, edge computational-intensive server, and 
edge regular server). Alternatively, each offloading application instance can be deployed separately:

```
kubectl apply -f cloud-site-service.yaml
kubectl apply -f edge-computational-site-service.yaml
kubectl apply -f edge-database-site-service.yaml
kubectl apply -f edge-regular-site-service.yaml
```

## Deploy ingress rules and controller
Ingress rules specify how the end-user HTTP API offloading requests will be processed and routed to offloading services:

```
kubectl apply -f off-site-ingress.yaml
```

The NGINX ingress controller as a reverse proxy interprets the above-mentioned ingress rules and executes them:

```
kubectl apply -f off-site-nginx-controller.yaml
```

In this manner, the NGINX controller exposes offloading services publically and makes them accessible to the end-user offloading requests.
