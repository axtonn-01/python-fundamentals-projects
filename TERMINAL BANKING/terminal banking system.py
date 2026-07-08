"""
Terminal Banking System
------------------------
Features:
  - Create / delete accounts (with PIN protection)
  - Deposit and withdraw funds
  - Check balance
  - View transaction history
  - List all accounts (admin view)
  - All data persisted to a JSON file (bank_data.json) so it survives restarts
 
Run:  python bank_system.py
"""

import json
import os
import uuid
from datetime import datetime

DATA_FILE = "bank_data.json"


class Storage:
    """Handles loading and saving bank data to a JSON file."""

    def __init__(self, filepath=DATA_FILE):
        self.filepath = filepath
        
    def load(self):
        if not os.path.exists(self.filepath):
            return {}
        try:
            with open(self.filepath, "r") as f:
             content = f.read(). strip()
            return json.loads(content) if content else {}
        except (json.JSONDecodeError , IOError):
            print("⚠️  Warning: data file was unreadable/corrupted. Starting fresh.")
            return {}
        
    def save(self, data):
        with open(self.filepath, "w") as f:
            json.dump(data, f, indent=2)



class BankSystem:
    """Main banking system class that manages accounts and transactions."""

    def __init__(self):
        self.storage = Storage()
        self.accounts = self.storage.load()

    def _save(self):
        self.storage.save(self.accounts)

    @staticmethod
    def _generate_account_number():
        """Generates a unique account number."""
        return str(uuid.uuid4().int)[:10]  # 10-digit unique number
    
    @staticmethod       
    def _timestamp():
        """Generates a timestamp for transactions."""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def _log_transaction(self, acc_no, txt_type, amount, balance_after, note=""):
        txn = {
            "id": str(uuid.uuid4())[:8],
            "type": txt_type,
            "amount": round(amount, 2),
            "balance_after": round(balance_after, 2),
            "timestamp": self._timestamp(),
            "note": note,
        }
        self.accounts[acc_no]["transactions"].append(txn)


    def create_account(self, name, pin, opening_balance=0.0):
        if opening_balance < 0:
            print("❌ Opening balance cannot be negative.")
            return None
    
        acc_no = self._generate_account_number()
        while acc_no in self.accounts:
            acc_no = self._generate_account_number()

        self.accounts[acc_no] = {
            "name": name,
            "pin": pin,
            "balance": round(opening_balance, 2),
            "transactions": [],
        }
        if opening_balance > 0:
            self._log_transaction(acc_no, "DEPOSIT", opening_balance, opening_balance, "Initial deposit")
        self._save()
        return acc_no, None
    
    def delete_account(self, acc_no, pin):
        ok, err = self.authenticate(acc_no, pin)
        if not ok:
            return False, err

        del self.accounts[acc_no]
        self._save()
        return True, None
    
    def authenticate(self, acc_no, pin):
        acc = self.accounts.get(acc_no)
        if acc is None:
            return False, "Account not found."

        if acc["pin"] != pin:
            return False, "Incorrect PIN."

        return True, None
    
    def deposit(self, acc_no, pin, amount):
        ok, err = self.authenticate(acc_no, pin)
        if not ok:
            return False, err   
        if amount <=0:
            return False, "Deposit amount must be positive."
        
        self.accounts[acc_no]["balance"] += round(amount, 2)
        new_balance = self.accounts[acc_no]["balance"]
        self._log_transaction(acc_no, "DEPOSIT", amount, new_balance)
        self._save()
        return True, new_balance
    
    def withdraw(self, acc_no, pin, amount):
        ok, err = self.authenticate(acc_no, pin)
        if not ok:
            return False, err   
        if amount <=0:
            return False, "Withdrawal amount must be positive."
        if amount > self.accounts[acc_no]["balance"]:
            return False, "Insufficient funds."
        
        self.accounts[acc_no]["balance"] -= round(amount, 2)
        new_balance = self.accounts[acc_no]["balance"]
        self._log_transaction(acc_no, "WITHDRAWAL", amount, new_balance)
        self._save()
        return True, new_balance
    
    def get_balance(self, acc_no, pin):
        ok, err = self.authenticate(acc_no, pin)
        if not ok:
            return None, err
        return self.accounts[acc_no]["balance"], None
    
    def get_transaction_history(self, acc_no, pin):
        ok, err = self.authenticate(acc_no, pin)
        if not ok:
            return None, err
        return self.accounts[acc_no]["transactions"], None
    
    def list_accounts(self):
        """admin view: account number, name, balance (no PINs, no history)."""
        return [
            {
                "account_number": acc_no,
                "name": acc_data["name"],
                "balance": acc_data["balance"]
            }
            for acc_no, acc_data in self.accounts.items()
        ]

def money(amount):
        return f"₹{amount:,.2f}"
    
def pause():
        input("\nPress Enter to continue...")

