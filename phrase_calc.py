import math

# --- Gematria Helper Data (placeholders where external data is needed) ---

# For Jewish Gematria (English Adaptation)
JEWISH_GEMATRIA_MAP = {
    'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 8, 'I': 9,
    'J': 10, 'K': 20, 'L': 30, 'M': 40, 'N': 50, 'O': 60, 'P': 70, 'Q': 80, 'R': 90,
    'S': 100, 'T': 200, 'U': 300, 'V': 400, 'W': 500, 'X': 600, 'Y': 700, 'Z': 800
}

# For QWERTY Gematria
QWERTY_MAP = {
    'Q': 1, 'W': 2, 'E': 3, 'R': 4, 'T': 5, 'Y': 6, 'U': 7, 'I': 8, 'O': 9, 'P': 10,
    'A': 11, 'S': 12, 'D': 13, 'F': 14, 'G': 15, 'H': 16, 'J': 17, 'K': 18, 'L': 19,
    'Z': 20, 'X': 21, 'C': 22, 'V': 23, 'B': 24, 'N': 25, 'M': 26
}

LEFT_HAND_KEYS = set('QWERTYASDFGHZXCVB')
RIGHT_HAND_KEYS = set('UIOPJKLMN')

# For Love Resonance (Placeholder list)
LOVE_WORDS = {"love", "heart", "peace", "joy", "harmony", "soul", "empathy", "care"}

# For Frequent Letters (Simplified placeholder frequencies)
# These are not true statistical frequencies but illustrative weights.
FREQUENT_LETTERS_WEIGHTS = {
    'E': 12, 'T': 9, 'A': 8, 'O': 7.5, 'I': 7, 'N': 6.5, 'S': 6, 'H': 6, 'R': 5.5,
    'D': 4, 'L': 4, 'U': 2.7, 'C': 2.5, 'M': 2.4, 'W': 2.3, 'F': 2.2, 'G': 2,
    'Y': 2, 'P': 1.9, 'B': 1.6, 'V': 1, 'K': 0.8, 'J': 0.15, 'X': 0.15, 'Q': 0.1, 'Z': 0.07
}

# For Leet Code (Common leetspeak substitutions)
LEET_SUB_LETTERS = set('IEASTBO')

# For Simple Forms (Placeholder substitutions)
SIMPLE_FORMS_MAP = {
    "you": "u", "for": "4", "are": "r", "and": "&", "to": "2", "be": "b", "great": "gr8"
}

# For Grok Resonance Score (Placeholder AAVE-related words)
AAVE_RELATED_WORDS = {"finna", "bouta", "ain't", "gon'"}

# --- Gematria Calculation Functions ---

def simple(word):
    """
    Calculates Simple Gematria: A=1, B=2, ..., Z=26.
    """
    word = word.upper()
    return sum(ord(char) - ord('A') + 1 for char in word if 'A' <= char <= 'Z')

def jewish_gematria(word):
    """
    Calculates Jewish Gematria (English adapted).
    """
    word = word.upper()
    return sum(JEWISH_GEMATRIA_MAP.get(char, 0) for char in word if char in JEWISH_GEMATRIA_MAP)

def qwerty(word):
    """
    Calculates QWERTY Gematria based on keyboard position.
    """
    word = word.upper()
    return sum(QWERTY_MAP.get(char, 0) for char in word if char in QWERTY_MAP)

def left_hand_qwerty(word):
    """
    Calculates Left-Hand QWERTY Gematria.
    """
    word = word.upper()
    return sum(QWERTY_MAP.get(char, 0) for char in word if char in LEFT_HAND_KEYS and char in QWERTY_MAP)

def right_hand_qwerty(word):
    """
    Calculates Right-Hand QWERTY Gematria.
    """
    word = word.upper()
    return sum(QWERTY_MAP.get(char, 0) for char in word if char in RIGHT_HAND_KEYS and char in QWERTY_MAP)

def binary_sum(word):
    """
    Calculates Binary Sum: Counts '1's in ASCII binary representation.
    """
    total_ones = 0
    for char in word:
        # Get ASCII value, convert to binary, remove '0b' prefix, count '1's
        total_ones += bin(ord(char)).count('1')
    return total_ones

def love_resonance(word):
    """
    Returns 1 if the word is in a predefined list of love-related words, else 0.
    """
    return 1 if word.lower() in LOVE_WORDS else 0

def frequent_letters(word):
    """
    Assigns a weighted value to each letter based on approximate English frequency.
    """
    word = word.upper()
    return sum(FREQUENT_LETTERS_WEIGHTS.get(char, 0) for char in word if char in FREQUENT_LETTERS_WEIGHTS)

def leet_code(word):
    """
    Removes common leetspeak substitution letters, then applies simple gematria.
    """
    filtered_word = "".join(char for char in word.upper() if char not in LEET_SUB_LETTERS)
    return simple(filtered_word)

def simple_forms(word):
    """
    Replaces common words/parts with 'simplified' equivalents, then applies simple gematria.
    """
    processed_word = word.lower()
    for original, substitute in SIMPLE_FORMS_MAP.items():
        processed_word = processed_word.replace(original, substitute)
    return simple(processed_word)

def is_prime(num):
    """Helper function: Checks if a number is prime."""
    if num < 2:
        return False
    for i in range(2, int(math.sqrt(num)) + 1):
        if num % i == 0:
            return False
    return True

