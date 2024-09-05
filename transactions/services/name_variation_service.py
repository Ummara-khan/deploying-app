from django.db import transaction
from transactions.models import SanctionRecord, NameVariation
from transactions.name_variations import phonetic_variations, doubling_consonants, vowel_variations, silent_letters, alternate_endings, add_remove_prefixes_suffixes, letter_to_number, loose_comparisons, permutations_of_words

import itertools
from fuzzywuzzy import fuzz

def phonetic_variations(name):
    phonetic_replacements = {
        'K': 'C', 'PH': 'F', 'Y': ['I', 'E'], 'S': 'Z'
    }
    
    variations = set()
    for original, replacement in phonetic_replacements.items():
        if isinstance(replacement, list):
            for rep in replacement:
                variation = name.replace(original, rep)
                if variation != name:
                    variations.add(variation)
        else:
            variation = name.replace(original, replacement)
            if variation != name:
                variations.add(variation)
    return variations

def doubling_consonants(name):
    consonants = "BCDFGHJKLMNPQRSTVWXYZ"
    
    variations = set()
    for consonant in consonants:
        if consonant in name:
            variation = name.replace(consonant, consonant * 2)
            if variation != name:
                variations.add(variation)
    return variations

def vowel_variations(name):
    vowel_replacements = {
        'A': 'E', 'O': 'U'
    }
    
    variations = set()
    for vowel, replacement in vowel_replacements.items():
        variation = name.replace(vowel, replacement)
        if variation != name:
            variations.add(variation)
    return variations

def silent_letters(name):
    silent_letters = {
        'E': [''], 'A': ['']
    }
    
    variations = set()
    for letter, replacements in silent_letters.items():
        for replacement in replacements:
            variation = name.replace(letter, replacement)
            if variation != name:
                variations.add(variation)
    return variations

def alternate_endings(name):
    endings = {
        'IE': 'Y', 'A': 'AH'
    }
    
    variations = set()
    for ending, replacement in endings.items():
        if name.endswith(ending):
            variations.add(name[:-len(ending)] + replacement)
    return variations

def add_remove_prefixes_suffixes(name):
    prefixes_suffixes = {
        'MC': '', 'MAC': '', 'SON': '', 'SEN': ''
    }
    
    variations = set()
    for prefix, replacement in prefixes_suffixes.items():
        if name.startswith(prefix):
            variations.add(replacement + name[len(prefix):])
        if name.endswith(prefix):
            variations.add(name[:-len(prefix)] + replacement)
    return variations

def letter_to_number(name):
    letter_to_number_map = {
        'O': '0', 'I': '1', 'R': '2', 'E': '3', 'A': '4',
        'S': '5', 'G': '6', 'T': '7', 'B': '8', 'P': '9'
    }
    
    # Convert each character in the name based on the mapping
    converted_name = ''.join(letter_to_number_map.get(ch.upper(), ch) for ch in name)
    
    return {converted_name}

def loose_comparisons(name):
    variations = set()
    
    for ch in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        if not name.endswith(ch):
            variations.add(name + ch)
    
    for i in range(len(name)):
        variations.add(name[:i] + name[i+1:])
    
    return variations

def permutations_of_words(name):
    words = name.split()
    
    variations = set()
    if len(words) > 1:
        variations.add(' '.join(reversed(words)))
    
    return variations

from transactions.models import NameVariation, SanctionRecord

from fuzzywuzzy import fuzz

from slugify import slugify
from fuzzywuzzy import fuzz  # Assuming you are using fuzzy matching for scoring

def generate_name_variations(name):
    name = name.upper()
    variations = set()

    # Generate variations using different algorithms
    variations.update(phonetic_variations(name))
    variations.update(doubling_consonants(name))
    variations.update(vowel_variations(name))
    variations.update(silent_letters(name))
    variations.update(alternate_endings(name))
    variations.update(add_remove_prefixes_suffixes(name))
    variations.update(letter_to_number(name))
    variations.update(loose_comparisons(name))
    variations.update(permutations_of_words(name))

    return variations

from fuzzywuzzy import fuzz
from slugify import slugify

def process_and_save_variations(first_name, last_name, record):
    # Ensure that 'record' is a valid SanctionRecord instance
    if not isinstance(record, SanctionRecord):
        raise ValueError("The 'record' must be a SanctionRecord instance")

    # Combine first and last name for generating variations
    full_name = f"{first_name} {last_name}".strip()
    
    if not full_name:
        print("Full name is empty, skipping variation generation.")
        return

    # Generate name variations
    variations = generate_name_variations(full_name)

    variations_to_create = []
    for variation in variations:
        try:
            # Ensure variation is not empty
            if variation.strip():
                score = fuzz.ratio(full_name, variation)
                # Create NameVariation instances
                variations_to_create.append(NameVariation(
                    sanction_record=record,
                    sanc_id=record.id_original,  # Use id_original as sanc_id
                    variation_id=slugify(variation),  # Use slugify to create variation_id
                    score=score
                ))
            else:
                print(f"Empty variation for {full_name}, skipping.")
        except Exception as e:
            print(f"Error creating NameVariation for {variation}: {e}")

    # Save variations in bulk if there are any to create
    if variations_to_create:
        try:
            NameVariation.objects.bulk_create(variations_to_create, batch_size=1000)
        except Exception as e:
            print(f"Error during bulk_create: {e}")
