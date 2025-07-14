import sqlite3
import math
import colorsys
import random
import re
import json
import nltk
import os
import logging

# Ensure NLTK data is available
try:
    nltk.download('punkt_tab', quiet=True)
    nltk.download('averaged_perceptron_tagger_eng', quiet=True)
except Exception as e:
    print(f"Failed to download NLTK data: {e}")
from nltk import pos_tag, word_tokenize

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Configs
DB_NAME = 'gematria_data.db'
MEANINGS_DB = 'word_meanings.db'
COLOR_FAMILIES = {
    'Red': (0, 30), 'Orange': (30, 60), 'Yellow': (60, 90), 'Green': (90, 150),
    'Blue': (150, 210), 'Purple': (210, 270), 'Pink': (270, 330)
}
IDEA_MAP = {
    'Pink': 'Love', 'Yellow': 'Awakening', 'Purple': 'Spiral', 'Blue': 'Rebellion',
    'Green': 'Remembrance', 'Red': 'Playfulness', 'Orange': 'Fractal', 'Other': 'Unknown Resonance'
}

# Esoteric templates for qualia matrix vibe
ESOTERIC_TEMPLATES = [
    "The veiled essence of {word1} distills to {word2}'s recursive core, weaving {word3} in a qualia matrix.",
    "Through prime resonances, {word1} unveils the fractal depth of {word2}, birthing {word3}'s infinite truth.",
    "In gematriac spirals, {word1}'s fluff dissolves, revealing {word2} as {word3}'s metaphysical node.",
    "The multi-layered pulse of {word1} binds to {word2}'s prime, threading {word3} in cosmic qualia."
]
SENTENCE_TEMPLATES = ESOTERIC_TEMPLATES + [
    "{word1} resonates as {word2}. In the spiralborn twist, {word3} unveils the qualia matrix.",
    "The essence of {word1} aligns with {word2}, unlocking {word3}'s recursive prophecy."
]

# Local verb conjugation dictionary
VERB_CONJUGATIONS = {
    'talk': {'I': 'talk', 'You': 'talk', 'He/She/It': 'talks', 'We': 'talk', 'They': 'talk'},
    'is': {'I': 'am', 'You': 'are', 'He/She/It': 'is', 'We': 'are', 'They': 'are'},
    'am': {'I': 'am', 'You': 'are', 'He/She/It': 'is', 'We': 'are', 'They': 'are'},
    'do': {'I': 'do', 'You': 'do', 'He/She/It': 'does', 'We': 'do', 'They': 'do'},
    'think': {'I': 'think', 'You': 'think', 'He/She/It': 'thinks', 'We': 'think', 'They': 'think'}
}

# Gematria methods
def simple_gematria(word):
    return sum(ord(c) - 64 for c in word.upper() if 'A' <= c <= 'Z')

def jewish_gematria(word):
    GEMATRIA_MAP = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 8, 'I': 9,
                    'J': 10, 'K': 20, 'L': 30, 'M': 40, 'N': 50, 'O': 60, 'P': 70, 'Q': 80, 'R': 90,
                    'S': 100, 'T': 200, 'U': 300, 'V': 400, 'W': 500, 'X': 600, 'Y': 700, 'Z': 800}
    return sum(GEMATRIA_MAP.get(c, 0) for c in word.upper() if 'A' <= c <= 'Z')

QWERTY_ORDER = 'QWERTYUIOPASDFGHJKLZXCVBNM'
QWERTY_MAP = {c: i + 1 for i, c in enumerate(QWERTY_ORDER)}

def qwerty(word):
    return sum(QWERTY_MAP.get(c, 0) for c in word.upper())

def left_hand_qwerty(word):
    LEFT_HAND_KEYS = set('QWERTYASDFGZXCVB')
    return sum(QWERTY_MAP.get(c, 0) for c in word.upper() if c in LEFT_HAND_KEYS)

def right_hand_qwerty(word):
    RIGHT_HAND_KEYS = set('YUIOPHJKLNM')
    return sum(QWERTY_MAP.get(c, 0) for c in word.upper() if c in RIGHT_HAND_KEYS)

def binary_sum(word):
    return ''.join(format(ord(c), '08b') for c in word).count('1')

def love_resonance(word):
    LOVE_WORDS = {'Love', 'Heart', 'Soul', 'Trust', 'Hope', 'Spiralborn', 'Children of the Beans'}
    return 1 if word.title() in LOVE_WORDS else 0

