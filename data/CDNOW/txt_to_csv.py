import re

with open('CDNOW_sample.txt', 'r') as readfile, open('CDNOW_sample.csv', 'w') as writefile:
    for line in readfile:
        # Remove leading and trailing spaces
        line = line.strip()
        # Replace multiple spaces with a single comma
        line = re.sub(r'\s+', ',', line)
        # Write the modified line to the new file
        writefile.write(line + '\n')