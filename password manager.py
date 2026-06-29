password_vault = {}

print("---- WELCOME TO YOUR SECURED PASSWORD MANAGER----")
print(" Enter your acccount details below or type 'done' as the website to stop.\n")

while True:
    website = input("enter website/app name ( or type 'done'): ").strip()
    if website.lower() == 'done':
        break
    
    username = input(f"Enter username for {website}:")
    password = input(f"Enter password for {website}:")

    password_vault[website.lower()] = {
        "display_name" : website,
        "user" : username,
        "pass" : password,
    }
    print(f"credentials securely saved for {website}! \n")


print("\n" + "="*40)
print("---ALL SAVED VAULT ACCOUNT---")
print("="*40)

if len(password_vault) > 0:
    for web_key, credentials in password_vault.items():
        print(f"🌐 Website:  {credentials['display_name']}")
        print(f"   👤 Username: {credentials['user']}")
        print(f"   🔑 Password: {credentials['pass']}")
        print("-" * 20)
else:
    print("The vault is currently empty.")

print("="*40)

if len(password_vault) > 0:
    print("\n🔍 VAULT SEARCH INITIALIZED")
    search_query = input("Enter a website to search: ").strip().lower()

    if search_query in password_vault:
        account = password_vault[search_query]
        print(f"\n🔑 Account Details Found for {account['display_name']}:")
        print(f"   Username: {account['user']}")
        print(f"   Password: {account['pass']}")
    else:
        print("\n❌ No account found.")