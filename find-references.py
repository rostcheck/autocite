import argparse
import re

parser = argparse.ArgumentParser(description='Extract all references from the provided text file')
parser.add_argument("file", help="file to parse")
args = parser.parse_args()

sentences = []
with open(args.file) as f:
    file_text = f.read()
    sentences = re.split(r'[.!?]+', file_text)
    # Identify if sentence contains now identify if a sentence contains a reference, which are integers in format "[12]" or list of integers of integers in format "[34, 23, 17]"
    #sentences = re.findall(r'[^.!?]+\[[0-9]+\]', file_text)
for sentence in sentences:
    #if re.match(r'[^.!?]+\[[0-9]+\]', sentence, re.M):
    #    print(sentence)
    print(f"> {sentence}")