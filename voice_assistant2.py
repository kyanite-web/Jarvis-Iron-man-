import speech_recognition as sr
import pyttsx3
import datetime
import webbrowser
import os
import random
import subprocess
import time
import re
import difflib

# Response variations for human-like interaction (more conversational, with contractions and small interjections)
GREETINGS = [
    "Hey! What can I do for you?",
    "Hi there — how can I help?",
    "Good to hear from you. What do you need?",
    "At your service. What would you like me to do?"
]

ACKNOWLEDGMENTS = [
    "Got it.",
    "On it.",
    "Consider it done.",
    "Absolutely."
]

FAREWELLS = [
    "Goodbye! Have a great one.",
    "See you later!",
    "Take care!",
    "Until next time."
]

CONFUSION = [
    "Sorry, I didn't catch that — could you say it again?",
    "I'm not quite sure I followed that. Can you rephrase?",
    "Hmm, I didn't understand. What would you like me to do?",
    "Could you give me a little more detail please?"
]

MIC_DEVICE_INDEX = None

# Brave browser path (adjust if installed elsewhere)
BRAVE_PATH = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"

# Audio settings - adjust these for your environment
ENERGY_THRESHOLD = 400  # Higher = less sensitive (reduce background noise pickup)
PAUSE_THRESHOLD = 0.6   # Seconds of silence before phrase is considered complete
PHRASE_THRESHOLD = 0.3  # Minimum seconds of speaking to consider

# Add small debug flag and simple per-listen calibration
DEBUG = True
PER_LISTEN_CALIBRATE = 0.6

# Debug and adaptive microphone settings
DYNAMIC_ENERGY = True   # Let recognizer adapt energy threshold at runtime
CALIBRATION_DURATION = 3.0  # seconds for initial ambient noise calibration
MIN_ENERGY_THRESHOLD = 150  # lower = more sensitive (be careful with noise)
AUTO_SELECT_MIC_KEYWORDS = ["mic", "microphone", "usb", "realtek", "input"]


def _init_tts_engine():
    """Initialize the TTS engine, setting a warmer voice and natural parameters."""
    global _TTS_ENGINE
    if _TTS_ENGINE is None:
        try:
            _TTS_ENGINE = pyttsx3.init()
            # Pick a warmer voice if available (try female/second voice)
            voices = _TTS_ENGINE.getProperty('voices')
            if len(voices) > 1:
                # prefer the second voice if it seems different
                _TTS_ENGINE.setProperty('voice', voices[1].id)
            _TTS_ENGINE.setProperty('rate', 170)
            _TTS_ENGINE.setProperty('volume', 0.9)
        except Exception as e:
            print(f"TTS init error: {e}")
            _TTS_ENGINE = None
    return _TTS_ENGINE


def humanize_response(text: str) -> str:
    """Apply small conversational touches: contractions and optional interjections."""
    if not text:
        return ""
    # Contractions / small normalization
    contractions = {
        "do not": "don't",
        "does not": "doesn't",
        "can not": "can't",
        "i am": "I'm",
        "i will": "I'll",
        "i have": "I've",
        "you are": "you're",
        "it is": "it's",
        "what is": "what's",
        "that is": "that's",
        "let us": "let's"
    }
    s = text.strip()
    s_lower = s.lower()
    for k, v in contractions.items():
        s_lower = re.sub(r'\b' + re.escape(k) + r'\b', v, s_lower)
    # Optionally prepend a mild interjection ~20% of time for realism
    if random.random() < 0.2:
        prefix = random.choice(["Alright, ", "Okay, ", "Sure, ", "Gotcha — "])
        s_lower = prefix + s_lower
    return s_lower.capitalize()


def speak(text):
    """Convert text to speech - creates fresh engine each time."""
    # utterance = humanize_response(text)
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


