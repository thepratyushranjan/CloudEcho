import os

import boto3
import pandas as pd
from config.config import Config

# Set environment variables using Config
os.environ['AWS_DEFAULT_REGION'] = Config.AWS_DEFAULT_REGION
os.environ['AWS_ACCESS_KEY_ID'] = Config.AWS_ACCESS_KEY_ID
os.environ['AWS_SECRET_ACCESS_KEY'] = Config.AWS_SECRET_ACCESS_KEY

# print("REGION:", Config.AWS_DEFAULT_REGION)
# print("KEY ID:", Config.AWS_ACCESS_KEY_ID[:4] + '…')

# # Use boto3 to interact with AWS
ec2 = boto3.client('ec2')
print("Default region:", ec2.meta.region_name)
print("Regions list:", [r['RegionName'] for r in ec2.describe_regions()['Regions']])


def collect_all_instance_types():
    rows = []
    ec2_default = boto3.client('ec2')
    regions = [r['RegionName'] for r in ec2_default.describe_regions()['Regions']]

    for region in regions:
        client = boto3.client('ec2', region_name=region)
        paginator = client.get_paginator('describe_instance_types')
        for page in paginator.paginate():
            for it in page['InstanceTypes']:
                mem_mib = it['MemoryInfo']['SizeInMiB']
                ram_gib = round(mem_mib / 1024, 2)
                net_perf = it.get('NetworkInfo', {}).get('NetworkPerformance')

                rows.append({
                    'Region':               region,
                    'InstanceType':         it['InstanceType'],
                    'vCPUs':                it['VCpuInfo']['DefaultVCpus'],
                    'MemoryMiB':            mem_mib,
                    'RAM (GiB)':            ram_gib,
                    'NetworkPerformance':   net_perf,
                    'StorageInfo':          it.get('InstanceStorageInfo'),
                    'Accelerators':         it.get('GpuInfo') or it.get('FpgaInfo')
                })

    return pd.DataFrame(rows)


print("Collecting EC2 instance details...")
df_types = collect_all_instance_types()
df_types.head()