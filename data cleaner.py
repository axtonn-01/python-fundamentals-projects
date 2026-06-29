raw_web_data = [ "23" ,"42" , "corrupted_text_here" , "93" , "44" , "missing_value"]
cleaned_numbers = []

print("STARTING DATA CLEANING PIPELINE....\n")

for item in raw_web_data:
    try:
        clean_number = int(item)
        cleaned_numbers.append(clean_number)
        print(f"success converted '{item}' to a number. ")

    except ValueError:
        print(f"Skipped bad data : found invalid text '{item}' ")


print("\n" + "="*35)
print("CLEANING COMPLETE")
print("="*35)
print(f"Original Data : {raw_web_data}")
print(f"Cleaned Data : {cleaned_numbers}")
print(f"Average value : {sum(cleaned_numbers) / len(cleaned_numbers)}")
print("="*35)