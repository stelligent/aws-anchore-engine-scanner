'''
This stores global variables for Anchore Engine deployment
'''

# USER DATA
USERDATA = '''#!/bin/bash
set -xe
source /etc/profile
mkdir -p /userdata
cat > /userdata/init-script.sh <<'INITSCRIPT'
#!/bin/bash
set -e

echo '==============================================================================='
echo '======================== System Setup  ========================================'
echo '==============================================================================='

# Configuration to allow ECS IAM Task Roles to be used
sysctl -w net.ipv4.conf.all.route_localnet=1
iptables -t nat -A PREROUTING -p tcp -d 169.254.170.2 --dport 80 -j DNAT --to-destination 127.0.0.1:51679
iptables -t nat -A OUTPUT -d 169.254.170.2 -p tcp -m tcp --dport 80 -j REDIRECT --to-ports 51679

echo '==============================================================================='
echo '======================== Start ECS Agent ======================================'
echo '==============================================================================='

# Start the AWS ECS Agent
apt-get update
apt-get -y install apt-transport-https ca-certificates curl software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"

echo '==============================================================================='
echo '========================= Install Docker ======================================'
echo '==============================================================================='

apt-get update
apt-get install -y docker-ce
docker run --name amazon-aws-ecs-agent --detach=true --restart=on-failure:10 --volume=/var/run/docker.sock:/var/run/docker.sock --volume=/var/log/ecs/:/log --volume=/var/lib/ecs/data:/data --volume=/sys/fs/cgroup:/sys/fs/cgroup:ro --volume=/run/containerd:/var/lib/docker/execdriver/native:ro --publish=127.0.0.1:51678:51678 --net=host --privileged --env=ECS_APPARMOR_CAPABLE=true --env=ECS_AVAILABLE_LOGGING_DRIVERS='["json-file","awslogs","syslog"]' --env=ECS_ENABLE_CONTAINER_METADATA=true --env=ECS_ENABLE_TASK_IAM_ROLE=true --env=ECS_ENABLE_TASK_IAM_ROLE_NETWORK_HOST=true --env=ECS_TASK_METADATA_RPS_LIMIT=100,150 --env=ECS_LOGFILE=/log/ecs-agent.log --env=ECS_LOGLEVEL=info --env=ECS_DATADIR=/data --env=ECS_CLUSTER=${Cluster} amazon/amazon-ecs-agent:latest
INITSCRIPT

bash /userdata/init-script.sh

apt-get -y install python-setuptools
easy_install https://s3.amazonaws.com/cloudformation-examples/aws-cfn-bootstrap-latest.tar.gz
/usr/local/bin/cfn-signal -e $? --stack ${AWS::StackName} --resource AutoScalingGroup --region ${AWS::Region}
'''

# VPC CFN Resource Logical IDs
EIP = 'VPCEIP'
NAT = 'NatGateway'
VPC = 'ANCHOREVPC'
IGW = 'InternetGateway'
PUB_ROUTE = 'PublicRoute'
PRIV_ROUTE = 'PrivateRoute'
ATTACH_GW = 'AttachGateway'
APP_SG = 'AppSecurityGroup'
PUB_RT = 'PublicRouteTable'
PRIV_RT = 'PrivateRouteTable'
PUB_SUBNET1 = 'PublicSubnet1'
PRIV_SUBNET1 = 'PrivateSubnet1'
PUB_SUBNET2 = 'PublicSubnet2'
PRIV_SUBNET2 = 'PrivateSubnet2'
PUB_RT_ASS1 = 'PublicSubnetRouteTableAssociation1'
PRIV_RT_ASS1 = 'PrivateSubnetRouteTableAssociation1'
PUB_RT_ASS2 = 'PublicSubnetRouteTableAssociation2'
PRIV_RT_ASS2 = 'PrivateSubnetRouteTableAssociation2'

# ALB CFN Resource Logical IDs
ALB = 'LoadBalancer'
ALB_TG = 'LoadBalancerTargetGroup'
LISTENER = 'LoadBalancerListener'
ALB_SG = 'LoadBalancerSecurityGroup'

# ECR CFN Resoucres Logical ID
IMAGE_TAG = 'ImageTag'
ECR_REPO = 'AppECRRepository'
TEST_IMAGE_REPO = 'TestedImageECRRepository'

# EC2 CFN Resources Logical ID
CLUSTER = 'Cluster'
SUP = 'ScaleUpPolicy'
SDP = 'ScaleDownPolicy'
INST_ROLE = 'InstanceRole'
INST_ASG = 'AutoScalingGroup'
INST_LC = 'LaunchConfiguration'
INST_PROFILE = 'InstanceProfile'
SSH_SG = 'InstanceSSHSecurityGroup'
INST_PROFILE_ROLE = 'InstanceProfileRole'
SSH_SG_ING = 'InstanceSSHSecurityGroupIngress'

# ECS CFN Resoucres Logical IDS
TASK = 'Task'
SERVICE = 'Service'
CLUSTER_SIZE = '2'
CLA = 'CpuLowAlarm'
CHA = 'CpuHighAlarm'
MLA = 'MemoryLowAlarm'
TASK_ROLE = 'TaskRole'
MHA = 'MemoryHighAlarm'
ENG_LOG = 'EngineLogGroup'
DB_LOG = 'DatabaseLogGroup'
SERVICE_ROLE = 'ServiceRole'

# ROUTE53 CFN Resources Logical Ids
RECORDSET = 'AnchoreEngineRecordSet'
# OUTPUTS
ALB_NAME = 'LoadBalancerDNSName'
ALB_TG_NAME = 'LoadBalancerTargetGroupName'

# CFN Template names
VPC_TEMPLATE = 'anchore_vpc.yml'
ALB_TEMPLATE = 'anchore_alb.yml'
ECS_TEMPLATE = 'anchore_ecs.yml'
ECR_TEMPLATE = 'anchore_ecr.yml'
EC2_INST_TEMPLATE = 'anchore_ec2_cluster.yml'
RECORDSET_TEMPLATE = 'anchore_recordset.yml'
