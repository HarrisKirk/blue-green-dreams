# blue-green-dreams

# Overview

A trivial web application (for now) whose deployment is fully automated 
via kubernetes and linode.  

"Blue Green Dreams" refers a) the dream of blue-green deployments of kubernetes clusters and b) the dream (present and future) of a deeply human and colorful reality.

It completely builds, deploys, tests and destroys a web application running on a k8s cluster.

![Architecture Vision](blue-green-arch.png)

# Development Environment
A make target will perform steps below (without pushing to dockerhub)

# Getting Started

* ```$ make build```
* ```$ make build_deploy```
* ```$ make alias```
* cut-paste the alias command or place into .bashrc
* Ensure your API key is set: LINODE_CLI_TOKEN=f1bb76c659875deec37108a58xxxxx
* Try the following commands
  
* ```$ bgdctl deploy dev```
* ```$ bgdctl switch-create```
* ```$ bgdctl switch-delete```




