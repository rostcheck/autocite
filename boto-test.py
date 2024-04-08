import boto3

bedrock = boto3.client('bedrock')

response = bedrock.list_foundation_models()
print(response)
for model in response['modelSummaries']:
    print(f"{model['modelArn']} {model['modelName']}")



