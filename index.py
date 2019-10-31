'''
Create Anchore-Engine cloudformation templates
and Launches all stacks for Anchore-Engine
'''
import tasks.github_token as token
from anchore.main import AnchoreEngine

KEYNAME = 'anchore_demo'
CONFIGS = 'configs/configs.yml'

def main():
    '''
    Anchore-Engine stacks creation entrypoint
    '''
    anchore_engine = AnchoreEngine()
    anchore_engine.create_vpc_template()
    anchore_engine.create_alb_template()
    anchore_engine.create_ecs_template()
    anchore_engine.create_ec2_cluster_template()
    anchore_engine.create_route53_recordset()
    anchore_engine.deploy_keypair(KEYNAME)
    anchore_engine.deploy_all(CONFIGS)
    return anchore_engine

if __name__ == '__main__':
    main()
