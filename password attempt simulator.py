correct_password = "axtonn01"
attempts_left = 3

while attempts_left > 0:
    user_input = input("Enter the password: ")
    
    if user_input == correct_password:
        print("Access granted!")
        break
    else:
        attempts_left -= 1
        print(f"Incorrect password. Attempts left: {attempts_left}")

        if attempts_left == 0:
            print("Access denied. No attempts left.")