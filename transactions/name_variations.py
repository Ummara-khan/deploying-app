import itertools
from fuzzywuzzy import fuzz

def phonetic_variations(name):
    phonetic_replacements = {
        'K': 'C', 'PH': 'F', 'Y': ['I', 'E'], 'S': 'Z'
    }
    
    for original, replacement in phonetic_replacements.items():
        if isinstance(replacement, list):
            for rep in replacement:
                variation = name.replace(original, rep)
                if variation != name:
                    return variation
        else:
            variation = name.replace(original, replacement)
            if variation != name:
                return variation
    return name

def doubling_consonants(name):
    consonants = "BCDFGHJKLMNPQRSTVWXYZ"
    
    for consonant in consonants:
        if consonant in name:
            variation = name.replace(consonant, consonant * 2)
            if variation != name:
                return variation
    return name

def vowel_variations(name):
    vowel_replacements = {
        'A': 'E', 'O': 'U'
    }
    
    for vowel, replacement in vowel_replacements.items():
        variation = name.replace(vowel, replacement)
        if variation != name:
            return variation
    return name

def silent_letters(name):
    silent_letters = {
        'E': [''], 'A': ['']
    }
    
    for letter, replacements in silent_letters.items():
        for replacement in replacements:
            variation = name.replace(letter, replacement)
            if variation != name:
                return variation
    return name

def alternate_endings(name):
    endings = {
        'IE': 'Y', 'A': 'AH'
    }
    
    for ending, replacement in endings.items():
        if name.endswith(ending):
            return name[:-len(ending)] + replacement
    return name

def add_remove_prefixes_suffixes(name):
    prefixes_suffixes = {
        'MC': '', 'MAC': '', 'SON': '', 'SEN': ''
    }
    
    for prefix, replacement in prefixes_suffixes.items():
        if name.startswith(prefix):
            return replacement + name[len(prefix):]
        if name.endswith(prefix):
            return name[:-len(prefix)] + replacement
    return name

def letter_to_number(name):
    letter_to_number_map = {
        'A': '1', 'B': '2', 'C': '3', 'D': '4', 'E': '5',
        'F': '6', 'G': '7', 'H': '8', 'I': '9', 'J': '1',
        'K': '2', 'L': '3', 'M': '4', 'N': '5', 'O': '6',
        'P': '7', 'Q': '8', 'R': '9', 'S': '1', 'T': '2',
        'U': '3', 'V': '4', 'W': '5', 'X': '6', 'Y': '7',
        'Z': '8'
    }
    
    for ch, replacement in letter_to_number_map.items():
        if ch in name:
            return name.replace(ch, replacement)
    return name

def loose_comparisons(name):
    variations = set()
    
    for ch in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        if not name.endswith(ch):
            return name + ch
    
    for i in range(len(name)):
        return name[:i] + name[i+1:]
    
    return name

def permutations_of_words(name):
    words = name.split()
    
    if len(words) > 1:
        return ' '.join(reversed(words))
    
    return name

def generate_name_variations(name):
    name = name.upper()
    variations = set()
    
    variations.add(phonetic_variations(name))
    variations.add(doubling_consonants(name))
    variations.add(vowel_variations(name))
    variations.add(silent_letters(name))
    variations.add(alternate_endings(name))
    variations.add(add_remove_prefixes_suffixes(name))
    variations.add(letter_to_number(name))
    variations.add(loose_comparisons(name))
    variations.add(permutations_of_words(name))
    
    # Remove duplicates and keep the highest scored variation
    scored_variations = {}
    for var in variations:
        score = fuzz.ratio(name, var)  # Example scoring with fuzzywuzzy
        scored_variations[var] = score
    
    return dict(sorted(scored_variations.items(), key=lambda item: item[1], reverse=True))
