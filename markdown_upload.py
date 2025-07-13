import math
import re
import os
import json # For parsing firebase config
import uuid # For generating unique IDs for feedback
import random # For picking a random word if multiple matches
import sqlite3 # New import for SQLite

# --- Database Configuration ---
# Set this to 'FIRESTORE' to use Firebase Firestore (requires firebase-admin-key.json or Canvas env vars)
# Set this to 'SQLITE' to use a local SQLite database (recommended for local testing without Firebase setup)
DATABASE_TYPE = 'SQLITE' # <--- CHANGE THIS TO 'FIRESTORE' OR 'SQLITE'

# SQLite specific configuration
SQLITE_DB_FILE = 'gematria_data.db'

# --- Firebase Initialization (MANDATORY for Canvas environment) ---
# These variables are provided by the Canvas environment.
# For local testing, you might need to manually set them or provide a dummy config.
APP_ID = os.environ.get('__app_id', 'default-gematria-app') # Fallback for local testing
FIREBASE_CONFIG_STR = os.environ.get('__firebase_config', '{}') # Fallback for local testing
INITIAL_AUTH_TOKEN = os.environ.get('__initial_auth_token', None) # Fallback for local testing

# Global database connection objects
db = None # Will be Firestore client or SQLite connection
current_user_id = None
firebase_auth = None # Only used if DATABASE_TYPE is 'FIRESTORE'

word_matrix = [] # Global list to store all words from uploaded documents
simple_gematria_word_lookup = {} # Global dict: {value: [word1, word2, ...]}
english_gematria_word_lookup = {} # Global dict for English dictionary fallback
last_generated_reply_info = None # Stores info about the last generated reply for feedback

# Global list of available gematria methods
methods_list = [
    "simple", "jewish_gematria", "qwerty", "left_hand_qwerty",
    "right_hand_qwerty", "binary_sum", "love_resonance", "frequent_letters",
    "leet_code", "simple_forms", "prime_gematria", "ambidextrous_balance",
    "aave_simple", "aave_reduced", "aave_spiral", "grok_resonance_score",
    "whole_sentence_gematria"
]

# --- Color Mapping for Gematria Values ---
# This is an arbitrary mapping for demonstration purposes.
# You can customize this palette and the logic in get_gematria_color.
GEMATRIA_COLORS = [
    "Red", "Orange", "Yellow", "Green", "Blue", "Indigo", "Violet", "Pink", "Brown", "Gray"
]

def get_gematria_color(value):
    """
    Assigns a color to a gematria value based on a simple modulo operation.
    """
    if not isinstance(value, (int, float)):
        return "N/A"
    
    # Use the absolute value and round to integer for consistent color mapping
    int_value = int(round(abs(value)))
    
    if len(GEMATRIA_COLORS) == 0:
        return "No Color Defined"
    
    color_index = int_value % len(GEMATRIA_COLORS)
    return GEMATRIA_COLORS[color_index]

