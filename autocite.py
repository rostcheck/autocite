# set command-line options
import argparse
import boto3
import json

skip_sections = ['Abstract', 'Conclusions']

parser = argparse.ArgumentParser(description='Automatically determine citations needed for a paper')
parser.add_argument("file", help="file to parse")
args = parser.parse_args()

bedrock = boto3.client('bedrock-runtime')

prompt = "Here is a sample prompt for Claude Haiku:"


# read a text file line by line and store its paragraphs in a list
section = ""
with open(args.file, "r") as f:
    paragraphs = f.read().split("\n\n")
    count = 0
    for paragraph in paragraphs:
        # if paragraph contains only one sentence, skip it
        if len(paragraph.split(".")) == 1:
            section = paragraph
            print(f"New section: {section}")
            continue
        else:
            if section in skip_sections:
                print(f"Skipping section: {section}")
                continue
            count += 1
            print(f"evaluating: {paragraph}")
            # Call Amazon Bedrock's Claude Haiku to determine if there are claims in the paragraph that need citations
            #response = bedrock.invoke_model(
            #    ModelArn='arn:aws:bedrock:us-east-1:123456789012:model/anthropic/claude-haiku',
            #    Input={
            #        'text': prompt
            #    }
            #)

            #print(json.dumps(response, indent=4))
    print(f"Found {count} paragraphs")
