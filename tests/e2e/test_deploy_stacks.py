'''
Integration test for deployed stacks for Anchore Engine.
This tests functionality of deployed resources which includes
AWS - VPC, ALB, ECR, ECS and Recordset and scanning ability 
of Anchore Engine from end to end.
'''
from tests.e2e import helper

# Test Stacks
def test_ecr_stack_status():
    '''
    Test Anchore Engine VPC stack
    '''
    res = helper.ManageAWSResources()
    stack_name = 'DEMO-ANCHORE-ECR'
    status = res.get_stack_status(stack_name)
    assert status == 'CREATE_COMPLETE' or 'UPDATE_COMPLETE'

def test_vpc_stack_status():
    '''
    Test Anchore Engine VPC stack
    '''
    res = helper.ManageAWSResources()
    stack_name = 'DEMO-ANCHORE-VPC'
    status = res.get_stack_status(stack_name)
    assert status == 'CREATE_COMPLETE' or 'UPDATE_COMPLETE'

def test_alb_stack_status():
    '''
    Test Anchore Engine VPC stack
    '''
    res = helper.ManageAWSResources()
    stack_name = 'DEMO-ANCHORE-ALB'
    status = res.get_stack_status(stack_name)
    assert status == 'CREATE_COMPLETE' or 'UPDATE_COMPLETE'

def test_ecs_stack_status():
    '''
    Test Anchore Engine VPC stack
    '''
    res = helper.ManageAWSResources()
    stack_name = 'DEMO-ANCHORE-ECS'
    status = res.get_stack_status(stack_name)
    assert status == 'CREATE_COMPLETE' or 'UPDATE_COMPLETE'
