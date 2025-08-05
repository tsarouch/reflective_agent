import os
from dotenv import load_dotenv


# keys
# Load from .env file
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_KEY')

TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
FROM_NUMBER = os.getenv('FROM_NUMBER')
TO_NUMBER = os.getenv('PHONE_NUMBER')



# paths
DATA_SCREEN_TIME_DIR = os.path.join("..", "data", "screen_time")
DATA_SCREEN_TIME_PICKLE = os.path.join("..", "data", "screen_time", "screen_time.pickle")
DATA_CALENDAR_DIR = os.path.join("..", "data", "calendar")
DATA_CALENDAR = os.path.join("..", "data", "calendar", "CT_calendar.CSV")
DATA_CALENDAR_PICKLE = os.path.join("..", "data", "calendar", "CT_calendar.pickle")
DATA_JOURNAL_DIR = os.path.join("..", "data", "journal")
DATA_JOURNAL_TXT_FILE = os.path.join("..", "data", "journal", "journal.txt")
DATA_JOURNAL_JSON_FILE = os.path.join("..", "data", "journal", "journal.json")
DATA_JOURNAL_PICKLE = os.path.join("..", "data", "journal", "journal.pickle")

DATA_WEEKLY_NOTES_DIR = os.path.join("..", "data", "weekly_notes")
DATA_WEEKLY_NOTES_PICKLE = os.path.join("..", "data", "weekly_notes", "weekly_notes.pickle")

DATA_WEEKLY_PERCEPTION_PICKLE = os.path.join("..", "data", "weekly_perception", "weekly_perception.pickle")
DATA_WEEKLY_PERCEPTION_JSON_FILE = os.path.join("..", "data", "weekly_perception", "weekly_perception.json")
