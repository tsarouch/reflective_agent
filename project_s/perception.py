import pandas as pd
from datetime import datetime
from graph_state import GraphState

# --- Utilities ---
def parse_week_range(week_str):
    """Convert 'Jun 23–29' to start and end datetime objects."""
    try:
        parts = week_str.replace("–", "-").split("-")
        start = datetime.strptime(parts[0].strip(), "%b %d")
        end_day = int(parts[1].strip())
        year = 2025  # can make dynamic if needed
        start = start.replace(year=year)
        end = start.replace(day=end_day)
        return start, end
    except Exception as e:
        print(f"Error parsing week string '{week_str}': {e}")
        return None, None


def summarize_calendar(calendar_df, start, end):
    """Summarize calendar events for the given week."""
    filtered = calendar_df[
        (pd.to_datetime(calendar_df["start"]) >= start) &
        (pd.to_datetime(calendar_df["start"]) <= end)
    ]
    if filtered.empty:
        return "No events scheduled."

    summary = {
        "total_events": len(filtered),
        "total_minutes": filtered["duration_min"].sum(),
        "time_of_day_breakdown": filtered["time_of_day"].value_counts().to_dict(),
        "meeting_type_distribution": filtered["type"].value_counts().to_dict()
    }
    return summary


# --- Main function ---
def perception_node(
    weekly_notes_df: pd.DataFrame,
    screen_time_df: pd.DataFrame,
    calendar_df: pd.DataFrame
) -> pd.DataFrame:

    weekly_contexts = []

    for _, row in weekly_notes_df.iterrows():
        week_str = row["week"]
        start_date, end_date = parse_week_range(week_str)
        if start_date is None:
            continue

        # Screen time for the week
        screen_subset = screen_time_df[screen_time_df["week"] == week_str]
        screen_data = screen_subset[["app_name", "time"]].to_dict(orient="records")

        # Calendar summary
        calendar_summary = summarize_calendar(calendar_df, start_date, end_date)

        weekly_contexts.append({
            "week": week_str,
            "work_highlights": row["work_highlights"],
            "life_highlights": row["life_highlights"],
            "weekly_notes_raw": row["raw_notes"],
            "screen_time": screen_data,
            "calendar_summary": calendar_summary
        })

    result_df = pd.DataFrame(weekly_contexts)
    return result_df

def perception_node_from_state(state: GraphState) -> GraphState:

    if state.weekly_notes_df is None:
        raise ValueError("weekly_notes_df is missing from GraphState.")
    if state.screen_time_df is None:
        raise ValueError("screen_time_df is missing from GraphState.")
    if state.calendar_df is None:
        raise ValueError("calendar_df is missing from GraphState.")

    weekly_notes_df = state.weekly_notes_df
    screen_time_df = state.screen_time_df
    calendar_df = state.calendar_df

    # perception = perception_node(weekly_notes_df, screen_time_df, calendar_df)
    # After calling the real perception_node
    perception_df = perception_node(weekly_notes_df, screen_time_df, calendar_df)

    # Convert to dict if it's a DataFrame (e.g., via .to_dict())
    if isinstance(perception_df, pd.DataFrame):
        perception_dict = perception_df.to_dict(orient="records")[0]  # single row
    else:
        perception_dict = perception_df  # already a dict

    # Assign to state
    state.perception = perception_dict

    return state