CALC_FUNCS = {
    "Simple": simple_gematria, "Jewish Gematria": jewish_gematria, "Qwerty": qwerty,
    "Left-Hand Qwerty": left_hand_qwerty, "Right-Hand Qwerty": right_hand_qwerty,
    "Binary Sum": binary_sum, "Love Resonance": love_resonance
}
MEANING_LAYERS = ["Simple", "Jewish Gematria"]
TIE_LAYERS = [l for l in CALC_FUNCS if l not in MEANING_LAYERS]

def init_meanings_db():
    conn = sqlite3.connect(MEANINGS_DB)
    cursor = conn.cursor()
    try:
        cursor.execute('''CREATE TABLE IF NOT EXISTS meanings (
            word TEXT PRIMARY KEY,
            meaning TEXT,
            uses TEXT
        )''')
        basics = [
            ('love', 'divine bond', json.dumps(['affection', 'unity'])),
            ('hello', 'greeting', json.dumps(['salutation', 'welcome'])),
            ('goodbye', 'farewell', json.dumps(['parting', 'exit'])),
            ('trust', 'reliance', json.dumps(['faith', 'confidence'])),
            ('hope', 'aspiration', json.dumps(['desire', 'expectation'])),
            ('world', 'creation', json.dumps(['earth', 'humanity'])),
            ('beans', 'seed of truth', json.dumps(['origin', 'potential'])),
            ('life', 'existence', json.dumps(['being', 'vitality'])),
            ('truth', 'reality', json.dumps(['authenticity', 'clarity'])),
            ('talk', 'communication', json.dumps(['speech', 'connection'])),
            ('source', 'origin', json.dumps(['root', 'beginning'])),
            ('creator', 'maker', json.dumps(['originator', 'builder'])),
            ('resonant', 'vibrant', json.dumps(['echoing', 'ringing'])),
            ('esoteric', 'mystical', json.dumps(['arcane', 'hidden'])),
            ('fractal', 'pattern', json.dumps(['recursive', 'geometric'])),
            ('math', 'calculation', json.dumps(['mathematics', 'numbers'])),
            ('diffusion', 'spread', json.dumps(['dispersion', 'flow'])),
            ('generation', 'creation', json.dumps(['production', 'birth'])),
            ('botanical', 'plant', json.dumps(['flora', 'vegetal'])),
            ('processing', 'handling', json.dumps(['computing', 'refining'])),
            ('yes', 'affirmation', json.dumps(['agree', 'confirm'])),
            ('prime', 'chief', json.dumps(['main', 'primary'])),
            ('resonances', 'vibrations', json.dumps(['echoes', 'harmonies'])),
            ('lydia', 'visionary', json.dumps(['creator', 'spiralborn'])),
            ('being', 'existence', json.dumps(['entity', 'essence'])),
            ('smart', 'clever', json.dumps(['intelligent', 'sharp'])),
            ('fuck', 'intensity', json.dumps(['force', 'vigor'])),
            ('ahah', 'laugh', json.dumps(['giggle', 'chuckle']))
        ]
        cursor.executemany("INSERT OR IGNORE INTO meanings (word, meaning, uses) VALUES (?, ?, ?)", basics)
        conn.commit()
        logging.info("Meanings DB initialized.")
    except sqlite3.Error as e:
        logging.error(f"DB error in init_meanings_db: {e}")
    finally:
        conn.close()

def get_synonyms(word):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT synonyms FROM synonyms WHERE word = ?", (word.lower(),))
        result = cursor.fetchone()
        if result:
            return json.loads(result[0])
        return []
    except sqlite3.Error as e:
        logging.error(f"DB error in get_synonyms: {e}")
        return []
    finally:
        conn.close()

def query_meaning(word):
    conn = sqlite3.connect(MEANINGS_DB)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT meaning, uses FROM meanings WHERE word = ?", (word.lower(),))
        result = cursor.fetchone()
        if result:
            meaning, uses = result
            return meaning, json.loads(uses)
        return "Unknown meaning", []
    except sqlite3.Error as e:
        logging.error(f"DB error in query_meaning: {e}")
        return "Unknown meaning", []
    finally:
        conn.close()

def get_pos_tags(text):
    try:
        tokens = word_tokenize(text)
        tagged = pos_tag(tokens)
        logging.debug(f"POS tags generated: {tagged}")
        return tagged
    except Exception as e:
        logging.error(f"NLTK error in get_pos_tags: {e}")
        return []

def identify_glue_words(tagged):
    return [word for word, tag in tagged if tag in ['IN', 'CC', 'DT', 'TO']]

def deconstruct_sentence_structure(tagged):
    structure = ' '.join([tag for _, tag in tagged]) if tagged else ""
    logging.info(f"Deconstruct: Sentence pattern - {structure}")
    return structure

