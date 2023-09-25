import boto3
from datetime import datetime, timedelta
import logging
import requests

# initialize data
region_name = ''
aws_access_key_id = ''
aws_secret_access_key = ''
account_id = ''
telegram_token = ''
chat_id = ''

# boto3 client intialization
client = boto3.client(
    'ce',
    region_name=region_name,
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key
)

# log initialization
logging.basicConfig(level=logging.INFO , format='%(asctime)s - %(levelname)s - %(message)s')


# daiy fuction
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
    # dis = len(cost_data) - 1
    # cost_data.pop(dis)

    return cost_data


# all used services daily cost
def catgories():

    # 设置起始日期为当前月的第一天，结束日期为今天
    end = datetime.now().strftime('%Y-%m-%d')
    start = datetime(datetime.now().year, datetime.now().month, 1).strftime('%Y-%m-%d')

    response = client.get_cost_and_usage(
        TimePeriod={
            'Start': start,
            'End': end
        },
        Granularity='DAILY',
        Metrics=['UnblendedCost'],
        GroupBy=[
            {
                'Type': 'DIMENSION',
                'Key': 'SERVICE'
            }
        ]
    )

    # 使用字典来累计每个服务的总费用
    services_total_cost = {}

    for result in response.get('ResultsByTime', []):
        for group in result.get('Groups', []):
            service_name = group['Keys'][0]
            cost = round(float(group['Metrics']['UnblendedCost']['Amount']), 2)

            # 如果该服务在字典中，则累加费用；否则，初始化该服务的费用
            if service_name in services_total_cost:
                services_total_cost[service_name] += cost
            else:
                services_total_cost[service_name] = cost

    # 根据费用对服务进行排序，并选择费用最高的前三个服务
    top_three_services = sorted(services_total_cost.items(), key=lambda x: x[1], reverse=True)[:3]

    # 格式化结果
    formatted_data = {}
    for service, cost in top_three_services:
        formatted_data[service] = f"{'{:.2f}'.format(cost)} USD"

    return formatted_data


# calculate last two day pricing functions
def caluclate_last_two_days_ratio(cost_data):
    if len(cost_data) < 2:
        return "Insufficient data to calculate ratio"
    
    last_day_cost_str = cost_data[-2]['費用'].split(' ')[0]
    second_last_day_cost_str = cost_data[-3]['費用'].split(' ')[0]

    last_day_cost = float(last_day_cost_str)
    second_last_day_cost = float(second_last_day_cost_str)

    if second_last_day_cost != 0:
        ratio = round((last_day_cost / second_last_day_cost) - 1, 4)

        # ratio data type float -> str
        ratio = str(ratio)

        return ratio
    else:
        return "Cannot calculate ratio: cost for the second last day is zero."


# calculate monthly fucntion
def monthly():
    end = datetime.now().strftime('%Y-%m-%d')
    start = datetime.now().strftime('%Y-%m-01')
    response = client.get_cost_and_usage(
        TimePeriod={
            'Start': start,
            'End': end
        },
        Granularity='MONTHLY',
        Metrics=['AmortizedCost'],
        Filter={
            "Dimensions": {
                "Key": "LINKED_ACCOUNT",
                "Values": [account_id]
            }
        }
    )

    cost_now = 0
    for item in response['ResultsByTime']:
        date = item['TimePeriod']['Start']
        cost_str = item['Total']['AmortizedCost']['Amount']
        unit = item['Total']['AmortizedCost']['Unit']

        cost_now += round(float(cost_str),2)
    return cost_now


# send telegram message function
def send_telegram_message(chat_id, text):
    base_url = f'https://api.telegram.org/bot{telegram_token}/sendMessage'
    payload = {
        "chat_id": chat_id,
        "text": text,
    }
    response = requests.post(base_url, data=payload)
    return response.json()


# grouping data of telegram messages function
def send_total_message():
    day_result = days(3)
    formatted_data = "\n".join([f"日期: {item['日期']} , 費用: {item['費用']}" for item in day_result])

    ratio = caluclate_last_two_days_ratio(day_result)
    monthly_data = monthly()

    services_data = catgories()
    formatted_services_data = "\n".join([f"服務: {service} , 費用: {cost}" for service, cost in services_data.items()])

    final = (
        f'AWS_ACCOUNT: {account_id}' + '\n'
        f'AWS_REGION: {region_name}' + '\n'
        f'消費日期暨時間: \n{formatted_data}' + ' (昨日尚未出帳完成僅供參考)' + '\n'
        f'消費成長比: {ratio} % (累積計算至出帳完成，不含昨日)' + '\n'
        f'本月壘積消費: {monthly_data} USD (包含未出帳數據總和)' + '\n'
        f'本月前三服務消費: \n{formatted_services_data}'
    )
    send_telegram_message(chat_id, final)
    return final

if __name__ == "__main__":

    print(send_total_message())
    logging.info(f'Send pricing data to telegram.')