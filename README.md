# Edge Offloading on Microservice Architectures
This is proactive fault-tolerant edge offloading framework modeled as Markov Decision Process (MDP) based on offloading service availability predictions from Support Vector Regression (SVR). The framework is composed out of following components:

- *Decision engine* computes the offloading decision policy from which offloading decisions are derived and executed,
- *Prediction engine* estimates future offloading service availability on the remote offloading site based on local historical failure trace logs,
- *Failure monitor* monitors local system operations on remote offloading site and logs failure events intro local failure file,
- *Failure detector* detects failures during runtime execution on remote offloading service sites and collects the failure estimation data from remote prediction engine,
- *Resource monitor* collects resource information about remote infrastructure,
- *Application profiler* profiles resource requirements of underlying mobile applications.

<img width="627" alt="edge_offloading_model" src="https://user-images.githubusercontent.com/89394269/153574960-a9df1b15-5ea7-42b3-90cc-59c6a149c1eb.png">

The workflow is as following. First, failure monitor collects historical failure trace logs and forwards them to the prediction engine (step 1a). Subsequently, the prediction engine estimates the service availability of each offloading site and sends information to the mobile device (step 2a). Simultaneously, the application profiler and the resource monitor collect information about mobile application requirements and remote infrastructure capabilities (step 2b and 2c). These data are used by the decision engine (steps 3a, 3b, and 3c) to output the offloading decision policy (Step 4a), based on which task offloading is performed (Step 5a and 5b).

# Prototype Implementation
The framework is based on microservice architecture where microservices are containerized in Docker containers and executed on the Kuberentes cluster. The containers are abstracted as Kubernetes services and exposed to the external devices/users as a offloading service. 

## Cluster Networking
The Raspberry Pi (RPi) nodes are used as single-hop away edge nodes. They are configured as Wi-Fi hostspots and have the responsibility to provide wireless connectivity to nearby
mobile device. Configuration requires installation of local DHCP and DNS servers which provides control over mobile IP address space.

The RPi nodes are located within private IP subnet while cloud node is in the public IP subnet which can causes networking issues due to firewall restrictions and NAT address translations. Hence, we deploy the private virtual networking solution called OpenVPN which bypasses aforementioned issues.
