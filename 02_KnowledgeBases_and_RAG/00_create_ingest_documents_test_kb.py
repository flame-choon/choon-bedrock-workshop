import json
import os
import time

import boto3
from botocore.exceptions import ClientError
import pprint
from utility import create_bedrock_execution_role, create_oss_policy_attach_bedrock_execution_role, create_policies_in_oss, interactive_sleep
import random
from retrying import retry



suffix = random.randrange(200, 900)

session = boto3.Session(profile_name='choon')
region_name = session.region_name
sts_client = session.client('sts')
bedrock_assume_role = sts_client.assume_role(
    RoleArn="arn:aws:iam::975049940746:role/starbucks-bedrock-assume-role",
    RoleSessionName="bedrock-session"
)

bedrock_agent_client = boto3.client('bedrock-agent', 
                                    region_name=region_name,
                                    aws_access_key_id=bedrock_assume_role['Credentials']['AccessKeyId'],
                                    aws_secret_access_key=bedrock_assume_role['Credentials']['SecretAccessKey'],
                                    aws_session_token=bedrock_assume_role['Credentials']['SessionToken']
                                    )
service = 'aoss'
s3_client = boto3.client('s3',
                         region_name=region_name,
                         aws_access_key_id=bedrock_assume_role['Credentials']['AccessKeyId'],
                         aws_secret_access_key=bedrock_assume_role['Credentials']['SecretAccessKey'],
                         aws_session_token=bedrock_assume_role['Credentials']['SessionToken'])

account_id = sts_client.get_caller_identity()["Account"]
s3_suffix = f"{region_name}-{account_id}"
bucket_name = f'bedrock-kb-{s3_suffix}' # replace it with your bucket name.
pp = pprint.PrettyPrinter(indent=2)

# Check if bucket exists, and if not create S3 bucket for knowledge base data source
try:
    s3_client.head_bucket(Bucket=bucket_name)
    print(f'Bucket {bucket_name} Exists')
except ClientError as e:
    print(f'Creating bucket {bucket_name}')
    if region_name == "us-east-1":
        s3bucket = s3_client.create_bucket(
            Bucket=bucket_name)
    else:
        s3bucket = s3_client.create_bucket(
        Bucket=bucket_name,
        CreateBucketConfiguration={ 'LocationConstraint': region_name }
    )

# ###        
# ### Create a vector store - OpenSearch Serverless index
# ###
# ## Step 1 - Create OSS policies and collection
# vector_store_name = f"bedrock-sample-rag-{suffix}"
# index_name = f"bedrock-sample-rag-index-{suffix}"
# aoss_client = boto3.client('opensearchserverless',
#                             region_name=region_name,
#                             aws_access_key_id=bedrock_assume_role['Credentials']['AccessKeyId'],
#                             aws_secret_access_key=bedrock_assume_role['Credentials']['SecretAccessKey'],
#                             aws_session_token=bedrock_assume_role['Credentials']['SessionToken'])
# bedrock_kb_execution_role = create_bedrock_execution_role(bucket_name=bucket_name)
# bedrock_kb_execution_role_arn = bedrock_kb_execution_role["Role"]["Arn"]

# print(bedrock_kb_execution_role_arn)

# # create security, network and data access policies within OSS
# encryption_policy, network_policy, access_policy = create_policies_in_oss(vector_store_name=vector_store_name,
#                        aoss_client=aoss_client,
#                        bedrock_kb_execution_role_arn=bedrock_kb_execution_role_arn)
# print(encryption_policy)
# print(network_policy)
# print(access_policy)
# collection = aoss_client.create_collection(name=vector_store_name,type='VECTORSEARCH')
# pp.pprint(collection)
# print(f'Created collection {vector_store_name}')


# # Get the OpenSearch serverless collection URL
# collection_id = collection['createCollectionDetail']['id']
# host = collection_id + '.' + region_name + '.aoss.amazonaws.com'
# print(host)

# # wait for collection creation
# # This can take couple of minutes to finish
# response = aoss_client.batch_get_collection(names=[vector_store_name])
# # Periodically check collection status
# while (response['collectionDetails'][0]['status']) == 'CREATING':
#     print('Creating collection...')
#     interactive_sleep(30)
#     response = aoss_client.batch_get_collection(names=[vector_store_name])
# print('\nCollection successfully created:')
# pp.pprint(response["collectionDetails"])

# # create opensearch serverless access policy and attach it to Bedrock execution role
# try:
#     create_oss_policy_attach_bedrock_execution_role(collection_id=collection_id,
#                                                     bedrock_kb_execution_role=bedrock_kb_execution_role)
#     # It can take up to a minute for data access rules to be enforced
#     interactive_sleep(60)
# except Exception as e:
#     print("Policy already exists")
#     pp.pprint(e)


