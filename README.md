# aws-anchore-engine-scanner

This guide details steps and procedures you can follow to create, launch and implement your own standalone container scanning solution within AWS ecosystem.  This approach uses an opensource container scanning tool called [Anchore Engine](https://anchore.com/) as a proof-of-concept and provides examples of how Anchore integrates with your favorite CI/CD systems orchestration platforms.

For more detailed understanding of concepts and overview on Anchore Engine, visit [anchore overview](https://docs.anchore.com/current/docs/overview/)

## Architecture

Here’s how to install Anchore Engine on AWS. The below diagram shows the high-level architecture of Anchore Engine.

![Anchore-Engine High-Level Architecture](https://github.com/stelligent/aws-anchore-engine-scanner/blob/master/docs/AWS%20anchore%20engine.jpg)


## Getting Started

Before running any commands review the [prerequisites](#Prerequisites) section to ensure you have required packages and installed needed software.

### Prerequisites

Ensure that the following are installed or configured on your workstation before deploying Anchore Engine:

- [Docker](https://www.docker.com/)
- Git
- AWS CLI
- [Make](https://www.gnu.org/software/make/manual/html_node/index.html#Top)
- Github Personal Token (Stored as an ssm parameter)

### Installation

Clone this [github repository](https://github.com/stelligent/aws-anchore-engine-scanner). Configure and Setup your AWS CLI.

#### Setup Credentials

If you have MFA configure with your AWS account, run the following commands and provide appropriate parameters to each environment variables. Else, configure your AWS session on your workstation as described in [Configuring the AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html).

```make
make get-cred \
    ACCOUNT_ID=<your-aws-account-id> \
    USERNAME=<your-aws-username> \
    PROFILE=<your-aws-profile> \
    REGION=<aws-target-region> \
    TOKEN=<auth-generated-token>

```

##### Example

```make
make get-cred \
    ACCOUNT_ID=123456789012 \
    USERNAME=johndoe \
    PROFILE=stelligent \
    REGION=us-east-2 \
    TOKEN=123456

```

#### Setup production environment

Build your deployment environment with docker.

```make
make build
```

This build your local dockerized image for deploying and launching Anchore-Engine. It installs various packages as defined within the `Dockerfile` and python packages listed within the `requirements.pip` file.

#### Setup test environment

Build a testing environment within docker by running:

```make
make build-test
```

This testing image provide a local environment to run all your local testing and helps with launching a quick development environment for troubleshooting. It installs additional python packages as stipulated within `requirements-test.pip` file.

### Deployments

This deployment comprises of the various AWS resources:

 1. Amazon Elastic Container Registry (ECR) Repository
 2. Amazon VPC
    - Two public subnets
    - Two private subnets
    - NAT gateways to allow internet access for services in private subnets
    - Internet Gateway
    - Security Groups
 3. Amazon Application Load Balancer
    - Load Balancer
    - Listeners
    - Target Groups
 4. Amazon EC2
    - AutoScaling Group
    - CloudWatch
    - AWS IAM
 5. Amazon Elastic Container Service
    - Cluster
    - Services
    - Task Definitions
 6. AWS CodePipeline

The application launches Anchore-Engine and sets up CodePipeline for automatic image vulnerability scan and detection.

#### Build the Anchore-Engine Docker Image

First, create an Amazon Elastic Container Registry repository to host your Anchore Engine Docker image. Then, build the anchore-engine image on your workstation and push it to the ECR repository. This can be achieved by running the following make command.

```make
make push-image ACCOUNT_ID=<your-aws-account-id>
```

#### Deploy Anchore-Engine Server

The following command utilizes `index.py` python module as entrypoint to create CloudFormation templates using [troposphere](https://github.com/cloudtools/troposphere/tree/master/troposphere) template generator and launches all stacks for each of these AWS resources: VPC, ALB, EC2, and ECS.

Run this make command

```make
make deploy-stacks
```

Each of these stack parameters are extracted from an accompanying configuration `YAML` templates within the `configs` folder. These `YAML` templates provides each CloudFormation stack's parameters at the point of deployment as shown below.

```yaml
---
# VPC
- region: us-east-2
  resource_name: ANCHORE-VPC
  template_file: anchore_vpc.yml
  parameters:
    Environment: DEMO
    VPCCIDRBlock: 10.0.0.0/16
    PublicSubnet1CIDRBlock: 10.0.0.0/24
    PrivateSubnet1CIDRBlock: 10.0.1.0/24
    PublicSubnet2CIDRBlock: 10.0.2.0/24
    PrivateSubnet2CIDRBlock: 10.0.3.0/24

# ALB
- region: us-east-2
  resource_name: ANCHORE-ALB
  template_file: anchore_alb.yml
  parameters:
    Environment: DEMO
    Subnet1: PUBLIC-SUBNET-1
    Subnet2: PUBLIC-SUBNET-2
    VpcId: VPCID
    CIDRBLK: 10.0.0.0/8

# EC2
- region: us-east-2
  resource_name: ANCHORE-EC2-INSTANCE
  template_file: anchore_ec2_cluster.yml
  parameters:
    Environment: DEMO
    AmiId: ami-0653e888ec96eab9b
    ClusterSize: '2'
    InstanceType: m4.large
    KeypairName: anchore_demo
    CIDRBLK: 10.0.0.0/8
    OpenCIDR: 0.0.0.0/0

# ECS
- region: us-east-2
  resource_name: ANCHORE-ECS
  template_file: anchore_ecs.yml
  parameters:
    Environment: DEMO
    TargetGroup: TARGETGROUP-ARN
    AnchoreEngineImage: anchore-engine-Image
    ArchoreDatabaseImage: 'postgres:9'
    PGDATA: '/var/lib/postgresql/data/pgdata/'
    AnchoreDBPassword: mypgpassword

```

#### Launch a sample pipeline to integrate Anchore-Engine scanning using CodePipeline

Deploying your pipeline to scan either publicly available images or private registry images can be achieved by configuring your client environment with `anchore-cli` client. For detailed information on installation, setup and CLI commnands visit [anchore-cli github repository](https://github.com/anchore/anchore-cli).

For quick implementation using AWS CodePipeline with Codebuild project as a stage within your pipeline, follow examples available within the `examples` folder. The content of this directory can be copied and saved along with your application source control into a repository targeted by AWS CodePipeline as source stage.

To launch a sample pipeline to test Anchore-Engine functionality, run the following commands:

```make
make pipeline
```

This command utilizes `pipeline.py` python module to launch a CloudfFormation stack using template `pipeline.yml` with a configuration `YAML` template that defines CloudFormation parameters. Modify and update the provided configuration template in `examples/aws-codepipeline/pipeline_configs.yml` directory with information for your target application and repository using the snippet example below.

```yaml
---
# Example CodePipeline
- region: us-east-2
  resource_name: ANCHORE-CLI-PIPELINE
  template_file: examples/aws-codepipeline/pipeline.yml
  parameters:
    Environment: DEMO
    GitHubAccountName: <replace-with-your-github-account-name>
    GitHubRepoName: <replace-with-your-github-application-repository>
    GitHubBranchName: <your-target-branch> (i.e master)
    BucketName: <demo-anchore-engine-pipeline-store>

```

This stack contains a codebuild job as a `Test` Stage which executes set of defined commands within a Codebuild using a `buidlspec.yml` as shown below. This defines a collection of build commands and related settings for automating building of your application image, scanning for CVEs and issuing a **PASS/FAIL** status based on scan results. If each each result passes, then each image is tagged and pushed to a staging repository.

```yaml
# Test Anchore Engine scanning functionality within a pipeline stage
version: 0.2

env:
  variables:
    TAG: latest
    SOURCE_IMAGE: nginx:latest
    STAGE_REPO_NAME: tested/nginx
    TESTED_SAMPLE_IMAGE: ${ACCOUNT_ID}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com/${STAGE_REPO_NAME}

phases:
  install:
    runtime-versions:
      python: 3.7
      docker: 18
    commands:
      - nohup /usr/local/bin/dockerd --host=unix:///var/run/docker.sock --host=tcp://127.0.0.1:2375 --storage-driver=overlay2&
      - timeout 15 sh -c "until docker info; do echo .; sleep 1; done"
      - echo Entering the install phase..... 
      - apt-get update -y
      - apt-get -y install python-pip -y
      - pip3 install awscli --upgrade --user
      - pip install boto3
      - pip install anchorecli

  pre_build:
    commands:
      - echo Image repository setup started on `date`
      - echo ECR Setup...
      - echo Logging into AWS ECR...
      - $(aws ecr get-login --no-include-email --region ${AWS_DEFAULT_REGION})
      - echo Configure Anchore Client...
      - export ANCHORE_CLI_PASS=foobar
      - export ANCHORE_CLI_USER=admin

  build:
    commands:
      - echo Deployment started on `date`
      - echo Testing...
      - anchore-cli --version
      - anchore-cli --debug system status
      - anchore-cli --debug image add ${SOURCE_IMAGE}
      - echo 'Waiting for image to finish analysis'
      - anchore-cli image wait ${SOURCE_IMAGE}
      - echo 'Analysis complete'
      - anchore-cli image vuln ${SOURCE_IMAGE} os
      - if [ '${ANCHORE_SCAN_POLICY}' = 'true' ] ; then anchore-cli evaluate check ${SOURCE_IMAGE}  ; fi
      - echo Build started on `date`
      - echo Building Tested Sample Image... 
      - docker build -t ${STAGE_REPO_NAME} .

  post_build:
    commands:
      - echo "Tag image to Docker Hub"
      - docker tag ${STAGE_REPO_NAME}:${TAG} ${ACCOUNT_ID}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com/${STAGE_REPO_NAME}:${TAG}
      - echo "Pushing image to Docker Hub"
      - docker push ${ACCOUNT_ID}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com/${STAGE_REPO_NAME}:${TAG}

```

The pipeline is triggered after the AWS CloudFormation stack creation is complete. You can log in to AWS Management Console to monitor the status of the pipeline. The vulenrability scan information is avaialble both within the CodeBuild online terminal or CloudWatch Logs and a JSON formatted result can be extracted for further analysis.

#### Deploy All

Run the following commands to deploy all above mentioned resources needed for Anchore Engine.

```make
make deploy ACCOUNT_ID=<your-aws-account-id>
```

This command combines all three above mentioned deployment and launches all resources with a click of a single command, provided all requirements are met as stated in [requirements](#Prerequisites).

#### Clean-Up

Run the following commands to teardown all deployed resources within AWS:

```make
make teardown
```

### Testing

Run all test locally:

```make
make test
```

This runs unit tests, linting and security checks for each of the deployments.

#### Linting

```make
make test-lint
```

Runs Pylint on every module created within this deployments.

#### Template Validation

```make
make test-validate
```

This executes clouformation template linting uisng [`cfn-lint`](https://pypi.org/project/cfn-lint/), security scan using [`cfn-nag`](https://github.com/stelligent/cfn_nag), and template validation using [`cfn boto3 calls`](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html).

#### Security Tests

```make
make test-security
```

Executes security linting of all python scripts and methods within your deployments files using a security tool - [`bandit`](https://pypi.org/project/bandit/).

#### Unit Tests

```make
make test-unit
```

Runs a Python Pytest test on each functions within `anchore` folder with a target coverage failure under *__95%__*

#### End-to-End Tests

```make
make test-e2e
```

This test for successful deployment of each of your CloudFormation stacks and anchore-engine account lifecycle. This should be ran after your Anchore-Engine deployment is up and running.

## Contributing

None yet

## Versioning

None yet

## License

MIT Licencse
Copyright (c) 2019 Mphasis-Stelligent, Inc. https://stelligent.com
