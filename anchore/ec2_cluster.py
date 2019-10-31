'''
Create cloudformation template for Anchore Engine EC2 Autoscaling Cluster
'''
from troposphere import (
    Sub, Ref, GetAtt, Parameter,
    Output, Export, Template,
    ImportValue, Base64
)
from troposphere.ecs import Cluster
from troposphere.ec2 import (
    SecurityGroup,
    EBSBlockDevice,
    BlockDeviceMapping,
    SecurityGroupRule,
)
from troposphere.iam import Role, Policy, InstanceProfile
from awacs.sts import AssumeRole
from awacs.aws import (
    Allow, Statement, Action,
    PolicyDocument, Principal
)
from troposphere.autoscaling import (
    AutoScalingGroup,
    LaunchConfiguration,
    ScalingPolicy,
)
from troposphere.policies import (
    CreationPolicy,
    UpdatePolicy,
    ResourceSignal,
    AutoScalingRollingUpdate,
    )
from troposphere.cloudwatch import Alarm, MetricDimension
import anchore.constants as constants

class EC2ClusterTemplate():
    '''
    Create EC2 Instance template to run ECS Cluster
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
                "AmiId",
                Type="String",
            )
        )
        self.cfn_template.add_parameter(
            Parameter(
                "ClusterSize",
                Type="String",
            )
        )
        self.cfn_template.add_parameter(
            Parameter(
                "InstanceType",
                Type="String",
            )
        )
        self.cfn_template.add_parameter(
            Parameter(
                "KeypairName",
                Type="String",
            )
        )
        self.cfn_template.add_parameter(
            Parameter(
                "CIDRBLK",
                Type="String",
            )
        )
        self.cfn_template.add_parameter(
            Parameter(
                "OpenCIDR",
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
                constants.CLUSTER,
                Description="ECS CLuster",
                Export=Export(Sub('${Environment}-CLUSTER')),
                Value=Ref(constants.CLUSTER),
            )
        )
        self.cfn_template.add_output(
            Output(
                constants.SSH_SG,
                Description="ec2 ssh security group",
                Export=Export(Sub('${Environment}-SSH-SG')),
                Value=GetAtt(constants.SSH_SG, 'GroupId'),
            )
        )
        return self.cfn_template

    def add_ecs_cluster(self):
        '''
        Add ECS cluster
        '''
        self.cfn_template.add_resource(
            Cluster(title=constants.CLUSTER)
        )
        return self.cfn_template

    def add_instance_role(self):
        '''
        Add Instance role
        '''
        self.cfn_template.add_resource(Role(
            title=constants.INST_ROLE,
            AssumeRolePolicyDocument=PolicyDocument(
                Statement=[
                    Statement(
                        Effect=Allow,
                        Action=[AssumeRole],
                        Principal=Principal('Service', ['ec2.amazonaws.com'])
                    )
                ]
            ),
            Policies=[
                Policy(
                    PolicyName='Demo-ECS-Cluster',
                    PolicyDocument=PolicyDocument(
                        Statement=[
                            Statement(
                                Effect=Allow,
                                Action=[
                                    Action('*')
                                ],
                                Resource=['*']
                            )
                        ]
                    )
                )
            ]
        ))
        return self.cfn_template

    def add_ssh_security(self):
        '''
        Add SSH security group
        '''
        self.cfn_template.add_resource(SecurityGroup(
            title=constants.SSH_SG,
            GroupDescription='Allow ssh connections to the cluster host instances',
            SecurityGroupIngress=[SecurityGroupRule(
                IpProtocol='tcp',
                FromPort=int('0'),
                ToPort=int('65535'),
                CidrIp=Ref('CIDRBLK')
            )],
            VpcId=ImportValue(Sub('${Environment}-VPCID'))
        ))
        return self.cfn_template

    def add_instance_profile(self):
        '''
        Add EC2 Instance profile
        '''
        self.cfn_template.add_resource(InstanceProfile(
            title=constants.INST_PROFILE,
            Path='/',
            Roles=[
                Ref(constants.INST_ROLE)
            ]
        ))
        return self.cfn_template

    def add_auto_scaling_group(self):
        '''
        Add Instance AutoScalingGroup
        '''
        self.cfn_template.add_resource(
            AutoScalingGroup(
                title=constants.INST_ASG,
                AvailabilityZones=[
                    ImportValue(Sub('${Environment}-PRIVATE-SUBNET-1-AZ')),
                    ImportValue(Sub('${Environment}-PRIVATE-SUBNET-2-AZ')),
                ],
                HealthCheckGracePeriod=int('150'),
                LaunchConfigurationName=Ref(constants.INST_LC),
                MaxSize='4',
                MinSize='2',
                VPCZoneIdentifier=[
                    ImportValue(Sub('${Environment}-PRIVATE-SUBNET-1')),
                    ImportValue(Sub('${Environment}-PRIVATE-SUBNET-2')),
                ],
                CreationPolicy=CreationPolicy(
                    ResourceSignal=ResourceSignal(
                        Count='2',
                        Timeout='PT30M'
                    )
                ),
                UpdatePolicy=UpdatePolicy(
                    AutoScalingRollingUpdate=AutoScalingRollingUpdate(
                        MaxBatchSize=int('1'),
                        MinInstancesInService=int('1'),
                        PauseTime='PT10M',
                        WaitOnResourceSignals='true'
                    )
                )
            )
        )
        return self.cfn_template

    def add_launch_config(self):
        '''
        Add autoscaling launch configurastion
        '''
        self.cfn_template.add_resource(
            LaunchConfiguration(
                title=constants.INST_LC,
                AssociatePublicIpAddress=False,
                BlockDeviceMappings=[
                    BlockDeviceMapping(
                        DeviceName='/dev/sda1',
                        Ebs=EBSBlockDevice(
                            DeleteOnTermination=True,
                            VolumeSize=int('100'),
                            VolumeType='gp2'
                        )
                    )
                ],
                IamInstanceProfile=Ref(constants.INST_PROFILE),
                ImageId=Ref('AmiId'),
                InstanceType=Ref('InstanceType'),
                KeyName=Ref('KeypairName'),
                SecurityGroups=[
                    Ref(constants.SSH_SG),
                    ImportValue(Sub('${Environment}-AppSecurityGroup')),
                ],
                UserData=Base64(
                    Sub(constants.USERDATA)
                )
            )
        )
        return self.cfn_template

    def add_scaling_policy(self, title, cd_number, adjustment):
        '''
        Add autoscaling policy
        '''
        self.cfn_template.add_resource(
            ScalingPolicy(
                title=title,
                AdjustmentType='ChangeInCapacity',
                AutoScalingGroupName=Ref(constants.INST_ASG),
                Cooldown=cd_number,
                ScalingAdjustment=adjustment
            )
        )
        return self.cfn_template

    def add_cloudwatch_alarm(
            self,
            title,
            scale_policy,
            alarm_desc,
            comparison,
            eval_period,
            metric_name,
            period,
            threshold
        ): # pylint: disable=too-many-arguments
        '''
        Add cloudwatch alarm
        '''
        self.cfn_template.add_resource(
            Alarm(
                title=title,
                ActionsEnabled=True,
                AlarmActions=[Ref(scale_policy)],
                AlarmDescription=alarm_desc,
                ComparisonOperator=comparison,
                Dimensions=[
                    MetricDimension(
                        Name='AutoScalingGroupName',
                        Value=Ref(constants.INST_ASG)
                    )
                ],
                EvaluationPeriods=eval_period,
                MetricName=metric_name,
                Namespace='AWS/ECS',
                Period=period,
                Statistic='Average',
                Threshold=threshold
            )
        )
        return self.cfn_template
