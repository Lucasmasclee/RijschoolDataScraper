import csv
import re

with open('clean_leads.csv', 'r', encoding='utf-8') as file:
    reader = csv.reader(file)
    for row in reader:
        if(row[2] != "None" and "@" not in row[2]):
            print(row)
        
        # emails are invalid if they don't contain @, or if they contain a space
        if(" " in row[2]):
            print(row)

        filteredemail = re.sub(r'[a-zA-Z0-9@.-]', '', row[2])
        if(filteredemail != ""):
            print(row)







