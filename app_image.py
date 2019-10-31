'''
Create ECR cloudformation template and
Launches ECR stack
'''
from anchore.main import AnchoreEngine

ECR_CONFIGS = 'configs/ecr_configs.yml'

def main():
    '''
    AWS ECR repository creation entrypoint
    '''
    anchore_engine = AnchoreEngine()
    anchore_engine.create_ecr_template()
    anchore_engine.deploy_all(ECR_CONFIGS)
    return anchore_engine

if __name__ == '__main__':
    main()
    