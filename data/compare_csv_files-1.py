import csv

# Function to read CSV files and skip the first column
def read_csv(file_path):
    with open(file_path, mode='r') as file:
        reader = csv.reader(file)
        data = [row for row in reader] 
    return data

# Function to compare two CSV files and print the differing lines
def compare_csv_files(file1, file2):
    data1 = read_csv(file1)
    data2 = read_csv(file2)

    # Initialize flags to check if there's any difference
    differences_found = False

    # Iterate over the rows and compare them
    for i, (row1, row2) in enumerate(zip(data1, data2)):
        if row1 != row2:
            differences_found = True
            print(f"Line {i + 1} is different:")
            print(f"File 1: {row1}")
            print(f"File 2: {row2}")
            print()

    if not differences_found:
        print("The data in both CSV files are identical.")

# Replace these paths with the actual file paths
file1 = 'x_python.csv'
file2 = 'x.csv'

# Compare the files
compare_csv_files(file1, file2)