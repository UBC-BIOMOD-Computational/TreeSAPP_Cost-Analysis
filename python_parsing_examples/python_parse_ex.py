"""
How to run this file: 
    - ensure you are in the folder /python_parsing_examples when you run this file
Recent as of: Charity May 24, 2025
"""

# IMPORTS ==================================================
'''
instructions: pip install these packages if you wish to use them
'''
import json # required only for: json
import pandas as pd # required only for: csv for pandas
import csv # required only for csv with csv package

# CONSTANTS
text_filename = 'example_text.txt' 

#%% TEXT ==================================================
def read_text():
    global text_filename # this line allows you to access global variables
    f = open(text_filename, 'r', encoding='utf-8')
    text_file = f.read()
    print(text_file)
    f.close() # please close file after use (will be auto-closed when program ends but good practice) 

def write_text_to_existing_file():
    global text_filename # this line allows you to access global variables
    f = open(text_filename, 'a', encoding='utf-8')
    f.write("This text was added to the file via a python script")
    f.write("\nThis text was added to the file via a python script but on a new line")
        # check the `example_text.txt` file after calling this function
    f.close() # please close file after use (will be auto-closed when program ends but good practice)

def write_text_to_new_file():
    new_text_filename = "example_new_text_file.txt"
    f = open(new_text_filename, "x")
    # Note: If the file already exist, an error will be raised.
    f.write("This line was written to a new file via")
    f.write("\nThis line was written on a new line using the \\n character")
    f.close() # please close file after use (will be auto-closed when program ends but good practice)

def read_text_line_by_line():
    global text_filename # this line allows you to access global variables
    f = open(text_filename, 'r', encoding='utf-8')
    for line in f:
        print(line)
    f.close() # please close file after use (will be auto-closed when program ends but good practice)

#%% CSV ==================================================

def read_csv_pandas():
    csv_filename = 'example_csv.csv'
    df = pd.read_csv(csv_filename)
    for i, row in df.iterrows():
        print(f"\n - Row {i}: ", row)

def write_csv_pandas():
    data = {
        "calories": [420, 380, 390],
        "duration": [50, 40, 45]
    }

    #load data into a DataFrame object:
    df = pd.DataFrame(data)
    df.to_csv("example_pandas_write.csv")

def read_csv_package_csv():
    f = open('example_csv.csv', mode ='r')
    csv_file = csv.reader(f)
    # next(csv_file) # uncomment this line to skip header
    for row in csv_file:
        print(row)

def write_csv_package_csv():
    data = [
        ['Nikhil', 'COE', 2, '9.0'],
        ['Sanchit', 'COE', 2, '9.1'],
        ['Aditya', 'IT', 2, '9.3'],
        ['Sagar', 'SE', 1, '9.5'],
        ['Prateek', 'MCE', 3, '7.8'],
        ['Sahil', 'EP', 2, '9.1']
    ]

    f = open('example_csv_package_write.csv', 'w', newline='')
    writer = csv.writer(f, delimiter=',')
    writer.writerows(data)
    f.close()

    
#%% JSON ==================================================

def read_json():
    json_filename = 'example_json.json' 
    f = open(json_filename, 'r', encoding='utf-8')
    json_object = json.load(f)
    print(json_object)
    f.close() # please close file after use (will be auto-closed when program ends but good practice)

def write_json():
    json_object = {"hello": "world", "name": "charity :)"}

    json_output_filename = 'example_json_output.json'
    f = open(json_output_filename, 'w', encoding='utf-8')
    json.dump(json_object, f, indent=2)
    f.close()  # please close file after use (will be auto-closed when program ends but good practice)