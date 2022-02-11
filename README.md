# Edge Offloading on Microservice Architectures
This is proactive fault-tolerant edge offloading framework modeled as Markov Decision Process (MDP) based on offloading service availability predictions from Support Vector Regression (SVR). The framework is composed out of following components:

- **Decision engine**: computes the offloading decision policy,
- **Prediction engine**: estimates future offloading service availability on the remote offloading site,
- **Failure monitor**: monitors local system operations and logs failure events into local failure file,
- **Failure detector**: detects offloading failures during runtime execution and collects the failure estimation data,
- **Resource monitor**: collects resource information about remote infrastructure,
- **Application profiler**: profiles resource requirements of underlying mobile applications.

<img width="627" alt="edge_offloading_model" src="https://user-images.githubusercontent.com/89394269/153574960-a9df1b15-5ea7-42b3-90cc-59c6a149c1eb.png">

The workflow begins with the failure monitor which collects historical failure trace logs and forwards them to the prediction engine (step 1a). Subsequently, the prediction engine estimates the service availability of each offloading site and sends information to the mobile device (step 2a). Simultaneously, the application profiler and the resource monitor collect information about mobile application requirements and remote infrastructure capabilities (step 2b and 2c). These data are used by the decision engine (steps 3a, 3b, and 3c) to output the offloading decision policy (Step 4a), based on which task offloading is performed (Step 5a and 5b).

<hr>

The repository consists of following directory elements:

- *common*: contains common features related to the entire edge offloading application,
- *database*: contains SQL injection file for populating PostgreSQL database with necessary parameters,
- *kubernetes*: contains YAML deployment and service configuration files for edge offloading application,
- *mobile device*: contains source and docker files for micro-services deployed on mobile device,
- *offloading site*: contains source and docker files for micro-services deployed on remote offloading sites,

<hr>

<br/>

## Prototype Implementation
The framework is based on microservice architecture where microservices are containerized in Docker containers and executed on the Kuberentes cluster. The containers are abstracted as Kubernetes services and exposed to the external devices/users as a offloading service. 

### Cluster Networking
The Raspberry Pi (RPi) nodes are used as single-hop away edge nodes. They are configured as Wi-Fi hostspots and have the responsibility to provide wireless connectivity to nearby mobile device. Configuration requires installation of local DHCP and DNS servers (dnsmasq software package) which provides control over mobile IP address space.

The RPi nodes are located within private IP subnet while cloud node is in the public IP subnet which can causes networking issues due to firewall restrictions and NAT address translations. Hence, the private virtual networking solution called OpenVPN is deployed which bypasses aforementioned issues.

### Microservice Containerization
Microservices are developed as Python applications (version 3.6) and containerized using Docker. Docker buildx command-line interface (CLI) plugin is installed to utilize machine processor emulator QEMU to build a common Docker container image for both RPi ARMv7 edge devices and AMD64 cloud-class host server. 

Micro-services on the mobile device are developed using Python Kivy mobile cross-platform framework. It is developed for Android OS mobile devices. These micro-services do not have to be containerized.

### Offloading Service Deployment
Offloading HTTP requests from mobile device are handled by Flask micro web service on each remote offloading site. It is instantiate as an micro-service docker container on each of the remote offloading site. It is deployed as part of single Kubernetes pod together with the failure monitor and prediction engine micro-services. This pod is abstracted as a Kubernets offloading service exposed publically through HTTP URL address. Additionally, the NGINX reverse proxy is employed to redirect mobile HTTP requests to appropriate offloading services. Combining both aforementioned web services, the offloading services are available to the mobile device for task offloading through HTTP protocol.

<br/>

## Experimental Test-bed
The edge offloading framework is evaluated on the test-bed shown in the following figures. Huawei P Smart Z is a mobile device, RPis are edge nodes, and AMD64 is used to simulate a cloud data center.

<p align="left">
  <img width="350" alt="infrastructure_schematics" src="https://user-images.githubusercontent.com/89394269/153597551-3dd0423b-503e-4490-9047-90a9864c0e62.png" align="left">
  <img width="200" alt="amd_server" src="https://user-images.githubusercontent.com/89394269/153597579-d5386de8-a2d2-4339-9b5e-b0e8fa86eb3a.png" align="center">
  <img width="200" alt="cluster_config" src="https://user-images.githubusercontent.com/89394269/153598398-426704be-f909-4b3c-b98a-6717d0d43fab.png" align="right">
</p>
