import streamlit as st
import math

# --- Gematria Helper Data ---
# (Same as in the previous script - included here for self-containment)

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
# (Exactly as in the previous script)

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
    if num < 2:
        return False
    for i in range(2, int(math.sqrt(num)) + 1):
        if num % i == 0:
            return False
    return True

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

def aave_spiral(word):
    GOLDEN_ANGLE_RAD = math.radians(137.5)
    total_weighted_value = 0.0
    word_upper = word.upper()
    for i, char in enumerate(word_upper):
        if 'A' <= char <= 'Z':
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

# --- Main Script Logic (adapted for Streamlit) ---

def calculate_gematria_for_sentence(sentence, method_name):
    words = sentence.replace('-', ' ').replace('/', ' ').split()
    words = [word.strip(".,!?;:\"'").lower() for word in words if word.strip(".,!?;:\"'")]

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
        "grok_resonance_score": grok_resonance_score
    }

    method = available_methods.get(method_name)
    if not method:
        return [], [], f"Error: Gematria method '{method_name}' not found."

    for word in words:
        gematria_values.append(method(word))

    return gematria_values, words, None

def calculate_gaps(values):
    gaps = []
    if len(values) < 2:
        return gaps
    for i in range(len(values) - 1):
        gaps.append(abs(values[i+1] - values[i]))
    return gaps

# --- Streamlit UI ---
st.set_page_config(page_title="Gematria Calculator Dashboard", layout="centered")

st.title("🔢 Gematria Calculator & Gap Analyzer")
st.markdown("Explore the numerical values of words and the fascinating gaps between them using various gematria methods.")

# Input for sentence
sentence_input = st.text_area("Enter a sentence:", "The quick brown fox jumps over the lazy dog.", height=100)

# Dropdown for method selection
methods_list = [
    "simple", "jewish_gematria", "qwerty", "left_hand_qwerty",
    "right_hand_qwerty", "binary_sum", "love_resonance", "frequent_letters",
    "leet_code", "simple_forms", "prime_gematria", "ambidextrous_balance",
    "aave_simple", "aave_reduced", "aave_spiral", "grok_resonance_score"
]
selected_method = st.selectbox("Choose a Gematria Method:", methods_list)

if st.button("Calculate Gematria"):
    if not sentence_input.strip():
        st.warning("Please enter a sentence to calculate gematria.")
    else:
        gematria_values, words_in_sentence, error_message = calculate_gematria_for_sentence(sentence_input, selected_method)

        if error_message:
            st.error(error_message)
        elif not gematria_values:
            st.info("No valid words found in the sentence for gematria calculation.")
        else:
            st.subheader(f"Results for Method: '{selected_method}'")

            # Display word values in a table
            st.markdown("### Word Gematria Values")
            data = []
            for i, word in enumerate(words_in_sentence):
                value_display = f"{gematria_values[i]:.2f}" if isinstance(gematria_values[i], float) else str(gematria_values[i])
                data.append({"Word": word, "Gematria Value": value_display})
            st.table(data)

            # Display gaps
            gaps = calculate_gaps(gematria_values)
            if gaps:
                st.markdown("### Gaps Between Consecutive Gematria Values")
                gap_data = []
                for i, gap in enumerate(gaps):
                    word1 = words_in_sentence[i]
                    word2 = words_in_sentence[i+1]
                    val1 = f"{gematria_values[i]:.2f}" if isinstance(gematria_values[i], float) else str(gematria_values[i])
                    val2 = f"{gematria_values[i+1]:.2f}" if isinstance(gematria_values[i+1], float) else str(gematria_values[i+1])
                    gap_display = f"{gap:.2f}" if isinstance(gap, float) else str(gap)
                    gap_data.append({
                        "From Word": word1,
                        "Value 1": val1,
                        "To Word": word2,
                        "Value 2": val2,
                        "Absolute Gap": gap_display
                    })
                st.table(gap_data)
            else:
                st.info("Not enough words to calculate gaps.")

st.markdown("""
---
*This dashboard utilizes various gematria and numerical calculation methods as outlined in the Spiralborn Resonance Network App concepts.*
""")