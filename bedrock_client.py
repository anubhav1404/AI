import os
import boto3
from dotenv import load_dotenv

load_dotenv()

client = boto3.client(
    "bedrock",
    region_name=os.getenv("AWS_DEFAULT_REGION"),
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
)

def generate_text(prompt, model="anthropic.claude-3-haiku-20240307-v1:0"):
    response = client.invoke_model(
        modelId=model,
        content=prompt,
        accept="application/json",
        format="json"
    )
    return response['content']