# ## Step 2 - Create vector index
# suffix = 592
# host = '7xmawqncch3tab02ugu7.us-east-1.aoss.amazonaws.com'

# from opensearchpy import OpenSearch, RequestsHttpConnection, AWSV4SignerAuth, RequestError
# credentials = boto3.Session(
#     aws_access_key_id=bedrock_assume_role['Credentials']['AccessKeyId'],
#     aws_secret_access_key=bedrock_assume_role['Credentials']['SecretAccessKey'],
#     aws_session_token=bedrock_assume_role['Credentials']['SessionToken']
# ).get_credentials()

# awsauth = auth = AWSV4SignerAuth(credentials, region_name, service)

# index_name = f"bedrock-sample-index-{suffix}"
# body_json = {
#    "settings": {
#       "index.knn": "true",
#        "number_of_shards": 1,
#        "knn.algo_param.ef_search": 512,
#        "number_of_replicas": 0,
#    },
#    "mappings": {
#       "properties": {
#          "vector": {
#             "type": "knn_vector",
#             "dimension": 1536,
#              "method": {
#                  "name": "hnsw",
#                  "engine": "faiss",
#                  "space_type": "l2"
#              },
#          },
#          "text": {
#             "type": "text"
#          },
#          "text-metadata": {
#             "type": "text"         
#         }
#       }
#    }
# }

# # Build the OpenSearch client
# oss_client = OpenSearch(
#     hosts=[{'host': host, 'port': 443}],
#     http_auth=awsauth,
#     use_ssl=True,
#     verify_certs=True,
#     connection_class=RequestsHttpConnection,
#     timeout=300
# )

# # Create index
# try:
#     response = oss_client.indices.create(index=index_name, body=json.dumps(body_json))
#     print('\nCreating index:')
#     pp.pprint(response)

#     # index creation can take up to a minute
#     interactive_sleep(60)
# except RequestError as e:
#     # you can delete the index if its already exists
#     # oss_client.indices.delete(index=index_name)
#     print(f'Error while trying to create the index, with error {e.error}\nyou may unmark the delete above to delete, and recreate the index')


# ###
# ### Create a vector store - OpenSearch Serverless index
# ###

# suffix = 592
# index_name = f"bedrock-sample-index-{suffix}"
# collectionArn = "arn:aws:aoss:us-east-1:975049940746:collection/7xmawqncch3tab02ugu7"

# opensearchServerlessConfiguration = {
#             "collectionArn": collectionArn,
#             "vectorIndexName": index_name,
#             "fieldMapping": {
#                 "vectorField": "vector",
#                 "textField": "text",
#                 "metadataField": "text-metadata"
#             }
#         }

# # Ingest strategy - How to ingest data from the data source
# chunkingStrategyConfiguration = {
#     "chunkingStrategy": "FIXED_SIZE",
#     "fixedSizeChunkingConfiguration": {
#         "maxTokens": 512,
#         "overlapPercentage": 20
#     }
# }

# # The data source to ingest documents from, into the OpenSearch serverless knowledge base index
# s3Configuration = {
#     "bucketArn": f"arn:aws:s3:::{bucket_name}",
#     # "inclusionPrefixes":["*.*"] # you can use this if you want to create a KB using data within s3 prefixes.
# }

# # The embedding model used by Bedrock to embed ingested documents, and realtime prompts
# embeddingModelArn = f"arn:aws:bedrock:{region_name}::foundation-model/amazon.titan-embed-text-v1"

# name = f"bedrock-sample-knowledge-base-{suffix}"
# description = "Amazon shareholder letter knowledge base."
# roleArn = "arn:aws:iam::975049940746:role/AmazonBedrockExecutionRoleForKnowledgeBase_808"

# # Create a KnowledgeBase
# from retrying import retry

# @retry(wait_random_min=1000, wait_random_max=2000,stop_max_attempt_number=7)
# def create_knowledge_base_func():
#     create_kb_response = bedrock_agent_client.create_knowledge_base(
#         name = name,
#         description = description,
#         roleArn = roleArn,
#         knowledgeBaseConfiguration = {
#             "type": "VECTOR",
#             "vectorKnowledgeBaseConfiguration": {
#                 "embeddingModelArn": embeddingModelArn
#             }
#         },
#         storageConfiguration = {
#             "type": "OPENSEARCH_SERVERLESS",
#             "opensearchServerlessConfiguration":opensearchServerlessConfiguration
#         }
#     )
#     return create_kb_response["knowledgeBase"]

