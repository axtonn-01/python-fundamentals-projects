print(" WELCOME TO THE DREAM CAREER TRACKER \n! ")

name = input("Enter your name: ")
age = int(input("Enter your age: "))

career_goal = []
print("\n Enter 3  of your top career goals: ")
      
for i in range (1,4):
    carrer = input (f"Dream carrer goal {i}: ")
    career_goal.append(carrer)

dream_careers = tuple(career_goal)

user_profile = {
    "user_name": name,
    "user_age": age,
    "tracked_goals": dream_careers
}

print("\n" + "="*35)
print(" USER GOAL PROFILE SUMMARY ")
print("="*35)
print(f"Profile owner: {user_profile['user_name']}")
print(f"current age : {user_profile['user_age']} years old")
print("n\Locked-In Career Targets ")

for index, job in enumerate(user_profile['tracked_goals'], 1):
    print(f"   {index}. {job}")

print("="*35)