def auto_select_mic():
    """If MIC_DEVICE_INDEX is None, try to pick a likely microphone index."""
    global MIC_DEVICE_INDEX
    if MIC_DEVICE_INDEX is not None:
        return
    try:
        names = sr.Microphone.list_microphone_names()
    except Exception as e:
        if DEBUG:
            print(f"Could not list microphones: {e}")
        return
    for i, name in enumerate(names):
        lname = name.lower()
        if any(k in lname for k in AUTO_SELECT_MIC_KEYWORDS):
            MIC_DEVICE_INDEX = i
            if DEBUG:
                print(f"Auto-selected microphone {i}: {name}")
            return
    # If nothing matched, keep default (None) but show available devices when debugging
    if DEBUG:
        print("No likely mic name matched; available devices:")
        for i, name in enumerate(names):
            print(f"  {i}: {name}")


def create_recognizer():
    """Create a recognizer with consistent settings."""
    recognizer = sr.Recognizer()
    recognizer.energy_threshold = ENERGY_THRESHOLD
    # allow short dynamic adjustments to help pickup quieter voices
    recognizer.dynamic_energy_threshold = True
    recognizer.pause_threshold = PAUSE_THRESHOLD
    recognizer.phrase_threshold = PHRASE_THRESHOLD
    recognizer.non_speaking_duration = 0.4
    if DEBUG:
        print(f"[create_recognizer] energy_threshold={recognizer.energy_threshold} dynamic={recognizer.dynamic_energy_threshold}")
    return recognizer


def listen(timeout=5, retries=2):
    """Listen for voice input and return text. Calibrate briefly before capture and retry on UnknownValueError."""
    recognizer = create_recognizer()

    with sr.Microphone(device_index=MIC_DEVICE_INDEX) as source:
        if PER_LISTEN_CALIBRATE and PER_LISTEN_CALIBRATE > 0:
            if DEBUG:
                print(f"[listen] calibrating for {PER_LISTEN_CALIBRATE}s...")
            try:
                recognizer.adjust_for_ambient_noise(source, duration=PER_LISTEN_CALIBRATE)
            except Exception as e:
                if DEBUG:
                    print(f"[listen] calibrate error: {e}")
        attempt = 0
        while attempt <= retries:
            attempt += 1
            if DEBUG:
                print(f"[listen] attempt {attempt} listening (timeout={timeout})")
            try:
                audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=10)
            except sr.WaitTimeoutError:
                if DEBUG:
                    print("[listen] wait timeout")
                return ""
            try:
                command = recognizer.recognize_google(audio).lower()
                if DEBUG:
                    print(f"[listen] recognized: {command}")
                if command.strip():
                    return command
            except sr.UnknownValueError:
                if DEBUG:
                    print("[listen] couldn't understand (UnknownValueError), retrying...")
                continue
            except sr.RequestError as e:
                if DEBUG:
                    print(f"[listen] RequestError: {e}")
                speak("Sorry, the speech service is currently unavailable.")
                return ""
        if DEBUG:
            print("[listen] all attempts failed")
        return ""


def wait_for_wake_word():
    """Continuously listen for various wake phrases and return a cleaned remaining command (or None)."""
    recognizer = create_recognizer()

    wake_phrases = [
        "hey jarvis", "jarvis", "yo jarvis", "okay jarvis", "ok jarvis",
        "hi jarvis", "hello jarvis", "excuse me jarvis", "hey j",
        "j", "mr jarvis", "mister jarvis", "dear jarvis", "oi jarvis"
    ]

    with sr.Microphone(device_index=MIC_DEVICE_INDEX) as source:
        # Calibrate ONCE at start
        if DEBUG:
            print("Calibrating microphone... please wait.")
        try:
            recognizer.adjust_for_ambient_noise(source, duration=2)
        except Exception as e:
            if DEBUG:
                print(f"[wait_for_wake_word] calibrate failed: {e}")
        if DEBUG:
            print(f"[wait_for_wake_word] energy_threshold={recognizer.energy_threshold}")
        print("Waiting for wake word...")

        while True:
            try:
                audio = recognizer.listen(source, timeout=None, phrase_time_limit=6)
                try:
                    text = recognizer.recognize_google(audio).lower()
                except sr.UnknownValueError:
                    if DEBUG:
                        print("[wait_for_wake_word] UnknownValueError - continuing")
                    continue
                except sr.RequestError as e:
                    if DEBUG:
                        print(f"[wait_for_wake_word] API error: {e}")
                    time.sleep(1)
                    continue

                if DEBUG:
                    print(f"Heard (raw): {text}")
                cleaned = normalize_text(text)

                # find any wake phrase inside the normalized text
                detected = None
                for phrase in wake_phrases:
                    if phrase in cleaned:
                        detected = phrase
                        break

                if detected:
                    # remove only first occurrence of detected phrase and return normalized remaining
                    # use word boundaries to avoid accidental partial matches
                    pattern = re.compile(r'\b' + re.escape(detected) + r'\b', flags=re.IGNORECASE)
                    remaining = pattern.sub('', cleaned, count=1).strip()
                    # final normalization to remove stray punctuation/whitespace
                    remaining = normalize_text(remaining)
                    if DEBUG:
                        print(f"Wake detected='{detected}', remaining(normalized)='{remaining}'")
                    return remaining if remaining else None

            except sr.UnknownValueError:
                pass
            except sr.WaitTimeoutError:
                pass
            except sr.RequestError as e:
                if DEBUG:
                    print(f"[wait_for_wake_word] outer RequestError: {e}")
                time.sleep(1)


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
        alt_path = os.path.expandvars(r"%LOCALAPPDATA%\BraveSoftware\Brave-Browser\Application\brave.exe")
        try:
            subprocess.Popen([alt_path, "--incognito"])
            return True
        except FileNotFoundError:
            return False


