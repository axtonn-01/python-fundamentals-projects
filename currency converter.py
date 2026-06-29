dollar = (float(input("Enter the amount in dollars: ")))

def conver_to_inr (dollar):
    inr = dollar * 94.74
    return inr

inr_amount = conver_to_inr(dollar)
print(f"The amount in INR is: {inr_amount}")