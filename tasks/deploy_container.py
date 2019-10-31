'''
Manage AWS ECR Resources and Stacks
'''
import traceback
from tasks.cloudformation import load_yaml_file
import ecr_deployer as ecr

print('Loading function ....')

def main(configs):
    '''
    Deploy AWS ECR resources
    '''
    setup_data = load_yaml_file(configs)

    try:
        for single_setup_data in setup_data:

        # declare variables
            ecr_image = single_setup_data['remote_image']
            tag = single_setup_data['tag']

        # Extract region to deploy container
            container_region = single_setup_data['region']
            print(f'Region to deploy container images = {container_region}')

        # Extract registry account to deploy container images
            account_id = single_setup_data['account_id']
            print(f'Registry account to deploy container images = {account_id}')

        # Get ECR authentication token for logins
            login = ecr.ECRDeployer(single_setup_data)

        # Login to ECR
            print('Logging in to Amazon ECR...')
            auth_conf = login.ecr_login()

        # Build image
            local_image = login.build_image(
                single_setup_data['dockerfile_path'],
                tag,
                single_setup_data['dockerfile']
            )

        # Tag image
            tag_response = login.tag_image(local_image, ecr_image, tag)
            print(tag_response)

        # Push image
            push_response = login.push_image(ecr_image, tag, auth_conf)
            print(push_response)

        print('Container Images Deployment Successful!!!')

    except Exception as exc: # pylint: disable=broad-except
        print(f'Function failed due to exception. {exc}')
        traceback.print_exc()
        print('Container Images Deployment Failed!!!')

    return True

if __name__ == "__main__":
    main('configs/ecr_configs.yml')
