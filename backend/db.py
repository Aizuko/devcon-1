import os, boto3

REGION = os.environ.get("AWS_REGION", "us-east-1")
TABLE_NAME = os.environ.get("DYNAMO_TABLE", "security-prep-progress")

_resource = boto3.resource("dynamodb", region_name=REGION)
table = _resource.Table(TABLE_NAME)


def get_progress(user_name: str, module_id: int) -> dict:
    """Return {question_id: {level, completed}} for a user+module."""
    prefix = f"m{module_id}_"
    resp = table.query(
        KeyConditionExpression="user_name = :u AND begins_with(question_id, :p)",
        ExpressionAttributeValues={":u": user_name, ":p": prefix},
    )
    return {
        item["question_id"]: {"level": int(item["level"]), "completed": item["completed"]}
        for item in resp.get("Items", [])
    }


def update_progress(user_name: str, question_id: str, level: int, completed: bool):
    table.put_item(Item={
        "user_name": user_name,
        "question_id": question_id,
        "level": level,
        "completed": completed,
    })


def create_table():
    """One-time table creation helper."""
    client = boto3.client("dynamodb", region_name=REGION)
    client.create_table(
        TableName=TABLE_NAME,
        KeySchema=[
            {"AttributeName": "user_name", "KeyType": "HASH"},
            {"AttributeName": "question_id", "KeyType": "RANGE"},
        ],
        AttributeDefinitions=[
            {"AttributeName": "user_name", "AttributeType": "S"},
            {"AttributeName": "question_id", "AttributeType": "S"},
        ],
        BillingMode="PAY_PER_REQUEST",
    )
    print(f"✅ Created table {TABLE_NAME}")


if __name__ == "__main__":
    create_table()
