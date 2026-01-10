import speech_recognition as sr
import pyttsx3
import datetime
import webbrowser
import os
import random
import subprocess
import time

# Response variations for human-like interaction
GREETINGS = [
    "Hello! What can I do for you?",
    "Hey there! How may I assist you?",
    "Good to hear from you! What do you need?",
    "At your service. What would you like me to do?"
]

ACKNOWLEDGMENTS = [
    "Right away, sir.",
    "On it.",
    "Consider it done.",
    "Absolutely."
]

FAREWELLS = [
    "Goodbye! Have a great day.",
    "See you later!",
    "Take care!",
    "Until next time."
]

CONFUSION = [
    "I'm not quite sure what you mean. Could you rephrase that?",
    "I didn't catch that. Could you try again?",
    "Sorry, I couldn't understand. What would you like me to do?",
    "Hmm, I'm not sure how to help with that. Can you be more specific?"
]

MIC_DEVICE_INDEX = None

# Brave browser path (adjust if installed elsewhere)
BRAVE_PATH = r"C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe"


def speak(text):
    """Convert text to speech - creates fresh engine each time."""
    print(f"Speaking: {text}")
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', 175)
        voices = engine.getProperty('voices')
        if voices:
            engine.setProperty('voice', voices[0].id)
        engine.say(text)
        engine.runAndWait()
        engine.stop()
        del engine
        time.sleep(0.1)
    except Exception as e:
        print(f"TTS Error: {e}")


def listen(timeout=5):
    """Listen for voice input and return text."""
    recognizer = sr.Recognizer()
    recognizer.energy_threshold = 300
    recognizer.dynamic_energy_threshold = False
    recognizer.pause_threshold = 0.8

    with sr.Microphone(device_index=MIC_DEVICE_INDEX) as source:
        print("Listening...")
        try:
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=10)
        except sr.WaitTimeoutError:
            return ""
    try:
        command = recognizer.recognize_google(audio).lower()
        print(f"You said: {command}")
        return command
    except sr.UnknownValueError:
        return ""
    except sr.RequestError:
        speak("Sorry, the speech service is currently unavailable.")
        return ""


def wait_for_wake_word():
    """Continuously listen for various wake phrases."""
    recognizer = sr.Recognizer()
    recognizer.energy_threshold = 300
    recognizer.dynamic_energy_threshold = False
    recognizer.pause_threshold = 0.8

    wake_phrases = [
        "hey jarvis", "jarvis", "yo jarvis", "okay jarvis", "ok jarvis",
        "hi jarvis", "hello jarvis", "excuse me jarvis", "hey j",
        "j", "mr jarvis", "mister jarvis", "dear jarvis", "oi jarvis"
    ]

    with sr.Microphone(device_index=MIC_DEVICE_INDEX) as source:
        print("Calibrating microphone once... please wait.")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        print(f"Energy threshold set to: {recognizer.energy_threshold}")
        print("Waiting for wake word...")

        while True:
            try:
                audio = recognizer.listen(source, phrase_time_limit=5)
                text = recognizer.recognize_google(audio).lower()
                print(f"Heard: {text}")

                detected_phrase = None
                for phrase in wake_phrases:
                    if phrase in text:
                        detected_phrase = phrase
                        break

                if detected_phrase:
                    print(f"Wake phrase detected: {detected_phrase}")
                    remaining = text.replace(detected_phrase, "").strip()
                    return remaining if remaining else None

            except sr.UnknownValueError:
                pass
            except sr.WaitTimeoutError:
                pass
            except sr.RequestError as e:
                print(f"API error: {e}")


def get_time_greeting():
    """Return appropriate greeting based on time of day."""
    hour = datetime.datetime.now().hour
    if hour < 12:
        return "Good morning"
    elif hour < 17:
        return "Good afternoon"
    else:
        return "Good evening"


def open_brave_incognito():
    """Open Brave browser in incognito mode."""
    try:
        subprocess.Popen([BRAVE_PATH, "--incognito"])
        return True
    except FileNotFoundError:
        # Try alternative path
        alt_path = os.path.expandvars(r"%LOCALAPPDATA%\\BraveSoftware\\Brave-Browser\\Application\\brave.exe")
        try:
            subprocess.Popen([alt_path, "--incognito"])
            return True
        except FileNotFoundError:
            return False


