import csv



def main():
    count = 0
    with open('rijscholen_leads.csv', 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            # print(row[2])
            one = row
            two = next(reader)
            if(two[0] == "None"):
                continue
            if((one[0] == two[0] and one[0] != "None") or (one[1] == two[1] and one[1] != "None") or (one[2] == two[2] and one[2] != "None") or (one[3] == two[3] and one[3] != "None")):
                print(one)
                print(two)

    # print(count)



if __name__ == "__main__":
    main()

