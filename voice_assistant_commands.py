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
from urllib.parse import quote
import threading
import queue

# Response variations for human-like interaction (more conversational, with contractions and small interjections)
GREETINGS = [
    "Hey! What can I do for you?",
    "Hi there — how can I help?",
    "Good to hear from you. What do you need?",
    "At your service. What would you like me to do?",
    "Hey there! What's up?",
    "Hi — tell me how I can help.",
    "Hello! Ready when you are.",
    "Yo! What can I do?",
    "Hiya! Need something?",
    "Hey, I'm listening.",
    "Hello — how can I assist?",
    "Hi! What would you like me to do today?",
    "Hey, good to hear from you.",
    "Hi. How can I make your day easier?",
    "Hey! Want me to do something for you?",
    "Hello! What's on the agenda?",
    "Hi there — how may I assist?",
    "Hey! I'm here for you.",
    "Hello — what can I help with?",
    "Hey — ask me anything.",
    "Hi! Need a hand?",
    "Hello! What do you need right now?",
    "Hey — tell me what you want.",
    "Hi! Ready to help.",
    "Hello! How can I be useful?"
]

ACKNOWLEDGMENTS = [
    "Got it.",
    "On it.",
    "Consider it done.",
    "Absolutely.",
    "Sure thing.",
    "Right away.",
    "I'll take care of that.",
    "Doing that now.",
    "Alright, will do.",
    "Okay, I'm on it.",
    "I'll handle that for you.",
    "Done — or starting now.",
    "Copy that.",
    "Understood.",
    "Working on it.",
    "I'll get right on that.",
    "Thanks — doing it now.",
    "Roger that.",
    "Affirmative.",
    "I'm taking care of it.",
    "All set — starting now.",
    "I'll take care of it right away.",
    "On my way with that.",
    "Consider it handled.",
    "Will do."
]

FAREWELLS = [
    "Goodbye! Have a great one.",
    "See you later!",
    "Take care!",
    "Until next time.",
    "Bye! Stay safe.",
    "Catch you later.",
    "Talk soon!",
    "Bye — let me know if you need me again.",
    "See ya!",
    "Have a good one!",
    "Farewell!",
    "I'm signing off — bye!",
    "Take it easy.",
    "Goodbye — reach out anytime.",
    "Until later!",
    "Peace out.",
    "Later, alligator.",
    "Be well!",
    "Stay awesome.",
    "Bye for now.",
    "Have a great day!"
]

CONFUSION = [
    "Sorry, I didn't catch that — could you say it again?",
    "I'm not quite sure I followed that. Can you rephrase?",
    "Hmm, I didn't understand. What would you like me to do?",
    "Could you give me a little more detail please?",
    "I didn't get that. Mind repeating it?",
    "That didn't come through clearly. Try again?",
    "I might've missed that — want to say it again?",
    "Not sure I understand. Can you explain differently?",
    "I couldn't make sense of that. Could you rephrase?",
    "Apologies, I didn't understand. Can you try again?",
    "I missed that — please repeat.",
    "Could you clarify what you meant?",
    "Sorry, I'm confused — what would you like?",
    "Hmm, I didn't catch the request. Please repeat.",
    "I couldn't parse that. Say it another way?",
    "I didn't understand — could you be more specific?",
    "Mind repeating that a little slower?",
    "That was unclear — can you try one more time?",
    "Sorry, can you say that again?",
    "I didn't quite get that. What did you want?"
]

# New trigger lists (many human phrasings per intent)
GREETING_TRIGGERS = [
    "hello", "hi", "hey", "hiya", "yo", "good morning", "good afternoon", "good evening",
    "greetings", "sup", "what's up", "whats up", "howdy", "hey there", "morning", "evening",
    "afternoon", "hello jarvis", "hi jarvis", "hey jarvis", "jarvis hello", "jarvis hi",
    "wake up", "are you there", "come online", "hiya jarvis", "yo jarvis", "good to see you",
    "nice to see you", "jarvis"
]

TIME_TRIGGERS = [
    "what time is it", "what's the time", "whats the time", "tell me the time", "time please",
    "current time", "time now", "what time", "do you know the time", "could you tell me the time",
    "give me the time", "what time is it right now", "time now please", "tell time", "what's the clock",
    "clock", "what time is it now", "can you tell the time", "what's the time right now",
    "what time is it currently", "time check", "time?"
]

