print("READING RECENT LOG DATA...\n")
with open("notes.txt", "r") as file:
    line_number = 1
    for line in file:
        clean_line = line.strip()
        print(f"Row {line_number}: {clean_line}")
        line_number += 1

print("\n🏁 All data successfully loaded from disk!")