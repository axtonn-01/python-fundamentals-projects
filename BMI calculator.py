weight = float(input("Enter your weight in kilograms: "))
height = float(input("Enter your height in meters: "))

def calculate_bmi(weight, height):
    bmi = weight / (height ** 2)
    return bmi

bmi = calculate_bmi(weight, height)
if bmi < 18.5:
    print(f"Your BMI is {bmi:.2f}. You are underweight.")
elif 18.5 <= bmi < 24.9:
    print(f"Your BMI is {bmi:.2f}. You have a normal weight.")
elif 25 <= bmi < 29.9:
    print(f"Your BMI is {bmi:.2f}. You are overweight.")
else:
    print(f"Your BMI is {bmi:.2f}. You are obese.")
    