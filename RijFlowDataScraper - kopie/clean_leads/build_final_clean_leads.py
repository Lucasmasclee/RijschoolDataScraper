import csv

def main():
    count_1 = 0
    count_2 = 0
    count_3 = 0
    count_4 = 0
    count_5 = 0
    count_6 = 0
    list_1 = []
    list_2 = []
    list_3 = []
    list_4 = []
    list_5 = []
    list_6 = []
    
        
    with open('contacted_leads.csv', 'r') as file1:
        reader1 = csv.reader(file1)
        for row in reader1:
            email = row[1]
            list_1.append(email)
            count_2 += 1
            


    with open('final_clean_leads.csv', 'r') as file2:
        reader2 = csv.reader(file2)
        with open('new_final_clean_leads.csv', 'w', newline='', encoding='utf-8') as file3:
            writer3 = csv.writer(file3)
            for row in reader2:
                email = row[2]
                list_2.append(email)
                count_1 += 1
                if email not in list_1:
                    count_3 += 1
                    writer3.writerow(row)
    

        

        print(count_1)
        print(count_2)
        print(count_3)


if __name__ == "__main__":
    main()