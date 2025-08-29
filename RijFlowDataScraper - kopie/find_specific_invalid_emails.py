import csv

def find_specific_invalid_emails(csv_file):
    """Find specific invalid email patterns in the CSV file"""
    invalid_emails = []
    
    with open(csv_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        for row_num, row in enumerate(reader, start=2):  # Start at 2 because of header
            email = row.get('Email', '').strip()
            rijschool_naam = row.get('RijschoolNaam', '').strip()
            
            # Check for specific invalid patterns
            if email and email != 'None' and email.strip() != '':
                # Pattern 1: Missing @ symbol
                if '@' not in email:
                    invalid_emails.append({
                        'line': row_num,
                        'rijschool': rijschool_naam,
                        'email': email,
                        'reason': 'Missing @ symbol'
                    })
                
                # Pattern 2: Starts with https:// (URL instead of email)
                elif email.startswith('https://'):
                    invalid_emails.append({
                        'line': row_num,
                        'rijschool': rijschool_naam,
                        'email': email,
                        'reason': 'URL instead of email'
                    })
                
                # Pattern 3: Contains spaces (invalid email format)
                elif ' ' in email:
                    invalid_emails.append({
                        'line': row_num,
                        'rijschool': rijschool_naam,
                        'email': email,
                        'reason': 'Contains spaces'
                    })
                
                # Pattern 4: Missing domain extension
                elif email.count('@') == 1 and '.' not in email.split('@')[1]:
                    invalid_emails.append({
                        'line': row_num,
                        'rijschool': rijschool_naam,
                        'email': email,
                        'reason': 'Missing domain extension'
                    })
    
    return invalid_emails

if __name__ == "__main__":
    csv_file = "clean_leads.csv"
    
    print("Zoeken naar specifieke ongeldige email patronen...")
    invalid_emails = find_specific_invalid_emails(csv_file)
    
    print(f"\nGevonden {len(invalid_emails)} ongeldige email adressen:")
    print("-" * 100)
    
    for item in invalid_emails:
        print(f"Regel {item['line']:4d} | {item['rijschool']:<40} | {item['email']:<30} | {item['reason']}")
    
    print(f"\nTotaal: {len(invalid_emails)} ongeldige emails gevonden")
