import re
# Cleanup file so that it contains 1 instead of 2 lists
with open('articles_temp.json', 'r') as infile, open('articles.json', 'w') as outfile:
    temp = re.sub("\n\]\[", ",", infile.read())
    outfile.write(temp)