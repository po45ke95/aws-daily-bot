import boto3
from datetime import datetime, timedelta
import logging
import os
from dotenv import load_dotenv

## load .env file for aws credentials
load_dotenv()
region_name = os.getenv('REGION_NAME')
aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
account_id = os.getenv('ACCOUNT_ID')

# boto3 client intialization
client = boto3.client(
    'ce',
    region_name=region_name,
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key
)

# log initialization
logging.basicConfig(level=logging.INFO , format='%(asctime)s - %(levelname)s - %(message)s')

def days(days):

    end = datetime.now().strftime('%Y-%m-%d')
    start = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

    response = client.get_cost_and_usage(
        TimePeriod={
            'Start': start,
            'End': end
        },
        Granularity='DAILY',
        Metrics=['AmortizedCost'],
        Filter={
            "Dimensions": {
                "Key": "LINKED_ACCOUNT",
                "Values": [account_id]
            }
        }
    )

    cost_data = []

    for item in response['ResultsByTime']:
        date = item['TimePeriod']['Start']
        cost_str = item['Total']['AmortizedCost']['Amount']
        unit = item['Total']['AmortizedCost']['Unit']

        cost = str(round(float(cost_str),2))

        cost_detail = {
            "日期": date,
            "費用": cost + ' ' + unit
        }

        cost_data.append(cost_detail)

    # remove latest -1 days data
    dis = len(cost_data) - 1
    cost_data.pop(dis)

    return cost_data

def caluclate_last_two_days_ratio(cost_data):
    if len(cost_data) < 2:
        return "Insufficient data to calculate ratio"
    
    last_day_cost_str = cost_data[-1]['費用'].split(' ')[0]
    second_last_day_cost_str = cost_data[-2]['費用'].split(' ')[0]

    last_day_cost = float(last_day_cost_str)
    second_last_day_cost = float(second_last_day_cost_str)

    if second_last_day_cost != 0:
        ratio = round((last_day_cost / second_last_day_cost) - 1, 4)

        # ratio data type float -> str
        ratio = str(ratio)

        return ratio
    else:
        return "Cannot calculate ratio: cost for the second last day is zero."

if __name__ == "__main__":

    day_result = days(3)
    formatted_cost_data = "\n".join([f"日期: {item['日期']} , 費用: {item['費用']}," for item in day_result])
    print("Data:", formatted_cost_data)

    ratio = caluclate_last_two_days_ratio(day_result)
    print("Ratio of last day cost to second last day cost:", ratio + '%')