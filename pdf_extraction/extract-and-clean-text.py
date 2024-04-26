# Extract text from a PDF file and call Claude 3 Haiku to clean it up
import os
from io import StringIO
import json
from pdfminer.high_level import extract_text
import argparse
import boto3
import time

parser = argparse.ArgumentParser(description='Extract and clean up text from a paper')
parser.add_argument("file", help="file to process (if a directory, proces all files in it)")
parser.add_argument("--timetest", action='store_true', help="Test the file processing at various token sizes")
args = parser.parse_args()

extracted_text_dir = "extracted-text"
cleaned_text_dir = "cleaned-text"
# If above directories don't exist, create them
if not os.path.exists(extracted_text_dir):
    os.makedirs(extracted_text_dir)
if not os.path.exists(cleaned_text_dir):
    os.makedirs(cleaned_text_dir)

bedrock = None

# read prompt.txt into a variable
with open('prompt2.txt', 'r') as file:
    base_prompt = file.read()


# Return a customized prompt made from the base prompt with the supplied text added
def get_prompt(text):
    return base_prompt + "\n\n" + text


# Claude 3 is multimodal and returns data in a different format using streamed chunks. Parse them and
# an integrated format, assuming response is in text
def read_claude3_response_stream_text(response, show_progress=False):
    cleaned_tokens = []
    ctr = 0
    for event in response["body"]:
        if "chunk" in event:
            chunk = event["chunk"]
            chunk_str = chunk['bytes'].decode('utf-8')
            chunk_data = json.loads(chunk_str)
            if "type" in chunk_data:
                message_type = chunk_data["type"]
                # if message_type == "message_start":
                #    print("Message started")
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


def extract_text_from_pdf(file_path):
    # If the file is a PDF, extract the text
    if file_path.endswith(".pdf"):
        this_filename = os.path.split(file_path)[-1]
        outfile = this_filename.replace(".pdf", ".txt")
        outfile_path = os.path.join(extracted_text_dir, outfile)
        if os.path.exists(outfile_path):
            with open(outfile_path, 'r') as file_out:
                text = file_out.read()
                return text
        else:
            text = extract_text(file_path)
            # write text to outfile
            with open(outfile_path, 'w') as file_out:
                file_out.write(text)
                return text
    else:
        return None


def call_claude3(prompt, max_tokens, show_progress=False):
    # call Amazon Bedrock's Claude 3 Haiku to clean up the text
    global bedrock
    if not bedrock:
        bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
    body = json.dumps({
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": f"{prompt}"}],
        "anthropic_version": "bedrock-2023-05-31"
    })

    model_id = "anthropic.claude-3-haiku-20240307-v1:0"
    # model_id = "anthropic.claude-3-sonnet-20240229-v1:0"
    response = bedrock.invoke_model_with_response_stream(body=body, modelId=model_id)
    return read_claude3_response_stream_text(response, show_progress=show_progress)


def extract_and_clean(file_path):
    text = extract_text_from_pdf(file_path)
    if text:
        current_filename = os.path.split(file_path)[-1]
        print("Cleaning " + current_filename)
        cleaned_file = current_filename.replace(".pdf", "-cleaned.txt")
        cleaned_file_path = os.path.join(os.path.dirname(cleaned_text_dir), cleaned_file)

        prompt = get_prompt(text)
        output_text = call_claude3(prompt, 1024, show_progress=True)
        with open(cleaned_file_path, 'w') as file_out:
            file_out.write(output_text)


def run_timetest(file_path):
    # Add the date and time to the filename
    current_time = time.strftime("%Y%m%d-%H%M%S")
    time_test_dir = "time-tests-" + current_time
    token_count = []
    processing_time = []

    if not os.path.exists(time_test_dir):
        os.makedirs(time_test_dir)
    print("Testing file processing at various token sizes")
    test_token_lengths = [240, 500, 1000, 2000, 4000, 8000, 16000, 32000]
    prompt = get_prompt(extract_text_from_pdf(file_path))
    words = prompt.split(' ')
    for token_length in test_token_lengths:
        word_length = int(token_length * .75)
        test_prompt = " ".join(words[1:word_length])
        test_prompt_path = os.path.join(time_test_dir, f"prompt-{token_length}.txt")
        with open(test_prompt_path, 'w') as file_out:
            file_out.write(test_prompt)
        start = time.time()
        output_text = call_claude3(test_prompt, token_length, show_progress=False)
        end = time.time()
        elapsed_time = end - start
        token_count.append(token_length)
        processing_time.append(elapsed_time)
        result_path = os.path.join(time_test_dir, f"result-{token_length}.txt")
        with open(result_path, 'w') as file_out:
            file_out.write(output_text)
        print(f"{token_length} tokens took {elapsed_time} seconds")
    # Write a CSV file with the token count and processing time
    csv_path = os.path.join(time_test_dir, "results.csv")
    with open(csv_path, 'w') as csv_file:
        csv_file.write("Token Count,Processing Time\n")
        for i in range(len(token_count)):
            csv_file.write(f"{token_count[i]},{processing_time[i]}\n")


# Check if file is a directory
if os.path.isdir(args.file):
    # If it is, iterate over all files in the directory
    for filename in os.listdir(args.file):
        if filename.endswith(".pdf"):
            # If the file is a PDF, extract the text
            extract_and_clean(filename)
else:
    if args.timetest:
        run_timetest(args.file)
    else:
        output_string = StringIO()
        with open(args.file, 'rb') as fin:
            extract_and_clean(args.file)
