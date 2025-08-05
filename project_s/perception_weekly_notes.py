import os
import openai
import base64
import pandas as pd
import json
from datetime import datetime, timedelta
import re
import textwrap
from tqdm import tqdm


def load_image_base64(image_path: str) -> str:
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")

def extract_week_range_from_filename(filename: str, default_year=2025) -> str:
    match = re.search(r'week_(\d{2})_(\d{2})', filename)
    if not match:
        return "Unknown"
    month, day = map(int, match.groups())
    start_date = datetime(default_year, month, day)
    end_date = start_date + timedelta(days=6)
    return f"{start_date.strftime('%b')} {start_date.day}–{end_date.day}"

def parse_weekly_reflection_image(image_path: str, openai_api_key: str) -> pd.DataFrame:
    base64_image = load_image_base64(image_path)
    filename = os.path.basename(image_path)
    week_range = extract_week_range_from_filename(filename)

    client = openai.OpenAI(api_key=openai_api_key)

    prompt = f"""
    You are reading a handwritten weekly reflection journal (in Greek and English).
    Extract structured content in the following JSON format:

    {{
        "work_highlights": "...",
        "life_highlights": "...",
        "raw_notes": "..."
    }}

    - "work_highlights": summary of achievements or reflections about work.
    - "life_highlights": reflections about personal or emotional life.
    - "raw_notes": full cleaned transcript of the handwritten note.
    - The journal may contain Greek and English mixed — often in the same sentence.
  Greek is used for emotional or personal reflection, while English is often used for technical or work-related terms (e.g., "demo", "stream", "company triathlon").
  Do not translate — keep the original expression.

    Return **only** valid JSON without markdown or commentary.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {
                            "url": f"data:image/png;base64,{base64_image}"
                        }},
                    ]
                }
            ],
            max_tokens=1500,
            temperature=0.3,
        )

        # raw_output = response.choices[0].message.content.strip()
        # structured = json.loads(raw_output)

        raw_output = response.choices[0].message.content.strip()
        # Remove triple backticks if present
        if raw_output.startswith("```"):
            raw_output = re.sub(r"```(?:json)?", "", raw_output)
            raw_output = raw_output.strip("` \n")
        structured = json.loads(raw_output)


    except Exception as e:
        print(f"❌ Error parsing {filename}: {e}")
        structured = {
            "work_highlights": None,
            "life_highlights": None,
            "raw_notes": raw_output if 'raw_output' in locals() else None
        }

    return pd.DataFrame([{
        "week": week_range,
        "work_highlights": structured.get("work_highlights"),
        "life_highlights": structured.get("life_highlights"),
        "raw_notes": structured.get("raw_notes"),
        "source_file": filename
    }])


def parse_all_weekly_reflections(folder_path: str, openai_api_key: str) -> pd.DataFrame:
    all_dfs = []

    for filename in tqdm(sorted(os.listdir(folder_path))):
        if filename.lower().endswith(".png"):
            image_path = os.path.join(folder_path, filename)
            try:
                df = parse_weekly_reflection_image(image_path, openai_api_key)
                all_dfs.append(df)
            except Exception as e:
                print(f"❌ Failed to process {filename}: {e}")

    if all_dfs:
        return pd.concat(all_dfs, ignore_index=True)
    else:
        return pd.DataFrame(columns=["week", "work_highlights", "life_highlights", "raw_notes", "source_file"])
