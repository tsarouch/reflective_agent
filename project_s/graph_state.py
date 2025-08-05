from pydantic import BaseModel
from typing import Optional, Dict, Any
import pandas as pd

class GraphState(BaseModel):
    journal_text: Optional[str] = None

    weekly_perception_text: Optional[str] = None

    weekly_notes_df: Optional[pd.DataFrame] = None
    screen_time_df: Optional[pd.DataFrame] = None
    calendar_df: Optional[pd.DataFrame] = None

    perception: Optional[Dict[str, Any]] = None
    interpretation: Optional[str] = None
    socratic_observation: Optional[str] = None

    whisper_status: Optional[Dict[str, Any]] = None


    twilio_sid: Optional[str] = None
    twilio_token: Optional[str] = None
    twilio_from: Optional[str] = None
    twilio_to: Optional[str] = None

    openai_key: Optional[str] = None


    class Config:
        arbitrary_types_allowed = True
