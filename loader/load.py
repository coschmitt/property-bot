import boto3
from datetime import datetime
import json

dynamodb = boto3.resource('dynamodb', region_name = 'us-east-2')
sqs = boto3.resource("sqs", region_name = "us-east-2")

def create_or_update(table, item):
    response = table.put_item(Item=item, ReturnValues='ALL_OLD')

    if 'Attributes' in response: # item with the same key already exists
        created_on = response["Attributes"]["created_on"]
        response = table.update_item(
            Key={"address": item["address"]}, 
            UpdateExpression='SET created_on = :val',
            ExpressionAttributeValues={':val': created_on}
        )
        

def get_key(address):
    return "".join(address["street"].split()) + "$" + address["zipcode"]

def load_from_sqs(event, context):
    table_name = "redfin-listings-table"
    queue = sqs.get_queue_by_name(QueueName="property-bot-queue")
    table = dynamodb.Table(table_name)
    entries = []
    print(context)
    
    for message in event['Records']:
        body = json.loads(message['body'])
        item = {
            "address"    : get_key(body["address"]),
            "zipcode"    : body["address"]["zipcode"],
            "created_on" : str(datetime.now()),
            "json_body"  : json.dumps(body)
        }

        create_or_update(table, item)
        entries.append({"Id": message["messageId"], "ReceiptHandle": message['receiptHandle']})
    queue.delete_messages(Entries = entries)


# if __name__ == '__main__':
#     load_from_sqs()

