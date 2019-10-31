'''
Lint cfn templates,
Check cfn templates for security issues, and
Validate cfn templates
'''
import os
import boto3

def lint_cfn(template):
    '''
    lint cfn template
    '''
    print(f'BEGINS: Linting template - {template}')
    os.system(f'cfn-lint {template}')

def cfn_security_scan(template):
    '''
    Check cfn templates for security issues
    '''
    print(f'BEGINS: Checking cfn template - {template} for security issues')
    os.system(f'cfn_nag_scan --input-path {template}')

def validate_cfn(template):
    '''
    validate cfn template
    '''
    print(f'BEGINS: Validating cfn template - {template} for accuracy')
    client = boto3.client('cloudformation')
    response = client.validate_template(TemplateBody=template)
    return response

def main():
    '''
    cfn template validation entrypoint
    '''
    templates = [
        'anchore_vpc.yml',
        'anchore_alb.yml',
        'anchore_ecr.yml',
        'anchore_ecs.yml',
        'anchore_ec2_cluster.yml',
        'examples/aws-codepipeline/pipeline.yml'
    ]
    for template in templates:
        lint_cfn(template)
        cfn_security_scan(template)
        # validate_cfn(vpc)
    return 

if __name__ == '__main__':
    main()