def process_command(command):
    """Process and execute commands."""
    print(f"Processing command: {command}")

    if "prepare the goon chair" in command or "goon chair" in command:
        speak("Yes, sir. Hard or light mode?")
        response = listen(timeout=10)
        if "hard" in response:
            speak("Hard mode activated. Brace yourself.")
            if open_brave_incognito():
                speak("Incognito window opened.")
            else:
                speak("Could not find Brave browser.")
        elif "light" in response:
            speak("Light mode it is. Enjoy.")
            if open_brave_incognito():
                speak("Incognito window opened.")
            else:
                speak("Could not find Brave browser.")
        else:
            speak("I'll set it to default mode.")
            if open_brave_incognito():
                speak("Incognito window opened.")
            else:
                speak("Could not find Brave browser.")
        return True

    if "joke" in command or "tell me a joke" in command or "make me laugh" in command:
        jokes = [
            "Why do programmers prefer dark mode? Because light attracts bugs!",
            "Why did the developer go broke? Because he used up all his cache!",
            "There are only 10 types of people in the world: those who understand binary and those who don't.",
            "A SQL query walks into a bar, walks up to two tables and asks, 'Can I join you?'"
        ]
        speak(random.choice(jokes))
        return True

    if any(phrase in command for phrase in ["exit", "quit", "goodbye", "bye", "stop", "shut up", "go away"]):
        speak(random.choice(FAREWELLS))
        return False

    if any(word in command for word in
           ["hello", "hi", "hey", "greetings", "good morning", "good afternoon", "good evening"]):
        speak(f"{get_time_greeting()}! {random.choice(GREETINGS)}")
        return True

    if any(phrase in command for phrase in ["what time", "current time", "tell me the time", "what's the time"]):
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        responses = [
            f"It's currently {current_time}.",
            f"The time is {current_time}.",
            f"Right now, it's {current_time}."
        ]
        speak(random.choice(responses))
        return True

    if any(phrase in command for phrase in ["what date", "today's date", "what day", "what's the date"]):
        current_date = datetime.datetime.now().strftime("%A, %B %d, %Y")
        speak(f"Today is {current_date}.")
        return True

    if any(phrase in command for phrase in ["how are you", "how do you feel", "how's it going", "what's up"]):
        responses = [
            "I'm functioning optimally, thank you for asking!",
            "All systems are running smoothly. How can I help?",
            "I'm doing great! Ready to assist you.",
            "Never better! What do you need?"
        ]
        speak(random.choice(responses))
        return True

    if any(phrase in command for phrase in
           ["what can you do", "your capabilities", "help me", "what are your functions"]):
        speak("I can help you with several things. I can tell you the time and date, "
              "open websites like Google and YouTube, search the web, open applications, "
              "and have a conversation with you. Just let me know what you need!")
        return True

    if any(phrase in command for phrase in ["thank you", "thanks", "appreciate"]):
        responses = [
            "You're welcome!",
            "Happy to help!",
            "Anytime!",
            "My pleasure!"
        ]
        speak(random.choice(responses))
        return True

    if "open google" in command:
        speak(random.choice(ACKNOWLEDGMENTS) + " Opening Google.")
        webbrowser.open("https://www.google.com")
        return True

    if "open youtube" in command:
        speak(random.choice(ACKNOWLEDGMENTS) + " Opening YouTube.")
        webbrowser.open("https://www.youtube.com")
        return True

    if "open github" in command:
        speak(random.choice(ACKNOWLEDGMENTS) + " Opening GitHub.")
        webbrowser.open("https://www.github.com")
        return True

    if "open reddit" in command:
        speak(random.choice(ACKNOWLEDGMENTS) + " Opening Reddit.")
        webbrowser.open("https://www.reddit.com")
        return True

    if "open twitter" in command or "open x" in command:
        speak(random.choice(ACKNOWLEDGMENTS) + " Opening Twitter.")
        webbrowser.open("https://www.twitter.com")
        return True

    if any(phrase in command for phrase in ["search for", "look up", "google", "find"]):
        for phrase in ["search for", "look up", "google", "find"]:
            command = command.replace(phrase, "")
        query = command.strip()
        if query:
            speak(f"Searching for {query}.")
            webbrowser.open(f"https://www.google.com/search?q={query}")
        else:
            speak("What would you like me to search for?")
            query = listen()
            if query:
                speak(f"Searching for {query}.")
                webbrowser.open(f"https://www.google.com/search?q={query}")
        return True

    if "open notepad" in command:
        speak(random.choice(ACKNOWLEDGMENTS))
        os.startfile("notepad.exe")
        return True

    if "open calculator" in command:
        speak(random.choice(ACKNOWLEDGMENTS))
        os.startfile("calc.exe")
        return True

    if "open file explorer" in command or "open explorer" in command:
        speak(random.choice(ACKNOWLEDGMENTS))
        os.startfile("explorer.exe")
        return True

    if "open command prompt" in command or "open cmd" in command:
        speak(random.choice(ACKNOWLEDGMENTS))
        os.startfile("cmd.exe")
        return True

    if "shutdown" in command or "shut down" in command:
        speak("Are you sure you want to shut down the computer?")
        confirm = listen()
        if any(word in confirm for word in ["yes", "yeah", "sure", "do it", "confirm"]):
            speak("Shutting down in 10 seconds.")
            os.system("shutdown /s /t 10")
        else:
            speak("Shutdown cancelled.")
        return True

    if "restart" in command:
        speak("Are you sure you want to restart the computer?")
        confirm = listen()
        if any(word in confirm for word in ["yes", "yeah", "sure", "do it", "confirm"]):
            speak("Restarting in 10 seconds.")
            os.system("shutdown /r /t 10")
        else:
            speak("Restart cancelled.")
        return True

    if any(phrase in command for phrase in ["who are you", "your name", "what are you"]):
        speak(
            "I am Jarvis, your personal assistant. I'm here to help you with various tasks and make your life a bit easier.")
        return True

    if "play music" in command or "play some music" in command:
        music_path = os.path.expanduser("~\\\u200bMusic")
        if os.path.exists(music_path):
            speak("Opening your music folder.")
            os.startfile(music_path)
        else:
            speak("I couldn't find your music folder.")
        return True

    speak(random.choice(CONFUSION))
    return True


def main():
    print("Available microphones:")
    for i, mic in enumerate(sr.Microphone.list_microphone_names()):
        print(f"  {i}: {mic}")
    print(f"\nUsing: {'System default' if MIC_DEVICE_INDEX is None else f'Device {MIC_DEVICE_INDEX}'}")
    print()

    speak(f"{get_time_greeting()}! I am Jarvis, your personal assistant. Just say my name to get my attention.")

    running = True
    while running:
        remaining_command = wait_for_wake_word()
        speak("Yes?")

        if remaining_command:
            running = process_command(remaining_command)
        else:
            command = listen(timeout=10)
            if command:
                running = process_command(command)


if __name__ == "__main__":
    main()
