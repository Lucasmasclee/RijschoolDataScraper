import csv


def main():
    count = 0
    valid_rows = []
    
    with open('rijscholen_leads.csv', 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            # print(row[2])
            if(row[2] != "None"):
                count += 1
                valid_rows.append(row)
    
    # Write all valid rows at once
    with open('clean_leads.csv', 'w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(valid_rows)

    print(count)


if __name__ == "__main__":
    main()

