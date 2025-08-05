from langgraph.graph import StateGraph, END
from perception import perception_node_from_state
from interpretation import interpretation_node_from_state
from socratic import socratic_node_from_state
from whisper import whisper_node_from_state
from graph_state import GraphState  # assuming you saved the class above


def build_graph():
    builder = StateGraph(GraphState)

    builder.add_node("perceive", perception_node_from_state)
    builder.add_node("reflect", socratic_node_from_state)
    builder.add_node("whisper", whisper_node_from_state)

    builder.set_entry_point("perceive")
    builder.add_edge("perceive", "reflect")
    builder.add_edge("reflect", "whisper")
    builder.add_edge("whisper", END)

    return builder.compile()
