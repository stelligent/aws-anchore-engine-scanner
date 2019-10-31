'''
Create cloudformation template for Anchore Engine VPC
'''
from troposphere import (
    Sub, Ref, Select, GetAZs, GetAtt,
    Output, Export, Template, Parameter
)
from troposphere.ec2 import (
    VPC, EIP, Route, Subnet,
    NatGateway, RouteTable, InternetGateway,
    VPCGatewayAttachment, SubnetRouteTableAssociation
)
from troposphere.ec2 import (
    SecurityGroup,
    SecurityGroupRule
)
import anchore.constants as constants

class VPCTemplate(): #pylint: disable=too-many-public-methods
    '''
    Create VPC template
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
                'Environment',
                Type='String',
            )
        )
        self.cfn_template.add_parameter(
            Parameter(
                'VPCCIDRBlock',
                Type='String',
                Description="Enter valid CIDR block values for VPC. Default is 10.0.0.0/16",
                MinLength='9',
                MaxLength='18',
                ConstraintDescription="must be a valid IP CIDR range of the form x.x.x.x/x.",
            )
        )
        self.cfn_template.add_parameter(
            Parameter(
                'PublicSubnet1CIDRBlock',
                Type='String',
                Description="Enter valid CIDR block values for public subnet-1. i.e 10.0.0.0/24",
                MinLength='9',
                MaxLength='18',
                ConstraintDescription="must be a valid IP CIDR range of the form x.x.x.x/x.",
            )
        )
        self.cfn_template.add_parameter(
            Parameter(
                'PrivateSubnet1CIDRBlock',
                Type='String',
                Description="Enter valid CIDR block values for private subnet-1.i.e 10.0.1.0/24",
                MinLength='9',
                MaxLength='18',
                ConstraintDescription="must be a valid IP CIDR range of the form x.x.x.x/x.",
            )
        )
        self.cfn_template.add_parameter(
            Parameter(
                'PublicSubnet2CIDRBlock',
                Type='String',
                Description="Enter valid CIDR block values for public subnet-2. i.e 10.0.2.0/24",
                MinLength='9',
                MaxLength='18',
                ConstraintDescription="must be a valid IP CIDR range of the form x.x.x.x/x.",
            )
        )
        self.cfn_template.add_parameter(
            Parameter(
                'PrivateSubnet2CIDRBlock',
                Type='String',
                Description="Enter valid CIDR block values for private subnet-2. i.e 10.0.3.0/24",
                MinLength='9',
                MaxLength='18',
                ConstraintDescription="must be a valid IP CIDR range of the form x.x.x.x/x.",
            )
        )
        return self.cfn_template

    def add_outputs(self):
        '''
        Add outputs to generated template
        '''
        self.cfn_template.add_output(
            Output(
                "NetVPC",
                Description="The VPC ID",
                Export=Export(Sub('${Environment}-VPCID')),
                Value=Ref(constants.VPC),
            )
        )
        self.cfn_template.add_output(
            Output(
                "PublicNetSubnet1",
                Description="The network's public subnet-1 ID",
                Export=Export(Sub('${Environment}-PUBLIC-SUBNET-1')),
                Value=Ref(constants.PUB_SUBNET1),
            )
        )
        self.cfn_template.add_output(
            Output(
                "PrivateNetSubnet1",
                Description="The network's private subnet-1 ID",
                Export=Export(Sub('${Environment}-PRIVATE-SUBNET-1')),
                Value=Ref(constants.PRIV_SUBNET1),
            )
        )
        self.cfn_template.add_output(
            Output(
                "PublicNetSubnet2",
                Description="The network's public subnet-2 ID",
                Export=Export(Sub('${Environment}-PUBLIC-SUBNET-2')),
                Value=Ref(constants.PUB_SUBNET2),
            )
        )
        self.cfn_template.add_output(
            Output(
                'PrivateNetSubnet2',
                Description="The network's private subnet-2 ID",
                Export=Export(Sub('${Environment}-PRIVATE-SUBNET-2')),
                Value=Ref(constants.PRIV_SUBNET2),
            )
        )
        self.cfn_template.add_output(
            Output(
                'PublicSubnet1AZ',
                Description="The public subnet-1 AZ to use for public servers",
                Export=Export(Sub('${Environment}-PUBLIC-SUBNET-1-AZ')),
                Value=GetAtt(constants.PUB_SUBNET1, 'AvailabilityZone'),
            )
        )
        self.cfn_template.add_output(
            Output(
                'PrivateSubnet1AZ',
                Description="The private subnet-1 AZ to use for private servers",
                Export=Export(Sub('${Environment}-PRIVATE-SUBNET-1-AZ')),
                Value=GetAtt(constants.PRIV_SUBNET1, 'AvailabilityZone'),
            )
        )
        self.cfn_template.add_output(
            Output(
                'PublicSubnet2AZ',
                Description='The public subnet-2 AZ to use for public servers',
                Export=Export(Sub('${Environment}-PUBLIC-SUBNET-2-AZ')),
                Value=GetAtt(constants.PUB_SUBNET2, 'AvailabilityZone'),
            )
        )
        self.cfn_template.add_output(
            Output(
                'PrivateSubnet2AZ',
                Description="The private subnet-2 AZ to use for private servers",
                Export=Export(Sub('${Environment}-PRIVATE-SUBNET-2-AZ')),
                Value=GetAtt(constants.PRIV_SUBNET2, 'AvailabilityZone'),
            )
        )
        self.cfn_template.add_output(
            Output(
                'NATIPAddress',
                Description="The VPC NAT ip address",
                Export=Export(Sub('${Environment}-NATIPAddress')),
                Value=Ref(constants.EIP),
            )
        )
        self.cfn_template.add_output(
            Output(
                'AppSecurityGroup',
                Description='The security group ID to use for apps',
                Export=Export(Sub('${Environment}-AppSecurityGroup')),
                Value=GetAtt(constants.APP_SG, 'GroupId'),
            )
        )
        return self.cfn_template


    def add_vpc(self):
        '''
        Add a VPC for Anchore Engine
        '''
        self.cfn_template.add_resource(VPC(
            title=constants.VPC,
            CidrBlock=Ref('VPCCIDRBlock'),
            EnableDnsSupport=bool('true'),
            EnableDnsHostnames=bool('true'),
            InstanceTenancy='default',
            ))
        return self.cfn_template

    def add_public_subnet1(self):
        '''
        Add a public subnet 1
        '''
        self.cfn_template.add_resource(Subnet(
            title=constants.PUB_SUBNET1,
            VpcId=Ref(constants.VPC),
            CidrBlock=Ref('PublicSubnet1CIDRBlock'),
            MapPublicIpOnLaunch="true",
            AvailabilityZone=Select('0', GetAZs())
            ))
        return self.cfn_template

    def add_private_subnet1(self):
        '''
        Add a private subnet 1
        '''
        self.cfn_template.add_resource(Subnet(
            title=constants.PRIV_SUBNET1,
            VpcId=Ref(constants.VPC),
            CidrBlock=Ref('PrivateSubnet1CIDRBlock'),
            AvailabilityZone=Select('0', GetAZs())
            ))
        return self.cfn_template

    def add_public_subnet2(self):
        '''
        Add a public subnet 2
        '''
        self.cfn_template.add_resource(Subnet(
            title=constants.PUB_SUBNET2,
            VpcId=Ref(constants.VPC),
            CidrBlock=Ref('PublicSubnet2CIDRBlock'),
            MapPublicIpOnLaunch="true",
            AvailabilityZone=Select('1', GetAZs())
            ))
        return self.cfn_template

    def add_private_subnet2(self):
        '''
        Add a private subnet 2
        '''
        self.cfn_template.add_resource(Subnet(
            title=constants.PRIV_SUBNET2,
            VpcId=Ref(constants.VPC),
            CidrBlock=Ref('PrivateSubnet2CIDRBlock'),
            AvailabilityZone=Select('1', GetAZs())
            ))
        return self.cfn_template

    def add_internet_gateway(self):
        '''
        Add an internet gateway
        '''
        self.cfn_template.add_resource(InternetGateway(
            title=constants.IGW,
            ))
        return self.cfn_template

    def add_attach_gateway(self):
        '''
        Add an internet gateway attachment
        '''
        self.cfn_template.add_resource(VPCGatewayAttachment(
            title=constants.ATTACH_GW,
            VpcId=Ref(constants.VPC),
            InternetGatewayId=Ref(constants.IGW)
            ))
        return self.cfn_template

    def add_vpc_eip(self):
        '''
        Add elastic ip to vpc
        '''
        self.cfn_template.add_resource(EIP(
            title=constants.EIP,
            Domain='vpc',
            DependsOn=constants.ATTACH_GW,
            ))
        return self.cfn_template

    def add_nat(self):
        '''
        Add a NAT Gateway
        '''
        self.cfn_template.add_resource(NatGateway(
            title=constants.NAT,
            AllocationId=GetAtt(constants.EIP, 'AllocationId'),
            SubnetId=Ref(constants.PUB_SUBNET1)
            ))
        return self.cfn_template

    def add_public_routetable(self):
        '''
        Add a public route-table
        '''
        self.cfn_template.add_resource(RouteTable(
            title=constants.PUB_RT,
            VpcId=Ref(constants.VPC),
            ))
        return self.cfn_template

    def add_private_routetable(self):
        '''
        Add a private route-table
        '''
        self.cfn_template.add_resource(RouteTable(
            title=constants.PRIV_RT,
            VpcId=Ref(constants.VPC),
            ))
        return self.cfn_template

    def add_public_route(self):
        '''
        Add a public route with internet gateway
        '''
        self.cfn_template.add_resource(Route(
            title=constants.PUB_ROUTE,
            RouteTableId=Ref(constants.PUB_RT),
            DestinationCidrBlock='0.0.0.0/0',
            GatewayId=Ref(constants.IGW),
            ))
        return self.cfn_template

    def add_private_route(self):
        '''
        Add a private route with nat gateway
        '''
        self.cfn_template.add_resource(Route(
            title=constants.PRIV_ROUTE,
            RouteTableId=Ref(constants.PRIV_RT),
            DestinationCidrBlock='0.0.0.0/0',
            NatGatewayId=Ref(constants.NAT),
            ))
        return self.cfn_template

    def add_public_subnet_routetable_association1(self):
        '''
        Add a public subnet route-table association
        to public subnet 1
        '''
        self.cfn_template.add_resource(SubnetRouteTableAssociation(
            title=constants.PUB_RT_ASS1,
            SubnetId=Ref(constants.PUB_SUBNET1),
            RouteTableId=Ref(constants.PUB_RT),
            ))
        return self.cfn_template

    def add_private_subnet_routetable_association1(self):
        '''
        Add a private subnet route-table association
        to private subnet 1
        '''
        self.cfn_template.add_resource(SubnetRouteTableAssociation(
            title=constants.PRIV_RT_ASS1,
            SubnetId=Ref(constants.PRIV_SUBNET1),
            RouteTableId=Ref(constants.PRIV_RT),
            ))
        return self.cfn_template

    def add_public_subnet_routetable_association2(self):
        '''
        Add a public subnet route-table association
        to public subnet 2
        '''
        self.cfn_template.add_resource(SubnetRouteTableAssociation(
            title=constants.PUB_RT_ASS2,
            SubnetId=Ref(constants.PUB_SUBNET2),
            RouteTableId=Ref(constants.PUB_RT),
            ))
        return self.cfn_template

    def add_private_subnet_routetable_association2(self):
        '''
        Add a private subnet route-table association
        to private subnet 2
        '''
        self.cfn_template.add_resource(SubnetRouteTableAssociation(
            title=constants.PRIV_RT_ASS2,
            SubnetId=Ref(constants.PRIV_SUBNET2),
            RouteTableId=Ref(constants.PRIV_RT),
            ))
        return self.cfn_template

    def add_app_secuirty_group(self):
        '''
        Add security group tfor all application
        '''
        self.cfn_template.add_resource(SecurityGroup(
            title=constants.APP_SG,
            GroupDescription='Allow communication between application servers',
            SecurityGroupIngress=[
                SecurityGroupRule(
                    IpProtocol='tcp',
                    FromPort=int('0'),
                    ToPort=int('65535'),
                    CidrIp=Ref('PublicSubnet1CIDRBlock'),
                ),
                SecurityGroupRule(
                    IpProtocol='tcp',
                    FromPort=int('0'),
                    ToPort=int('65535'),
                    CidrIp=Ref('PrivateSubnet1CIDRBlock'),
                ),
                SecurityGroupRule(
                    IpProtocol='tcp',
                    FromPort=int('0'),
                    ToPort=int('65535'),
                    CidrIp=Ref('PublicSubnet2CIDRBlock'),
                ),
                SecurityGroupRule(
                    IpProtocol='tcp',
                    FromPort=int('0'),
                    ToPort=int('65535'),
                    CidrIp=Ref('PrivateSubnet2CIDRBlock'),
                ),
            ],
            SecurityGroupEgress=[
                SecurityGroupRule(
                    IpProtocol='-1',
                    CidrIp='0.0.0.0/0'
                )
            ],
            VpcId=Ref(constants.VPC)
        ))
        return self.cfn_template
