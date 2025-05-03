import json
import re

def clean_output(raw_output: str) -> dict:
    """
    Cleans the output string by removing unwanted characters and formatting,
    and converts it to a Python dictionary.

    Args:
        raw_output (str): The raw output string to be cleaned.

    Returns:
        dict: The cleaned and parsed dictionary.
    """
    # Remove code fences and escape characters
    raw_output = raw_output.strip().replace("```json", "").replace("```", "")
    raw_output = raw_output.replace('\r', '').replace('\\', '')
    
    # Replace newlines with space and remove excess spaces
    raw_output = raw_output.replace('\n', ' ')
    # Remove duplicate and trailing spaces
    raw_output = ' '.join(raw_output.split())

    return raw_output


def finalize_output(cleaned_output: dict) -> dict:
    output ={}
    try:
        # print("Finalizing output...", cleaned_output,type(cleaned_output), flush=True)
        if type(cleaned_output) == list:
            # print('inside list', flush=True)
            cleaned_output = cleaned_output[0]
        # print('type of cleaned_output: ',type(cleaned_output), flush=True)
        for key, value in cleaned_output.items():
            # print('key: ',key, 'value: ', value, flush=True)
            if len(value) > 0:
                # If the value is a list with more than one item, join them into a single string
                output[key] = value[0].get('text','')
        return output
    except Exception as e:
        raise ValueError(f"Failed to finalize output: {e}")
    return cleaned_output

def finalize_invoice_output(cleaned_output: dict) -> dict:
    output ={}
    try:
        # print("Finalizing output...", cleaned_output,type(cleaned_output), flush=True)
        if type(cleaned_output) == list:
            # print('inside list', flush=True)
            cleaned_output = cleaned_output[0]
        # print('type of cleaned_output: ',type(cleaned_output), flush=True)
        for key, value in cleaned_output.items():
            # print('key: ',key, 'value: ', value, flush=True)
            if len(value) == 1 and key != "Items":
                # If the value is a list with more than one item, join them into a single string
                output[key] = value[0].get('text','')
            elif key == 'Items':
                output[key] = []
                # print('finding items', flush=True)
                # print(value, flush=True)
                for val in value:
                    item_data = {}
                    for k, v in val.items():
                        item_data[k] = v[0].get('text', '')
                    # print(item_data, flush=True)
                    output[key].append(item_data)
        return output
    except Exception as e:
        raise ValueError(f"Failed to finalize output: {e}")
    return cleaned_output