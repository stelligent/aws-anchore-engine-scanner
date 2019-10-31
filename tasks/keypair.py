'''
Manage EC2 key-pair deployment and Resources
'''
import boto3

def create_keypair(region, keyname):
    '''
    Creates key pair for ec2

    Args:
        region: target aws region
        keyname: A unique name for the key pair.
    Returns:
        An unencrypted PEM encoded RSA private key
    Raises:
        Any exceptions raised

    '''
    ec2 = boto3.client('ec2', region_name=region)
    res = ec2.create_key_pair(KeyName=keyname)
    return res['KeyMaterial']

def delete_keypair(region, keyname):
    '''
    Delete key pair for ec2

    Args:
        region: target aws region
        keyname: A unique name for the key pair.
    Returns:
        none
    Raises:
        Any exceptions raised

    '''
    ec2 = boto3.client('ec2', region_name=region)
    ec2.delete_key_pair(KeyName=keyname)
    return True