# try:
#     kb = create_knowledge_base_func()
# except Exception as err:
#     print(f"{err=}, {type(err)=}")

# pp.pprint(kb)

# # Get KnowledgeBase 
# get_kb_response = bedrock_agent_client.get_knowledge_base(knowledgeBaseId = kb['knowledgeBaseId'])
# print(f"Get KnowledgeBase response: {get_kb_response}")

# # Create a DataSource in KnowledgeBase 
# create_ds_response = bedrock_agent_client.create_data_source(
#     name = name,
#     description = description,
#     knowledgeBaseId = kb['knowledgeBaseId'],
#     dataSourceConfiguration = {
#         "type": "S3",
#         "s3Configuration":s3Configuration
#     },
#     vectorIngestionConfiguration = {
#         "chunkingConfiguration": chunkingStrategyConfiguration
#     }
# )
# ds = create_ds_response["dataSource"]
# pp.pprint(ds)

# # Get DataSource 
# bedrock_agent_client.get_data_source(knowledgeBaseId = kb['knowledgeBaseId'], dataSourceId = ds["dataSourceId"])

# # Start an ingestion job
# interactive_sleep(30)
# start_job_response = bedrock_agent_client.start_ingestion_job(knowledgeBaseId = kb['knowledgeBaseId'], dataSourceId = ds["dataSourceId"])

# job = start_job_response["ingestionJob"]
# pp.pprint(job)

# # Get job 
# while(job['status']!='COMPLETE' ):
#     get_job_response = bedrock_agent_client.get_ingestion_job(
#       knowledgeBaseId = kb['knowledgeBaseId'],
#         dataSourceId = ds["dataSourceId"],
#         ingestionJobId = job["ingestionJobId"]
#   )
#     job = get_job_response["ingestionJob"]
    
#     interactive_sleep(30)

# pp.pprint(job)

# # Print the knowledge base Id in bedrock, that corresponds to the Opensearch index in the collection we created before, we will use it for the invocation later
# kb_id = kb["knowledgeBaseId"]
# pp.pprint(kb_id)



###
### Test the knowledge base
###

kb_id = "2DQTFBFRN1"

bedrock_agent_runtime_client = boto3.client("bedrock-agent-runtime", 
                                            region_name=region_name,
                                            aws_access_key_id=bedrock_assume_role['Credentials']['AccessKeyId'],
                                            aws_secret_access_key=bedrock_assume_role['Credentials']['SecretAccessKey'],
                                            aws_session_token=bedrock_assume_role['Credentials']['SessionToken']
                                            )
# Lets see how different Anthropic Claude 3 models responds to the input text we provide
claude_model_ids = [ ["Claude 3 Sonnet", "anthropic.claude-3-sonnet-20240229-v1:0"], ["Claude 3 Haiku", "anthropic.claude-3-haiku-20240307-v1:0"]]

query = "What is Amazon's doing in the field of generative AI?"

## Using RetrieveAndGenerate API

# def ask_bedrock_llm_with_knowledge_base(query: str, model_arn: str, kb_id: str) -> str:
#     response = bedrock_agent_runtime_client.retrieve_and_generate(
#         input={
#             'text': query
#         },
#         retrieveAndGenerateConfiguration={
#             'type': 'KNOWLEDGE_BASE',
#             'knowledgeBaseConfiguration': {
#                 'knowledgeBaseId': kb_id,
#                 'modelArn': model_arn
#             }
#         },
#     )

#     return response

# for model_id in claude_model_ids:
#     model_arn = f'arn:aws:bedrock:{region_name}::foundation-model/{model_id[1]}'
#     response = ask_bedrock_llm_with_knowledge_base(query, model_arn, kb_id)
#     generated_text = response['output']['text']
#     citations = response["citations"]
#     contexts = []
#     for citation in citations:
#         retrievedReferences = citation["retrievedReferences"]
#         for reference in retrievedReferences:
#             contexts.append(reference["content"]["text"])
#     print(f"---------- Generated using {model_id[0]}:")
#     pp.pprint(generated_text )
#     print(f'---------- The citations for the response generated by {model_id[0]}:')
#     pp.pprint(contexts)
#     print()

## Using Retrieve API
# retrieve api for fetching only the relevant context.
relevant_documents = bedrock_agent_runtime_client.retrieve(
    retrievalQuery= {
        'text': query
    },
    knowledgeBaseId=kb_id,
    retrievalConfiguration= {
        'vectorSearchConfiguration': {
            'numberOfResults': 3 # will fetch top 3 documents which matches closely with the query.
        }
    }
)

pp.pprint(relevant_documents["retrievalResults"])