import os
import re
import string
import glob
import json
import unicodedata
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

nltk.download('punkt')
nltk.download('stopwords')

class NormalizeText:

    @staticmethod
    def remove_accents(text):
        # Normalize the string to decompose characters with accents
        nfkd_form = unicodedata.normalize('NFKD', text)
        
        # Remove the accents (by keeping only the base characters)
        return ''.join([c for c in nfkd_form if not unicodedata.combining(c)])

    @staticmethod
    def replace_characters(text, remove_chars_regex, replacement_char):
        return re.sub(f'[{remove_chars_regex}]+', replacement_char, text)
    
    @staticmethod
    def remove_conjunctions_prepositions_nltk(text):
        # Get French stopwords (includes prepositions & conjunctions)
        french_stopwords = set(stopwords.words('french'))
    
        french_stopwords.discard('mon') #Exeception, is abreviation for maison
    
        # Tokenize the text
        words = word_tokenize(text.lower(), language='french')
        
        # Filter words that are NOT in the stopwords list
        filtered_words = [word for word in words if word not in french_stopwords]
        
        return " ".join(filtered_words)

    @staticmethod
    def split_text(text, split_chars_regex):
        return re.split(f'[{split_chars_regex}]+', text)

    @staticmethod
    def clean_arrow_texts(text):
        """
        Finds and removes the opening (↑) and closing (↓) arrows from substrings enclosed by them,
        ensuring there are no nested arrows inside.
        
        :param text: The input string to process.
        :return: The modified string with arrows removed from valid matches.
        """
        pattern = r'↑([^↑↓]+)↓'  # Match text between ↑ and ↓ without nested arrows
        return re.sub(pattern, r'\1', text)

    @staticmethod
    def separate_crossed_out(text):
        crossed_out = re.findall(r'×(.*?)±', text)
        non_crossed_out = re.sub(r'×.*?±', '', text)
        
        crossed = ' '.join(crossed_out)
        non_crossed = non_crossed_out
    
        return non_crossed, crossed

    @staticmethod
    def remove_leading_zeros(text):
        match = re.match(r'^[0]+', text)
        cleaned_text = text[match.span(0)[1]:]
        return cleaned_text

    @staticmethod
    def trim_whitespace(s):
        return s.strip()

    def merged_cells_with_arrows(values):
        i = 0
        while i < len(values):
            current_val = values[i]
            if current_val.strip().endswith("→"):
                chain = [current_val]
                j = i + 1
                while j < len(values):
                    next_val = values[j]
                    if next_val.strip().startswith("←"):
                        chain.append(next_val)
                        if not next_val.strip().endswith("→"):
                            break
                        j += 1
                    else:
                        break
                full_text = "".join(chain)
                for k in range(i, i + len(chain)):
                    values[k] = full_text
                i += len(chain)
            else:
                i += 1
        return values


