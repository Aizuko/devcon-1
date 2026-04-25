import os

REGION = os.environ.get("AWS_REGION", os.environ.get("AWS_DEFAULT_REGION", "us-west-2"))
TABLE_NAME = os.environ.get("DYNAMO_TABLE", "security-prep-progress")

# Try DynamoDB, fall back to in-memory store
_use_dynamo = False
_memory_store = {}  # {user_name: {question_id: {level, completed}}}

try:
    import boto3
    _resource = boto3.resource("dynamodb", region_name=REGION)
    table = _resource.Table(TABLE_NAME)
    table.table_status  # triggers credential check
    _use_dynamo = True
    print(f"✅ Using DynamoDB table: {TABLE_NAME}")
except Exception:
    print("⚠️  DynamoDB unavailable, using in-memory storage (progress resets on restart)")


def get_progress(user_name: str, module_id: int) -> dict:
    prefix = f"m{module_id}_"
    if _use_dynamo:
        resp = table.query(
            KeyConditionExpression="user_name = :u AND begins_with(question_id, :p)",
            ExpressionAttributeValues={":u": user_name, ":p": prefix},
        )
        return {
            item["question_id"]: {"level": int(item["level"]), "completed": item["completed"]}
            for item in resp.get("Items", [])
        }
    else:
        return {
            qid: v for qid, v in _memory_store.get(user_name, {}).items()
            if qid.startswith(prefix)
        }


def update_progress(user_name: str, question_id: str, level: int, completed: bool):
    if _use_dynamo:
        table.put_item(Item={
            "user_name": user_name,
            "question_id": question_id,
            "level": level,
            "completed": completed,
        })
    else:
        _memory_store.setdefault(user_name, {})[question_id] = {
            "level": level, "completed": completed,
        }
