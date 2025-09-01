import csv

def main():
    emailcount = 0
    invalidemailcount = 0
    validemailcount = 0
    count1 = 0
    count2 = 0
    count3 = 0
    count4 = 0
    count5 = 0
    count6 = 0
    validemailcount2 = 0
    donotmailemailcount = 0
    list_1 = [] # invalid emails
    list_2 = [] # donotmail emails
    list_3 = []
    list_4 = []
    list_5 = []
    list_6 = []
    with open('clean_leads_abuse.csv', 'r') as file2:
        reader2 = csv.reader(file2)
        for row in reader2:
            list_1.append(row[2])
    with open('clean_leads_catch_all.csv', 'r') as file3:
        reader3 = csv.reader(file3)
        for row in reader3:
            list_2.append(row[2])
    with open('clean_leads_donotmail.csv', 'r') as file4:
        reader4 = csv.reader(file4)
        for row in reader4:
            list_3.append(row[2])
    with open('clean_leads_invalid.csv', 'r') as file5:
        reader5 = csv.reader(file5)
        for row in reader5:
            # list_1.append(row[2])
            list_4.append(row[2])
    with open('clean_leads_unknown.csv', 'r') as file6:
        reader6 = csv.reader(file6)
        for row in reader6:
            list_5.append(row[2])
        with open('instantly_invalid_leads.csv', 'r') as file3:
            reader3 = csv.reader(file3)
            for row in reader3:
                email = row[1]
                if email in list_1 or email in list_2 or email in list_3 or email in list_4 or email in list_5:
                    # print("invalid email: " + email)
                    invalidemailcount += 1
                else:
                    # print("valid email: " + email)
                    validemailcount += 1
        





            with open('instantly_verified_emails.csv', 'r') as file4:
                reader4 = csv.reader(file4)
                for row in reader4:
                    email = row[1]
                    if email in list_1:
                        # print("invalid email: " + email)
                        count1 += 1
                    elif email in list_2:
                        count2 += 1
                    elif email in list_3:
                        count3 += 1
                    elif email in list_4:
                        count4 += 1
                    elif email in list_5:
                        count5 += 1
                    else:
                        # print("valid email: " + email)
                        count6 += 1
                


    print("total emailcount: " + str(emailcount))
    print("invalidemailcount: " + str(invalidemailcount))
    print("validemailcount: " + str(validemailcount))
    print("count1: " + str(count1))
    print("count2: " + str(count2))
    print("count3: " + str(count3))
    print("count4: " + str(count4))
    print("count5: " + str(count5))
    print("count6: " + str(count6))
    print("validemailcount2: " + str(validemailcount2))
    print("donotmailemailcount: " + str(donotmailemailcount))
# run the script
if __name__ == "__main__":
    main()
