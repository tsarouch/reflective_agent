# project_s/whisper.py

from twilio.rest import Client
from graph_state import GraphState



def send_reflective_message(
    message: str,
    account_sid: str,
    auth_token: str,
    from_number: str,
    to_number: str = None,
    recipient: str = None
) -> dict:
    """
    Sends a message using Twilio to a given recipient.

    Args:
        message (str): The reflective insight or question to send.
        account_sid (str): Twilio Account SID.
        auth_token (str): Twilio Auth Token.
        from_number (str): Your Twilio-registered sending number.
        to_number (str): Primary recipient number (e.g. WhatsApp: 'whatsapp:+123456789').
        recipient (str): Optional override recipient (alias for to_number).

    Returns:
        dict: Contains status and metadata.
    """
    client = Client(account_sid, auth_token)

    final_to_number = recipient or to_number
    if not final_to_number:
        raise ValueError("You must provide a recipient phone number.")

    response = client.messages.create(
        body=message,
        from_=from_number,
        to=final_to_number
    )

    return {
        "status": response.status,
        "sid": response.sid,
        "to": final_to_number
    }


def whisper_node(state: dict) -> dict:

    observation = state.get("socratic_observation", "").strip()
    if not observation:
        raise ValueError("socratic_observation empty.")


    # Build message body
    # message = f"🌿 Reflective Insight:\n{observation}\n\n❓Question:\n{question}"
    message = f"🌿 Reflective Insight:\n{observation}\n"

    response = send_reflective_message(
        message=message,
        account_sid=state["twilio_sid"],
        auth_token=state["twilio_token"],
        from_number=state["twilio_from"],
        to_number=state["twilio_to"]
    )

    state["whisper_status"] = {
        "status": response["status"],
        "sid": response["sid"],
        "to": response["to"],
        "preview": message[:60]
    }

    return state




def whisper_node_from_state(state: GraphState) -> GraphState:
    # Convert GraphState → raw dict
    raw_state = {
        "socratic_observation": state.socratic_observation,
        "twilio_to": state.twilio_to,
        "twilio_from": state.twilio_from,
        "twilio_sid": state.twilio_sid,
        "twilio_token": state.twilio_token,
    }

    # Run core node
    result = whisper_node(raw_state)

    # Map back to GraphState
    state.whisper_status = result.get("whisper_status")
    return state
