#!/bin/bash

# usage:
# $ ./get_temp_cred.sh <account-id> <user name> <profile> <mfa-token value> <region>

# example:
# ./get_temp_cred.sh XXXXXXXXXXXX username stelligent us-east-2 123456 

# NOTE: generate a MFA Token before running this script using aws console or an authenticator

unset AWS_ACCESS_KEY_ID
unset AWS_SECRET_ACCESS_KEY
unset AWS_SESSION_TOKEN

echo "ACCOUNT NUMBER = $1"
echo "USER NAME = $2"
echo "PROFILE ACCOUNT = $3"
echo "DEFAULT REGION = $4"
echo "MFA TOKEN = $5"

# Get the MFA-protected session details
TEMP_CREDS=$(aws sts get-session-token \
	--duration-seconds 129600 \
	--serial-number arn:aws:iam::$1:mfa/$2 \
	--profile $3 \
	--token-code $5 \
	--region $4 \
	--query 'Credentials.[SecretAccessKey,AccessKeyId,SessionToken]' \
	--output text)

aws_access_key_id=$(echo ${TEMP_CREDS} | cut -f2 -d ' ')
aws_secret_access_key=$(echo ${TEMP_CREDS} | cut -f1 -d ' ')
aws_session_token=$(echo ${TEMP_CREDS} | cut -f3 -d ' ')

echo "AWS_PROFILE=${3}"
echo "AWS_ACCESS_KEY_ID=${aws_access_key_id}"
echo "AWS_SECRET_ACCESS_KEY=${aws_secret_access_key}"
echo "AWS_SESSION_TOKEN=${aws_session_token}"

# Export Variables
export AWS_PROFILE=${3}
export AWS_ACCESS_KEY_ID=${aws_access_key_id}
export AWS_SECRET_ACCESS_KEY=${aws_secret_access_key}
export AWS_SESSION_TOKEN=${aws_session_token}
