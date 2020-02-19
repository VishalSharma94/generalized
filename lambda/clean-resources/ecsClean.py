import json
import botocore
import boto3
import logging
import datetime
from helpers import *
from datetime import timezone
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
#=================================================================================
#                               ECS CLEAN
#=================================================================================
def ecs_cleaning():
    try:
        regions = get_regions()
        for region in regions['Regions']:
            ecs = boto3.client('ecs', region_name=region['RegionName'])
            try:
                ecs_result = ecs.list_clusters()
                logger.info('REGION >> ------------- '+str(region['RegionName'])+" | status: "+str(region['OptInStatus']))
                cl = ecs.describe_clusters(clusters=ecs_result['clusterArns'], include=['TAGS'])
                for cluster in cl['clusters']:
                    if len(cluster['tags'])>0:
                        check_terminate_ecs(ecs, cluster, cluster['tags'], False)
                    else:
                        check_terminate_ecs(ecs, cluster, None, True)
                logger.info('REGION >> ------------ END')
            except botocore.exceptions.ClientError as e:
                logger.info('CleanUp >> ECS '+str(e.response['Error']['Message']))
    except botocore.exceptions.ClientError as e:
        logger.info('CleanUp >> Error listing ECS '+str(e.response['Error']['Message']))

def check_terminate_ecs(ecs_client, cluster, tags, terminate_now):
    try:
        if terminate_now:
            logger.info('CleanUp >> Terminating Now, has no tags (Stopping for now): '+cluster['clusterName'])
            #delete_cluster(ecs_client, cluster['clusterArn'])
        else:
            if check_tags_exist(tags, get_mandatory_tags(), 3):
                logger.info('CleanUp >> ECS cluster '+cluster['clusterName']+' | has mandatory tags...')
                #delete_cluster(ecs_client, cluster['clusterArn'])
            else:
                logger.info('CleanUp >> ECS cluster '+cluster['clusterName']+' missing mandatory tags, will be terminated')
                #delete_cluster(ecs_client, cluster['clusterArn'])
    except botocore.exceptions.ClientError as e:
        logger.info('CleanUp >> Error terminating ECS Cluster: '+cluster['clusterName']+': '+str(e.response['Error']['Message']))

def delete_cluster(ecs_client, cluster_arn):
    try:
        instances = ecs_client.list_container_instances(cluster=cluster_arn)
        for i in instances['containerInstanceArns']:
            ecs_client.deregister_container_instance(cluster=cluster_arn,containerInstance=i,force=True)
            logger.info('CleanUp >> deregistering container instance: '+str(i))
        ecs_client.delete_cluster(cluster=cluster_arn)
    except botocore.exceptions.ClientError as e:
         logger.info('CleanUp >> Error terminating ECS Cluster: '+cluster['clusterName']+': '+str(e.response['Error']['Message']))
#=================================================================================