'''
Create cloudformation template for Anchore Engine ECS
'''
from troposphere import (
    Sub, Ref, GetAtt,
    Output, Export, Template, Parameter,
    ImportValue, Join
)
from troposphere.ecs import (
    Service, LoadBalancer,
    TaskDefinition, PlacementStrategy,
    ContainerDefinition, Environment,
    PortMapping, Volume, LogConfiguration,
    MountPoint, DeploymentConfiguration
)
from troposphere.iam import Role, Policy
from troposphere.logs import LogGroup
from awacs.sts import AssumeRole
from awacs.aws import (
    Allow, Statement, Action,
    PolicyDocument, Principal
)
import anchore.constants as constants

class ECSTemplate():
    '''
    Create ECS template
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
                "TargetGroup",
                Type="String",
            )
        )
        self.cfn_template.add_parameter(
            Parameter(
                "AnchoreEngineImage",
                Type="String",
            )
        )
        self.cfn_template.add_parameter(
            Parameter(
                "ArchoreDatabaseImage",
                Type="String",
            )
        )
        self.cfn_template.add_parameter(
            Parameter(
                "PGDATA",
                Type="String",
            )
        )
        self.cfn_template.add_parameter(
            Parameter(
                "AnchoreDBPassword",
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
                constants.SERVICE,
                Description="ECS Service",
                Export=Export(Sub('${Environment}-SERVICE')),
                Value=Ref(constants.SERVICE),
            )
        )
        self.cfn_template.add_output(
            Output(
                constants.TASK,
                Description="ECS Task",
                Export=Export(Sub('${Environment}-TASK')),
                Value=Ref(constants.TASK),
            )
        )
        return self.cfn_template

    def add_ecs_service(self):
        '''
        Add ECS service
        '''
        self.cfn_template.add_resource(Service(
            title=constants.SERVICE,
            Cluster=ImportValue(Sub('${Environment}-CLUSTER')),
            LaunchType='EC2',
            DesiredCount=int('1'),
            TaskDefinition=Ref(constants.TASK),
            Role=Ref(constants.SERVICE_ROLE),
            DeploymentConfiguration=DeploymentConfiguration(
                MaximumPercent=int('200'),
                MinimumHealthyPercent=int('100')
            ),
            LoadBalancers=[
                LoadBalancer(
                    ContainerName='anchore-engine',
                    ContainerPort=int('8228'),
                    TargetGroupArn=ImportValue(
                        Sub('${Environment}-TARGETGROUP-ARN')
                    )
                )
            ],
            PlacementStrategies=[
                PlacementStrategy(
                    Type='spread',
                    Field='attribute:ecs.availability-zone'
                ),
                PlacementStrategy(
                    Type='spread',
                    Field='instanceId'
                )
            ]
        ))
        return self.cfn_template

    def add_ecs_task(self):
        '''
        Add ECS Task
        '''
        self.cfn_template.add_resource(TaskDefinition(
            title=constants.TASK,
            Volumes=[
                Volume(
                    Name='anchore_db_vol'
                )
            ],
            TaskRoleArn=GetAtt(constants.TASK_ROLE, 'Arn'),
            ContainerDefinitions=[
                ContainerDefinition(
                    Name='anchore-engine',
                    Hostname='anchore-engine',
                    Cpu=int('512'),
                    MemoryReservation=int('1536'),
                    Essential=bool('true'),
                    Image=ImportValue(
                        Sub('${Environment}-${AnchoreEngineImage}')
                    ),
                    PortMappings=[
                        PortMapping(
                            ContainerPort=int('8228'),
                            HostPort=int('8228'),
                            Protocol='tcp',
                        ),
                        PortMapping(
                            ContainerPort=int('8338'),
                            HostPort=int('8338'),
                            Protocol='tcp',
                        ),
                    ],
                    DockerSecurityOptions=['apparmor:docker-default'],
                    Environment=[
                        Environment(
                            Name='ANCHORE_HOST_ID',
                            Value='anchore-engine'
                        ),
                        Environment(
                            Name='ANCHORE_ENDPOINT_HOSTNAME',
                            Value='anchore-engine'
                        ),
                        Environment(
                            Name='ANCHORE_DB_HOST',
                            Value='anchore-db'
                        ),
                        Environment(
                            Name='ANCHORE_DB_PASSWORD',
                            Value=Ref('AnchoreDBPassword')
                        ),
                        Environment(
                            Name='AWS_DEFAULT_REGION',
                            Value=Ref('AWS::Region')
                        ),
                        Environment(
                            Name='region',
                            Value=Ref('AWS::Region')
                        ),
                    ],
                    LogConfiguration=LogConfiguration(
                        LogDriver='awslogs',
                        Options={
                            "awslogs-group": Ref('EngineLogGroup'),
                            "awslogs-region": Ref('AWS::Region'),
                            "awslogs-stream-prefix": Join('', [
                                'anchore-engine',
                                'logs'
                            ])
                        }
                    ),
                    Links=['anchore-db']
                ),
                ContainerDefinition(
                    Name='anchore-db',
                    Hostname='anchore-db',
                    Cpu=int('512'),
                    MemoryReservation=int('1536'),
                    Essential=bool('true'),
                    Image=Ref('ArchoreDatabaseImage'),
                    PortMappings=[
                        PortMapping(
                            ContainerPort=int('5432'),
                            HostPort=int('5432'),
                            Protocol='tcp',
                        )
                    ],
                    DockerSecurityOptions=['apparmor:docker-default'],
                    MountPoints=[
                        MountPoint(
                            ContainerPath=Ref('PGDATA'),
                            SourceVolume='anchore_db_vol'
                        )
                    ],
                    Environment=[
                        Environment(
                            Name='POSTGRES_PASSWORD',
                            Value=Ref('AnchoreDBPassword')
                        ),
                        Environment(
                            Name='PGDATA',
                            Value=Ref('PGDATA')
                        ),
                        Environment(
                            Name='AWS_DEFAULT_REGION',
                            Value=Ref('AWS::Region')
                        ),
                        Environment(
                            Name='region',
                            Value=Ref('AWS::Region')
                        ),
                    ],
                    LogConfiguration=LogConfiguration(
                        LogDriver='awslogs',
                        Options={
                            "awslogs-group": Ref('DatabaseLogGroup'),
                            "awslogs-region": Ref('AWS::Region'),
                            "awslogs-stream-prefix": Join('', [
                                'anchore-db',
                                'logs'
                            ])
                        }
                    )
                )
            ]
        ))
        return self.cfn_template

    def add_ecs_service_role(self):
        '''
        Add ECS Service Role to template
        '''
        self.cfn_template.add_resource(Role(
            title=constants.SERVICE_ROLE,
            AssumeRolePolicyDocument=PolicyDocument(
                Statement=[
                    Statement(
                        Effect=Allow,
                        Action=[AssumeRole],
                        Principal=Principal('Service', ['ecs.amazonaws.com'])
                    )
                ]
            ),
            Policies=[
                Policy(
                    PolicyName='AmazonEC2ContainerServiceRole',
                    PolicyDocument=PolicyDocument(
                        Statement=[
                            Statement(
                                Effect=Allow,
                                Action=[
                                    Action(
                                        'ec2',
                                        'AuthorizeSecurityGroupIngress'
                                    ),
                                    Action(
                                        'ec2',
                                        'Describe*'
                                    ),
                                    Action(
                                        'elasticloadbalancing',
                                        'DeregisterInstancesFromLoadBalancer'
                                    ),
                                    Action(
                                        'ecelasticloadbalancing2',
                                        'Describe*'
                                    ),
                                    Action(
                                        'elasticloadbalancing',
                                        'RegisterInstancesWithLoadBalancer'
                                    ),
                                    Action(
                                        'elasticloadbalancing',
                                        'DeregisterTargets'
                                    ),
                                    Action(
                                        'elasticloadbalancing',
                                        'DescribeTargetGroups'
                                    ),
                                    Action(
                                        'elasticloadbalancing',
                                        'DescribeTargetHealth'
                                    ),
                                    Action(
                                        'elasticloadbalancing',
                                        'RegisterTargets'
                                    )
                                ],
                                Resource=['*']
                            )
                        ]
                    )
                )
            ]
        ))
        return self.cfn_template

    def add_ecs_task_role(self):
        '''
        Add ECS Task Role to template
        '''
        self.cfn_template.add_resource(Role(
            title=constants.TASK_ROLE,
            AssumeRolePolicyDocument=PolicyDocument(
                Statement=[
                    Statement(
                        Effect=Allow,
                        Action=[AssumeRole],
                        Principal=Principal('Service', ['ecs-tasks.amazonaws.com'])
                    )
                ]
            ),
            Policies=[
                Policy(
                    PolicyName='ECSTaskDefinitionContainerRole',
                    PolicyDocument=PolicyDocument(
                        Statement=[
                            Statement(
                                Effect=Allow,
                                Action=[
                                    Action('s3', 'GetObject'),
                                    Action('kms', 'Encrypt'),
                                    Action('kms', 'Decrypt')
                                ],
                                Resource=['*']
                            )
                        ]
                    )
                ),
                Policy(
                    PolicyName='DemoAppContainerRole',
                    PolicyDocument=PolicyDocument(
                        Statement=[
                            Statement(
                                Effect=Allow,
                                Action=[
                                    Action('dynamodb', 'BatchGetItem'),
                                    Action('dynamodb', 'BatchWriteItem'),
                                    Action('dynamodb', 'GetItem'),
                                    Action('dynamodb', 'ListTables'),
                                    Action('dynamodb', 'PutItem'),
                                    Action('dynamodb', 'Query'),
                                    Action('dynamodb', 'Scan'),
                                    Action('dynamodb', 'UpdateItem'),
                                    Action('dynamodb', 'DeleteItem')
                                ],
                                Resource=['*']
                            )
                        ]
                    )
                )
            ]
        ))
        return self.cfn_template

    def add_engine_log_group(self):
        '''
        Add Anchore Engine log group to template
        '''
        self.cfn_template.add_resource(
            LogGroup(
                title=constants.ENG_LOG,
                LogGroupName='demo-anchore-engine',
                RetentionInDays=int('7')
            )
        )
        return self.cfn_template

    def add_database_log_group(self):
        '''
        Add Anchore Database log group to template
        '''
        self.cfn_template.add_resource(
            LogGroup(
                title=constants.DB_LOG,
                LogGroupName='demo-anchore-database',
                RetentionInDays=int('7')
            )
        )
        return self.cfn_template
