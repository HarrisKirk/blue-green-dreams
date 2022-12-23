.PHONY: help build
.SILENT: 
BCI_CONTAINER_WORKDIR = /opt/devops-bci/gwa
DOCKER_IMAGE_NAME = cjtkirk1/gwa
DOCKER_IMAGE = $(DOCKER_IMAGE_NAME):latest	
DOCKER_RUN_CMD = docker container run --rm --name=gwa --workdir $(BCI_CONTAINER_WORKDIR) --user $(id -u):$(id -g)
APP_TAG = `git describe --tags --always`

help:
	@echo ""
	@echo "Makefile for gwa - Good Weather Application"
	@echo ""
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

build: ## Basic build of gwa image
	docker image build --tag $(DOCKER_IMAGE) . ;\

_push: ## Push image to dockerhub
	echo "The tag is $(APP_TAG)"
	docker tag $(DOCKER_IMAGE_NAME):latest $(DOCKER_IMAGE_NAME):$(APP_TAG)
	docker image push $(DOCKER_IMAGE_NAME):latest
	docker image push $(DOCKER_IMAGE_NAME):$(APP_TAG)

gwa: build ## Enter the command line environment 
	$(DOCKER_RUN_CMD) -it $(DOCKER_IMAGE)