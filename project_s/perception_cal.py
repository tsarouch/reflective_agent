import pandas as pd
from datetime import datetime

def parse_and_clean_cal_data(data_cal: str) -> pd.DataFrame:
    df_cal = pd.read_csv(data_cal)
    return compress_calendar_df(df_cal)

def compress_calendar_df(df: pd.DataFrame) -> pd.DataFrame:
    # Combine Start Date and Start Time into datetime
    df['start_datetime'] = pd.to_datetime(df['Start Date'] + ' ' + df['Start Time'])
    df['end_datetime'] = pd.to_datetime(df['End Date'] + ' ' + df['End Time'])

    # Calculate duration in minutes
    df['duration_min'] = (df['end_datetime'] - df['start_datetime']).dt.total_seconds() // 60

    # Time of day
    def get_time_of_day(hour):
        if 5 <= hour < 12:
            return 'Morning'
        elif 12 <= hour < 17:
            return 'Afternoon'
        elif 17 <= hour < 22:
            return 'Evening'
        else:
            return 'Night'

    df['time_of_day'] = df['start_datetime'].dt.hour.apply(get_time_of_day)

    # Simplify subject and truncate description
    df['subject'] = df['Subject'].astype(str).str.slice(0, 50)
    df['description'] = df['Description'].fillna('').astype(str).str.replace('\r\n', ' ').str.slice(0, 100)

    # Type (guess based on category or keywords)
    def classify_type(row):
        subject = row['subject'].lower()
        if 'ooo' in subject or 'out of office' in subject:
            return 'OOO'
        elif '1:1' in subject or 'one-on-one' in subject:
            return '1:1'
        elif 'standup' in subject:
            return 'Standup'
        elif 'review' in subject:
            return 'Review'
        elif 'feedback' in subject:
            return 'Feedback'
        else:
            return 'Meeting'

    df['type'] = df.apply(classify_type, axis=1)

    # Keep relevant columns
    compact_df = df[[
        'start_datetime', 'duration_min', 'time_of_day',
        'subject', 'type', 'Private', 'description'
    ]].rename(columns={
        'start_datetime': 'start',
        'Private': 'private',
        'Sensitivity': 'sensitivity'
    })

    # Optional: sort by date
    compact_df = compact_df.sort_values(by='start').reset_index(drop=True)

    return compact_df
