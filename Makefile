# RESOURCE DEPLOYMENT FOR ANCHORE ENGINE

REGION ?= us-east-2
PROFILE ?= set-a-profile
ACCOUNT_ID ?= account-id-number
USERNAME ?= aws-user-name

export DOCKER_BUILDKIT=1
export AWS_DEFAULT_REGION=$(REGION)

TAG=1.0
IMAGE=demo/anchore-engine
TEST_IMAGE=tested/nginx
DOCKERFILE_PATH=anchore/anchore-engine/

default: all

#############
### LOGIN ###
#############
# get temporary mfa credentials
# USAGE: make get-cred REGION=xx-xxxx-x PROFILE=xxxx ACCOUNT_ID=xxxxx USERNAME=xxxx TOKEN=xxxx
get-cred:
	@echo "=== Creating a MFA-protected temporary session... ==="
	chmod +x tasks/scripts/get_temp_cred.sh
	bash tasks/scripts/get_temp_cred.sh $(ACCOUNT_ID) $(USERNAME) $(PROFILE) $(REGION) $(TOKEN)
	@echo "===== Temporary credential session ready!!! ====="

#############
### BUILD ###
#############
build:
	@echo "=== Building Image ==="
	docker build \
		--build-arg AWS_PROFILE=$(AWS_PROFILE) \
		--build-arg AWS_ACCESS_KEY_ID=$(AWS_ACCESS_KEY_ID) \
		--build-arg AWS_SECRET_ACCESS_KEY=$(AWS_SECRET_ACCESS_KEY) \
		--build-arg AWS_SESSION_TOKEN=$(AWS_SESSION_TOKEN) \
		--target prod \
	  	-t aws-anchore-engine:prod .

build-test:
	@echo "=== Building Test Image ==="
	docker build \
		--build-arg AWS_PROFILE=$(AWS_PROFILE) \
		--build-arg AWS_ACCESS_KEY_ID=$(AWS_ACCESS_KEY_ID) \
		--build-arg AWS_SECRET_ACCESS_KEY=$(AWS_SECRET_ACCESS_KEY) \
		--build-arg AWS_SESSION_TOKEN=$(AWS_SESSION_TOKEN) \
		--target test \
	  	-t aws-anchore-engine:test .

###############
### DEVELOP ###
###############
develop:
	@echo "=== Develop ==="
	docker run -it --rm \
		-e AWS_PROFILE \
		-e AWS_DEFAULT_REGION \
		-e AWS_ACCESS_KEY_ID \
		-e AWS_SECRET_ACCESS_KEY \
		-e AWS_SESSION_TOKEN \
		-v $(PWD):/src \
		-w /src \
		aws-anchore-engine:test

############
### TEST ###
############
test-%:
	@echo "=== Testing and Validating CFN templates ==="
	docker run -it --rm \
		-e AWS_PROFILE \
		-e AWS_DEFAULT_REGION \
		-e AWS_ACCESS_KEY_ID \
		-e AWS_SECRET_ACCESS_KEY \
		-e AWS_SESSION_TOKEN \
		-v $(PWD):/src \
		aws-anchore-engine:test \
		make $*
lint:
	python -m pylint anchore tasks

validate:
	python tests/validate.py

security:
	bandit -r .

unit:
	python -m pytest -vv \
		-W ignore::DeprecationWarning \
		--cov-report term-missing \
		--cov=anchore \
		--cov-fail-under=95 \
		tests/unit
e2e:
	python -m pytest -vv -W ignore::DeprecationWarning tests/e2e

test:
ifeq ($(TEST),)
	$(eval CMD=test-)
else
	$(eval CMD:=)
endif
	make $(CMD)lint
	make $(CMD)validate
	make $(CMD)security
	make $(CMD)unit
# 	make $(CMD)e2e

##############
### DEPLOY ###
##############
# push container images to ECR registry
push-image:
	docker run -t --rm \
		-e AWS_PROFILE \
		-e AWS_DEFAULT_REGION \
		-e AWS_ACCESS_KEY_ID \
		-e AWS_SECRET_ACCESS_KEY \
		-e AWS_SESSION_TOKEN \
		-v $(PWD):/src \
		aws-anchore-engine:prod \
		python app_image.py

	@echo "=== Pushing local image to remote registry... ==="
	chmod +x tasks/scripts/push_image.sh
	bash tasks/scripts/push_image.sh \
		$(IMAGE) \
		$(DOCKERFILE_PATH) \
		$(ACCOUNT_ID) \
		$(TAG) \
		$(AWS_DEFAULT_REGION)
	@echo "===== Image Pushed to ECR Complete!!!! ====="

# deploy cloudformation stacks
deploy-stacks:
	docker run -t --rm \
		-e AWS_PROFILE \
		-e AWS_DEFAULT_REGION \
		-e AWS_ACCESS_KEY_ID \
		-e AWS_SECRET_ACCESS_KEY \
		-e AWS_SESSION_TOKEN \
		-v $(PWD):/src \
		aws-anchore-engine:prod \
		python index.py

# USAGE: make deploy ACCOUNT_ID=12345678901
deploy: push-image deploy-stacks

pipeline:
	docker run -t --rm \
		-e AWS_PROFILE \
		-e AWS_DEFAULT_REGION \
		-e AWS_ACCESS_KEY_ID \
		-e AWS_SECRET_ACCESS_KEY \
		-e AWS_SESSION_TOKEN \
		-v $(PWD):/src \
		aws-anchore-engine:prod \
		python pipeline.py

##############
### DELETE ###
##############
teardown:
	docker run -it --rm \
		-e AWS_PROFILE \
		-e AWS_DEFAULT_REGION \
		-e AWS_ACCESS_KEY_ID \
		-e AWS_SECRET_ACCESS_KEY \
		-e AWS_SESSION_TOKEN \
		-v $(PWD):/src \
		-w /src \
		aws-anchore-engine:prod \
		aws ecr delete-repository --repository-name $(TEST_IMAGE) --force

	docker run -it --rm \
		-e AWS_PROFILE \
		-e AWS_DEFAULT_REGION \
		-e AWS_ACCESS_KEY_ID \
		-e AWS_SECRET_ACCESS_KEY \
		-e AWS_SESSION_TOKEN \
		-v $(PWD):/src \
		-w /src \
		aws-anchore-engine:prod \
		python tasks/teardown_stack.py

	docker run -it --rm \
		-e AWS_PROFILE \
		-e AWS_DEFAULT_REGION \
		-e AWS_ACCESS_KEY_ID \
		-e AWS_SECRET_ACCESS_KEY \
		-e AWS_SESSION_TOKEN \
		-v $(PWD):/src \
		-w /src \
		aws-anchore-engine:prod \
		aws ecr delete-repository --repository-name $(IMAGE) --force

all: build-test test build deploy test-e2e

.PHONY: build all test develop 