DATE_TRIGGERS = [
    "what date is it", "what's the date", "whats the date", "tell me the date", "date please",
    "current date", "what day is it", "what day", "what is today's date", "today's date",
    "date now", "what's today's date", "what day is it today", "which day is it", "date?"
]

THANKS_TRIGGERS = [
    "thank you", "thanks", "thx", "appreciate it", "much appreciated", "thanks a lot",
    "thanks very much", "cheers", "thanks jarvis", "thank you jarvis", "thanks so much",
    "i appreciate that", "thankyou"
]

EXIT_TRIGGERS = [
    "exit", "quit", "goodbye", "bye", "stop", "shut up", "go away", "see ya", "see you later",
    "i'm done", "close", "terminate", "shutdown assistant", "log off", "sign off", "end",
    "that's all", "stop listening", "sleep", "power down"
]

HOWAREYOU_TRIGGERS = [
    "how are you", "how do you feel", "how's it going", "how is it going", "what's up",
    "whats up", "how are you doing", "how are you jarvis", "are you okay", "are you fine",
    "how you doing"
]

WHATCANDO_TRIGGERS = [
    "what can you do", "your capabilities", "help me", "what are your functions", "what do you do",
    "what can you help with", "what are you able to do", "how can you help me"
]

OPEN_GOOGLE_TRIGGERS = ["open google", "go to google", "open google.com", "launch google", "google page"]
OPEN_YOUTUBE_TRIGGERS = ["open youtube", "go to youtube", "launch youtube", "youtube please", "open youtube.com"]
OPEN_GITHUB_TRIGGERS = ["open github", "go to github", "launch github", "open github.com"]
OPEN_REDDIT_TRIGGERS = ["open reddit", "go to reddit", "open reddit.com", "launch reddit"]
OPEN_TWITTER_TRIGGERS = ["open twitter", "open x", "go to twitter", "launch twitter", "open twitter.com"]

JOKE_TRIGGERS = ["joke", "tell me a joke", "make me laugh", "say something funny", "i want a joke", "jokes"]

# Expanded templates for time/date/things
TIME_RESPONSES = [
    "It's currently {time}.",
    "Right now it's {time}.",
    "The time is {time}.",
    "At the moment it's {time}.",
    "Looking at the clock, it's {time}.",
    "It's {time} right now.",
    "Clock shows {time}.",
    "It's about {time}.",
    "According to my clock, {time}.",
    "Time now: {time}.",
    "I'd say it's {time}.",
    "It reads {time}.",
    "That's {time} on the clock.",
    "It is {time} at the moment.",
    "Currently the time is {time}.",
    "Right this second it's {time}.",
    "It's {time}, if that helps.",
    "The current time is {time}.",
    "Time check: {time}.",
    "It appears to be {time}."
]

DATE_RESPONSES = [
    "Today is {date}.",
    "It's {date} today.",
    "The date is {date}.",
    "Today: {date}.",
    "According to my calendar, it's {date}.",
    "Calendar says {date}.",
    "That's {date} today.",
    "It's {date}, in case you were wondering.",
    "{date} is today's date.",
    "Right now it's {date}.",
    "Today's date is {date}.",
    "The day and date: {date}.",
    "It's {date} on the calendar.",
    "Today happens to be {date}.",
    "I see {date} today."
]

THANKS_RESPONSES = [
    "You're welcome!",
    "No problem!",
    "Anytime!",
    "Happy to help!",
    "My pleasure!",
    "Glad I could help.",
    "Don't mention it.",
    "Always here for you.",
    "Sure thing!",
    "No worries!",
    "You got it.",
    "Glad to assist.",
    "It was nothing.",
    "Always happy to help.",
    "Anytime you need me."
]

EXIT_RESPONSES = [
    "Goodbye!",
    "See you later!",
    "Signing off. Bye!",
    "Alright, take care.",
    "I'll be here when you need me again. Bye!",
    "Farewell!",
    "See ya!",
    "Done for now — bye!",
    "Okay, logging off.",
    "Bye! Reach out when you need me."
]

HOWAREYOU_RESPONSES = [
    "I'm functioning optimally — thanks for asking!",
    "All systems are running smoothly.",
    "Doing well! Ready to help.",
    "I'm fine, thanks. How can I assist?",
    "Feeling helpful today!",
    "I'm great — what's up?",
    "Couldn't be better. What do you need?",
    "Working perfectly. What can I do?",
    "I'm doing well — ready when you are.",
    "All good here!"
]

