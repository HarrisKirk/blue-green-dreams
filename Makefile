.PHONY: help build
.SILENT: 
DOCKER_IMAGE = $(DOCKER_IMAGE_NAME):latest
DOCKER_IMAGE_NAME = cjtkirk1/gwa
APP_TAG = `git describe --tags --always`

help:
	@echo ""
	@echo "Makefile for gwa - Good Weather Application"
	@echo ""
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

build: ## Basic build of gwa image
	# docker image build --tag $(DOCKER_IMAGE) . 1> /dev/null;\
	docker image build --tag $(DOCKER_IMAGE) . ;\

_push: ## Push image to dockerhub
	echo "The tag is $(APP_TAG)"
	docker tag $(DOCKER_IMAGE_NAME):latest $(DOCKER_IMAGE_NAME):$(APP_TAG)
	docker image push $(DOCKER_IMAGE_NAME):latest
	docker image push $(DOCKER_IMAGE_NAME):$(APP_TAG)