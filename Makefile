.PHONY: help build
.SILENT: 
DOCKER_IMAGE_NAME = cjtkirk1/gwa
DOCKER_IMAGE = $(DOCKER_IMAGE_NAME):latest	

DOCKER_DEPLOY_IMAGE_NAME = cjtkirk1/gwa_deploy
DOCKER_DEPLOY_IMAGE = $(DOCKER_DEPLOY_IMAGE_NAME):latest

DOCKER_ENV_STRING = -e LINODE_CLI_TOKEN -e LINODE_ROOT_PASSWORD 

APP_TAG = `git describe --tags --always`

help:
	@echo ""
	@echo "Makefile for gwa - Good Weather Application"
	@echo ""
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

build: ## Basic build of gwa: ie, image with all application code
	docker image build --quiet --tag $(DOCKER_IMAGE) . ;\

build_deploy: ## Basic build of gwa_deploy: ie, image with all deployment code
	docker image build --quiet -f Dockerfile_deploy --tag $(DOCKER_DEPLOY_IMAGE_NAME) . ;\

_push: ## Push application image to dockerhub
	echo "The tag is $(APP_TAG)"
	docker tag $(DOCKER_IMAGE_NAME):latest $(DOCKER_IMAGE_NAME):$(APP_TAG)
	docker image push $(DOCKER_IMAGE_NAME):latest
	docker image push $(DOCKER_IMAGE_NAME):$(APP_TAG)

test: build ## Test the gwa app  
	./test.sh

deploy_dev: build_deploy ## Test the code to deploy infrastructure
	docker container run $(DOCKER_ENV_STRING) -it --rm --name gwa_deploy --network host $(DOCKER_DEPLOY_IMAGE_NAME) python manage.py gwa_dev

deploy_test: build_deploy ## Test the code to deploy infrastructure
	docker container run $(DOCKER_ENV_STRING) --rm --name gwa_deploy --network host $(DOCKER_DEPLOY_IMAGE_NAME) python manage.py gwa_test

format: ## format the python code consistently
	docker container run -v $(PWD)/gwa:/gwa $(DOCKER_IMAGE_NAME) black --verbose --line-length=120 /gwa;\
	docker container run -v $(PWD)/gwa-deploy:/gwa-deploy	 $(DOCKER_DEPLOY_IMAGE_NAME) black --verbose --line-length=120 /gwa-deploy;\

