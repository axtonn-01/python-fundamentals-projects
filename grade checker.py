marks = (float(input("Enter your marks: ")))

if marks >= 90:
    print("You got an A grade! Excellent work!")

elif marks <=89 and marks >=75:
    print("You got a B grade! Good job!")   

elif marks <=74 and marks >=50:
    print("You got a C grade! You need to work harder!")

else:
    print("You got an F grade! You need to retake the exam!")