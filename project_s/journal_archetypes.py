import openai
import pandas as pd
import json
import re

def extract_journal_archetypes(journal_df: pd.DataFrame, openai_key: str, sample_size: int = 500) -> dict:
    """
    Analyze a journal DataFrame and return emergent soul/psychological themes.

    Parameters:
    - journal_df: DataFrame with a 'content' column
    - openai_key: OpenAI API key
    - sample_size: how many recent entries to analyze (default = 50)

    Returns:
    - dict of theme name → description
    """
    openai.api_key = openai_key

    entries = journal_df.sort_values("date", ascending=False).head(sample_size)
    journal_text = "\n".join(entries["content"].tolist())

    prompt = f"""
        You are a philosophical AI trained to extract latent soul patterns from a personal journal.

        Given the journal below, identify 3–7 inner themes that emerge across the entries.

        Each theme should:
        - Be named in a word or short phrase (e.g. "Restlessness", "Desire for Meaning", "Fear of Invisibility", "Yearning for Connection", "Creative Urge", "Existential Reflection", etc)
        - Include a short description (1–2 sentences) that reflects the essence of that theme as it shows up in this person

        Avoid clinical or diagnostic labels. Use poetic, precise, human language.

        Journal:
        \"\"\"{journal_text}\"\"\"

        Return your answer in JSON format, like:
        {{
        "Theme Name 1": "Description...",
        "Theme Name 2": "Description...",
        ...
        }}
        """

    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You extract the psychological and philosophical structure behind journals."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=700
        )

        result_text = response.choices[0].message.content.strip()
        if result_text.startswith("```"):
            result_text = re.sub(r"^```json|```$", "", result_text, flags=re.MULTILINE).strip()
        return json.loads(result_text)

    except Exception as e:
        print(f"[Error] Could not parse GPT output: {e}")
        return {"raw_output": result_text}
