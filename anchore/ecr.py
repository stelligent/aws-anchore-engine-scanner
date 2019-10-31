'''
Create cloudformation template for
Anchore Engine ECR Repository
'''
from troposphere import (
    Sub, Ref, Output, Join,
    Export, Template, Parameter
)
from troposphere.ecr import Repository
from awacs.aws import (
    Allow, Action, PolicyDocument,
    AWSPrincipal, Statement
)
import anchore.constants as constants

class ECRTemplate():
    '''
    Create ECR template
    '''
    def __init__(self):
        self.cfn_template = Template()

    def add_descriptions(self, descriptions):
        '''
        Add descriptions to template
        '''
        self.cfn_template.set_description(descriptions)
        return self.cfn_template

    def add_version(self, version):
        '''
        Add a version of the template file to template
        '''
        self.cfn_template.set_version(version)
        return self.cfn_template

    def add_parameters(self):
        '''
        Add parameters to generated template
        '''
        self.cfn_template.add_parameter(
            Parameter(
                "Environment",
                Type="String",
            )
        )
        self.cfn_template.add_parameter(
            Parameter(
                "AppRepoName",
                Type="String",
            )
        )
        self.cfn_template.add_parameter(
            Parameter(
                "ImageTag",
                Type="String",
            )
        )
        self.cfn_template.add_parameter(
            Parameter(
                "TestImageRepoName",
                Type="String",
            )
        )
        return self.cfn_template

    def add_outputs(self):
        '''
        Add outputs to generated template
        '''
        self.cfn_template.add_output(
            Output(
                constants.ECR_REPO,
                Export=Export(Sub('${Environment}-anchore-engine-Image')),
                Value=Join(
                    '', [
                        Ref('AWS::AccountId'),
                        '.dkr.ecr.',
                        Ref('AWS::Region'),
                        '.amazonaws.com/',
                        Ref(constants.ECR_REPO),
                        ':',
                        Ref(constants.IMAGE_TAG),
                    ]
                )
            )
        )
        return self.cfn_template

    def add_ecr_repository(self, title, repo_name):
        '''
        Add ECR repository to template

        Args:
            title: logical resources name
            repo_name: target repository name
        '''
        self.cfn_template.add_resource(
            Repository(
                title=title,
                RepositoryName=Ref(repo_name),
                RepositoryPolicyText=PolicyDocument(
                    Version='2012-10-17',
                    Statement=[
                        Statement(
                            Sid='AllowPushPull',
                            Effect=Allow,
                            Action=[
                                Action('ecr', '*')
                            ],
                            Principal=AWSPrincipal('*')
                        )
                    ]
                )
            )
        )
        return self.cfn_template
