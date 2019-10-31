'''
Deploys AWS Cloudformation Stacks
'''
import yaml
import boto3
import botocore

# pylint: disable=no-member
def load_yaml_file(yaml_file):
    '''
    Read input configuration file that contains
    stack creation arguments and parameters

    Args:
      yaml_file: .yaml file to be read
    Returns:
      The input dictionary found returned as a list
    Raises:
      Exception: If no matching artifact is found
    '''
    try:
        # Get the configuration parameters
        file = open(yaml_file).read()
        config = list(yaml.load_all(file))[0]

    except Exception as exc:
        # We're expecting the user parameters to be encoded as YAML
        # so we can pass multiple values. If the YAML can't be decoded
        # then return failure with a helpful message.
        print(exc)
        raise Exception('Input configuration parameters could not be decoded as YAML')

    return config

def build_stack_parameters(config):
    '''
    Read input configuration file that contains
    stack creation arguments and parameters to create stack

    Args:
        config: dictionary containing parameter values to be read
    Returns:
        List of Parameters for cloudformation template
    '''
    params_list = []
    for key, value in config.items():
        params = {}
        params['ParameterKey'] = key
        params['ParameterValue'] = value
        params_list.append(params)

    return params_list

def regional_client(config):
    '''
    Read input configuration file that contains
    stack creation arguments and parameters
    and read Region parameter to define regional
    client to create stack

    Args:
      config: loaded yaml file to be read
    Returns:
      The low-level client representing AWS CloudFormation
    Raises:
      Exception: If no matching region is found or
      client could not be extracted from yaml file
    '''
    try:
        # get the loaded yaml file and extract "Region" parameter to define cloudformation client
        region = config['region']
        cfn = boto3.client('cloudformation', region_name=region)
        return cfn
    except botocore.exceptions.ClientError as exc:
        return exc

# pylint: disable=no-else-return
class DeploymentManager():
    '''
    Manage AWS resource deployment
    '''
    def __init__(self, config):
        self.cfn = regional_client(config)

    def stack_exists(self, stack):
        '''
            Check if a stack exists or not

        Args:
            stack: The stack to check

        Returns:
            True or False depending on whether the stack exists

        Raises:
            Any exceptions raised .describe_stacks() besides that
            the stack doesn't exist.
        '''
        try:
            self.cfn.describe_stacks(StackName=stack)
            return True
        except botocore.exceptions.ClientError as exc:
            if "does not exist" in exc.response['Error']['Message']:
                return False
            else:
                raise exc

    def get_stack_status(self, stack):
        '''
        Get the status of an existing CloudFormation stack

        Args:
            stack: The name of the stack to check

        Returns:
            The CloudFormation status string of the stack such as CREATE_COMPLETE

        Raises:
             Exception: Any exception thrown by .describe_stacks()
        '''
        stack_description = self.cfn.describe_stacks(StackName=stack)
        return stack_description['Stacks'][0]['StackStatus']

    def create_stack(self, stack, template, parameters):
        '''
        Starts a new CloudFormation stack creation

        Args:
            stack: The stack to be created
            template: The template for the stack to be created with

        Throws:
            Exception: Any exception thrown by .create_stack()
        '''
        self.cfn.create_stack(
            StackName=stack,
            TemplateBody=template,
            Parameters=parameters,
            Capabilities=['CAPABILITY_IAM', 'CAPABILITY_NAMED_IAM']
        )
        waiter = self.cfn.get_waiter('stack_create_complete')
        waiter.wait(StackName=stack)

    def update_stack(self, stack, template, parameters):
        '''
        Start a CloudFormation stack update

        Args:
            stack: The stack to update
            template: The template to apply

        Returns:
            True if an update was started, false if there were no changes
            to the template since the last update.

        Raises:
            Exception: Any exception besides "No updates are to be performed."
        '''
        try:
            self.cfn.update_stack(
                StackName=stack,
                TemplateBody=template,
                Parameters=parameters,
                Capabilities=['CAPABILITY_IAM', 'CAPABILITY_NAMED_IAM']
            )
            waiter = self.cfn.get_waiter('stack_update_complete')
            waiter.wait(StackName=stack)
            return True

        except botocore.exceptions.ClientError as exc:
            if exc.response['Error']['Message'] == 'No updates are to be performed.':
                return False
            else:
                raise Exception('Error updating CloudFormation stack "{0}"'.format(stack), exc)

    def delete_stack(self, stack):
        '''
        Delete existing stack based on stackname and status

        If stack status is in ROLLBACK_COMPLETE or
        teardown commands is initiated then delete stack.

        Args:
         stack_name: The name of the stack to delete
        '''
        try:
            self.cfn.delete_stack(StackName=stack)
            print('Deleting stack:- ' + stack)
            waiter = self.cfn.get_waiter('stack_delete_complete')
            waiter.wait(StackName=stack)
            return True

        except botocore.exceptions.ClientError as exc:
            if exc.response['Error']['Message'] == 'No stacks deletion performed.':
                return False
            else:
                raise Exception('Error deleting CloudFormation stack "{0}"'.format(stack), exc)

    def create_or_update_stack(self, stack, template, parameters):
        '''
        Starts the stack creation or update process

        If the stack exists then update, otherwise create.

        Args:
            stack_name: The name of stack to create or update
            template: The template to create or update the stack with
        '''
        if self.stack_exists(stack):
            status = self.get_stack_status(stack)
            if status not in [
                    'CREATE_COMPLETE',
                    'ROLLBACK_COMPLETE',
                    'UPDATE_COMPLETE',
                    'UPDATE_ROLLBACK_COMPLETE'
                ]:
                # If the CloudFormation stack is not in a state where
                # it can be updated again then fail the job right away.
                print('Stack cannot be updated when status is: ' + status)
                return
            resource_updates = self.update_stack(stack, template, parameters)
            if resource_updates:
                # If there were updates then continue and succeed with progress of the update.
                print('Stack updated')
            else:
                # If there were no updates then succeed the job immediately
                print('There were no stack updates')
        else:
            # If the stack doesn't already exist then create it instead of updating it.
            self.create_stack(stack, template, parameters)
            # Continue the job so the pipeline will wait for the CloudFormation stack to be created.
            print('Stack creation started....')
