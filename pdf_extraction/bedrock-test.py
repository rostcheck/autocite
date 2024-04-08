import boto3
import json


# Return a customized prompt made from the base prompt with the supplied text added
def get_prompt(text):
    return base_prompt + "\n\n" + text


# Claude 3 is multimodal and returns data in a different format using streamed chunks. Parse them and
# an integrated format, assuming response is in text
def read_claude3_response_stream_text(response, show_progress = False):
    cleaned_tokens = []
    ctr = 0
    for event in response["body"]:
        if "chunk" in event:
            chunk = event["chunk"]
            chunk_str = chunk['bytes'].decode('utf-8')
            chunk_data = json.loads(chunk_str)
            if "type" in chunk_data:
                message_type = chunk_data["type"]
                if message_type == "message_start":
                    print("Message started")
                if message_type == "content_block_delta":
                    if show_progress:
                        if ctr != 0 and ctr % 120 == 0:
                            print('.')
                            ctr = 0
                        else:
                            print(".", end="")
                            ctr = ctr + 1
                    cleaned_tokens.append(chunk_data["delta"]["text"])
                if "message_stop" in chunk_data:
                    print("Message complete")
    if show_progress:
        print("\n")
    return "".join(cleaned_tokens)


# read prompt.txt into a variable
with open('prompt.txt', 'r') as file:
    base_prompt = file.read()

# read test text into a variable
with open('test.txt', 'r') as file:
    text = file.read()

prompt = get_prompt(text)

# call Amazon Bedrock's Claude 3 Haiku to clean up the text
bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
body = json.dumps({
    "max_tokens": 1024,
    "messages": [{"role": "user", "content": f"{prompt}"}],
    "anthropic_version": "bedrock-2023-05-31"
})

model_id = "anthropic.claude-3-haiku-20240307-v1:0"
# model_id = "anthropic.claude-3-sonnet-20240229-v1:0"
response = bedrock.invoke_model_with_response_stream(body=body, modelId=model_id)
output_text = read_claude3_response_stream_text(response,  show_progress=True)
print(output_text)
# response_body = json.loads(response.get("body").read())
