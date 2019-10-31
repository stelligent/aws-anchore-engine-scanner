'''
Create cloudformation template for Anchore Engine ALB
'''
from troposphere import (
    Sub, Ref, GetAtt, ImportValue,
    Output, Export, Template, Parameter
)
from troposphere.elasticloadbalancingv2 import (
    LoadBalancer, LoadBalancerAttributes,
    Listener, TargetGroup, Action, Matcher,
    TargetGroupAttribute
)
from troposphere.ec2 import (
    SecurityGroup,
    SecurityGroupRule
)
import anchore.constants as constants

class ALBTemplate():
    '''
    Create ALB template
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
                "Subnet1",
                Type="String",
                Description="A list of subnet IDs to associate with the load balancer",
            )
        )
        self.cfn_template.add_parameter(
            Parameter(
                "Subnet2",
                Type="String",
                Description="A list of subnet IDs to associate with the load balancer",
            )
        )
        self.cfn_template.add_parameter(
            Parameter(
                "VpcId",
                Type="String",
                Description="The physical ID of the VPC",
            )
        )
        self.cfn_template.add_parameter(
            Parameter(
                "CIDRBLK",
                Type="String",
                Description="Cidr block to permit access through security group",
                MinLength='9',
                MaxLength='18',
                ConstraintDescription="must be a valid IP CIDR range of the form x.x.x.x/x.",
            )
        )
        return self.cfn_template

    def add_load_balancer(self):
        '''
        Add load balancer to template
        '''
        self.cfn_template.add_resource(LoadBalancer(
            title=constants.ALB,
            LoadBalancerAttributes=[LoadBalancerAttributes(
                Key='deletion_protection.enabled',
                Value='false'
            )],
            Scheme='internal',
            SecurityGroups=[Ref(constants.ALB_SG)],
            Subnets=[
                ImportValue(Sub('${Environment}-${Subnet1}')),
                ImportValue(Sub('${Environment}-${Subnet2}'))
            ]
        ))
        return self.cfn_template

    def add_alb_listener(self):
        '''
        Add an ALB listner
        '''
        self.cfn_template.add_resource(Listener(
            title=constants.LISTENER,
            DefaultActions=[Action(
                TargetGroupArn=Ref(constants.ALB_TG),
                Type='forward')],
            LoadBalancerArn=Ref(constants.ALB),
            Port=int('8228'),
            Protocol='HTTP'))
        return self.cfn_template

    def add_alb_target_group(self):
        '''
        Add load balancer target group to template
        '''
        self.cfn_template.add_resource(TargetGroup(
            title=constants.ALB_TG,
            HealthCheckIntervalSeconds=int('5'),
            HealthCheckPath='/health',
            HealthCheckProtocol='HTTP',
            HealthCheckTimeoutSeconds=int('3'),
            HealthyThresholdCount=int('2'),
            Matcher=Matcher(HttpCode='200'),
            Port=int('8228'),
            Protocol='HTTP',
            UnhealthyThresholdCount=int('5'),
            TargetGroupAttributes=[
                TargetGroupAttribute(
                    Key='deregistration_delay.timeout_seconds',
                    Value='20'
                )
            ],
            VpcId=ImportValue(Sub('${Environment}-${VpcId}'))
        ))
        return self.cfn_template

    def add_alb_secuirty_group(self):
        '''
        Add security group to load balancer
        '''
        self.cfn_template.add_resource(SecurityGroup(
            title=constants.ALB_SG,
            GroupDescription='Load balancer security group',
            SecurityGroupIngress=[
                SecurityGroupRule(
                    IpProtocol='tcp',
                    FromPort=int('80'),
                    ToPort=int('80'),
                    CidrIp=Ref('CIDRBLK'),
                ),
                SecurityGroupRule(
                    IpProtocol='-1',
                    FromPort=int('-1'),
                    ToPort=int('-1'),
                    SourceSecurityGroupId=ImportValue(Sub('${Environment}-AppSecurityGroup')),
                )
            ],
            SecurityGroupEgress=[
                SecurityGroupRule(
                    IpProtocol='-1',
                    CidrIp='0.0.0.0/0'
                )
            ],
            VpcId=ImportValue(Sub('${Environment}-${VpcId}'))
        ))
        return self.cfn_template

    def add_outputs(self):
        '''
        Add outputs to generated template
        '''
        self.cfn_template.add_output(
            Output(
                constants.ALB_NAME,
                Description="Load Balancer Name",
                Export=Export(Sub('${Environment}-DNS-NAME')),
                Value=GetAtt(constants.ALB, 'DNSName'),
            )
        )
        self.cfn_template.add_output(
            Output(
                constants.ALB_TG_NAME,
                Description="Load Balancer Target Group",
                Export=Export(Sub('${Environment}-TARGETGROUP-ARN')),
                Value=Ref(constants.ALB_TG),
            )
        )
        return self.cfn_template
