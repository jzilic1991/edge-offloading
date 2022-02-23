# Edge Offloading on Microservice Architectures
This is a proactive fault-tolerant edge offloading framework modeled as Markov Decision Process (MDP) based on offloading service availability predictions from Support Vector Regression (SVR). The framework is composed of the following components:

- **Decision engine**: computes the offloading decision policy,
- **Prediction engine**: estimates future offloading service availability on the remote offloading site,
- **Failure monitor**: monitors local system operations and logs failure events into local failure file,
- **Failure detector**: detects offloading failures during runtime execution and collects the failure estimation data,
- **Resource monitor**: collects resource information about remote infrastructure,
- **Application profiler**: profiles resource requirements of underlying mobile applications.

<img width="627" alt="edge_offloading_model" src="https://user-images.githubusercontent.com/89394269/153574960-a9df1b15-5ea7-42b3-90cc-59c6a149c1eb.png">

The workflow begins with the failure monitor which collects historical failure trace logs and forwards them to the prediction engine (step 1a). Subsequently, the prediction engine estimates the service availability of each offloading site and sends information to the mobile device (step 2a). Simultaneously, the application profiler and the resource monitor collect information about mobile application requirements and remote infrastructure capabilities (steps 2b and 2c). These data are used by the decision engine (steps 3a, 3b, and 3c) to output the offloading decision policy (Step 4a), based on which task offloading is performed (Step 5a and 5b).

<hr>

The repository consists of the following directory elements:

- *common*: contains common features related to the entire edge offloading application,
- *database*: contains SQL injection file for populating PostgreSQL database with necessary parameters,
- *kubernetes*: contains YAML deployment and service configuration files for the edge offloading application,
- *mobile device*: contains source files for micro-services deployed on the mobile device,
- *offloading site*: contains source and docker files for micro-services deployed on remote offloading sites,

<hr>

<br/>

## Prototype Implementation
The framework is based on microservice architecture where microservices are containerized in Docker containers and executed on the Kubernetes cluster. The containers are abstracted as Kubernetes services and exposed to the external devices/users as an offloading service. 

### Cluster Networking
The Raspberry Pi (RPi) nodes are used as single-hop away edge nodes. They are configured as Wi-Fi hotspots and have the responsibility to provide wireless connectivity to the nearby mobile device. Configuration requires installation of local DHCP and DNS servers (dnsmasq software package) which provides control over mobile IP address space.

The RPi nodes are located within the private IP subnet while the cloud node is in the public IP subnet which can cause networking issues due to firewall restrictions and NAT address translations. Hence, the private virtual networking solution called OpenVPN is deployed which bypasses the aforementioned issues.

### Microservice Containerization
Microservices are developed as Python applications (version 3.6) and containerized using Docker. Docker buildx command-line interface (CLI) plugin is installed to utilize machine processor emulator QEMU to build a common Docker container image for both RPi ARMv7 edge devices and AMD64 cloud-class host server. 

Micro-services on the mobile device are developed using Python Kivy mobile cross-platform framework. It is developed for Android OS mobile devices. These micro-services do not have to be containerized.

### Offloading Service Deployment
Offloading HTTP requests from the mobile device are handled by Flask micro web service on each remote offloading site. It is instantiated as a micro-service docker container on each of the remote offloading sites. It is deployed as part of a single Kubernetes pod together with the failure monitor and prediction engine micro-services. This pod is abstracted as a Kubernetes offloading service exposed publically through an HTTP URL address. Additionally, the NGINX reverse proxy is employed to redirect mobile HTTP requests to appropriate offloading services. Combining both aforementioned web services, the offloading services are available to the mobile device for task offloading through HTTP protocol.

<br/>

## Experimental Test-bed
The edge offloading framework is evaluated on the test-bed shown in the following figures. Huawei P Smart Z is a mobile device, RPis are edge nodes, and AMD64 is used to simulate a cloud data center.

<p align="left">
  <img width="350" alt="infrastructure_schematics" src="https://user-images.githubusercontent.com/89394269/153597551-3dd0423b-503e-4490-9047-90a9864c0e62.png">
  <img width="200" alt="amd_server" src="https://user-images.githubusercontent.com/89394269/153597579-d5386de8-a2d2-4339-9b5e-b0e8fa86eb3a.png">
  <img width="200" alt="cluster_config" src="https://user-images.githubusercontent.com/89394269/153598398-426704be-f909-4b3c-b98a-6717d0d43fab.png">
</p>

<br/>

## Datasets
Datasets used in our work are:
-Los Alamos National Laboratory (LANL) failure dataset of high-performance computing (HPC) clusters [1]
-LiveLab application usage traces [2]
<br/>

## Acknowledgments
This work is partially funded through the Rucon project (Runtime Control in Multi Clouds), FWF Y 904 START-Programm 2015.

## References
[1] Schroeder, Bianca, and Garth A. Gibson. "A large-scale study of failures in high-performance computing systems." IEEE transactions on Dependable and Secure Computing 7.4 (2009): 337-350.

[2] Shepard, Clayton, et al. "LiveLab: measuring wireless networks and smartphone users in the field." ACM SIGMETRICS Performance Evaluation Review 38.3 (2011): 15-20.
