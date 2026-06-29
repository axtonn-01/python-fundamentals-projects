expenses = []

print("--- WELCOME TO YOUR PERSONAL EXPENSE TRACKER ---")
print("enter your expenses one by one (numbers only). Type 'done when finished. \n")

while True:
    user_input = input("Enter expense amount in (₹): ")
    if user_input.lower() == "done":
        break

    try:
        amount = float(user_input)
        if amount < 0:
            print("❌ expense cannnot be negative. please enter a valid amount!")
            continue
        expenses.append(amount)
    except ValueError:
        print(" ❌ invalid input ! please enter a valid inoput or type 'done'.")


if len(expenses) > 0:
    total_expenses = sum(expenses)
    highest_expenses = max(expenses)
    lowest_expenses = min(expenses)
    average_expenses = total_expenses / len(expenses)


    print("\n" + "=" *35)
    print(" 📊 FINANCIAL SUMMARY REPORT 📊 ")
    print("="*35)
    print(f"Total spent:            ₹{total_expenses:,.2f}")
    print(f"highest spent:          ₹{highest_expenses:,.2f}")
    print(f"lowest spent:           ₹{lowest_expenses:,.2f}")
    print(f"average spent:          ₹{average_expenses:,.2f}")
    print(f"total transaction:       {len(expenses)}")
    print("="*35)

else:
    print("\n📝 No expenses were recorded. Your wallet is safe!")