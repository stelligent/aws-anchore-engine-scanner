'''
Mock cloudformation boto3 API calls
'''
import boto3
import botocore
import tests.config as config
from botocore.stub import Stubber

def get_stack_status(stack_status_response, expected_params):
    client = boto3.client (
        'cloudformation',
        aws_access_key_id=config.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY,
        aws_session_token=config.AWS_SESSION_TOKEN,
    )
    stubber = Stubber(client)

    stubber.add_response('stack_status', stack_status_response, expected_params)
    stubber.activate()
    return client
    