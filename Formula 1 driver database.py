f1_driver_registry = {

    "VER" : {
        "Driver_name" : "Max Verstappen",
        "team" : "Red Bull Racing", 
        "car_number" : 1, 
        "podiums" : 105,
    },

    "HAM" : {
        "Driver_name" : "Lewis Hamilton",
        "team" : "Ferrari",
        "car_number" : 44,  
        "podiums" : 201,
    },

    "LEC" : {
        "Driver_name" : "Charles Leclerc",
        "team" : "Ferrari",
        "car_number" : 16,  
        "podiums" : 20,
    },

    "NOR" : {
        "Driver_name" : "Lando Norris",
        "team" : "McLaren",
        "car_number" : 4,  
        "podiums" : 5,
    },
      
}

print("--- F1 TEAM STRATEGY PORTAL ---")
search_driver = input("Enter the driver's code (e.g., VER, HAM, LEC, NOR): ").upper()

if search_driver in f1_driver_registry:
    profile = f1_driver_registry[search_driver]
    print(f"\n Driver Profile found for{search_driver}:")
    print(f"Name: {profile['Driver_name']}")
    print(f"Team: {profile['team']}")
    print(f"Car Number: {profile['car_number']}")
    print(f"Podiums: {profile['podiums']}")

else:
    print(f"\n No profile found for driver code: {search_driver}. Please check the code and try again.")