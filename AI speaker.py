import pyttsx3
import os

print(" INITIALIZING LOCAL AI AUDIO ENGINE...\n")

try:
    
    engine = pyttsx3.init()

    engine.setProperty('rate' , 175)

    ai_prompt = input("Enter text to convert to speech: ")
    print(f"ai is generating speech '{ai_prompt}'")

    output_filename = "ai_generation.mp3"
    engine.save_to_file(ai_prompt , output_filename)

    engine.runAndWait()
    print("\n" + "="*35)
    print("SUCCESS AUDIO FILE CREATED")
    print("="*35)

    if os.path.exists(output_filename):
        print(f" file saved as : {os.path.abspath(output_filename)}")
    print("="*35)
except Exception as e:
    print(f" audio generation failed: {e}")