'''
Manage ECR deployment and Resources
'''
import base64
import boto3
import docker
import botocore

class ECRDeployer():
    '''
    ECR Deployer
    '''
    def __init__(self, config):
        self.region = config['region']
        self.account_id = config['account_id']
        self.ecr = boto3.client('ecr', region_name=self.region)
        self.docker_api = docker.APIClient(base_url='unix://var/run/docker.sock')

    def get_ecr_creds(self):
        '''
        Provides a tlogin credentials for ecr logins

        Args:
            none
        Returns:
            1. authorization token
            2. repository proxy endpoint
        Raises:
            Any exceptions raised

        '''
        try:
            credentials = {}
            cred = self.ecr.get_authorization_token()
            credentials['token'] = cred['authorizationData'][0]['authorizationToken']
            credentials['url'] = cred['authorizationData'][0]['proxyEndpoint']
            return credentials
        except botocore.exceptions.ClientError as error:
            return error

    def ecr_login(self):
        '''
        Creates a login session for ecr

        Args:
            none
        Returns:
            none
        Raises:
            Any exceptions raised

        '''
        creds = self.get_ecr_creds()
        token = creds['token']
        auth_token = base64.b64decode(token).decode()
        username, password = auth_token.split(':')
        registry = f'https://{self.account_id}.dkr.ecr.{self.region}.amazonaws.com'
        self.docker_api.login(
            username=username,
            password=password,
            email=None,
            registry=registry
        )
        auth_config_payload = {'username': username, 'password': password}
        return auth_config_payload

    def build_image(self, dockerfile_path, tag, dockerfile):
        '''
        Build an image using a Dockerfile

        Args:
            dockerfile_path (str) – Path to the directory containing the Dockerfile
            tag (str) – A tag to add to the final image
            dockerfile (str) – path within the build context to the Dockerfile

        Returns:
            Image object for the image that was built

        Raises:
            docker.error.APIerror - if the server returns an error
        '''
        local_image = self.docker_api.build(
            path=dockerfile_path,
            tag=tag,
            dockerfile=dockerfile
        )
        return local_image

    def tag_image(self, local_image, ecr_image, tag):
        '''
        Tag an image into a repository

        Args:
            account_id: AWS account ID
            local_image: Name of built image to be pushed to repository
            ecr_image: AWS ECR remote repository name
            tag: Tag for image to be pushed

        Returns:
            True if succesful

        Raises:
            docker.error.APIerror - if the server returns an error
        '''
        remote_repository = f'{self.account_id}.dkr.ecr.{self.region}.amazonaws.com/{ecr_image}'
        self.docker_api.tag(local_image, remote_repository, tag, force=True)
        return remote_repository

    def push_image(self, ecr_image, tag, auth_config):
        '''
        Push an image into a repository

        Args:
            account_id: AWS account ID
            local_image: Name of built image to be pushed to repository
            ecr_image: AWS ECR remote repository name
            tag: Tag for image to be pushed

        Returns:
            True if successful

        Raises:
            docker.error.APIerror - if the server returns an error
        '''
        try:

            tagged_image = f'{self.account_id}.dkr.ecr.{self.region}.amazonaws.com/{ecr_image}'
            print(tagged_image)
            status = self.docker_api.push(
                tagged_image,
                tag=tag,
                stream=True,
                auth_config=auth_config,
                decode=True
            )
            return status
        except Exception as error: # pylint: disable=broad-except
            return error
    