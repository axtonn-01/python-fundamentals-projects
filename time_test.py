import time
print(" INITIALIZING AI DATA STREAM...")
time.sleep(2)
print("\n STREAMING RESULTS :")
words = [ "GENERATING" , "ANALYZING" , "PROCESSING" , "COMPLETE!" ]

for word in words:
    print(f"-> {word}")
    time.sleep(1)

print("\n task finished using the external 'time' module! ")
