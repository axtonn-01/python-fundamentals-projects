student_marks = []

print("---WELCOME TO THE STUDENT MARKS MANAGER---")
print("Enter the marks of students (type 'done' when finished):")
while True:
    user_input = input("Enter marks or type 'done' to finish: ")
    if user_input.lower() == 'done':
        break
    marks = float(user_input)
    student_marks.append(marks)

if len(student_marks) > 0:
    total_marks = sum(student_marks)
    number_of_subjects = len(student_marks)
    average_marks = total_marks / number_of_subjects

    print("\n--- FINAL REPORT CARD ---")
    print(f"Total Marks:        {total_marks}")
    print(f"Number of Subjects: {number_of_subjects}")  
    print(f"Average Marks:      {average_marks}")