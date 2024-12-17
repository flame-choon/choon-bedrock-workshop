import json
import os
import sys

import boto3
import botocore

# Set up the session
session = boto3.Session(profile_name='choon')
sts_client = session.client('sts')
bedrock_assume_role = sts_client.assume_role(
    RoleArn="arn:aws:iam::975049940746:role/starbucks-bedrock-assume-role",
    RoleSessionName="bedrock-session"
)

# Create the Bedrock client
bedrock_runtime = boto3.client('bedrock-runtime',
    region_name='us-east-1',
    aws_access_key_id=bedrock_assume_role['Credentials']['AccessKeyId'],
    aws_secret_access_key=bedrock_assume_role['Credentials']['SecretAccessKey'],
    aws_session_token=bedrock_assume_role['Credentials']['SessionToken']
)

# create the prompt
prompt_data = """
Command: Write an email from Bob, Customer Service Manager, to the customer "John Doe" 
who provided negative feedback on the service provided by our customer support 
engineer"""

body = json.dumps(
    {
        "inputText": prompt_data,
        "textGenerationConfig": {"maxTokenCount": 1024, "topP": 0.95, "temperature": 0.1},
    }
)


# modelId = 'amazon.titan-text-premier-v1:0' # Make sure Titan text premier is available in the account you are doing this workhsop in before uncommenting!
modelId = "amazon.titan-text-express-v1"  # "amazon.titan-tg1-large"
accept = "application/json"
contentType = "application/json"
outputText = "\n"

# Bedrock의 invoke_model API를 이용하여 결과 호출
# try:

#     response = bedrock_runtime.invoke_model(
#         body=body, modelId=modelId, accept=accept, contentType=contentType
#     )
#     response_body = json.loads(response.get("body").read())

#     outputText = response_body.get("results")[0].get("outputText")

# except botocore.exceptions.ClientError as error:

#     if error.response["Error"]["Code"] == "AccessDeniedException":
#         print(
#             f"\x1b[41m{error.response['Error']['Message']}\
#                 \nTo troubeshoot this issue please refer to the following resources.\
#                  \nhttps://docs.aws.amazon.com/IAM/latest/UserGuide/troubleshoot_access-denied.html\
#                  \nhttps://docs.aws.amazon.com/bedrock/latest/userguide/security-iam.html\x1b[0m\n"
#         )

#     else:
#         raise error
    
# email = outputText[outputText.index("\n") + 1:]
# print(email)

# Bedrock의 invoke_model_with_response_stream API를 이용하여 결과 호출
output = []
try:
    response = bedrock_runtime.invoke_model_with_response_stream(
        body=body, modelId=modelId, accept=accept, contentType=contentType
    )
    stream = response.get("body")

    i = 1
    if stream:
        for event in stream:
            chunk = event.get("chunk")
            if chunk:
                chunk_obj = json.loads(chunk.get("bytes").decode())
                text = chunk_obj["outputText"]
                output.append(text)
                print(f"\t\t\x1b[31m**Chunk {i}**\x1b[0m\n{text}\n")
                i += 1

except botocore.exceptions.ClientError as error:

    if error.response["Error"]["Code"] == "AccessDeniedException":
        print(
            f"\x1b[41m{error.response['Error']['Message']}\
                \nTo troubeshoot this issue please refer to the following resources.\
                 \nhttps://docs.aws.amazon.com/IAM/latest/UserGuide/troubleshoot_access-denied.html\
                 \nhttps://docs.aws.amazon.com/bedrock/latest/userguide/security-iam.html\x1b[0m\n"
        )

    else:
        raise error