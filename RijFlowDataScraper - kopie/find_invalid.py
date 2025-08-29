import csv

names = []
phones = []
emails = []
websites = []

def main():
    count = 0
    rows_to_keep = []
    with open('rijscholen_leads.csv', 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            duplicate = False
            if(row[0] in names):
                print(row)
                duplicate = True
            if(row[1] in phones):
                print(row)
                duplicate = True
            if(row[2] in emails):
                print(row)
                duplicate = True
            if(row[3] in websites):
                print(row)
                duplicate = True
            
            if not duplicate:
                rows_to_keep.append(row)
                if(row[0] != "None"):
                    names.append(row[0])
                if(row[1] != "None"):
                    phones.append(row[1])
                if(row[2] != "None"):
                    emails.append(row[2])
                if(row[3] != "None"):
                    websites.append(row[3])

    # Write back the non-duplicate rows
    with open('rijscholen_leads.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(rows_to_keep)
            # if(two[0] == "None"):
            #     continue
            # if((one[0] == two[0] and one[0] != "None") or (one[1] == two[1] and one[1] != "None") or (one[2] == two[2] and one[2] != "None") or (one[3] == two[3] and one[3] != "None")):
            #     print(one)
            #     print(two)
            # if(row[2] != "None" and "@" not in row[2]):
            #     print(row)
            


    # print(count)



if __name__ == "__main__":
    main()

