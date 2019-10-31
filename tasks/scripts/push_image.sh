#!/bin/bash

#############################################################################################
# This script builds, tag and push docker images into AWS ECR 
#     Note - Ensure the ECR repository does exist in the registry         																																
#     Usage - ./push_image.sh \
#				<image-name> \
#				<dockerfile-path> \
#				<aws-account-id> \
#				<image-tag> \
#				<region>	
#############################################################################################

# authenticate your Docker client to AWS ECR registry
echo Logging in to Amazon ECR...
ECR_LOGINS=$(aws ecr get-login --no-include-email --region ${5})

echo "creating login temp file"
_ECR_LOGINS=$(echo ${ECR_LOGINS} | tr -d '\r')
echo ${_ECR_LOGINS} > ecr_logins.out

echo "login into ecr"
$(cat ecr_logins.out)

# build image
echo Building images....
docker build -t ${1} -f ${2}/Dockerfile .

# tag image
echo Tagging built image....
docker tag ${1} ${3}.dkr.ecr.${5}.amazonaws.com/${1}:${4}

# push image
echo Pushing built image to AWS ECR.....
docker push ${3}.dkr.ecr.${5}.amazonaws.com/${1}:${4}

echo "removing temp file"
rm -rf ecr_logins.out

echo ${1} Image Deployment Complete!
