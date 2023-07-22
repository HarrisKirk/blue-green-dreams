.PHONY: help build

.SILENT: 
PROJECT_ACRONYM = bgd
DOCKER_IMAGE_NAME = cjtkirk1/gwa
DOCKER_IMAGE = $(DOCKER_IMAGE_NAME):latest	
DOCKER_DEPLOY_IMAGE_NAME = cjtkirk1/$(PROJECT_ACRONYM)_deploy
DOCKER_DEPLOY_IMAGE = $(DOCKER_DEPLOY_IMAGE_NAME):latest
DOCKER_ENV_STRING = -e LINODE_CLI_TOKEN -e LINODE_ROOT_PASSWORD -e WEATHER_API_TOKEN
DOCKER_DEPLOY_VOLUMES = -v ~/.kube:/root/.kube

APP_TAG = `git describe --tags --always`

help:
	@echo ""
	@echo "Makefile for PROJECT_ACRONYM = $(PROJECT_ACRONYM)"
	@echo ""
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

build: ## Basic build of $(PROJECT_ACRONYM): ie, image with all application code
	docker image build --quiet --tag $(DOCKER_IMAGE) . ;\

build_deploy: ## Basic build of $(PROJECT_ACRONYM)_deploy: ie, image with all deployment code
	docker image build --quiet -f Dockerfile_deploy --tag $(DOCKER_DEPLOY_IMAGE_NAME) . ;\

_push: ## Push application image to dockerhub
	echo "The tag is $(APP_TAG)"
	docker tag $(DOCKER_IMAGE_NAME):latest $(DOCKER_IMAGE_NAME):$(APP_TAG)
	docker image push $(DOCKER_IMAGE_NAME):latest
	docker image push $(DOCKER_IMAGE_NAME):$(APP_TAG)

test_deploy_unit: build_deploy ## run all unit tests
	docker container run $(DOCKER_ENV_STRING) --rm --name $(PROJECT_ACRONYM)_deploy --network host --entrypoint "python" $(DOCKER_DEPLOY_IMAGE_NAME) -m unittest test/test_basic.py ;\

test: ## Test the $(PROJECT_ACRONYM) app  
	./test.sh

deploy_test: test_deploy_unit ## Deploy infrastructure
	docker container run $(DOCKER_ENV_STRING) --rm --name $(PROJECT_ACRONYM)_deploy --network host $(DOCKER_DEPLOY_IMAGE_NAME) deploy test

format: ## format the python code consistently
	docker container run -v $(PWD)/gwa:/gwa --entrypoint "black" $(DOCKER_IMAGE_NAME) --verbose --line-length=120 /gwa
	docker container run -v $(PWD)/gwa-deploy:/gwa-deploy --entrypoint "black" $(DOCKER_DEPLOY_IMAGE_NAME) --verbose --line-length=120 /gwa-deploy

web: build ## Launch a local docker flask site
	docker container rm -f $(PROJECT_ACRONYM) ;\
	docker container run -e WEATHER_API_TOKEN --rm -it --name $(PROJECT_ACRONYM) --network host --detach cjtkirk1/gwa:latest ;\

alias: ## Echo an alias to run bgdctl from docker
	echo "alias bgdctl='docker container run $(DOCKER_DEPLOY_VOLUMES) $(DOCKER_ENV_STRING) --rm --name $(PROJECT_ACRONYM)_deploy --network host $(DOCKER_DEPLOY_IMAGE_NAME)'"