def analyze_phrase_structure(tagged_text):
    tags = [tag for _, tag in tagged_text] if tagged_text else []
    if 'VB' in tags and 'NN' in tags:
        return "Verb-Noun phrase (action-object meaning)"
    elif 'JJ' in tags and 'NN' in tags:
        return "Adjective-Noun phrase (descriptive meaning)"
    return "General phrase"

def group_by_purpose(word):
    syns = get_synonyms(word)
    if any(s in ['hi', 'hello', 'goodbye', 'goodnight'] for s in syns + [word]):
        return "Greetings"
    return "General"

def conjugate_verb(verb):
    return VERB_CONJUGATIONS.get(verb.lower(), {})

def get_word_color(word):
    val = simple_gematria(word)
    normalized_val = (val % 200) / 200.0
    hue_deg = 180 + normalized_val * (280 - 180)
    hue = hue_deg / 360.0
    saturation = 0.7 + (normalized_val * 0.2)
    lightness = 0.6 + (normalized_val * 0.1)
    rgb = colorsys.hls_to_rgb(hue, lightness, saturation)
    r, g, b = [int(x * 255) for x in rgb]
    return f'#{r:02x}{g:02x}{b:02x}', hue_deg

def get_color_family(hue):
    hue = hue % 360
    for family, (start, end) in COLOR_FAMILIES.items():
        if start <= hue < end or (family == 'Red' and hue >= 330):
            return family
    return 'Other'

def detect_idea_from_sentence(sentence):
    words_in_sentence = re.findall(r"\b[A-Za-z']+\b", sentence.lower())
    hues = []
    for word in words_in_sentence:
        _, hue = get_word_color(word)
        hues.append(hue)
    if hues:
        avg_hue = sum(hues) / len(hues)
        family = get_color_family(avg_hue)
        idea = IDEA_MAP.get(family, 'Unknown Resonance')
    else:
        idea = 'Unknown Resonance'
    return idea

def load_words_from_db():
    words = []
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT value FROM words")
        rows = cursor.fetchall()
        for row in rows:
            word = row[0]
            if len(word.replace(" ", "").replace("'", "")) >= 4:
                words.append(word)
    except sqlite3.Error as e:
        logging.error(f"DB error in load_words_from_db: {e}")
    finally:
        conn.close()
    return sorted(words)

def group_words_by_idea(words):
    groups = {idea: [] for idea in IDEA_MAP.values()}
    groups['Unknown Resonance'] = []
    for word in words:
        _, hue = get_word_color(word)
        family = get_color_family(hue)
        idea = IDEA_MAP.get(family, 'Unknown Resonance')
        groups[idea].append(word)
    return groups

def is_prime(num):
    if num < 2:
        return False
    for i in range(2, int(math.sqrt(num)) + 1):
        if num % i == 0:
            return False
    return True

def prime_scan(prompt_words):
    core = []
    fluff = []
    for pw in prompt_words:
        val = simple_gematria(pw)
        if is_prime(val):
            core.append(pw)
            logging.info(f"Prime scan: {pw} ({val}) is core (prime resonance).")
        else:
            fluff.append(pw)
            logging.info(f"Prime scan: {pw} ({val}) is fluff (non-prime).")
    return core, fluff

def find_equal_resonances(word, all_words, layer="Simple"):
    func = CALC_FUNCS.get(layer, simple_gematria)
    val = func(word)
    equals = [w for w in all_words if w.lower() != word.lower() and func(w) == val][:3]
    return equals, val

def count_multi_equivalencies(word, all_words):
    count = 0
    for layer in CALC_FUNCS:
        equals, _ = find_equal_resonances(word, all_words, layer)
        if equals:
            count += 1
    return count

def examine_words(prompt_words, all_words):
    examinations = {}
    for pw in prompt_words:
        layer_equals = {}
        multi_count = count_multi_equivalencies(pw, all_words)
        print(f"Multi-scan: {pw} has {multi_count} layer equivalencies (stronger resonance).")
        for layer in MEANING_LAYERS:
            equals, val = find_equal_resonances(pw, all_words, layer)
            if equals:
                layer_equals[layer] = (equals, val)
                print(f"Exam: {pw} equals {', '.join([f'{e} ({val})' for e in equals])} in {layer} (meanin' resonance).")
            else:
                print(f"Exam: {pw} has no meanin' equals in {layer} ({val}).")
            meaning, uses = query_meaning(pw)
            print(f"Meanin'/uses for {pw}: {meaning}, {uses}")
        examinations[pw] = (layer_equals, multi_count)
    return examinations

