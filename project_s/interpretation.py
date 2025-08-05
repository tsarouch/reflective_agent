import openai
import os
import pandas as pd
from graph_state import GraphState


# --- Prompt Template ---
BASE_PROMPT = """
You are a reflective AI assistant that analyzes weekly patterns in work and life.

You will receive:
- A set of weekly notes with highlights
- A summary of screen time
- A summary of calendar events
- An optional sample from a personal journal (long-term memory)

Your task is to identify:
1. Frictions or tensions in the person's behavior
2. Contradictions between intention and action
3. Latent patterns (e.g. pushing creativity late, always on-call, recurring emotions)
4. Insights from screen time — what is capturing attention, and is it aligned?

Be thoughtful, not judgmental. Use simple, reflective language.

---------------------
WEEKLY INPUT:

Week: {week}
Work highlights: {work_highlights}
Life highlights: {life_highlights}
Weekly raw notes: {weekly_notes_raw}

Screen time breakdown (per app and duration) is provided below. Please reflect on:

- What apps dominate this week’s attention?
- Are these apps aligned with deep work, shallow work, or distraction?
- Are there any surprising absences or spikes?
- Is creative or purposeful time well-represented?

Screen time data:
{screen_time}

Calendar summary:
{calendar_summary}

Optional journal memory (background themes):
{journal_sample}

---------------------
Output:
Write a 3–6 sentence paragraph that reflects meaningful insights about this week. Focus on helping the person notice what they may be missing.
"""


# --- Utility to sample journal ---
def sample_journal(journal_df, n=10):
    sorted_journal = journal_df.sort_values("date", ascending=False)
    return "\n".join(sorted_journal["content"].head(n).tolist())

# --- Main callable function ---
def interpretation_node(state: dict, journal_df: pd.DataFrame, openai_key: str) -> dict:
    journal_sample = sample_journal(journal_df, n=10)

    prompt = BASE_PROMPT.format(
        week=state["week"],
        work_highlights=state["work_highlights"],
        life_highlights=state["life_highlights"],
        weekly_notes_raw=state["weekly_notes_raw"],
        screen_time=state["screen_time"],
        calendar_summary=state["calendar_summary"],
        journal_sample=journal_sample
    )

    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a perceptive and thoughtful reflection assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=300
    )

    interpretation = response.choices[0].message.content.strip()
    state["interpretation"] = interpretation
    return state


def interpretation_node_from_state(state: GraphState) -> GraphState:
    journal_text = state.journal_text
    journal_df = state.journal_df

    perception = state.perception
    openai_key = state.openai_key

    result = interpretation_node(journal_text, perception, openai_key)
    state.interpretation = result
    return state