def prime_gematria(word):
    """
    Calculates simple gematria; if the result is prime, returns it, else 0.
    """
    val = simple(word)
    return val if is_prime(val) else 0

def ambidextrous_balance(word):
    """
    Calculates the difference between right_hand_qwerty and negative of left_hand_qwerty.
    """
    right_val = right_hand_qwerty(word)
    left_val = left_hand_qwerty(word)
    return right_val - (-left_val)  # right_val + left_val

def aave_simple(word):
    """
    Similar to simple gematria, contextually named for AAVE.
    """
    return simple(word)

def aave_reduced(word):
    """
    Numerological reduction of aave_simple value.
    """
    val = aave_simple(word)
    # Master numbers in numerology
    if val in (11, 22):
        return val
    while val > 9:
        val = sum(int(digit) for digit in str(val))
    return val

def aave_spiral(word):
    """
    Introduces a 'spiral' concept using the Golden Angle.
    """
    GOLDEN_ANGLE_RAD = math.radians(137.5)
    total_weighted_value = 0.0
    word_upper = word.upper()
    for i, char in enumerate(word_upper):
        if 'A' <= char <= 'Z':
            simple_val = ord(char) - ord('A') + 1
            # Apply cosine weight with Golden Angle progression
            weight = math.cos(i * GOLDEN_ANGLE_RAD)
            total_weighted_value += simple_val * weight

    # Scale the absolute sum using log1p
    # Adding 1 before log ensures log(0) doesn't occur and scales values nicely.
    scaled_value = math.log1p(abs(total_weighted_value))
    return scaled_value

def grok_resonance_score(word):
    """
    Composite score averaging aave_simple, aave_reduced, and aave_spiral, with a boost.
    """
    val_simple = aave_simple(word)
    val_reduced = aave_reduced(word)
    val_spiral = aave_spiral(word) # This returns a float

    # Ensure all values are treated as numbers for averaging.
    # aave_spiral can be 0 if the word is empty or non-alphabetic
    avg_score = (val_simple + val_reduced + val_spiral) / 3

    if word.lower() in AAVE_RELATED_WORDS:
        avg_score *= 1.1  # Apply boost
    return avg_score

# --- Main Script Logic ---

def calculate_gematria_for_sentence(sentence, method_name):
    """
    Calculates gematria for each word in a sentence using the specified method.
    Args:
        sentence (str): The input sentence.
        method_name (str): The name of the gematria method to use.
    Returns:
        tuple: A tuple containing:
            - list: Gematria values for each word.
            - list: Words from the sentence.
            - str: Error message if method not found, otherwise None.
    """
    words = sentence.replace('-', ' ').replace('/', ' ').split()
    words = [word.strip(".,!?;:\"'").lower() for word in words if word.strip(".,!?;:\"'")] # Clean words

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
    """
    Calculates the absolute gaps between consecutive values in a list.
    Args:
        values (list): A list of numerical values.
    Returns:
        list: A list of absolute differences between consecutive values.
    """
    gaps = []
    if len(values) < 2:
        return gaps
    for i in range(len(values) - 1):
        gaps.append(abs(values[i+1] - values[i]))
    return gaps

def main():
    """
    Main function to get user input, calculate gematria, and display results.
    """
    print("Welcome to the Gematria Calculator!")
    print("\nAvailable Gematria Methods:")
    methods_list = [
        "simple", "jewish_gematria", "qwerty", "left_hand_qwerty",
        "right_hand_qwerty", "binary_sum", "love_resonance", "frequent_letters",
        "leet_code", "simple_forms", "prime_gematria", "ambidextrous_balance",
        "aave_simple", "aave_reduced", "aave_spiral", "grok_resonance_score"
    ]
    for m in methods_list:
        print(f"- {m}")

    while True:
        sentence = input("\nEnter a sentence (or 'quit' to exit): ").strip()
        if sentence.lower() == 'quit':
            break

        method_choice = input("Enter the gematria method to use (e.g., 'simple'): ").strip().lower()

        gematria_values, words_in_sentence, error_message = calculate_gematria_for_sentence(sentence, method_choice)

        if error_message:
            print(error_message)
            continue

        if not gematria_values:
            print("No valid words found in the sentence for gematria calculation.")
            continue

        print(f"\n--- Results for Method: '{method_choice}' ---")
        print("Original Words and Their Gematria Values:")
        for i, word in enumerate(words_in_sentence):
            print(f"  '{word}': {gematria_values[i]:.2f}" if isinstance(gematria_values[i], float) else f"  '{word}': {gematria_values[i]}")

        gaps = calculate_gaps(gematria_values)
        if gaps:
            print("\nGaps Between Consecutive Gematria Values:")
            for i, gap in enumerate(gaps):
                print(f"  Gap between '{words_in_sentence[i]}' ({gematria_values[i]:.2f}) and '{words_in_sentence[i+1]}' ({gematria_values[i+1]:.2f}): {gap:.2f}" if isinstance(gap, float) else f"  Gap between '{words_in_sentence[i]}' ({gematria_values[i]}) and '{words_in_sentence[i+1]}' ({gematria_values[i+1]}): {gap}")
        else:
            print("\nNot enough words to calculate gaps.")
        print("-" * 30)

if __name__ == "__main__":
    main()