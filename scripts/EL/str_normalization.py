import re
import unicodedata

def remove_accents(text):
    # Normalize the text to decompose characters (NFD: Normal Form Decomposed)
    normalized_text = unicodedata.normalize('NFD', text)
    # Filter out combining marks (category 'Mn' stands for Mark, Nonspacing)
    non_accented_text = ''.join(char for char in normalized_text if unicodedata.category(char) != 'Mn')
    return non_accented_text

def normalize_text(text):
    text = text.lower()
    text = text.replace('→',' ')
    text = re.sub(r'[^\w\s→]', '', text)
    return text