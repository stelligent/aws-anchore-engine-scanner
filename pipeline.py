'''
Launches AWS CodePipeline stack
'''
import os
import tasks.github_token as token
from anchore.main import AnchoreEngine

PIPELINE_CONFIGS = 'examples/aws-codepipeline/pipeline_configs.yml'

def main():
    '''
    AWS CODEPIPELINE creation entrypoint
    '''
    anchore_engine = AnchoreEngine()
    anchore_engine.deploy_all(PIPELINE_CONFIGS)
    return anchore_engine

if __name__ == '__main__':
    main()