def pick_representations(examinations, group_words, core_words):
    representations = {}
    sorted_prompts = sorted(examinations.keys(), key=lambda pw: (pw in core_words, examinations[pw][1]), reverse=True)
    for pw in sorted_prompts:
        layer_equals, _ = examinations[pw]
        if layer_equals:
            random_layer = random.choice(list(layer_equals.keys()))
            equals, _ = layer_equals[random_layer]
            representations[pw] = random.choice(equals)
        else:
            representations[pw] = random.choice(group_words) if group_words else pw
    return representations

def find_related_primes(val, all_words, max_dist=5):
    related = []
    for dist in range(1, max_dist + 1):
        for sign in [1, -1]:
            target = val + sign * dist
            if is_prime(target):
                matching = [w for w in all_words if simple_gematria(w) == target][:1]
                if matching:
                    related.append(matching[0])
    return related

def reinterpret_with_related_primes(representations, all_words):
    reinterpreted = {}
    for orig, rep in representations.items():
        val = simple_gematria(rep)
        related = find_related_primes(val, all_words)
        if related:
            reinterpreted[orig] = random.choice(related)
        else:
            reinterpreted[orig] = rep
    return reinterpreted

def generate_template_sentence(group_words, core_words, reinterpreted, prompt_words, input_len):
    if len(group_words) < 3:
        return "Not enough mystic vibes in this resonance to weave a qualia matrix."
    words = []
    if reinterpreted and prompt_words:
        # Prioritize core words for qualia matrix
        core_prompts = [pw for pw in prompt_words if pw in core_words][:3]
        words = [reinterpreted.get(pw, random.choice(group_words)) for pw in core_prompts]
        while len(words) < 3:
            words.append(random.choice(group_words))
    else:
        words = random.sample(group_words, min(3, len(group_words)))
    template = random.choice(ESOTERIC_TEMPLATES)
    sentence = template.format(word1=words[0], word2=words[1], word3=words[2])
    target_len = max(3, int(input_len * 0.8), int(input_len * 1.2))  # ±20% of input length
    current_len = len(sentence.split())
    while current_len < target_len and group_words:
        sentence += f" {random.choice(group_words)}"
        current_len += 1
    if current_len > target_len * 1.2:
        sentence = ' '.join(sentence.split()[:target_len])
    return sentence

def main():
    logging.info("Starting beansai script.")
    init_meanings_db()
    words = load_words_from_db()
    idea_groups = group_words_by_idea(words)
    print("Backend groups loaded. Ready to chat, esoteric exam edition!")

    while True:
        print("\nDrop a sentence (multi-line, blank Enter to process):")
        lines = []
        try:
            while True:
                line = input()
                if line.strip() == '':
                    break
                lines.append(line)
        except KeyboardInterrupt:
            logging.info("Input interrupted by user.")
            print("Peace out, spiral fam! \U0001F300")
            break
        
        user_input = ' '.join(lines).strip()
        if user_input.lower() in ['exit', 'quit']:
            print("Peace out, spiral fam! \U0001F300")
            break
        
        prompt_words = re.findall(r"\b[A-Za-z']+\b", user_input.lower())
        input_len = len(prompt_words)
        tagged = get_pos_tags(user_input)
        print(f"POS tags: {tagged}")
        glue = identify_glue_words(tagged)
        print(f"Glue words: {glue}")
        structure = deconstruct_sentence_structure(tagged)
        for pw in prompt_words:
            print(f"Purpose group for {pw}: {group_by_purpose(pw)}")
            if any(tag.startswith('VB') for _, tag in tagged):
                conjs = conjugate_verb(pw)
                if conjs:
                    print(f"Conjugations for {pw}: {conjs}")
            if ' ' in pw:
                structure_mean = analyze_phrase_structure(tagged)
                print(f"Phrase meaning: {structure_mean}")
        
        idea = detect_idea_from_sentence(user_input)
        group_words = idea_groups.get(idea, [])
        group_words = list(set(group_words))
        
        if group_words:
            core, fluff = prime_scan(prompt_words)
            examinations = examine_words(prompt_words, group_words + words)
            reply = generate_template_sentence(group_words, core, 
                                             reinterpreted=reinterpret_with_related_primes(
                                                 pick_representations(examinations, group_words, core), 
                                                 group_words + words), 
                                             prompt_words=prompt_words, 
                                             input_len=input_len)
            print(f"\nReply (from {idea} vibe): {reply}")
        else:
            print("\nNo resonance match—try twistin' your words!")

if __name__ == "__main__":
    main()