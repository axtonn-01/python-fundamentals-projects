num = (int(input("Enter a number: ")))

def even_odd_checker(num):
    if num % 2 == 0:
        print(f"{num} is an even number.")
    else:
        print(f"{num} is an odd number.")

even_odd_checker(num)