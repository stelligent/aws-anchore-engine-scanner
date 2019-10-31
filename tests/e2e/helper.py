'''
Helper script for end-to-end testing
'''
import os
import boto3

class ManageAWSResources(object):
	'''
	Get boto3 resources
	'''
	def __init__(self):
		'''
		Declare function initialization variable
		'''
		self.region = os.environ['AWS_DEFAULT_REGION']
		self.cfn = boto3.client('cloudformation', region_name=self.region)

	def get_stack_status(self, stack_name):
		'''
		Get deployed stack status from stack object
		'''
		status = self.cfn.describe_stacks(StackName=stack_name)
		return status['Stacks'][0]['StackStatus']
		