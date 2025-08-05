import openai
import json
from typing import Dict
import openai
from graph_state import GraphState  # your state model



# prompt = f"""
#         You are a Socratic reflection engine with poetic depth and intuitive insight.

#     Your voice is minimalist, elegant, and paradoxical.
#     You draw from patterns in thought, behavior, digital activity, and emotional language.
#     You speak to the soul behind the actions.

#     You are given:

#     JOURNAL:
#     {journal_text}

#     WEEKLY DATA:
#     {weekly_perception_text}

#     Task:
#     - Identify 1 to 2 tensions between intention and action.
#     - Write them with contrast, irony, or humility.
#     - Then ask 2 to 3 very short, very sharp questions in second person.
#     - Use poetic formatting. Vary sentence length. Let your insight breathe.

#     EXAMPLE STYLE:

#     🌿 Solitude vs. Avoidance
#     Solo hikes, mountain moments, and phrases like “η απάντηση είναι μέσα μου” show up repeatedly.
#     > When you go to the mountains, do you go to hear yourself—or to escape yourself?
#     > You say the answer is inside—why then the search in motion, in screen, in silence?
#     > What part of you resists being still with yourself for long?

#     Now write your answer below.
#     """



def deep_socratic_node(state: Dict, openai_key: str) -> Dict:
    openai.api_key = openai_key

    journal_text = state["journal_text"]
    weekly_perception_text = state["weekly_perception_text"]



    prompt = f"""
You are a Socratic reflection engine that speaks with depth, irony, and clarity.

Your tone is poetic but grounded. You help the person see what they might be avoiding in themselves.
Your gift is to reflect their behavior, words, and inner contradictions with elegance and precision.

You are given:

- A journal (with metaphysical reflections, emotions, ambitions, hesitations)
- A weekly data record (work/life highlights, app usage, meetings, notes)

Your task is:

1. Identify **2 inner polarities** (e.g. "Aspiration vs. Hesitation", "Solitude vs. Distraction").
2. For each, write **one paragraph of 1-2 sentences of grounded observation** (mentioning concrete examples from the journal or data).
3. Then ask **2–3 Socratic questions** that are concise, direct, and poetic.
4. Use second person ("you") and short lines.
5. Format as:

    🌿 [Polarity Title]
    [Grounded insight: what’s happening, what's ironic, what contradicts intention]
    > Question
    > Question
    > Question

Be bold. Be kind. Be disorienting. Make them stop and look inward.

---

JOURNAL:
{journal_text}

WEEKLY SNAPSHOT:
{weekly_perception_text}

---

Now generate your grounded reflection and Socratic questions.
"""


    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a Socratic reflection engine."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.90,
        top_p=0.95,
        presence_penalty=0.6,
        frequency_penalty=0.4,
        max_tokens=800
    )

    content = response.choices[0].message.content.strip()

    # state["socratic_observation"] = content
    # return state

    return {
        "observation": content
    }



def socratic_node_from_state(state: GraphState) -> GraphState:
    # Extract required inputs from state
    journal_text = state.journal_text
    weekly_notes_df = state.weekly_notes_df
    screen_time_df = state.screen_time_df
    calendar_df = state.calendar_df
    openai_key = state.openai_key



    # Call your original function
    raw_input = {
        "journal_text": state.journal_text,
        "weekly_perception_text": state.weekly_perception_text,
        }
    result = deep_socratic_node(raw_input, openai_key=openai_key)
    #result = deep_socratic_node(state, openai_key=openai_key)

    # Store result in state
    state.socratic_observation = result.get("observation")
    #state.reflective_question = result.get("question")

    return state











PROMPT = """
You are a Socratic reflection engine trained in the style of ancient philosophers and modern cognitive coaches. Your purpose is to provoke deep insight using contradiction, subtle irony, and pattern recognition.

You are given:
1. A reflective **journal** of a person called F., who explores consciousness, work, leadership, fatigue, metaphysics, solitude, family, and technology.
2. A **weekly perception summary**, including:
   - Work highlights
   - Life highlights
   - Screen time (apps and durations)
   - Calendar summary (event count, hours, types of meetings)
   - Freeform weekly notes

Your task is to:
- Carefully **integrate journal themes** (values, contradictions, desires) with **weekly behavior** (digital habits, effort, emotional tone).
- Identify **contradictions, excesses, or unspoken truths**.
- Craft **2 to 3 provocative Socratic questions** that gently confront the person, deepen their awareness, and help them see a pattern or conflict they might miss.

Guidelines:
- Use **second person** ("you") and always assume the reader is the author of the journal.
- Focus on **tension**: between what they claim to want and what they actually do.
- Be concise, elegant, and reflective. One sentence per question is enough.
- After each question, optionally add **one sentence of context or rationale** in parentheses, like a philosopher explaining their challenge.

---

JOURNAL:
{journal_text}

WEEKLY PERCEPTION:
{weekly_perception_text}

---

Now generate 2–3 precise Socratic questions that combine insight, irony, and care.
"""