def get_float(prompt):
        while True:
            raw = input(prompt).strip()
            try:
                return float(raw)
            except ValueError:
                print("❌ Invalid input. Please enter a numeric value.")

def menu():
        print("\n" + "="*40)
        print("          TERMINAL BANKING SYSTEM")
        print("="*40)
        print("1. Create Account")
        print("2. Delete Account")
        print("3. Deposit Funds")
        print("4. Withdraw Funds")
        print("5. Check Balance")
        print("6. View Transaction History")
        print("7. List All Accounts (Admin)")
        print("8. Exit")
        return input("Select an option (1-8): ").strip()

def handle_create(bank):
    print("\n--- CREATE ACCOUNT ---")
    name = input("Enter account holder's name: ").strip()
    if not name:
        print("❌ Name cannot be empty.")
        return
    pin: str = input("Set a 4-digit PIN: ").strip()
    if not pin.isdigit() or len(pin) != 4:
        print("❌ PIN must be a 4-digit number.")
        return
    opening = get_float("Enter opening balance (or leave blank for 0): ")
    acc_no, err = bank.create_account(name, pin, opening)
    if err:
        print(f"Error : {err}")
    else:
        print(f"✅ Account created successfully!")
        print(f"Account Number: {acc_no}")
        print(f"keep this number and your PIN safe for future transactions.")


def handle_deposit(bank):
    print("\n--- DEPOSIT FUNDS ---")
    acc_no = input("Enter account number: ").strip()
    pin = input("Enter PIN: ").strip()
    amount = get_float("Enter amount to deposit: ")
    ok, result = bank.deposit(acc_no, pin, amount)
    if ok:
        print(f"✅ Deposit successful! New balance: {money(result)}")    
    else:
        print(f"❌ Deposit failed: {result}")


def handle_withdraw(bank):
    print("\n--- WITHDRAW FUNDS ---")
    acc_no = input("Enter account number: ").strip()
    pin = input("Enter PIN: ").strip()
    amount = get_float("Enter amount to withdraw: ")
    ok, result = bank.withdraw(acc_no, pin, amount)
    if ok:
        print(f"✅ Withdrawal successful! {BankSystem.money(amount)}. New balance: {BankSystem.money(result)}")    
    else:
        print(f"❌ Withdrawal failed: {result}")


def handle_check_balance(bank):
    print("\n--- CHECK BALANCE ---")
    acc_no = input("Enter account number: ").strip()
    pin = input("Enter PIN: ").strip()
    balance, err = bank.get_balance(acc_no, pin)
    if err:
        print(f"❌ Error: {err}")
    else:
        print(f"✅ Current balance: {BankSystem.money(balance)}")


def handle_transaction_history(bank):
    print("\n--- TRANSACTION HISTORY ---")
    acc_no = input("Enter account number: ").strip()
    pin = input("Enter PIN: ").strip()
    history, err = bank.get_transaction_history(acc_no, pin)
    if err:
        print(f"❌ Error: {err}")
        return
    if not history:
        print("No transactions found.")
        return
    print(f"\n{'date':<20} {'type':<12} {'amount':<12} {'balance_after':<15} {'note'}")
    print("-" * 80)
    for txn in history:
        print(f"{txn['timestamp']:<20} {txn['type']:<12}"
              f"{money(txn['amount']):>14} {money(txn['balance_after']):>16}") 
        

def handle_delete(bank):
    print("\n--- DELETE ACCOUNT ---")
    acc_no = input("Enter account number: ").strip()
    pin = input("Enter PIN: ").strip()
    confirm = input("Type YES to confirm pemanent deletion of this account: ").strip()
    if confirm != "YES":
        print("❌ Account deletion cancelled.")
        return
    ok, err = bank.delete_account(acc_no, pin)
    if ok:
         print("✅ Account deleted successfully.")
    else:
            print(f"❌ Account deletion failed: {err}")

def handle_list(bank):
    print("\n--- LIST ALL ACCOUNTS (ADMIN VIEW) ---")
    accounts = bank.list_accounts()
    if not accounts:
        print("No accounts yet.")
        return
    print(f"\n{'Account Number':<15} {'Name':<20} {'Balance':<15}")
    print("-" * 50)
    for acc in accounts:
        print(f"{acc['account_number']:<15} {acc['name']:<20} {BankSystem.money(acc['balance']):<15}")


def main():
    bank = BankSystem()
    actions = {
        "1": handle_create,
        "2": handle_delete,
        "3": handle_deposit,
        "4": handle_withdraw,
        "5": handle_check_balance,
        "6": handle_transaction_history,
        "7": handle_list,
    }
        
    while True:
        choice = menu()
        if choice == "8":
            print("\n Thanks for banking with us! Goodbye.")
            break
        action = actions.get(choice)
        if action:
            action(bank)
        else:
            print("❌ Invalid option, try again.")

if __name__ == "__main__":
    main()