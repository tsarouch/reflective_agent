import os
import base64
import openai
from tqdm import tqdm
import re
import json
from datetime import datetime
from babel.dates import parse_date
import pandas as pd

def load_image_base64(image_path: str) -> str:
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")

def parse_journal_image(image_path: str, openai_api_key: str) -> str:
    base64_image = load_image_base64(image_path)
    openai.api_key = openai_api_key

    prompt = """
        You are transcribing a handwritten Greek personal journal.
        Extract everything you can read, even if handwriting is messy.

        If you find a date (like '27 Ιουλίου', '2025-07-27', or similar), use it as a section header:
        === 27 Ιουλίου 2025 ===

        Then write the full content below.
        Preserve line breaks if meaningful. Do not add any explanation.
    """

    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {
                    "url": f"data:image/png;base64,{base64_image}"
                }}
            ]}
        ],
        max_tokens=1500,
        temperature=0.3,
    )

    return response.choices[0].message.content.strip()


def parse_all_journal_images(folder_path: str, openai_api_key: str) -> str:
    all_texts = []

    for filename in tqdm(sorted(os.listdir(folder_path))):
        if filename.lower().endswith(".png"):
            image_path = os.path.join(folder_path, filename)
            try:
                entry = parse_journal_image(image_path, openai_api_key)
                all_texts.append(entry)
            except Exception as e:
                print(f"Error in {filename}: {e}")

    return "\n\n".join(all_texts)



import re
import json
from datetime import datetime
from babel.dates import parse_date
# Greek month name map (normalized form → month number)
GREEK_MONTHS = {
    'Ιανουαρίου': 1,
    'Φεβρουαρίου': 2,
    'Μαρτίου': 3,
    'Απριλίου': 4,
    'Μαΐου': 5,
    'Ιουνίου': 6,
    'Ιουλίου': 7,
    'Αυγούστου': 8,
    'Σεπτεμβρίου': 9,
    'Οκτωβρίου': 10,
    'Νοεμβρίου': 11,
    'Δεκεμβρίου': 12,
}

def parse_date_greek(raw_date: str, default_year=2025):
    match = re.match(r'(\d{1,2})\s+([Α-Ωα-ωΐΰάέίόύήώ]+)', raw_date)
    if not match:
        raise ValueError(f"Unrecognized date format: '{raw_date}'")

    day = int(match.group(1))
    month_name = match.group(2).strip()
    month = GREEK_MONTHS.get(month_name)

    if not month:
        raise ValueError(f"Unknown Greek month: {month_name}")

    return datetime(default_year, month, day)

def parse_date_flexible(raw_date: str, default_year=2025):
    raw_date = raw_date.strip()

    # Try Greek format first
    match = re.match(r'(\d{1,2})\s+([Α-Ωα-ωΐΰάέίόύήώ]+)', raw_date)
    if match:
        day = int(match.group(1))
        month_name = match.group(2).capitalize()
        month = GREEK_MONTHS.get(month_name)
        if month:
            return datetime(default_year, month, day)

    # Try English format: '5 May'
    match = re.match(r'(\d{1,2})\s+([A-Za-z]+)', raw_date)
    if match:
        try:
            return datetime.strptime(f"{raw_date} {default_year}", "%d %B %Y")
        except ValueError:
            pass

    # Try numeric format: 24/2/95 → assume it's DD/MM/YY
    match = re.match(r'(\d{1,2})/(\d{1,2})/(\d{2,4})', raw_date)
    if match:
        day, month, year = map(int, match.groups())
        year = 2000 + year if year < 100 else year
        return datetime(year, month, day)

    raise ValueError(f"Unrecognized date format: '{raw_date}'")

def parse_journal_text(file_path: str, default_year=2025):
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    # Match === 6 Ιανουαρίου === followed by content
    pattern = r"===\s*(.*?)\s*===\s*([\s\S]*?)(?=\n===|$)"
    matches = re.findall(pattern, text)

    results = []

    for raw_date, content in matches:
        try:
            parsed_date = parse_date_flexible(raw_date, default_year)
            iso_date = parsed_date.strftime("%Y-%m-%d")
            results.append({
                "date": iso_date,
                "content": content.strip()
            })
        except Exception as e:
            print(f"❌ Error parsing '{raw_date}': {e}")

    return results

def save_to_json(data, output_path="journal_entries.json"):
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ Saved {len(data)} entries to {output_path}")



def read_json_to_dataframe(file_path):
    """
    Reads a JSON file and converts it into a pandas DataFrame.

    Parameters:
        file_path (str): Path to the JSON file.

    Returns:
        pd.DataFrame: DataFrame containing the JSON data.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # If the JSON is a list of records, convert directly to DataFrame
    if isinstance(data, list):
        df = pd.DataFrame(data)
    # If the JSON is a dictionary, you might need to adjust this
    elif isinstance(data, dict):
        df = pd.json_normalize(data)
    else:
        raise ValueError("Unsupported JSON format")

    return df

# Example usage:
# parsed = parse_journal_text("my_journal.txt")
# save_to_json(parsed)
