import os
import boto3
from datetime import datetime, timedelta
from dotenv import load_dotenv

## load .env file for aws credentials
load_dotenv()
region_name = os.getenv('REGION_NAME')
aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')

# boto3 client intialization
client = boto3.client(
    'ce', 
    region_name=region_name,
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key
)

# data by day
days = 2
end = datetime.now().strftime('%Y-%m-%d')
start = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

response = client.get_cost_and_usage_with_resources(
    TimePeriod={
        'Start': start,
        'End': end
    },
    Granularity='DAILY',
    Metrics=['BlendedCost'],
    Filter={
        'Dimensions':{
            'Key': 'SERVICE',
            'Values':['Amazon Elastic Compute Cloud - Compute']
        }
    },
    GroupBy=[
        {
            'Type': 'DIMENSION',
            'Key': 'RESOURCE_ID'
        }
    ]
)

# 初始化一個變數用來保存Amount的總和
total_amount = 0.0

# 迭代每個時間區段的結果
for result_by_time in response.get('ResultsByTime', []):
    # 迭代每個資源組
    for group in result_by_time.get('Groups', []):
        # 獲取BlendedCost的Amount
        amount = group.get('Metrics', {}).get('BlendedCost', {}).get('Amount', 0)
        # 轉換為浮點數並加到總和中
        total_amount += float(amount)

total_amount = round(total_amount,2)

print(
    f"The total BlendedCost Amount is: {total_amount} USD,\n"
    f"Time periods: {start} - {end}"
    )