import os
import csv
import random

# Create directory
output_dir = "dummy_students"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Data pools
first_names_male = [
    "Aarav", "Amit", "Rohan", "Aditya", "Rahul", "Kunal", "Sameer", "Harsh", 
    "Vivek", "Sanjay", "Rajesh", "Arjun", "Sandeep", "Gaurav", "Nitin", "Ajay", 
    "Vijay", "Ankit", "Akash", "Neeraj", "Manish", "Shivam", "Saurabh", "Pankaj", 
    "Rohit", "Sachin", "Deepak", "Karan", "Himanshu", "Tarun", "Abhay", "Ashish"
]
first_names_female = [
    "Maitri", "Neha", "Priya", "Manisha", "Anjali", "Riya", "Divya", "Sakshi", 
    "Deepika", "Pooja", "Sunita", "Sneha", "Shruti", "Preeti", "Kavita", "Jyoti", 
    "Sonia", "Payal", "Komal", "Aarti", "Swati", "Kiran", "Nisha", "Shweta"
]
last_names = [
    "Sharma", "Verma", "Gupta", "Joshi", "Kumar", "Singh", "Bisht", "Purohit", 
    "Goyal", "Mehta", "Rawat", "Negi", "Pandey", "Pant", "Bhatt", "Nautiyal", 
    "Semwal", "Dimri", "Uniyal", "Raturi", "Rana", "Bhandari", "Chaudhary", 
    "Mishra", "Shukla", "Dubey", "Tiwari", "Saxena", "Srivastava", "Kapoor"
]
locations = ["Dehradun", "Haldwani", "Rishikesh", "Haridwar", "Roorkee", "Nainital", "Delhi", "Noida", "Gurugram"]
branches = ["CSE", "ECE", "ME", "Civil"]

print(f"Generating 100 dummy student CSV files in '{output_dir}'...")

used_phones = set()
used_emails = set()

for i in range(1, 101):
    gender = random.choice(["Male", "Female"])
    if gender == "Male":
        first_name = random.choice(first_names_male)
    else:
        first_name = random.choice(first_names_female)
    
    last_name = random.choice(last_names)
    full_name = f"{first_name} {last_name}"
    
    # Generate unique phone and email
    phone = f"98765{random.randint(10000, 99999)}"
    while phone in used_phones:
        phone = f"98765{random.randint(10000, 99999)}"
    used_phones.add(phone)
    
    email_local = f"{first_name.lower()}.{last_name.lower()}{random.randint(10, 99)}"
    email = f"{email_local}@example.com"
    while email in used_emails:
        email_local = f"{first_name.lower()}.{last_name.lower()}{random.randint(10, 99)}"
        email = f"{email_local}@example.com"
    used_emails.add(email)
    
    dob = f"{random.randint(2004, 2007)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}"
    location = random.choice(locations)
    tenth_pct = round(random.uniform(70.0, 98.0), 1)
    twelfth_pct = round(random.uniform(65.0, 96.0), 1)
    preferred_branch = random.choice(branches)
    hostel_required = random.choice(["Yes", "No"])
    
    filename = os.path.join(output_dir, f"student_{i:03d}.csv")
    
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        # Write headers
        writer.writerow([
            "full_name", "dob", "gender", "personal_email", "phone", 
            "location", "tenth_pct", "twelfth_pct", "preferred_branch", "hostel_required"
        ])
        # Write student row
        writer.writerow([
            full_name, dob, gender, email, phone, 
            location, tenth_pct, twelfth_pct, preferred_branch, hostel_required
        ])

print("Dummy CSV generation complete! 100 files created successfully.")
