# blue-green-dream

![Architecture Vision](blue-green-arch.png)

A trivial web application (for now) whose deployment is fully automated 
via kubernetes and linode.  

It completely builds, deploys, tests and destroys a web application running on a k8s cluster.

# Development Environment
A make target will perform steps below (without pushing to dockerhub)

# CD via GitHub Actions
The GitHub Actions will do the following
* build the docker web app image 
* test it
* push the image to dockerhub
* build the docker image containing deployment code
* run the deployment which performs:
    * create k8s cluster in linode cloud
    * creates k8s deployment and service
    * waits for loadbalancer
    * tests the web application
    * destroys the k8s cluster and all associated artifacts


