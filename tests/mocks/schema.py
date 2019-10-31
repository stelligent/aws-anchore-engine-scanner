'''
define mocks for expected outputs
'''
from anchore.vpc import VPCTemplate
from anchore.main import AnchoreEngine

MOCKED_DESCRIPTION = '''Description: foobar
Resources: {}
'''

MOCKED_VERSION = '''AWSTemplateFormatVersion: '2010-09-09'
Resources: {}
'''

def mocked_vpc_template():
    test_obj = AnchoreEngine()
    test_obj.create_vpc_template()
    return True

def mocked_alb_template():
    test_obj = AnchoreEngine()
    test_obj.create_alb_template()
    return True

def mocked_ecs_template():
    test_obj = AnchoreEngine()
    test_obj.create_ecs_template()
    return True

def mocked_ecr_template():
    test_obj = AnchoreEngine()
    test_obj.create_ecr_template()
    return True

def mocked_ec2_cluster_template():
    test_obj = AnchoreEngine()
    test_obj.create_ec2_cluster_template()
    return True
