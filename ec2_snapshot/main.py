import boto3
import logging
import datetime
import pytz

# initialize data
region_name = ''
aws_access_key_id = ''
aws_secret_access_key = ''


# boto3 client connection
ec2_client = boto3.client(
    'ec2',
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key
    )


# log initialization
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# create ebs snapshot function
def create_snapshots(volume_ids, description="Backup Snapshot"):
    """
    为给定的 EBS volume_ids 创建快照，并增加标签
    :param volume_ids: 一个包含 volume IDs 的列表
    :param description: 快照的描述
    """
    ec2_client = boto3.client('ec2')
    snapshot_ids = []

    for volume_id in volume_ids:
        try:
            response = ec2_client.create_snapshot(
                VolumeId=volume_id,
                Description=description
            )
            snapshot_id = response['SnapshotId']
            snapshot_ids.append(snapshot_id)
            logging.info(f"Successfully created snapshot {snapshot_id} from volume {volume_id}")

            # 创建标签
            create_time = datetime.datetime.now(pytz.timezone('Asia/Taipei')).strftime('%Y-%m-%d %H:%M:%S')
            tags = [
                {
                    'Key': 'Volume_ID',
                    'Value': volume_id
                },
                {
                    'Key': 'Create_Time',
                    'Value': create_time
                }
            ]
            ec2_client.create_tags(Resources=[snapshot_id], Tags=tags)

        except Exception as e:
            logging.error(f"Failed to create snapshot for volume {volume_id}. Error: {e}")

    return snapshot_ids


def delete_snapshots_7(volume_ids):
    ec2_client = boto3.client('ec2')
    current_time = datetime.datetime.now(pytz.timezone('Asia/Taipei'))

    deleted_flag = False

    for volume_id in volume_ids:
        try:
            snapshots = ec2_client.describe_snapshots(Filters=[{'Name': 'volume-id', 'Values': [volume_id]}])
        except Exception as e:
            logging.error(f"Error fetching snapshots for volume {volume_id}. Error: {e}")
            continue

        for snapshot in snapshots['Snapshots']:
            if (current_time - snapshot['StartTime'].replace(tzinfo=pytz.timezone('Asia/Taipei'))).days > 7:
                try:
                    ec2_client.delete_snapshot(SnapshotId=snapshot['SnapshotId'])
                    logging.info(f"Deleted snapshot {snapshot['SnapshotId']} for volume {volume_id}")
                    deleted_flag = True
                except Exception as e:
                    logging.error(f"Error deleting snapshot {snapshot['SnapshotId']} for volume {volume_id}. Error: {e}")

    if not deleted_flag:
        logging.info("Did not delete any snapshot")


# main function
if __name__ == "__main__":

    volumes_id = ['vol-07b7f5409dbf720be']

    tz = pytz.timezone('Asia/Taipei')
    current_time_utc_8 = datetime.datetime.now(tz)
    timestamp = current_time_utc_8.strftime('%Y%m%d%H%M%S')

    create_snapshots(volumes_id, f"{timestamp}")

    delete_snapshots_7(volumes_id)