def normalize_text(text: str) -> str:
    """Lowercase, remove leading/trailing punctuation, collapse whitespace."""
    if not text:
        return ""
    s = text.lower()
    # remove punctuation but keep spaces and alphanumerics
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def process_command(command):
    """Process and execute commands."""
    print(f"Processing command: {command}")
    cleaned = normalize_text(command)

    # Detect combined queries for both date AND time first
    date_keywords = {"date", "day", "today"}
    time_keywords = {"time", "clock", "currenttime", "current", "now"}

    has_date = any(k in cleaned for k in date_keywords)
    has_time = any(k in cleaned for k in time_keywords)

    if has_date and has_time:
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        current_date = datetime.datetime.now().strftime("%A, %B %d, %Y")
        speak(f"Today is {current_date} and the time is {current_time}.")
        return True

    if "prepare the goon chair" in command or "goon chair" in command:
        speak("Yes, sir. Hard or light mode?")
        response = listen(timeout=10)
        if "hard" in response:
            speak("Hard mode activated. Brace yourself.")
        elif "light" in response:
            speak("Light mode it is. Enjoy.")
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

    # Replace time-only and date-only checks to use `cleaned`
    if any(phrase in cleaned for phrase in ["what time", "current time", "tell me the time", "whats the time", "whats time", "time"]):
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        responses = [
            f"It's currently {current_time}.",
            f"The time is {current_time}.",
            f"Right now, it's {current_time}."
        ]
        speak(random.choice(responses))
        return True

    if any(phrase in cleaned for phrase in ["what date", "todays date", "what day", "whats the date", "date", "today"]):
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
        music_path = os.path.expanduser("~\\Music")
        if os.path.exists(music_path):
            speak("Opening your music folder.")
            os.startfile(music_path)
        else:
            speak("I couldn't find your music folder.")
        return True

    speak(random.choice(CONFUSION))
    return True


def main():
    auto_select_mic()
    print("Available microphones:")
    for i, mic in enumerate(sr.Microphone.list_microphone_names()):
        print(f"  {i}: {mic}")
    print(f"\nUsing: {'System default' if MIC_DEVICE_INDEX is None else f'Device {MIC_DEVICE_INDEX}'}")
    print()

    # Slightly more casual startup greeting
    speak(f"{get_time_greeting()} — I'm Jarvis. Say my name when you need me.")

    running = True
    while running:
        remaining_command = wait_for_wake_word()
        # More natural wake acknowledgement
        speak(random.choice(["Yes?", "You called?", "I'm here.", "Yeah?"]))

        if remaining_command:
            running = process_command(remaining_command)
        else:
            command = listen(timeout=10)
            if command:
                running = process_command(command)


if __name__ == "__main__":
    main()