WHATCANDO_RESPONSES = [
    "I can tell you the time and date, open websites, search the web, open applications, and chat with you.",
    "I can do various tasks: give time/date, open sites like Google or YouTube, run apps and search the web.",
    "I can help with time, date, opening apps and websites, searching, and light conversation.",
    "I can look things up, open programs, tell the time and date, and more.",
    "I can open sites, run apps, search the web, tell you the time/date, and assist with simple tasks.",
    "Ask me to open websites, search for things, run apps, or just have a chat."
]

# Helper to check many triggers quickly

def match_any(text: str, phrases: list) -> bool:
    if not text:
        return False
    for p in phrases:
        if p in text:
            return True
    return False

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

# Add persistent TTS globals
_TTS_ENGINE = None
_TTS_QUEUE = None
_TTS_THREAD = None


def _init_tts_engine():
    """Initialize the TTS engine and set natural parameters (used by the worker)."""
    try:
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        # prefer a different voice if available
        if len(voices) > 1:
            engine.setProperty('voice', voices[1].id)
        engine.setProperty('rate', 170)
        engine.setProperty('volume', 0.9)
        return engine
    except Exception as e:
        print(f"TTS init error: {e}")
        return None


def _tts_worker():
    """Background worker that consumes text from a queue and speaks using a single engine."""
    global _TTS_ENGINE, _TTS_QUEUE
    _TTS_ENGINE = _init_tts_engine()
    if _TTS_QUEUE is None:
        _TTS_QUEUE = queue.Queue()
    q = _TTS_QUEUE
    while True:
        item = q.get()
        if item is None:
            # shutdown signal
            q.task_done()
            break
        text, ev = item
        try:
            if _TTS_ENGINE is None:
                # fallback to print if engine failed
                print(text)
            else:
                _TTS_ENGINE.say(text)
                _TTS_ENGINE.runAndWait()
        except Exception as e:
            print(f"TTS worker error: {e}")
        finally:
            if ev:
                ev.set()
            q.task_done()


def _start_tts_thread():
    """Create and start the TTS thread and queue lazily."""
    global _TTS_QUEUE, _TTS_THREAD
    if _TTS_QUEUE is None:
        _TTS_QUEUE = queue.Queue()
    if _TTS_THREAD is None or not _TTS_THREAD.is_alive():
        _TTS_THREAD = threading.Thread(target=_tts_worker, daemon=True)
        _TTS_THREAD.start()

# Replace previous speak implementation with queued TTS.

def speak(text: str, block: bool = False):
    """Enqueue speech. By default non-blocking (fast return). Set block=True when you need to wait."""
    if not text:
        return
    utter = humanize_response(text)
    # ensure TTS system is running
    _start_tts_thread()
    if block:
        ev = threading.Event()
        _TTS_QUEUE.put((utter, ev))
        ev.wait()
    else:
        _TTS_QUEUE.put((utter, None))
    # no sleep here to keep responsiveness



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



def open_spotify(query: str = None) -> bool:
    """Try to open Spotify app with a search URI, fallback to web player search."""
    try:
        if query:
            # spotify URI scheme - many systems will open the native app if installed
            uri = f"spotify:search:{quote(query)}"
            try:
                os.startfile(uri)
                return True
            except Exception:
                # fallback to using web URL if URI fails
                webbrowser.open(f"https://open.spotify.com/search/{quote(query)}")
                return True
        else:
            # open app (spotify:) or web player
            try:
                os.startfile("spotify:")
                return True
            except Exception:
                webbrowser.open("https://open.spotify.com")
                return True
    except Exception as e:
        if DEBUG:
            print(f"[open_spotify] error: {e}")
        return False


# Add comprehensive Spotify trigger variants and help triggers
OPEN_SPOTIFY_TRIGGERS = [
    "open spotify", "launch spotify", "start spotify", "spotify open", "spotify please",
    "open spotify app", "open the spotify app", "open spotify web", "spotify web player",
    "spotify open web", "start the spotify app", "launch the spotify app"
]

