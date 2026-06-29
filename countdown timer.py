import time 

seconds = int(input("Enter the number of seconds for the countdown timer: "))

while seconds > 0:
    print(f"Time remaining: {seconds} seconds")
    time.sleep(1)
    seconds -= 1

    
