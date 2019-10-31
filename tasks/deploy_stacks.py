'''
Deploys cloudformation stacks
'''
import traceback
import tasks.cloudformation as cfn

print('Loading function ....')

def deploy_stack(configs):
    '''
    Get deployment configurations and deploy stacks
    '''
    setup_data = cfn.load_yaml_file(configs)
    print('Listing configuration to setup Stacks in specified regions.......')

    try:
        for single_setup_data in setup_data:

        # Extract region and environemnt to deploy stack
            stack_region = single_setup_data['region']
            environment = single_setup_data['parameters']['Environment']
            print(f'Region to deploy resource = {stack_region}')
            print(f'Environment to deploy resource = {environment}')

        # Extract resource name and region and create a stack name
            resource_name = single_setup_data['resource_name']
            stack_name = environment+'-'+resource_name
            print('Stack name for deployed resource = ' + stack_name)

        # Extract the template file to create stack
            template_file = single_setup_data['template_file']
            with open(template_file, 'r') as template:
                template_body = template.read()
            print(f'Template file used to deploy resource = {template_file}')

        # Extract the input parameters to create or update stack
            parameter_values = cfn.build_stack_parameters(single_setup_data['parameters'])
            print(f'Parameter key-value for resource stack = {parameter_values}')

        # Deploy Stack
            print('provisioning resources.......')
            stacks = cfn.DeploymentManager(single_setup_data)
            stacks.create_or_update_stack(stack_name, template_body, parameter_values)
            print('Stack Deployment Complete!!!')


    except Exception as error: # pylint: disable=broad-except

        print(f'Function failed due to exception.{error}')
        traceback.print_exc()
        print('Stack Deployment Failed!!!')

    return True