PLAY_SPOTIFY_TRIGGERS = [
    "play on spotify", "play on spotify please", "play spotify", "play spotify please",
    "play song on spotify", "play music on spotify", "play {query} on spotify",
    "spotify play", "spotify play {query}", "play {query} spotify", "play {song} on spotify",
    "play artist on spotify", "play artist spotify", "listen on spotify", "listen to spotify",
    "listen to {query} on spotify", "put on spotify", "put on spotify please",
    "queue on spotify", "queue spotify", "play playlist on spotify", "play my spotify",
    "open spotify and play", "open spotify and play {query}", "spotify start", "spotify play music",
    "play some spotify", "play some music on spotify", "play from spotify", "play via spotify",
    "spotify, play", "jarvis play on spotify", "jarvis play spotify"
]

HELP_TRIGGERS = [
    "how do i tell you", "how to tell you", "how to ask", "show commands",
    "what can i say", "list commands", "examples", "help me use you",
    "how to use", "commands list", "how do i ask", "example commands"
]


# small helper to provide example phrases (prints full lists to console and gives a short vocal hint)

def provide_examples():
    examples = {
        "Spotify (play)": PLAY_SPOTIFY_TRIGGERS,
        "Spotify (open)": OPEN_SPOTIFY_TRIGGERS,
        "Google": OPEN_GOOGLE_TRIGGERS,
        "YouTube": OPEN_YOUTUBE_TRIGGERS,
        "GitHub": OPEN_GITHUB_TRIGGERS,
        "Reddit": OPEN_REDDIT_TRIGGERS,
        "Twitter/X": OPEN_TWITTER_TRIGGERS,
        "Time queries": TIME_TRIGGERS[:8],
        "Date queries": DATE_TRIGGERS[:8],
        "Search": ["search for {query}", "google {query}", "look up {query}", "find {query}"]
    }
    # Short vocal pointer
    speak("I'll list example phrases in the console so you can copy or test them.")
    # Print full examples so they're easy to review
    print("\n=== Example command phrases ===")
    for k, v in examples.items():
        print(f"\n{k}:")
        for ph in v:
            print(f"  - {ph}")
    print("\nYou can say e.g. 'Jarvis, play blinding lights on Spotify' or 'Jarvis, open Spotify'.")



