print(f"FILE WRITER INITIALIZED")

with open("notes.txt" , "a") as file:

    while True:
        user_note = input("Enter a line of text to save (or type 'exit'):")

        if user_note.lower() == 'exit':
            break

        file.write(user_note + "\n")
        print("saved to notes.txt!")


print("system closed. please check your VS code sidebar for notes.txt!")
