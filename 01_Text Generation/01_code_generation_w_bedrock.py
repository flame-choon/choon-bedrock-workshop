import json
import sys
import os
import csv

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

data = [
    ["date", "product_id", "price", "units_sold"],
    ["2023-01-01", "P001", 50, 20],
    ["2023-01-02", "P002", 60, 15],
    ["2023-01-03", "P001", 50, 18],
    ["2023-01-04", "P003", 70, 30],
    ["2023-01-05", "P001", 50, 25],
    ["2023-01-06", "P002", 60, 22],
    ["2023-01-07", "P003", 70, 24],
    ["2023-01-08", "P001", 50, 28],
    ["2023-01-09", "P002", 60, 17],
    ["2023-01-10", "P003", 70, 29],
    ["2023-02-11", "P001", 50, 23],
    ["2023-02-12", "P002", 60, 19],
    ["2023-02-13", "P001", 50, 21],
    ["2023-02-14", "P003", 70, 31],
    ["2023-03-15", "P001", 50, 26],
    ["2023-03-16", "P002", 60, 20],
    ["2023-03-17", "P003", 70, 33],
    ["2023-04-18", "P001", 50, 27],
    ["2023-04-19", "P002", 60, 18],
    ["2023-04-20", "P003", 70, 32],
    ["2023-04-21", "P001", 50, 22],
    ["2023-04-22", "P002", 60, 16],
    ["2023-04-23", "P003", 70, 34],
    ["2023-05-24", "P001", 50, 24],
    ["2023-05-25", "P002", 60, 21]
]

# Write data to sales.csv
with open('sales.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerows(data)

print("sales.csv has been created!")

# Create the prompt
# Analyzing sales

prompt_data = """
You have a CSV, sales.csv, with columns:
- date (YYYY-MM-DD)
- product_id
- price
- units_sold

Create a python program to analyze the sales data from a CSV file. The program should be able to read the data, and determine below:

- Total revenue for the year
- The product with the highest revenue
- The date with the highest revenue
- Visualize monthly sales using a bar chart

Ensure the code is syntactically correct, bug-free, optimized, not span multiple lines unnessarily, and prefer to use standard libraries. Return only python code without any surrounding text, explanation or context.
Do not use pandas library for the solution.
"""

body = json.dumps({
    "anthropic_version": "bedrock-2023-05-31",
    "max_tokens": 4096,
    "temperature": 0.1,
    "top_k":250,
    "top_p":0.99,
    "messages": [
        {
            "role": "user",
            "content": [{"type": "text", "text": prompt_data}]
        }
    ],
})

from IPython.display import clear_output, display, display_markdown, Markdown
modelId = "anthropic.claude-3-sonnet-20240229-v1:0"
accept = 'application/json'
contentType = 'application/json'

response = bedrock_runtime.invoke_model(body=body, modelId=modelId, accept=accept, contentType=contentType)
response_body = json.loads(response.get('body').read())

display_markdown(Markdown(print(response_body["content"][0]["text"], end='')))