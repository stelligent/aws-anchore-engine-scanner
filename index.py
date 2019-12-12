'''
Create Anchore-Engine cloudformation templates
and Launches all stacks for Anchore-Engine
'''
from anchore.main import AnchoreEngine

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
    anchore_engine.deploy_all(CONFIGS)
    return anchore_engine

if __name__ == '__main__':
    main()
