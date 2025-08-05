

import os
import openai
import base64
import pandas as pd
from io import StringIO
from tqdm import tqdm
from datetime import datetime, timedelta
import re

def load_image_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def parse_screentime_image(image_path: str, openai_api_key: str) -> str:
    base64_image = load_image_base64(image_path)

    openai.api_key = openai_api_key

    prompt = """
            You are a data extractor for a digital wellness agent.
            The user has uploaded a screenshot of their iPhone Screen Time weekly report.

            Extract the following structured CSV data from the image:

            Format:
            week, app_name, time

            Rules:
            - Use the week shown at the top of the image (e.g. 'Jun 23–30') as the 'week' for all rows.
            - For each app listed under 'Show Apps', extract its name and time.
            - Ignore usage categories like 'Productivity & Finance' or 'Social'.
            - Output the CSV data as plain text only — no Markdown, no backticks, no formatting, no explanations.
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
    )

    return response.choices[0].message.content.strip()


def clean_csv_output(raw_output: str) -> str:
    lines = raw_output.strip().splitlines()
    return "\n".join(line for line in lines if not line.strip().startswith("```"))


def update_week_column_from_source_file(df: pd.DataFrame) -> pd.DataFrame:
    def extract_week_from_filename(filename):
        # Extract the date part from the filename using regex
        match = re.search(r'week_(\d{2})_(\d{2})', filename)
        if not match:
            return None
        month_num, day = match.groups()
        month_num = int(month_num)
        day = int(day)

        # Use a default year (this could be improved if year is relevant)
        year = 2025
        start_date = datetime(year, month_num, day)
        end_date = start_date + timedelta(days=6)

        # Format like 'Jun 23–30'
        return f"{start_date.strftime('%b')} {start_date.day}–{end_date.day}"

    df['week'] = df['source_file'].apply(extract_week_from_filename)
    return df



# Path to your uploaded image
# image_path = "../data/screen_time/week_06_23.png"
# csv_output = parse_screentime_image(image_path, OPENAI_API_KEY)
# print(csv_output)

def parse_all_screentime_images(folder_path: str, openai_api_key: str) -> pd.DataFrame:
    all_rows = []

    for filename in tqdm(sorted(os.listdir(folder_path))):
        if filename.lower().endswith(".png"):
            image_path = os.path.join(folder_path, filename)
            try:
                csv_output = parse_screentime_image(image_path, openai_api_key)
                df = pd.read_csv(StringIO(csv_output))

                # Drop duplicate header rows if GPT outputs a header as a row
                if df.columns.tolist() == df.iloc[0].tolist():
                    df = df[1:]

                df.columns = ["week", "app_name", "time"]  # force correct columns
                df["source_file"] = filename
                all_rows.append(df)
            except Exception as e:
                print(f"Error processing {filename}: {e}")

    if all_rows:
        df_raw = pd.concat(all_rows, ignore_index=True)
        # fix also the date
        return update_week_column_from_source_file(df_raw)

    else:
        return pd.DataFrame(columns=["week", "app_name", "time", "source_file"])
