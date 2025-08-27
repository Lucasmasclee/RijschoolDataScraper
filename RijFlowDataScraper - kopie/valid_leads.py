import csv



def main():
    count = 0
    with open('rijscholen_leads.csv', 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            print(row[2])
            if(row[2] != "None"):
                count += 1

    print(count)



if __name__ == "__main__":
    main()

