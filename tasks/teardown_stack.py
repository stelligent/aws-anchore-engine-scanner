'''
Clean-up deployed aws resources
'''
import os
import sys
import traceback
import cloudformation as cfn
import keypair
from cloudformation import load_yaml_file # pylint: disable=no-name-in-module


print('Loading teardown function ....')

def main(configs):
    '''
    clean-up deployed stacks
    '''
    setup_data = load_yaml_file(configs)
    print('Listing configuration to delete Stacks in specified regions ...')

    try:
        for single_setup_data in setup_data:

        # Extract region and environemnt to deploy stack
            stack_region = single_setup_data['region']
            environment = single_setup_data['parameters']['Environment']
            print(f'Region to delete resource = {stack_region}')
            print(f'Environment to delete resource = {environment}')

        # Extract resource name and region
            resource_name = single_setup_data['resource_name']
            stack_name = environment+'-'+resource_name
            print(f'Stack name to be deleted = {stack_name}')

        # Delete non-empty bucket objects
            if stack_name == 'DEMO-ANCHORE-CLI-PIPELINE':
                bucket_name = single_setup_data['parameters']['BucketName']
                print(f'Bucket to delete objects = {bucket_name}')
                os.system(f"aws s3 rm s3://{bucket_name} --recursive")
                print(f'Bucket - {bucket_name} object removed')

        # Delete Stacks
            stacks = cfn.DeploymentManager(single_setup_data) # pylint: disable=no-member
            stacks.delete_stack(stack_name)
            print(f'Tearing down deployed stack {stack_name} ...')
            print('Teardown Complete!!!')

    except Exception as exc: # pylint: disable=broad-except
        print(f'Function failed due to exception. {exc}')
        traceback.print_exc()
        print('Stack Teardown Failed!!!')

    # Delete keypair
    keypair.delete_keypair(os.environ.get('AWS_DEFAULT_REGION'), 'anchore_demo')

    return "Teardown Complete!!!"

if __name__ == "__main__":
    main(f'{sys.argv[1]}')
