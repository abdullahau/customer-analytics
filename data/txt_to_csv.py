import re

with open('Donation-Incidence/1995_cohort_binary.txt', 'r', encoding='utf-16') as readfile, open('Donation-Incidence/1995_cohort_binary.csv', 'w') as writefile:
    for line in readfile:
        # Remove leading and trailing spaces
        line = line.strip()
        # Replace multiple spaces with a single comma
        line = re.sub(r'\s+', ',', line)
        # Write the modified line to the new file
        writefile.write(line + '\n')