def process_command(command):
    """Process and execute commands."""
    print(f"Processing command: {command}")
    cleaned = normalize_text(command)

    # quick intent matching using expanded triggers/responses

    # help / examples
    if match_any(cleaned, HELP_TRIGGERS) or "how do i" in cleaned or "examples" in cleaned:
        provide_examples()
        return True

    # Spotify handling (open or play)
    # If user asked to open Spotify app or web
    if match_any(cleaned, OPEN_SPOTIFY_TRIGGERS) and not match_any(cleaned, PLAY_SPOTIFY_TRIGGERS):
        speak(random.choice(ACKNOWLEDGMENTS) + " Opening Spotify.")
        success = open_spotify(None)
        if not success:
            speak("I couldn't open Spotify.")
        return True

    # If user requested to play something on Spotify
    if match_any(cleaned, PLAY_SPOTIFY_TRIGGERS) or ("spotify" in cleaned and "play" in cleaned):
        # try to extract a query after words like 'play' or 'on spotify'
        q = cleaned
        # remove generic tokens to leave the search query
        for phrase in ["play on spotify", "play spotify", "spotify play", "on spotify", "play", "please", "some", "music", "song", "listen to", "put on", "play from", "via spotify", "jarvis"]:
            q = q.replace(phrase, " ")
        q = re.sub(r"\s+", " ", q).strip()
        if q:
            speak(random.choice(ACKNOWLEDGMENTS) + f" Playing {q} on Spotify.")
            success = open_spotify(q)
            if not success:
                speak("I couldn't open Spotify.")
        else:
            # no query found — just open spotify
            speak(random.choice(ACKNOWLEDGMENTS) + " Opening Spotify.")
            success = open_spotify(None)
            if not success:
                speak("I couldn't open Spotify.")
        return True

    # exit/quit
    if match_any(cleaned, EXIT_TRIGGERS):
        speak(random.choice(EXIT_RESPONSES))
        return False

    # greetings
    if match_any(cleaned, GREETING_TRIGGERS):
        speak(random.choice(GREETINGS))
        return True

    # thanks
    if match_any(cleaned, THANKS_TRIGGERS):
        speak(random.choice(THANKS_RESPONSES))
        return True

    # how are you
    if match_any(cleaned, HOWAREYOU_TRIGGERS):
        speak(random.choice(HOWAREYOU_RESPONSES))
        return True

    # what can you do
    if match_any(cleaned, WHATCANDO_TRIGGERS):
        speak(random.choice(WHATCANDO_RESPONSES))
        return True

    # jokes
    if match_any(cleaned, JOKE_TRIGGERS):
        # reuse existing short jokes list if present; otherwise canned fallback
        try:
            jokes = [
                "Why do programmers prefer dark mode? Because light attracts bugs!",
                "Why did the developer go broke? Because he used up all his cache!",
                "There are only 10 types of people in the world: those who understand binary and those who don't.",
                "A SQL query walks into a bar, walks up to two tables and asks, 'Can I join you?'"
            ]
            speak(random.choice(jokes))
        except Exception:
            speak("Here's a joke: Why did the coder quit his job? Because he didn't get arrays.")
        return True

    # time (use TIME_RESPONSES templates)
    if match_any(cleaned, TIME_TRIGGERS):
        current_time = datetime.datetime.now().strftime("%I:%M %p").lstrip("0")
        template = random.choice(TIME_RESPONSES)
        speak(template.format(time=current_time))
        return True

    # date
    if match_any(cleaned, DATE_TRIGGERS):
        current_date = datetime.datetime.now().strftime("%A, %B %d, %Y")
        template = random.choice(DATE_RESPONSES)
        speak(template.format(date=current_date))
        return True

    # open sites (google/youtube/github/reddit/twitter)
    if match_any(cleaned, OPEN_GOOGLE_TRIGGERS):
        speak(random.choice(ACKNOWLEDGMENTS) + " Opening Google.")
        webbrowser.open("https://www.google.com")
        return True

    if match_any(cleaned, OPEN_YOUTUBE_TRIGGERS):
        speak(random.choice(ACKNOWLEDGMENTS) + " Opening YouTube.")
        webbrowser.open("https://www.youtube.com")
        return True

    if match_any(cleaned, OPEN_GITHUB_TRIGGERS):
        speak(random.choice(ACKNOWLEDGMENTS) + " Opening GitHub.")
        webbrowser.open("https://www.github.com")
        return True

    if match_any(cleaned, OPEN_REDDIT_TRIGGERS):
        speak(random.choice(ACKNOWLEDGMENTS) + " Opening Reddit.")
        webbrowser.open("https://www.reddit.com")
        return True

    if match_any(cleaned, OPEN_TWITTER_TRIGGERS):
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
        speak("Are you sure you want to shut down the computer?", block=True)
        confirm = listen()
        if any(word in confirm for word in ["yes", "yeah", "sure", "do it", "confirm"]):
            speak("Shutting down in 10 seconds.")
            os.system("shutdown /s /t 10")
        else:
            speak("Shutdown cancelled.")
        return True

    if "restart" in command:
        speak("Are you sure you want to restart the computer?", block=True)
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

    # Spotify: handle "play ... on spotify" or "play spotify" or "spotify play ..."
    if "spotify" in cleaned and any(w in cleaned for w in ["play", "listen", "music", "song"]):
        # remove common words to extract a simple query
        q = cleaned
        for phrase in ["play on spotify", "play on spotify", "on spotify", "play spotify", "spotify play", "play", "please", "some", "music", "song", "listen to"]:
            q = q.replace(phrase, " ")
        q = re.sub(r"\s+", " ", q).strip()
        if q:
            speak(random.choice(ACKNOWLEDGMENTS) + f" Playing {q} on Spotify.")
            success = open_spotify(q)
            if not success:
                speak("I couldn't open Spotify.")
        else:
            speak(random.choice(ACKNOWLEDGMENTS) + " Opening Spotify.")
            success = open_spotify(None)
            if not success:
                speak("I couldn't open Spotify.")
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

    # Slightly more casual startup greeting (non-blocking ok)
    speak(f"{get_time_greeting()} — I'm Jarvis. Say my name when you need me.")

    running = True
    while running:
        remaining_command = wait_for_wake_word()
        # Make wake acknowledgement blocking so the user won't overlap speech with listening
        speak(random.choice(["Yes?", "You called?", "I'm here.", "Yeah?"]), block=True)

        if remaining_command:
            running = process_command(remaining_command)
        else:
            command = listen(timeout=10)
            if command:
                running = process_command(command)


if __name__ == "__main__":
    main()