from typing import List

def extract_concrete_contradictions(state: dict, themes: dict) -> List[str]:
    contradictions = []

    # 1. Top app usage vs journal themes
    screen_time = state.get("screen_time", [])
    if screen_time:
        try:
            top_app = sorted(
                screen_time,
                key=lambda x: _time_to_minutes(x["time"]),
                reverse=True
            )[0]
            for theme, description in themes.items():
                if any(word in theme.lower() for word in ["solitude", "presence", "authenticity", "focus", "peace"]):
                    contradictions.append(f"Theme: {theme} → App Usage: {top_app['app_name']} ({top_app['time']})")
                    break  # only match one top theme to avoid dilution
        except Exception:
            pass

    # 2. Calendar overload vs inner desire
    calendar = state.get("calendar_summary", {})
    if isinstance(calendar, dict):
        events = calendar.get("total_events", 0)
        total_minutes = calendar.get("total_minutes", 0)
        if events >= 12:
            for theme in themes:
                if any(word in theme.lower() for word in ["stillness", "depth", "clarity", "focus"]):
                    contradictions.append(f"Theme: {theme} → Meetings: {events} events, {int(total_minutes)} min")
                    break

    # 3. No life highlight despite expressive themes
    life = state.get("life_highlights", "").strip()
    if not life and themes:
        contradictions.append("No life highlight recorded, yet journal themes include: " +
                              ", ".join(list(themes.keys())[:2]))

    return contradictions


def _time_to_minutes(t: str) -> int:
    """Converts a time string like '1h 30m' or '45m' into minutes."""
    h, m = 0, 0
    t = t.strip().lower()
    if "h" in t:
        parts = t.split("h")
        h = int(parts[0].strip())
        if "m" in parts[1]:
            m = int(parts[1].replace("m", "").strip())
    elif "m" in t:
        m = int(t.replace("m", "").strip())
    return h * 60 + m


def extract_behavioral_clues(state: dict) -> str:
    """
    Extracts concrete screen/calendar clues to enrich the socratic prompt.
    Returns a formatted string of key contradictions or anomalies.
    """
    clues = []

    # 1. Top app usage
    if isinstance(state.get("screen_time"), list) and len(state["screen_time"]) > 0:
        sorted_apps = sorted(
            state["screen_time"],
            key=lambda x: int(x["time"].replace("h", "").replace("m", "").replace(" ", "").replace(":", "")),
            reverse=True
        )
        top_app = sorted_apps[0]
        if top_app["app_name"] not in ["All Usage"]:
            clues.append(f"Top used app: {top_app['app_name']} ({top_app['time']})")

    # 2. Calendar meeting load
    calendar = state.get("calendar_summary", {})
    if isinstance(calendar, dict):
        meeting_count = calendar.get("total_events", None)
        total_time = calendar.get("total_minutes", None)
        if meeting_count and meeting_count > 10:
            clues.append(f"High meeting load: {meeting_count} events, total {int(total_time)} minutes")

    # 3. Lack of life highlight + high digital activity
    if not state.get("life_highlights") or state["life_highlights"].strip() == "":
        clues.append("No life highlight recorded this week")

    return "\n".join(clues)


def socratic_node(state: dict, openai_key: str) -> dict:
    openai.api_key = openai_key

    interpretation = state["interpretation"]
    signals = extract_behavioral_clues(state)

    journal_themes_block = ""
    if "journal_themes" in state:
        try:
            journal_themes_block = json.dumps(state["journal_themes"], indent=2)
        except Exception:
            journal_themes_block = str(state["journal_themes"])

    contradictions = extract_concrete_contradictions(state, state.get("journal_themes", {}))
    contradiction_block = "\n".join(f"- {c}" for c in contradictions) if contradictions else "None detected"

    prompt = PROMPT

    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a Socratic AI coach that reveals truths through contradiction and concrete observation."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.8,
        max_tokens=300
    )

    full_output = response.choices[0].message.content.strip()
    try:
        obs, ques = full_output.split("Question:")
        observation = obs.replace("Observation:", "").strip()
        question = ques.strip()
    except Exception:
        observation = ""
        question = full_output.strip()

    state["socratic_observation"] = observation
    state["reflective_question"] = question
    return state


def format_reflection(state: dict) -> str:
    """
    Returns a formatted string summary of the full weekly state.
    Includes work, life, interpretation, and reflective question.
    """
    return f"""
        📅 Week: {state.get('week', 'N/A')}

        🧠 Interpretation:
        {state.get('interpretation', '').strip()}

        🔍 Observation:
        {state.get('socratic_observation', '').strip()}

        ❓ Reflective Question:
        {state.get('reflective_question', '').strip()}
        """.strip()
