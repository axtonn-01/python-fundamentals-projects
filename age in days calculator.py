age = int(input("Enter your age in years: "))

def age_in_days_calculator(age):
    days = age * 365
    return days

days = age_in_days_calculator(age)
print(f"Wow! You are approximately {days} days old.")