class TableValuesPostTreatment:

    @staticmethod
    def idem_replacements(cell_text, previous_cell_text, idem_list=['§','Ø','id','idem','le meme','la meme','les memes']):
        """
        If cell value is one of the "idem" values, replace it by the value of the same cell in the previous line
        """
        text = str(cell_text).lower()
        text = NormalizeText.remove_accents(text)
        if text in idem_list:
            return previous_cell_text
        else:
            return cell_text

    @staticmethod
    def ditto_replacements(cell_text, next_cell_text, ditto_list=['☼']):
        """
        If cell value is one of the "ditto" values, replace it by the value of the same cell in the next line
        """
        text = str(cell_text).lower()
        text = NormalizeText.remove_accents(text)
        if text in ditto_list:
            return next_cell_text
        else:
            return cell_text

    @staticmethod
    def apply_idem_replacements_to_list(values, idem_list=['§', 'Ø', 'id', 'idem', 'le meme', 'la meme', 'les memes']):
        """
        Applies idem_replacements function to a list of values.
        """
        previous_value = None
        processed_list = []
        
        for value in values:
            processed_value = TableValuesPostTreatment.idem_replacements(value, previous_value, idem_list)
            processed_list.append(processed_value)
            previous_value = processed_value
        
        return processed_list

    @staticmethod
    def apply_ditto_replacements_to_list(values, ditto_list=['☼']):
        """
        Applies ditto_replacements function to a list of values.
        If a value is in the ditto_list, it is replaced by the value in the next row.
        If it's the last row, it remains unchanged.
        """
        processed_list = values[:]  # Copy input list to avoid modifying the original
        length = len(values)
    
        for i in range(length - 1):  # Iterate normally, stopping at second-to-last element
            if str(values[i]) in ditto_list:
                processed_list[i] = processed_list[i + 1]  # Replace with the next value
    
        return processed_list  # Last element remains unchanged
        
    @staticmethod
    def turn_list_of_dict_to_lists(data, SPECIAL_VALUE):
        """
        Converts a list of dictionaries to a dictionary of lists.
        Missing values of certain entities in dictionnaries are replaced by a special value
        """
        all_keys = {key for d in data for key in d.keys()}
        
        # Extract each key into its own list, filling missing values with SPECIAL_VALUE
        separated_lists = {key: [d.get(key, SPECIAL_VALUE) for d in data] for key in all_keys}
        
        return separated_lists
        
    @staticmethod
    def merge_lists_to_dicts(separated_lists):
        """
        Converts a dictionary of lists back into a list of dictionaries.
        Assumes all lists are of the same length.
        """
        keys = separated_lists.keys()
        length = len(next(iter(separated_lists.values())))  # Get the length of any value list
    
        # Reconstruct dictionaries
        return [{key: separated_lists[key][i] for key in keys} for i in range(length)]

    @staticmethod
    def process_idem_ditto_replacements(data, SPECIAL_VALUE="MISSING", 
                                    idem_list=['§', 'Ø', 'id', 'idem', 'le meme', 'la meme', 'les memes'],
                                    ditto_list=['☼'],to_remove=["uri","detection_order","true_order","status"]):
        """
        Processes a list of dictionaries representing table rows by replacing "idem" and "ditto" values.
        Adds an 'interpreted_text' field while keeping the original structure.
    
        Args:
            data (list of dict): The table data where each dict represents a row.
            SPECIAL_VALUE (str): Placeholder for missing values.
            idem_list (list of str): List of values considered as "idem" replacements.
            ditto_list (list of str): List of values considered as "ditto" replacements.
    
        Returns:
            list of dict: Updated table data with 'interpreted_text' field added.
        """
    
        # Convert list of dictionaries into a dictionary of lists (column-wise transformation)
        separated_lists = TableValuesPostTreatment.turn_list_of_dict_to_lists(data, SPECIAL_VALUE)
    
        keys = list(separated_lists.keys())  # Get column keys
        
        for elem in to_remove:
            if elem in keys:
                keys.remove(elem)
            del separated_lists[elem]
            
        # Extract text values and ensure they are strings
        for key in keys:
            separated_lists[key] = [str(value["text"]) if isinstance(value, dict) and "text" in value else SPECIAL_VALUE 
                                    for value in separated_lists[key]]

        # Apply arrow-based cell merging BEFORE any replacements
        for key in keys:
            separated_lists[key] = NormalizeText.merged_cells_with_arrows(separated_lists[key])
    
        # Apply "idem" replacements column-wise
        for key in keys:
            separated_lists[key] = TableValuesPostTreatment.apply_idem_replacements_to_list(separated_lists[key], idem_list)
    
        # Apply "ditto" replacements column-wise
        for key in keys:
            separated_lists[key] = TableValuesPostTreatment.apply_ditto_replacements_to_list(separated_lists[key], ditto_list)
    
        # Convert back to list of dictionaries (row-wise)
        updated_data = TableValuesPostTreatment.merge_lists_to_dicts(separated_lists)
    
        # Inject "interpreted_text" into the original data structure
        # Ensure 'interpreted_text' is added correctly, handling cases where row[key] is a string or a dict
        for i, row in enumerate(data):
            for key in row:
                if key not in to_remove:
                    # Check if the current value is a dictionary and contains "text"
                    if isinstance(row[key], dict) and "text" in row[key]:
                        row[key]["interpreted_text"] = updated_data[i][key]
                    else:
                        # If not a dictionary, assume it's a string (add interpreted_text as an additional string value)
                        row[key] = {"interpreted_text": updated_data[i][key]}
    
        return data

    @staticmethod
    def update_jsons_with_objects_details(dir_:str, chars_to_split=["Ⓐ", "Ⓑ", "Ⓒ", "Ⓓ", "Ⓔ", "Ⓕ", "Ⓖ"]):
        """
        Process the JSON files and add "objects_details" to each page.
        """
        jsons = glob.glob(dir_ + '/*.json')
            
        for page_json in jsons:
            with open(page_json) as f:
                page_name = page_json.replace(dir_,'').replace('.json','')
                page = json.load(f)
            
            # Extract the lines (objects) from the current page
            lines = page.get("objects", [])
            entities_dict = []
            
            # Iterate through lines, process them and create the necessary dictionaries
            for i in range(len(lines)):
                transcription = lines[i].get("text", "")
    
                # Assuming `create_split_dictionary` is a function you have for processing transcription
                dict_ = create_split_dictionary(transcription, chars_to_split)
                
                # Collect the processed entities for later use
                entities_dict.append(dict_)
            
            # Process 'idem' and 'ditto' replacements
            updated_entities_dict = TableValuesPostTreatment.process_idem_ditto_replacements(entities_dict, SPECIAL_VALUE="MISSING", 
                                    idem_list=['§', 'Ø', 'id', 'idem', 'le meme', 'la meme', 'les memes'],
                                    ditto_list=['☼'],to_remove=["uri","detection_order","true_order","status"])
            
            # Add `objects_details` to the original page data
            page["entities"] = updated_entities_dict
            
            # Save the updated JSON data back to the file
            with open(page_json, 'w') as f:
                json.dump(page, f, indent=4)