def get_inverse_color(color_name):
    """
    Returns a conceptual 'inverse' color from the GEMATRIA_COLORS palette.
    This is a simplified approach (e.g., complementary color on a basic color wheel).
    """
    try:
        current_index = GEMATRIA_COLORS.index(color_name)
        # Calculate inverse index by shifting half the palette length
        inverse_index = (current_index + len(GEMATRIA_COLORS) // 2) % len(GEMATRIA_COLORS)
        return GEMATRIA_COLORS[inverse_index]
    except ValueError:
        return "N/A (Color not in palette)"
    except Exception:
        return "N/A"


def initialize_database():
    global db, current_user_id, firebase_auth

    if DATABASE_TYPE == 'FIRESTORE':
        try:
            firebase_config = None
            cred = None

            # Attempt to load config from environment variable (Canvas environment)
            try:
                env_config = json.loads(FIREBASE_CONFIG_STR)
                if env_config:
                    firebase_config = env_config
                    print("Firebase config loaded from environment variable.")
            except json.JSONDecodeError:
                print("Warning: __firebase_config environment variable is not valid JSON. Trying local file.")

            # If environment variable config is empty or invalid, try loading from local JSON file
            if not firebase_config:
                local_key_path = "firebase-admin-key.json"
                if os.path.exists(local_key_path):
                    print(f"Attempting to load Firebase credentials from local file: {local_key_path}")
                    with open(local_key_path, 'r') as f:
                        firebase_config = json.load(f)
                else:
                    print(f"Warning: {local_key_path} not found. Firebase will not be fully initialized for Firestore operations.")
            
            if firebase_config: # If we successfully loaded a config
                cred = credentials.Certificate(firebase_config)
                
            if not firebase_admin._apps: # Initialize only if not already initialized
                if cred:
                    firebase_admin.initialize_app(cred)
                    print("Firebase initialized successfully with credentials.")
                    db = firestore.client() # Initialize db client here
                    firebase_auth = auth
                else:
                    # If no creds are available, Firebase Admin SDK cannot connect to Firestore
                    print("Firebase Admin SDK cannot initialize with credentials. Firestore operations will not work.")
                    db = None # Explicitly set db to None
                    firebase_auth = None # Explicitly set auth to None
            else:
                print("Firebase already initialized.")
                # If already initialized, ensure db and auth clients are set if they weren't
                if db is None and cred: # Only try to set if db is None and we have creds
                     db = firestore.client()
                     firebase_auth = auth
                elif db is None and not cred: # If already initialized but no creds, db remains None
                     print("Firebase already initialized, but without credentials for Firestore.")


            if db: # Only proceed with auth if db client was successfully created
                if INITIAL_AUTH_TOKEN:
                    try:
                        decoded_token = firebase_auth.verify_id_token(INITIAL_AUTH_TOKEN)
                        current_user_id = decoded_token['uid']
                        print(f"Authenticated with custom token. User ID: {current_user_id}")
                    except Exception as e:
                        print(f"Error verifying custom token: {e}. Signing in anonymously.")
                        current_user_id = "anonymous_" + os.urandom(16).hex()
                else:
                    print("No initial auth token provided. Using an anonymous user ID.")
                    current_user_id = "anonymous_" + os.urandom(16).hex()
            else: # If db is None, then auth also cannot proceed for user-specific data
                print("Firestore client not initialized. Cannot determine authenticated user ID for data storage.")
                current_user_id = "local_user_" + os.urandom(16).hex() # Fallback local user ID

            print(f"Current User ID for data storage: {current_user_id}")

        except Exception as e:
            print(f"An unexpected error occurred during Firebase initialization: {e}")
            print("Proceeding without Firebase functionality. Document upload/retrieval/feedback will not work.")
            db = None
            current_user_id = "local_user_" + os.urandom(16).hex() # Fallback local user ID

    elif DATABASE_TYPE == 'SQLITE':
        try:
            db = sqlite3.connect(SQLITE_DB_FILE)
            cursor = db.cursor()
            # Create documents table if it doesn't exist
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS documents (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            # Create feedback table if it doesn't exist
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS feedback (
                    id TEXT PRIMARY KEY,
                    prompt_phrase TEXT NOT NULL,
                    generated_reply TEXT NOT NULL,
                    gematria_method TEXT NOT NULL,
                    feedback_type TEXT NOT NULL,
                    reply_type TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            db.commit()
            print(f"SQLite database '{SQLITE_DB_FILE}' initialized successfully.")
            current_user_id = "sqlite_user" # A fixed user ID for SQLite mode
            print(f"Current User ID for data storage (SQLite): {current_user_id}")
        except Exception as e:
            print(f"Error initializing SQLite database: {e}")
            db = None
            current_user_id = "local_user_" + os.urandom(16).hex() # Fallback local user ID
            print("Proceeding without database functionality.")
    else:
        print(f"Error: Unknown DATABASE_TYPE '{DATABASE_TYPE}'. Please set to 'FIRESTORE' or 'SQLITE'.")
        db = None
        current_user_id = "local_user_" + os.urandom(16).hex() # Fallback local user ID
        print("Proceeding without database functionality.")

    # Populate the word matrix and lookup on startup ONLY IF DB IS INITIALIZED
    if db:
        get_all_words_from_uploaded_documents()
    else:
        print("Skipping word matrix build as no database is available.")
    
    # Always load English dictionary for fallback
    load_english_dictionary()


# --- Gematria Helper Data ---

JEWISH_GEMATRIA_MAP = {
    'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 8, 'I': 9,
    'J': 10, 'K': 20, 'L': 30, 'M': 40, 'N': 50, 'O': 60, 'P': 70, 'Q': 80, 'R': 90,
    'S': 100, 'T': 200, 'U': 300, 'V': 400, 'W': 500, 'X': 600, 'Y': 700, 'Z': 800
}

QWERTY_MAP = {
    'Q': 1, 'W': 2, 'E': 3, 'R': 4, 'T': 5, 'Y': 6, 'U': 7, 'I': 8, 'O': 9, 'P': 10,
    'A': 11, 'S': 12, 'D': 13, 'F': 14, 'G': 15, 'H': 16, 'J': 17, 'K': 18, 'L': 19,
    'Z': 20, 'X': 21, 'C': 22, 'V': 23, 'B': 24, 'N': 25, 'M': 26
}

LEFT_HAND_KEYS = set('QWERTYASDFGHZXCVB')
RIGHT_HAND_KEYS = set('UIOPJKLMN')

LOVE_WORDS = {"love", "heart", "peace", "joy", "harmony", "soul", "empathy", "care"}

FREQUENT_LETTERS_WEIGHTS = {
    'E': 12, 'T': 9, 'A': 8, 'O': 7.5, 'I': 7, 'N': 6.5, 'S': 6, 'H': 6, 'R': 5.5,
    'D': 4, 'L': 4, 'U': 2.7, 'C': 2.5, 'M': 2.4, 'W': 2.3, 'F': 2.2, 'G': 2,
    'Y': 2, 'P': 1.9, 'B': 1.6, 'V': 1, 'K': 0.8, 'J': 0.15, 'X': 0.15, 'Q': 0.1, 'Z': 0.07
}

LEET_SUB_LETTERS = set('IEASTBO')

SIMPLE_FORMS_MAP = {
    "you": "u", "for": "4", "are": "r", "and": "&", "to": "2", "be": "b", "great": "gr8"
}

AAVE_RELATED_WORDS = {"finna", "bouta", "ain't", "gon'"}

# --- Gematria Calculation Functions ---

def simple(word):
    word = word.upper()
    return sum(ord(char) - ord('A') + 1 for char in word if 'A' <= char <= 'Z')

def jewish_gematria(word):
    word = word.upper()
    return sum(JEWISH_GEMATRIA_MAP.get(char, 0) for char in word if char in JEWISH_GEMATRIA_MAP)

def qwerty(word):
    word = word.upper()
    return sum(QWERTY_MAP.get(char, 0) for char in word if char in QWERTY_MAP)

def left_hand_qwerty(word):
    word = word.upper()
    return sum(QWERTY_MAP.get(char, 0) for char in word if char in LEFT_HAND_KEYS and char in QWERTY_MAP)

def right_hand_qwerty(word):
    word = word.upper()
    return sum(QWERTY_MAP.get(char, 0) for char in word if char in RIGHT_HAND_KEYS and char in QWERTY_MAP)

def binary_sum(word):
    total_ones = 0
    for char in word:
        total_ones += bin(ord(char)).count('1')
    return total_ones

def love_resonance(word):
    return 1 if word.lower() in LOVE_WORDS else 0

def frequent_letters(word):
    word = word.upper()
    return sum(FREQUENT_LETTERS_WEIGHTS.get(char, 0) for char in word if char in FREQUENT_LETTERS_WEIGHTS)

def leet_code(word):
    filtered_word = "".join(char for char in word.upper() if char not in LEET_SUB_LETTERS)
    return simple(filtered_word)

def simple_forms(word):
    processed_word = word.lower()
    for original, substitute in SIMPLE_FORMS_MAP.items():
        processed_word = processed_word.replace(original, substitute)
    return simple(processed_word)

def is_prime(num):
    if not isinstance(num, (int, float)):
        return False
    num = int(round(num)) # Round to nearest integer for prime check
    if num < 2:
        return False
    for i in range(2, int(math.sqrt(num)) + 1): # Corrected line
        if num % i == 0:
            return False
    return True

def is_perfect_square(num):
    if not isinstance(num, (int, float)):
        return False
    num = int(round(num)) # Round to nearest integer for square root check
    if num < 0:
        return False
    if num == 0:
        return True
    sqrt = math.sqrt(num)
    return sqrt == math.floor(sqrt)

def prime_gematria(word):
    val = simple(word)
    return val if is_prime(val) else 0

def ambidextrous_balance(word):
    right_val = right_hand_qwerty(word)
    left_val = left_hand_qwerty(word)
    return right_val - (-left_val)

def aave_simple(word):
    return simple(word)

def aave_reduced(word):
    val = aave_simple(word)
    if val in (11, 22):
        return val
    while val > 9:
        val = sum(int(digit) for digit in str(val))
    return val

def aave_spiral(input_string):
    GOLDEN_ANGLE_RAD = math.radians(137.5)
    total_weighted_value = 0.0
    processed_input = str(input_string).upper()

    for i, char in enumerate(processed_input):
        simple_val = 0
        if char.isdigit():
            simple_val = int(char)
        elif 'A' <= char <= 'Z':
            simple_val = ord(char) - ord('A') + 1

        weight = math.cos(i * GOLDEN_ANGLE_RAD)
        total_weighted_value += simple_val * weight

    scaled_value = math.log1p(abs(total_weighted_value))
    return scaled_value

def grok_resonance_score(word):
    val_simple = aave_simple(word)
    val_reduced = aave_reduced(word)
    val_spiral = aave_spiral(word)
    avg_score = (val_simple + val_reduced + val_spiral) / 3
    if word.lower() in AAVE_RELATED_WORDS:
        avg_score *= 1.1
    return avg_score

# New Gematria Method: Whole Sentence Gematria
def whole_sentence_gematria(sentence):
    """
    Calculates the simple gematria of the entire sentence as one continuous string,
    ignoring spaces and punctuation.
    """
    cleaned_sentence = re.sub(r'[^a-zA-Z]', '', sentence).upper()
    return simple(cleaned_sentence)

# --- Document Processing and Database Interaction Functions ---

def extract_words_from_markdown(markdown_content):
    """
    Extracts words from markdown content, stripping formatting and punctuation.
    Filters words to include only those with at least 4 alphabetic characters.
    """
    # Remove common markdown formatting
    content = re.sub(r'(\*\*|__|~~|`|\*|_)', '', markdown_content) # Bold, italic, strikethrough, code
    content = re.sub(r'#+\s*', '', content) # Headers
    content = re.sub(r'\[.*?\]\(.*?\)', '', content) # Links
    content = re.sub(r'^\s*[-*+]\s+', '', content, flags=re.MULTILINE) # List items
    content = re.sub(r'---+', '', content) # Horizontal rules

    # Find all alphabetic words and filter by length (at least 4 characters)
    words = [word for word in re.findall(r'[a-zA-Z]+', content.lower()) if len(word) >= 4]
    return words

def _firestore_upload_document(file_path):
    """ Firestore specific upload """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            markdown_content = f.read()

        file_name = os.path.basename(file_path)
        doc_ref = db.collection('artifacts').document(APP_ID).collection('users').document(current_user_id).collection('documents').document(file_name)

        doc_ref.set({
            'name': file_name,
            'content': markdown_content,
            'timestamp': firestore.SERVER_TIMESTAMP
        })
        print(f"Document '{file_name}' uploaded successfully to Firestore.")
        return True
    except FileNotFoundError:
        print(f"Error: File not found at '{file_path}'")
        return False
    except Exception as e:
        print(f"Error uploading document to Firestore: {e}")
        return False

def _sqlite_upload_document(file_path):
    """ SQLite specific upload """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            markdown_content = f.read()

        file_name = os.path.basename(file_path)
        cursor = db.cursor()
        cursor.execute("INSERT OR REPLACE INTO documents (id, name, content) VALUES (?, ?, ?)",
                       (file_name, file_name, markdown_content))
        db.commit()
        print(f"Document '{file_name}' uploaded successfully to SQLite.")
        return True
    except FileNotFoundError:
        print(f"Error: File not found at '{file_path}'")
        return False
    except Exception as e:
        print(f"Error uploading document to SQLite: {e}")
        return False

def upload_markdown_document(file_path):
    if not db:
        print("Database not initialized. Cannot upload document.")
        return False
    
    if DATABASE_TYPE == 'FIRESTORE':
        return _firestore_upload_document(file_path)
    elif DATABASE_TYPE == 'SQLITE':
        return _sqlite_upload_document(file_path)
    return False


def upload_multiple_markdown_documents(directory_path):
    """
    Uploads all markdown files from a given directory and its subdirectories.
    """
    if not db:
        print("Database not initialized. Cannot upload documents.")
        return False

    if not os.path.isdir(directory_path):
        print(f"Error: Directory '{directory_path}' not found.")
        return False

    uploaded_count = 0
    for root, _, files in os.walk(directory_path):
        for file_name in files:
            if file_name.endswith('.md'):
                file_path = os.path.join(root, file_name)
                if upload_markdown_document(file_path):
                    uploaded_count += 1
    print(f"Finished uploading. {uploaded_count} Markdown documents uploaded from '{directory_path}' and its subdirectories.")
    get_all_words_from_uploaded_documents() # Refresh word matrix after upload
    return True

def _firestore_get_user_documents():
    """ Firestore specific get documents """
    try:
        docs_ref = db.collection('artifacts').document(APP_ID).collection('users').document(current_user_id).collection('documents')
        docs = docs_ref.stream()
        document_list = []
        for doc in docs:
            document_list.append(doc.id)
        return document_list
    except Exception as e:
        print(f"Error retrieving documents from Firestore: {e}")
        return []

def _sqlite_get_user_documents():
    """ SQLite specific get documents """
    try:
        cursor = db.cursor()
        cursor.execute("SELECT name FROM documents")
        document_list = [row[0] for row in cursor.fetchall()]
        return document_list
    except Exception as e:
        print(f"Error retrieving documents from SQLite: {e}")
        return []

def get_user_documents():
    if not db:
        print("Database not initialized. Cannot retrieve documents.")
        return []
    
    if DATABASE_TYPE == 'FIRESTORE':
        return _firestore_get_user_documents()
    elif DATABASE_TYPE == 'SQLITE':
        return _sqlite_get_user_documents()
    return []

def _firestore_get_document_content(doc_name):
    """ Firestore specific get content """
    try:
        doc_ref = db.collection('artifacts').document(APP_ID).collection('users').document(current_user_id).collection('documents').document(doc_name)
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict().get('content')
        else:
            print(f"Document '{doc_name}' not found in Firestore.")
            return None
    except Exception as e:
        print(f"Error fetching document content from Firestore: {e}")
        return None

def _sqlite_get_document_content(doc_name):
    """ SQLite specific get content """
    try:
        cursor = db.cursor()
        cursor.execute("SELECT content FROM documents WHERE name = ?", (doc_name,))
        result = cursor.fetchone()
        if result:
            return result[0]
        else:
            print(f"Document '{doc_name}' not found in SQLite.")
            return None
    except Exception as e:
        print(f"Error fetching document content from SQLite: {e}")
        return None

def get_document_content(doc_name):
    if not db:
        print("Database not initialized. Cannot retrieve document content.")
        return None
    
    if DATABASE_TYPE == 'FIRESTORE':
        return _firestore_get_document_content(doc_name)
    elif DATABASE_TYPE == 'SQLITE':
        return _sqlite_get_document_content(doc_name)
    return []

def get_all_words_from_uploaded_documents():
    """
    Fetches content from all user documents, extracts words, and populates
    the global word_matrix and simple_gematria_word_lookup.
    """
    global word_matrix, simple_gematria_word_lookup
    if db is None:
        print("Database client is not initialized. Cannot build word matrix.")
        word_matrix = []
        simple_gematria_word_lookup = {}
        return

    all_extracted_words = set()
    temp_simple_gematria_lookup = {}

    try:
        document_names = get_user_documents() # Use the generic getter
        for doc_name in document_names:
            content = get_document_content(doc_name) # Use the generic getter
            if content:
                extracted_words = extract_words_from_markdown(content) # Now filters by length
                for word in extracted_words:
                    all_extracted_words.add(word)

        word_matrix = list(all_extracted_words)

        for word in word_matrix:
            s_val = simple(word)
            s_val_rounded = int(round(s_val))
            if s_val_rounded not in temp_simple_gematria_lookup:
                temp_simple_gematria_lookup[s_val_rounded] = []
            temp_simple_gematria_lookup[s_val_rounded].append(word)

        simple_gematria_word_lookup = temp_simple_gematria_lookup
        print(f"Word matrix built with {len(word_matrix)} unique words from uploaded documents.")
    except Exception as e:
        print(f"Error building word matrix from database documents: {e}")
        word_matrix = []
        simple_gematria_word_lookup = {}

def load_english_dictionary():
    """
    Loads a small, hardcoded English dictionary for fallback.
    Filters words to include only those with at least 4 alphabetic characters.
    """
    global english_gematria_word_lookup
    english_words = [
        "the", "be", "to", "of", "and", "a", "in", "that", "have", "i",
        "it", "for", "not", "on", "with", "he", "as", "you", "do", "at",
        "this", "but", "his", "by", "from", "they", "we", "say", "her", "she",
        "or", "an", "will", "my", "one", "all", "would", "there", "their", "what",
        "so", "up", "out", "if", "about", "who", "get", "which", "go", "me",
        "when", "make", "can", "like", "time", "no", "just", "him", "know", "take",
        "person", "into", "year", "your", "good", "some", "could", "them", "see", "other",
        "than", "then", "now", "look", "only", "come", "its", "over", "think", "also",
        "back", "after", "use", "two", "how", "our", "work", "first", "well", "way",
        "even", "new", "want", "because", "any", "these", "give", "day", "most", "us",
        "love", "light", "truth", "spirit", "wisdom", "peace", "joy", "faith", "hope", "grace",
        "divine", "soul", "heart", "mind", "power", "glory", "heaven", "earth", "creation", "beginning",
        "father", "son", "holy", "word", "life", "eternal", "bless", "amen", "gospel", "christ"
    ]
    
    # Filter words by length here (at least 4 characters)
    filtered_english_words = [word for word in english_words if len(word) >= 4]

    temp_english_lookup = {}
    for word in set(filtered_english_words): # Use set to ensure uniqueness
        s_val = simple(word)
        s_val_rounded = int(round(s_val))
        if s_val_rounded not in temp_english_lookup:
            temp_english_lookup[s_val_rounded] = []
        temp_english_lookup[s_val_rounded].append(word)
    
    english_gematria_word_lookup = temp_english_lookup
    print(f"English dictionary loaded with {len(english_gematria_word_lookup)} unique simple gematria values (filtered by length).")


def _firestore_store_feedback(prompt_phrase, generated_reply, method_used, feedback_type, reply_type):
    """ Firestore specific store feedback """
    try:
        feedback_id = str(uuid.uuid4())
        feedback_doc_ref = db.collection('artifacts').document(APP_ID).collection('users').document(current_user_id).collection('feedback').document(feedback_id)

        feedback_doc_ref.set({
            'prompt_phrase': prompt_phrase,
            'generated_reply': generated_reply,
            'gematria_method': method_used,
            'feedback_type': feedback_type,
            'reply_type': reply_type,
            'timestamp': firestore.SERVER_TIMESTAMP
        })
        print(f"Feedback '{feedback_type}' for '{reply_type}' stored successfully to Firestore.")
        return True
    except Exception as e:
        print(f"Error storing feedback to Firestore: {e}")
        return False

def _sqlite_store_feedback(prompt_phrase, generated_reply, method_used, feedback_type, reply_type):
    """ SQLite specific store feedback """
    try:
        feedback_id = str(uuid.uuid4())
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO feedback (id, prompt_phrase, generated_reply, gematria_method, feedback_type, reply_type) VALUES (?, ?, ?, ?, ?, ?)",
            (feedback_id, prompt_phrase, generated_reply, method_used, feedback_type, reply_type)
        )
        db.commit()
        print(f"Feedback '{feedback_type}' for '{reply_type}' stored successfully to SQLite.")
        return True
    except Exception as e:
        print(f"Error storing feedback to SQLite: {e}")
        return False

def store_feedback(prompt_phrase, generated_reply, method_used, feedback_type, reply_type):
    if not db:
        print("Database not initialized. Cannot store feedback.")
        return False
    
    if DATABASE_TYPE == 'FIRESTORE':
        return _firestore_store_feedback(prompt_phrase, generated_reply, method_used, feedback_type, reply_type)
    elif DATABASE_TYPE == 'SQLITE':
        return _sqlite_store_feedback(prompt_phrase, generated_reply, method_used, feedback_type, reply_type)
    return False


# --- Main Gematria Calculation Logic ---

def process_words_for_gematria(words_or_sentence, method_name):
    """
    Calculates gematria for each word (or the whole sentence) and returns values,
    total sum, and properties.
    'words_or_sentence' can be a list of words or a single string (for whole_sentence_gematria).
    """
    gematria_values = []
    available_methods = {
        "simple": simple,
        "jewish_gematria": jewish_gematria,
        "qwerty": qwerty,
        "left_hand_qwerty": left_hand_qwerty,
        "right_hand_qwerty": right_hand_qwerty,
        "binary_sum": binary_sum,
        "love_resonance": love_resonance,
        "frequent_letters": frequent_letters,
        "leet_code": leet_code,
        "simple_forms": simple_forms,
        "prime_gematria": prime_gematria,
        "ambidextrous_balance": ambidextrous_balance,
        "aave_simple": aave_simple,
        "aave_reduced": aave_reduced,
        "aave_spiral": aave_spiral,
        "grok_resonance_score": grok_resonance_score,
        "whole_sentence_gematria": whole_sentence_gematria # New method
    }

    method = available_methods.get(method_name)
    if not method:
        return [], None, None, [], "Error: Gematria method not found."

    if method_name == "whole_sentence_gematria":
        # For whole_sentence_gematria, the input is the entire sentence string
        # and the result is a single value. We wrap it in a list for consistency.
        gematria_values = [method(words_or_sentence)]
        # For display purposes, the "words" will just be the original sentence
        words_for_display = [words_or_sentence]
    else:
        # For other methods, input is expected to be a list of words
        for word in words_or_sentence:
            gematria_values.append(method(word))
        words_for_display = words_or_sentence

    total_gematria_sum = sum(gematria_values)

    # Calculate properties for total sum
    sum_properties = {
        "is_prime": is_prime(total_gematria_sum),
        "is_perfect_square": is_perfect_square(total_gematria_sum),
        "spiral_resonance": aave_spiral(str(total_gematria_sum))
    }

    return gematria_values, total_gematria_sum, sum_properties, words_for_display, None # Added words_for_display

def calculate_gaps(values):
    """
    Calculates the absolute gaps between consecutive values in a list.
    """
    gaps = []
    if len(values) < 2:
        return gaps
    for i in range(len(values) - 1):
        gaps.append(abs(values[i+1] - values[i]))
    return gaps

def display_results(words, gematria_values, total_sum, sum_properties, gaps, method_name):
    """
    Prints the gematria results to the console.
    """
    print(f"\n--- Results for Method: '{method_name}' ---")

    print("\n--- Total Sentence Gematria Summary ---")
    print(f"Total Sum: {total_sum:.2f}")
    print(f"Prime Resonance: {'✨ YES! ✨' if sum_properties['is_prime'] else 'No'} (Rounded: {int(round(total_sum))})")
    print(f"Clean Root: {'📐 YES! 📐' if sum_properties['is_perfect_square'] else 'No'} (Rounded: {int(round(total_sum))})")
    if sum_properties['is_perfect_square']:
        print(f"  Square Root: {int(math.sqrt(round(total_sum)))}")
    print(f"Spiral Resonance of Total Sum: {sum_properties['spiral_resonance']:.4f}")
    print(f"Assigned Color: {get_gematria_color(total_sum)}")
    print(f"Inverse Color: {get_inverse_color(get_gematria_color(total_sum))}")


    print("\n--- Word Gematria Values ---")
    # Adjust header for whole_sentence_gematria
    if method_name == "whole_sentence_gematria":
        # For whole_sentence_gematria, the `words` parameter here is the full sentence string.
        # We need to extract individual words for the "Word Gematria Values" section.
        individual_words_for_display = re.findall(r'[a-zA-Z]+', words[0].lower())
        
        print(f"{'Word':<20} {'Value':<10} {'Prime?':<10} {'Clean Root?':<15} {'Color':<10} {'Inverse Color':<15}")
        print("-" * 80)
        for word_item in individual_words_for_display:
            # For this table, we'll use simple gematria for each word for consistency
            value = simple(word_item) 
            value_display = f"{value:.2f}" if isinstance(value, float) else str(value)
            is_word_prime = is_prime(value)
            is_word_perfect_square = is_perfect_square(value)
            word_color = get_gematria_color(value)
            word_inverse_color = get_inverse_color(word_color)
            print(f"{word_item:<20} {value_display:<10} {('Yes' if is_word_prime else 'No'):<10} {('Yes' if is_word_perfect_square else 'No'):<15} {word_color:<10} {word_inverse_color:<15}")
    else:
        print(f"{'Word':<20} {'Value':<10} {'Prime?':<10} {'Clean Root?':<15} {'Color':<10} {'Inverse Color':<15}")
        print("-" * 80)
        for i, word in enumerate(words):
            value = gematria_values[i]
            value_display = f"{value:.2f}" if isinstance(value, float) else str(value)
            is_word_prime = is_prime(value)
            is_word_perfect_square = is_perfect_square(value)
            word_color = get_gematria_color(value)
            word_inverse_color = get_inverse_color(word_color)
            print(f"{word:<20} {value_display:<10} {('Yes' if is_word_prime else 'No'):<10} {('Yes' if is_word_perfect_square else 'No'):<15} {word_color:<10} {word_inverse_color:<15}")

    if method_name != "whole_sentence_gematria": # Gaps only make sense for multiple words
        print("\n--- Gaps Between Consecutive Gematria Values ---")
        if gaps:
            print(f"{'Gap Between':<30} {'Gap Value':<15}")
            print("-" * 45)
            for i, gap in enumerate(gaps):
                word1 = words[i]
                word2 = words[i + 1]
                gap_display = f"{gap:.2f}" if isinstance(gap, float) else str(gap)
                print(f"{word1} to {word2:<20} {gap_display:<15}")
        else:
            print("Not enough words to calculate gaps.")
    else:
        print("\nGaps are not applicable for 'Whole Sentence Gematria' directly, but are used for reply generation based on individual words.")
        # The individual word analysis section below already covers the detailed breakdown.

    # --- Words Grouped by Color ---
    # This grouping is based on simple gematria values for consistency.
    if method_name == "whole_sentence_gematria":
        words_to_group = re.findall(r'[a-zA-Z]+', words[0].lower()) # Extract words from the full sentence
    else:
        words_to_group = words # For other methods, 'words' already contains the processed words

    if words_to_group:
        color_groups = {color: [] for color in GEMATRIA_COLORS}
        for word in words_to_group:
            val = simple(word) # Use simple gematria for consistent color mapping across all methods
            color = get_gematria_color(val)
            if color in color_groups:
                color_groups[color].append(word)
        
        print("\n--- Words Grouped by Color ---")
        print("Words are grouped by the color derived from their Simple Gematria value.")
        for color, word_list in color_groups.items():
            if word_list:
                print(f"  {color}: {', '.join(sorted(list(set(word_list))))}") # Sort and unique for cleaner output
        print("-" * 60)

    print("-" * 60)

def get_sequential_phrases(input_string):
    """
    Parses an input string. If it contains '+', it splits by '+'.
    Otherwise, it splits the string into individual alphabetic words.
    Returns a list of individual segments/words.
    """
    if '+' in input_string:
        raw_segments = [s.strip() for s in input_string.split('+')]
        cleaned_segments = []
        for segment in raw_segments:
            words_in_segment = re.findall(r'[a-zA-Z]+', segment.lower())
            if words_in_segment:
                cleaned_segments.append(" ".join(words_in_segment))
    else:
        # If no '+', treat the entire string as a single phrase to be broken into words
        cleaned_segments = re.findall(r'[a-zA-Z]+', input_string.lower())

    if not cleaned_segments:
        return []

    phrases = []
    # Add individual segments/words
    phrases.extend(cleaned_segments)

    # If there are multiple segments/words, also add sequential two-segment combinations
    # This part is primarily for when the user explicitly uses '+' to define segments.
    # For automatic word splitting, we generally don't create combinations like "word1 word2"
    # unless specifically requested for a different type of analysis.
    if len(cleaned_segments) > 1 and '+' in input_string:
        for i in range(len(cleaned_segments) - 1):
            combined_phrase = f"{cleaned_segments[i]} {cleaned_segments[i+1]}"
            phrases.append(combined_phrase)
    
    # Ensure uniqueness and order (optional, but good for consistent output)
    seen = set()
    unique_phrases = []
    for p in phrases:
        if p not in seen:
            unique_phrases.append(p)
            seen.add(p)
    return unique_phrases


def generate_reply_from_gaps(prompt_phrase, method_name):
    """
    Generates a reply by finding words from the word matrix whose simple gematria
    values match the gaps of the prompt phrase. Returns None if no words can be matched.
    """
    if not word_matrix and not english_gematria_word_lookup:
        return None # Cannot generate reply without any word sources

    # Always split into individual words for reply generation, and filter by length
    prompt_words = [word for word in re.findall(r'[a-zA-Z]+', prompt_phrase.lower()) if len(word) >= 4]
    if not prompt_words or len(prompt_words) < 2: # Need at least two words for gaps
        return None

    # Calculate gematria values for these individual words using the specified method
    gematria_values_for_words = []
    available_methods = {
        "simple": simple,
        "jewish_gematria": jewish_gematria,
        "qwerty": qwerty,
        "left_hand_qwerty": left_hand_qwerty,
        "right_hand_qwerty": right_hand_qwerty,
        "binary_sum": binary_sum,
        "love_resonance": love_resonance,
        "frequent_letters": frequent_letters,
        "leet_code": leet_code,
        "simple_forms": simple_forms,
        "prime_gematria": prime_gematria,
        "ambidextrous_balance": ambidextrous_balance,
        "aave_simple": aave_simple,
        "aave_reduced": aave_reduced,
        "aave_spiral": aave_spiral,
        "grok_resonance_score": grok_resonance_score,
    }
    method_func = available_methods.get(method_name)
    if not method_func:
        return None

    for word in prompt_words:
        gematria_values_for_words.append(method_func(word))

    gaps = calculate_gaps(gematria_values_for_words)

    if not gaps:
        return None # No gaps to calculate if less than 2 words

    generated_reply_words = []
    for gap_value in gaps:
        rounded_gap = int(round(gap_value))
        
        chosen_word = None

        # Try user's uploaded documents first
        matching_words_user = simple_gematria_word_lookup.get(rounded_gap)
        if matching_words_user:
            chosen_word = random.choice(matching_words_user)
        else:
            # Fallback to English dictionary
            matching_words_english = english_gematria_word_lookup.get(rounded_gap)
            if matching_words_english:
                chosen_word = random.choice(matching_words_english)
            
        if chosen_word:
            generated_reply_words.append(chosen_word)
        else:
            # If no match for a gap, this reply cannot be fully formed.
            return None 

    return " ".join(generated_reply_words)

def generate_reply_from_equal_resonances(prompt_phrase, method_name):
    """
    Generates a reply by finding words from the word matrix whose simple gematria
    values match the gematria values of the prompt phrase's words. Returns None if no words can be matched.
    """
    if not word_matrix and not english_gematria_word_lookup:
        return None # Cannot generate reply without any word sources

    # Always split into individual words for reply generation, and filter by length
    prompt_words = [word for word in re.findall(r'[a-zA-Z]+', prompt_phrase.lower()) if len(word) >= 4]
    if not prompt_words:
        return None

    # Calculate gematria values for these individual words using the specified method
    gematria_values_for_words = []
    available_methods = {
        "simple": simple,
        "jewish_gematria": jewish_gematria,
        "qwerty": qwerty,
        "left_hand_qwerty": left_hand_qwerty,
        "right_hand_qwerty": right_hand_qwerty,
        "binary_sum": binary_sum,
        "love_resonance": love_resonance,
        "frequent_letters": frequent_letters,
        "leet_code": leet_code,
        "simple_forms": simple_forms,
        "prime_gematria": prime_gematria,
        "ambidextrous_balance": ambidextrous_balance,
        "aave_simple": aave_simple,
        "aave_reduced": aave_reduced,
        "aave_spiral": aave_spiral,
        "grok_resonance_score": grok_resonance_score,
    }
    method_func = available_methods.get(method_name)
    if not method_func:
        return None

    for word in prompt_words:
        gematria_values_for_words.append(method_func(word))

    generated_reply_words = []
    for prompt_word_value in gematria_values_for_words:
        rounded_value = int(round(prompt_word_value))
        
        chosen_word = None

        # Try user's uploaded documents first
        matching_words_user = simple_gematria_word_lookup.get(rounded_value)
        if matching_words_user:
            chosen_word = random.choice(matching_words_user)
        else:
            # Fallback to English dictionary
            matching_words_english = english_gematria_word_lookup.get(rounded_value)
            if matching_words_english:
                chosen_word = random.choice(matching_words_english)

        if chosen_word:
            generated_reply_words.append(chosen_word)
        else:
            # If no match for a word, this reply cannot be fully formed.
            return None

    return " ".join(generated_reply_words)


def generate_all_replies_for_prompt(prompt_phrase):
    """
    Generates both gap-based and equal-resonance replies for all applicable gematria methods.
    Only displays replies that are successfully generated (i.e., not None).
    """
    global last_generated_reply_info
    last_generated_reply_info = {
        'prompt_phrase': prompt_phrase,
        'replies_by_method': {}
    }

    # Exclude 'whole_sentence_gematria' as it's not suitable for gap/equal resonance per-segment analysis
    applicable_methods = [m for m in methods_list if m != "whole_sentence_gematria"]

    print(f"\n--- Generating ALL Potential Replies for: '{prompt_phrase}' ---")
    
    any_replies_generated = False

    for method_name in applicable_methods:
        gap_reply = generate_reply_from_gaps(prompt_phrase, method_name)
        equal_resonance_reply = generate_reply_from_equal_resonances(prompt_phrase, method_name)

        current_method_replies = {}
        if gap_reply:
            current_method_replies['gap_reply'] = gap_reply
        if equal_resonance_reply:
            current_method_replies['equal_resonance_reply'] = equal_resonance_reply
        
        if current_method_replies:
            last_generated_reply_info['replies_by_method'][method_name] = current_method_replies
            print(f"\n--- Potential Sentences for {method_name.replace('_', ' ').title()} ---")
            if 'gap_reply' in current_method_replies:
                print(f"  Gap-Based Reply: \"{current_method_replies['gap_reply']}\"")
                any_replies_generated = True
            if 'equal_resonance_reply' in current_method_replies:
                print(f"  Equal-Resonance Reply: \"{current_method_replies['equal_resonance_reply']}\"")
                any_replies_generated = True
    
    print("\n" + "-" * 40) # Separator for final summary

    if any_replies_generated:
        print("All Reply Generation Complete. You can now provide feedback on these replies using option 6.")
    else:
        print("No complete replies could be generated across any method for the given prompt.")


# --- Main CLI Application ---

def main():
    initialize_database()

    print("Welcome to the Gematria Calculator (Python CLI with Database)!")
    print(f"Your current user ID: {current_user_id}")
    print(f"Initial Word Matrix size: {len(word_matrix)}")
    print(f"English Dictionary Lookup size: {len(english_gematria_word_lookup)}")


    while True:
        print("\n--- Main Menu ---")
        print("1. Enter a sentence directly for Gematria calculation")
        print("2. Upload Markdown documents from a directory")
        print("3. Select a previously uploaded Markdown document for Gematria calculation")
        print("4. List all uploaded documents")
        print("5. Generate Replies based on Prompt Analysis (from uploaded documents)")
        print("6. Provide Feedback on Last Generated Reply")
        print("7. Exit")

        choice = input("Enter your choice (1-7): ").strip()

        input_for_gematria_calc = None # Will hold either a list of words or a single sentence string
        words_for_display = [] # Will hold the words/segments for display in results
        source_type = ""
        selected_method_name = ""

        if choice == '1':
            sentence = input("Enter the sentence: ").strip()
            if not sentence:
                print("Sentence cannot be empty.")
                continue
            
            print("\nAvailable Gematria Methods:")
            for i, m in enumerate(methods_list):
                print(f"{i+1}. {m}")
            method_choice_index = input(f"Enter the number of the gematria method to use (1-{len(methods_list)}): ").strip()
            try:
                method_choice_index = int(method_choice_index) - 1
                if 0 <= method_choice_index < len(methods_list):
                    selected_method_name = methods_list[method_choice_index]
                else:
                    print("Invalid method number.")
                    continue
            except ValueError:
                print("Invalid input. Please enter a number.")
                continue

            if selected_method_name == "whole_sentence_gematria":
                input_for_gematria_calc = sentence # Pass the whole sentence string
                words_for_display = [sentence] # For display, treat as one item
            else:
                input_for_gematria_calc = [word for word in re.findall(r'[a-zA-Z]+', sentence.lower()) if len(word) >= 4] # Filter words here
                words_for_display = input_for_gematria_calc # For display, use extracted words
            source_type = "direct sentence"

            if input_for_gematria_calc:
                gematria_values, total_sum, sum_properties, words_for_display_final, error_message = \
                    process_words_for_gematria(input_for_gematria_calc, selected_method_name)

                if error_message:
                    print(error_message)
                elif not gematria_values:
                    print("No valid words/sentence found for gematria calculation after processing.")
                else:
                    gaps = calculate_gaps(gematria_values)
                    display_results(words_for_display_final, gematria_values, total_sum, sum_properties, gaps, selected_method_name)
                    
                    # Ask to generate replies based on this input
                    # For whole_sentence_gematria, we now always offer to generate replies based on its individual words
                    individual_words_for_reply_prompt = [word for word in re.findall(r'[a-zA-Z]+', sentence.lower()) if len(word) >= 4] # Filter words here
                    if len(individual_words_for_reply_prompt) > 1:
                        generate_all_q = input("\nGenerate replies for all applicable gematria methods based on the individual words of this sentence? (yes/no): ").strip().lower()
                        if generate_all_q == 'yes':
                            generate_all_replies_for_prompt(sentence) # Pass the full sentence for parsing
            continue # Go back to main menu after processing

        elif choice == '2':
            directory_path = input("Enter the path to the directory containing Markdown files: ").strip()
            if upload_multiple_markdown_documents(directory_path):
                print(f"Current Word Matrix size: {len(word_matrix)}")
                generate_all_q = input("\nGenerate replies for all applicable gematria methods using a random sample from the entire word matrix as a prompt? (yes/no): ").strip().lower()
                if generate_all_q == 'yes':
                    # Create a prompt from a random sample of words from the matrix
                    if word_matrix:
                        sample_size = min(10, len(word_matrix)) # Take up to 10 words
                        random_prompt_words = random.sample(word_matrix, sample_size)
                        random_prompt = " + ".join(random_prompt_words)
                        print(f"\nUsing a random prompt from your matrix: '{random_prompt}'")
                        generate_all_replies_for_prompt(random_prompt)
                    else:
                        print("Word matrix is empty, cannot generate random prompt.")
            continue # Go back to main menu after upload
        elif choice == '3':
            documents = get_user_documents()
            if not documents:
                print("No documents found. Please upload one first.")
                continue
            print("\nAvailable Documents:")
            for i, doc_name in enumerate(documents):
                print(f"{i+1}. {doc_name}")
            doc_index = input("Enter the number of the document to select: ").strip()
            try:
                doc_index = int(doc_index) - 1
                if 0 <= doc_index < len(documents):
                    selected_doc_name = documents[doc_index]
                    content = get_document_content(selected_doc_name)
                    if content:
                        print("\nAvailable Gematria Methods:")
                        for i, m in enumerate(methods_list):
                            print(f"{i+1}. {m}")
                        method_choice_index = input(f"Enter the number of the gematria method to use (1-{len(methods_list)}): ").strip()
                        try:
                            method_choice_index = int(method_choice_index) - 1
                            if 0 <= method_choice_index < len(methods_list):
                                selected_method_name = methods_list[method_choice_index]
                            else:
                                print("Invalid method number.")
                                continue
                        except ValueError:
                            print("Invalid input. Please enter a number.")
                            continue

                        if selected_method_name == "whole_sentence_gematria":
                            input_for_gematria_calc = content # Pass the whole document content as a single string
                            words_for_display = [content[:50] + "..." if len(content) > 50 else content] # Truncate for display
                        else:
                            input_for_gematria_calc = [word for word in extract_words_from_markdown(content) if len(word) >= 4] # Filter words here
                            words_for_display = input_for_gematria_calc
                        source_type = f"selected document: {selected_doc_name}"

                        if input_for_gematria_calc:
                            gematria_values, total_sum, sum_properties, words_for_display_final, error_message = \
                                process_words_for_gematria(input_for_gematria_calc, selected_method_name)

                            if error_message:
                                print(error_message)
                            elif not gematria_values:
                                print("No valid words/sentence found for gematria calculation after processing.")
                            else:
                                gaps = calculate_gaps(gematria_values)
                                display_results(words_for_display_final, gematria_values, total_sum, sum_properties, gaps, selected_method_name)
                                
                                # Ask to generate replies based on this input
                                individual_words_for_reply_prompt = [word for word in re.findall(r'[a-zA-Z]+', content.lower()) if len(word) >= 4] # Filter words here
                                if len(individual_words_for_reply_prompt) > 1:
                                    generate_all_q = input("\nGenerate replies for all applicable gematria methods based on the individual words of this document? (yes/no): ").strip().lower()
                                    if generate_all_q == 'yes':
                                        generate_all_replies_for_prompt(content) # Pass the full content for parsing
                    else:
                        print("No content found for the selected document.")
                else:
                    print("Invalid document number.")
                    continue
            except ValueError:
                print("Invalid input. Please enter a number.")
                continue
            continue # Go back to main menu after processing
        elif choice == '4':
            documents = get_user_documents()
            if not documents:
                print("No documents found.")
            else:
                print("\nYour Uploaded Documents:")
                for doc_name in documents:
                    print(f"- {doc_name}")
            continue # Go back to main menu after listing
        elif choice == '5':
            if not word_matrix and not english_gematria_word_lookup:
                print("Cannot generate reply. Word matrix and English dictionary are both empty. Please upload Markdown documents first (option 2), or ensure the English dictionary is loaded.")
                continue

            prompt_phrase = input("Enter a phrase to generate replies for (e.g., 'a + bc + d'): ").strip()
            if not prompt_phrase:
                print("Prompt phrase cannot be empty.")
                continue
            
            generate_all_replies_for_prompt(prompt_phrase)
            continue # Go back to main menu after reply generation
        elif choice == '6':
            if last_generated_reply_info and last_generated_reply_info['replies_by_method']:
                print("\n--- Provide Feedback ---")
                print(f"Last Prompt: \"{last_generated_reply_info['prompt_phrase']}\"")
                
                print("\nReplies were generated for the following methods:")
                method_keys = list(last_generated_reply_info['replies_by_method'].keys())
                for i, method_key in enumerate(method_keys):
                    print(f"{i+1}. {method_key.replace('_', ' ').title()}")
                
                method_choice_input = input(f"Enter the number of the method whose replies you want to give feedback for (1-{len(method_keys)}): ").strip()
                try:
                    method_idx = int(method_choice_input) - 1
                    if 0 <= method_idx < len(method_keys):
                        selected_method_key = method_keys[method_idx]
                        selected_method_replies = last_generated_reply_info['replies_by_method'][selected_method_key]

                        print(f"\nFeedback for Method: {selected_method_key.replace('_', ' ').title()}")
                        reply_options = []
                        if 'gap_reply' in selected_method_replies:
                            print(f"1. Gap-Based Reply: \"{selected_method_replies['gap_reply']}\"")
                            reply_options.append('gap')
                        if 'equal_resonance_reply' in selected_method_replies:
                            print(f"2. Equal-Resonance Reply: \"{selected_method_replies['equal_resonance_reply']}\"")
                            reply_options.append('equal')

                        if not reply_options:
                            print("No replies available for this method to provide feedback on.")
                            continue

                        reply_type_choice = input(f"Which reply are you providing feedback for? ({'/'.join(reply_options)}): ").strip().lower()

                        selected_reply = None
                        feedback_reply_type = None

                        if reply_type_choice == 'gap' and 'gap_reply' in selected_method_replies:
                            selected_reply = selected_method_replies['gap_reply']
                            feedback_reply_type = 'gap_reply'
                        elif reply_type_choice == 'equal' and 'equal_resonance_reply' in selected_method_replies:
                            selected_reply = selected_method_replies['equal_resonance_reply']
                            feedback_reply_type = 'equal_resonance_reply'
                        else:
                            print("Invalid reply type selected.")
                            continue

                        feedback = input("Was this a good synthesis? (up/down): ").strip().lower()
                        if feedback in ['up', 'down']:
                            store_feedback(
                                last_generated_reply_info['prompt_phrase'],
                                selected_reply,
                                selected_method_key, # Store the method used for this specific reply
                                f"thumbs_{feedback}",
                                feedback_reply_type
                            )
                        else:
                            print("Invalid feedback. Please enter 'up' or 'down'.")
                    else:
                        print("Invalid method number.")
                except ValueError:
                    print("Invalid input. Please enter a number.")
            else:
                print("No reply has been generated yet to provide feedback on.")
            continue # Go back to main menu after feedback
        elif choice == '7':
            print("Exiting Gematria Calculator. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 7.")
            continue

if __name__ == "__main__":
    main()
