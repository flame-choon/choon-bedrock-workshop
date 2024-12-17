import json
import os
import sys

import boto3
import botocore

# Set up the session
session = boto3.Session(profile_name='YOUR_AWS_PROFILE_NAME')
sts_client = session.client('sts')
bedrock_assume_role = sts_client.assume_role(
    RoleArn="arn:aws:iam::YOUR_AWS_ACCOUNT_ID:role/YOUR_ASSUME_ROLE_NAME",
    RoleSessionName="bedrock-session"
)

# Create the Bedrock client
bedrock_client = boto3.client('bedrock', 
    region_name='us-east-1',
    aws_access_key_id=bedrock_assume_role['Credentials']['AccessKeyId'],
    aws_secret_access_key=bedrock_assume_role['Credentials']['SecretAccessKey'],
    aws_session_token=bedrock_assume_role['Credentials']['SessionToken']
)
bedrock_runtime = boto3.client('bedrock-runtime',
    region_name='us-east-1',
    aws_access_key_id=bedrock_assume_role['Credentials']['AccessKeyId'],
    aws_secret_access_key=bedrock_assume_role['Credentials']['SecretAccessKey'],
    aws_session_token=bedrock_assume_role['Credentials']['SessionToken']
)

# AWS Bedrock 모델을 호출하여 텍스트를 생성하는 함수
def invoke_bedrock_model(bedrock_runtime, 
                         prompt_text, 
                         model_id="amazon.titan-text-express-v1", 
                         max_tokens=1024, 
                         top_p=0.95, 
                         temperature=0.2):
    """
    Invoke AWS Bedrock model with given parameters
    
    Args:
        bedrock_runtime: Bedrock runtime client
        prompt_text: Input text prompt
        model_id: Bedrock model ID
        max_tokens: Maximum number of tokens to generate
        top_p: Top P sampling parameter
        temperature: Temperature parameter for text generation
    
    Returns:
        str: Generated text response
    """
    try:
        body = json.dumps({
            "inputText": prompt_text,
            "textGenerationConfig": {
                "maxTokenCount": max_tokens,
                "topP": top_p,
                "temperature": temperature
            }
        })
        
        response = bedrock_runtime.invoke_model(
            body=body,
            modelId=model_id,
            accept="application/json",
            contentType="application/json"
        )
        response_body = json.loads(response.get("body").read())
        return response_body.get("results")[0].get("outputText")

    except botocore.exceptions.ClientError as error:
        if error.response['Error']['Code'] == 'AccessDeniedException':
            print(f"\x1b[41m{error.response['Error']['Message']}\
                \nTo troubeshoot this issue please refer to the following resources.\
                \nhttps://docs.aws.amazon.com/IAM/latest/UserGuide/troubleshoot_access-denied.html\
                \nhttps://docs.aws.amazon.com/bedrock/latest/userguide/security-iam.html\x1b[0m\n")
        else:
            raise error
        return None

# Usage example
prompt_data = """Command: Write me a blog about making strong business decisions as a leader.

Blog:
"""

response_text = invoke_bedrock_model(bedrock_runtime, prompt_data)
if response_text:
    print(response_text)
