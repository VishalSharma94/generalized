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
#                               EKS CLEAN
#=================================================================================
def eks_cleaning():
    try:
        regions = get_regions()
        for region in regions['Regions']:
            eks = boto3.client('eks', region_name=region['RegionName'])
            try:
                eks_result = eks.list_clusters()
                logger.info('REGION >> ------------- '+str(region['RegionName'])+" | status: "+str(region['OptInStatus']))
                for cluster in eks_result['clusters']:
                    cl = eks.describe_cluster(name=cluster)
                    t = cl['cluster']['tags']
                    if len(t)>0:
                        check_terminate_eks(eks, cl['cluster'], t, False)
                    else:
                        check_terminate_eks(eks, cl['cluster'], None, True)
                logger.info('REGION >> ------------ END')
            except botocore.exceptions.ClientError as e:
                logger.info('CleanUp >> EKS '+str(e.response['Error']['Message']))
    except botocore.exceptions.ClientError as e:
        logger.info('CleanUp >> Error listing EKS '+str(e.response['Error']['Message']))

def check_terminate_eks(eks_client, cluster, tags, terminate_now):
    try:
        if terminate_now:
            logger.info('CleanUp >> EKS has no tags mandatory tags, terminating EKS cluster: '+cluster['name'])
            #delete_eks_cluster(eks_client, cluster)
        else:
            if check_tags_exist(tags, get_mandatory_tags(), 2):
                logger.info('CleanUp >> EKS cluster '+cluster['name']+' | has mandatory tags...')
                #delete_eks_cluster(eks_client, cluster)      
            else:
                logger.info('CleanUp >> EKS cluster '+cluster['name']+' missing mandatory tags, will be terminated')
                #delete_eks_cluster(eks_client, cluster)
    except botocore.exceptions.ClientError as e:
        logger.info('CleanUp >> Error terminating EKS Cluster: '+cluster['name']+': '+str(e.response['Error']['Message']))

def delete_eks_node_groups(eks_client, cluster):
    try:
        node_groups = eks_client.list_nodegroups(clusterName=cluster['name'])
        for ng in node_groups['nodegroups']:
            try:
                eks_client.delete_nodegroup(clusterName=cluster['name'], nodegroupName=ng)
            except botocore.exceptions.ClientError as e:
                logger.info('CleanUp >> Error deleting nodegroup :'+str(ng))
    except botocore.exceptions.ClientError as e:
        logger.info('CleanUp >> Error terminating EKS Cluster: '+cluster['name']+': '+str(e.response['Error']['Message'])) 

def delete_eks_fargateprofile(eks_client, cluster):
    try:
        fargate_profiles = eks_client.list_fargate_profiles(clusterName=cluster['name'])
        for fargate in fargate_profiles['fargateProfileNames']:
            try:
                eks_client.delete_fargate_profile(clusterName=cluster['name'], fargateProfileName=fargate)
            except botocore.exceptions.ClientError as e:
                logger.info('CleanUp >> Error deleting fargate profile :'+str(fargate))
    except botocore.exceptions.ClientError as e:
        logger.info('CleanUp >> Error terminating EKS Cluster: '+cluster['name']+': '+str(e.response['Error']['Message']))

def delete_eks_cluster(eks_client, cluster):
    try:
        delete_eks_node_groups(eks_client, cluster)
        delete_eks_fargateprofile(eks_client, cluster)
        eks_client.delete_cluster(name=cluster['name'])
    except botocore.exceptions.ClientError as e:
        logger.info('CleanUp >> Error terminating EKS Cluster: '+cluster['name']+': '+str(e.response['Error']['Message']))
#=================================================================================