# Read a file line by line, applying a regular expression to each line.
import re
import argparse

parser = argparse.ArgumentParser(description='Remove references from a paper')
parser.add_argument("file", help="file to parse")
args = parser.parse_args()

pattern = r' \[\d+(?:, *\d+)*\]'
outfile = args.file.replace(".txt", "_dereferenced.txt")
with open(args.file, "r") as infile:
    with open(outfile, "w") as outfile:
        for line in infile:
            # Apply a regular expression to transform the line
            newline = re.sub(pattern, "", line)
            outfile.write(newline)
            #print(newline)