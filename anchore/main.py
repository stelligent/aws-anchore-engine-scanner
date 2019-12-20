'''
Anchore-Engine

This create cloudformation templates to deploy Anchore Engine
'''
import os
from anchore.vpc import VPCTemplate
from anchore.alb import ALBTemplate
from anchore.ecs import ECSTemplate
from anchore.ecr import ECRTemplate
from anchore.ec2_cluster import EC2ClusterTemplate
import anchore.constants as constants
from tasks.deploy_stacks import deploy_stack
from tasks.keypair import create_keypair

#pylint: disable=too-many-instance-attributes
class AnchoreEngine():
    '''
    Create Anchore engine deployment class object
    '''
    def __init__(self):
        self.version = "2010-09-09"
        self.region = os.environ.get('AWS_DEFAULT_REGION')
        self.vpc_template = VPCTemplate()
        self.alb_template = ALBTemplate()
        self.ecs_template = ECSTemplate()
        self.ecr_template = ECRTemplate()
        self.ec2_template = EC2ClusterTemplate()

    def write_file(self, filename, template):
        '''
        Write template into a YAML file
        '''
        with open(filename, 'w') as yaml_file:
            yaml_file.write(template.to_yaml())

    def create_vpc_template(self):
        '''
        VPC Template creation entrypoint
        '''

        # Create Anchore Engine VPC template
        self.vpc_template.add_descriptions("Launch a simple VPC")
        self.vpc_template.add_version(self.version)
        self.vpc_template.add_parameters()
        self.vpc_template.add_outputs()
        self.vpc_template.add_nat()
        self.vpc_template.add_vpc()
        self.vpc_template.add_vpc_eip()
        self.vpc_template.add_public_route()
        self.vpc_template.add_private_route()
        self.vpc_template.add_public_subnet1()
        self.vpc_template.add_public_subnet2()
        self.vpc_template.add_private_subnet1()
        self.vpc_template.add_private_subnet2()
        self.vpc_template.add_internet_gateway()
        self.vpc_template.add_attach_gateway()
        self.vpc_template.add_public_routetable()
        self.vpc_template.add_private_routetable()
        self.vpc_template.add_app_secuirty_group()
        self.vpc_template.add_public_subnet_routetable_association1()
        self.vpc_template.add_private_subnet_routetable_association1()
        self.vpc_template.add_public_subnet_routetable_association2()
        vpc_template_file = self.vpc_template.add_private_subnet_routetable_association2()

        # write template file to directory
        self.write_file(constants.VPC_TEMPLATE, vpc_template_file)
        return True

    def create_alb_template(self):
        '''
        ALB Template creation entrypoint
        '''

        # Create Anchore Engine ALB template
        self.alb_template.add_descriptions("Archore-Engine Container Scanning System Load Balancer")
        self.alb_template.add_version(self.version)
        self.alb_template.add_parameters()
        self.alb_template.add_load_balancer()
        self.alb_template.add_alb_listener()
        self.alb_template.add_alb_target_group()
        self.alb_template.add_alb_secuirty_group()
        alb_template_file = self.alb_template.add_outputs()

        # write template file to directory
        self.write_file(constants.ALB_TEMPLATE, alb_template_file)
        return True

    def create_ecr_template(self):
        '''
        ECR Template creation entrypoint
        '''

        # Create Anchore Engine ECR template
        self.ecr_template.add_descriptions("Demo Anchore-Engine ECR Repository")
        self.ecr_template.add_version(self.version)
        self.ecr_template.add_parameters()
        self.ecr_template.add_ecr_repository(constants.ECR_REPO, 'AppRepoName')
        self.ecr_template.add_ecr_repository(constants.TEST_IMAGE_REPO, 'TestImageRepoName')
        ecr_template_file = self.ecr_template.add_outputs()

        # write template file to directory
        self.write_file(constants.ECR_TEMPLATE, ecr_template_file)
        return True

    def create_ec2_cluster_template(self):
        '''
        EC2 Instance Template creation entrypoint
        '''

        # Create Anchore Engine EC2 template
        self.ec2_template.add_descriptions("Demo Anchore-Engine EC2 Instance")
        self.ec2_template.add_version(self.version)
        self.ec2_template.add_parameters()
        self.ec2_template.add_ecs_cluster()
        self.ec2_template.add_instance_role()
        self.ec2_template.add_ssh_security()
        self.ec2_template.add_instance_profile()
        self.ec2_template.add_auto_scaling_group()
        self.ec2_template.add_launch_config()
        self.ec2_template.add_scaling_policy(
            constants.SDP,
            '300',
            constants.CLUSTER_SIZE
        )
        self.ec2_template.add_scaling_policy(
            constants.SUP,
            '600',
            '-1'
        )
        self.ec2_template.add_cloudwatch_alarm(
            constants.MHA,
            constants.SUP,
            'Cluster memory above 75%',
            'GreaterThanThreshold',
            1,
            'MemoryReservation',
            300,
            75
        )
        self.ec2_template.add_cloudwatch_alarm(
            constants.MLA,
            constants.SDP,
            'Cluster Memory below 60%',
            'LessThanThreshold',
            2,
            'MemoryReservation',
            900,
            60
        )
        self.ec2_template.add_cloudwatch_alarm(
            constants.CHA,
            constants.SUP,
            'Cluster CPU above 75%',
            'GreaterThanThreshold',
            1,
            'CPUReservation',
            300,
            75
        )
        self.ec2_template.add_cloudwatch_alarm(
            constants.CLA,
            constants.SDP,
            'Cluster CPU below 60%',
            'LessThanThreshold',
            2,
            'CPUReservation',
            900,
            60
        )
        ec2_template_file = self.ec2_template.add_outputs()

        # write template file to directory
        self.write_file(constants.EC2_INST_TEMPLATE, ec2_template_file)
        return True

    def create_ecs_template(self):
        '''
        ECS Template creation entrypoint
        '''

        # Create Anchore Engine ECS template
        self.ecs_template.add_descriptions("Demo Anchore-Engine Cluster")
        self.ecs_template.add_version(self.version)
        self.ecs_template.add_parameters()
        self.ecs_template.add_ecs_service()
        self.ecs_template.add_ecs_task()
        self.ecs_template.add_ecs_service_role()
        self.ecs_template.add_ecs_task_role()
        self.ecs_template.add_engine_log_group()
        self.ecs_template.add_database_log_group()
        ecs_template_file = self.ecs_template.add_outputs()

        # write template file to directory
        self.write_file(constants.ECS_TEMPLATE, ecs_template_file)
        return True

    def deploy_keypair(self, keyname):
        '''
        Create EC2 key pair
        '''
        res = create_keypair(self.region, keyname)
        with open('anchore_demo.pem', 'w+') as key_file:
            key_file.write(res)

    def deploy_all(self, configs):
        '''
        Deploy cloudformation stack
        '''
        res = deploy_stack(configs)
        return res
        