def delete_property_from_json(json_, property_):

    with open(json_, "r") as f:
        data = json.load(f)
    
    if property_ in data:
        del data[property_]
    
    with open(json_, "w") as f:
        json.dump(data, f)

def delete_characters(text, chars_to_delete):
    """
    Delete a list of characters from a given text.

    Parameters:
    text (str): The original text from which characters will be deleted.
    chars_to_delete (list): A list of characters to be deleted from the text.

    Returns:
    str: The text with the specified characters removed.
    """
    # Create a translation table that maps each character to be deleted to None
    translation_table = str.maketrans('', '', ''.join(chars_to_delete))

    # Use the translate method to remove the characters
    cleaned_text = text.translate(translation_table)

    return cleaned_text

def split_text_at_characters(text, chars_to_split):
    """
    Split a text at the occurrences of characters from a given list.

    Parameters:
    text (str): The original text to be split.
    chars_to_split (list): A list of characters at which to split the text.

    Returns:
    list: A list of substrings split at the specified characters.
    """
    # Create a set of characters to split at for faster lookup
    split_chars = set(chars_to_split)

    # Initialize an empty list to hold the split substrings
    result = []
    # Initialize a temporary string to build the current substring
    current_substring = []

    special_chars = []
    # Iterate through each character in the text
    for char in text:
        if char in split_chars:
            special_chars.append(char)
            # If the character is in the split list, join the current substring and add it to the result
            if current_substring:
                result.append(''.join(current_substring))
                current_substring = []
        else:
            # Otherwise, add the character to the current substring
            current_substring.append(char)

    # Add the last substring to the result if it's not empty
    if current_substring:
        result.append(''.join(current_substring))
    return result, special_chars

def create_split_dictionary(text, chars_to_split):
    """
    Create a dictionary with characters used to split as keys and the following text as values,
    including the index of the first character of each split and the length of the split part.

    Parameters:
    text (str): The original text to be split.
    chars_to_split (list): A list of characters at which to split the text.

    Returns:
    dict: A dictionary with split characters as keys and the following text as values,
          including the offset and length of the split part.
    """
    # Split the text at the specified characters
    split_text,special_chars = split_text_at_characters(text, chars_to_split)
    # Initialize an empty dictionary to hold the result
    result_dict = {}

    # Initialize the current index
    i = 0
    offset = 0
    for char in special_chars:
        if i < len(special_chars)-1:
            char = special_chars[i]
            span = split_text[i]
            result_dict[char] = {
                        'text': split_text[i][:-1],
                        'offset': offset,
                        'length': len(split_text[i][:-1])
                    }
            offset = offset + len(split_text[i])
            i += 1

        else:
            char = special_chars[i]
            span = split_text[i]
            result_dict[char] = {
                        'text': split_text[i],
                        'offset': offset,
                        'length': len(split_text[i])
                    }
            offset = offset + len(split_text[i])
            i += 1
    return result_dict

def decode_and_create_updated_files(input_folder, output_folder):
    """
    # Example usage: Provide the paths to the input and output folders
    input_folder_path = '/home/STual/inference/res3'
    output_folder_path = '/home/STual/inference/res3'
    decode_and_create_updated_files(input_folder_path, output_folder_path)
    """
    
    # Ensure the output folder exists; create it if necessary
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Iterate over all files in the specified input folder
    for filename in os.listdir(input_folder):
        input_file_path = os.path.join(input_folder, filename)

        # Check if the file is a JSON file
        if filename.endswith('.json'):
            # Load the JSON content from the input file
            with open(input_file_path, 'r', encoding='utf-8') as input_file:
                data = json.load(input_file)
                
                # Create a new filename for the output file
                output_filename = f"{filename}"
                output_file_path = os.path.join(output_folder, output_filename)

                # Save the modified JSON to the new output file
                with open(output_file_path, 'w', encoding='utf-8') as output_file:
                    json.dump(data, output_file, ensure_ascii=False, indent=2)
                    print(f"Created {filename} with updated 'text' key")