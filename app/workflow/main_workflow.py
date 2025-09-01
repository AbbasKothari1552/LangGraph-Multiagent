from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver

# import agents
from app.conditional_edges import route_from_start, route_from_intent, fanout_products_node
from app.agents.parser_agent import parser_agent
from app.agents.initent_classification_agent import intent_classifier_agent
from app.agents.product_orchestrator_agent import product_orchestrator
from app.agents.general_orchestrator_agent import general_orchestrator
from app.agents.query_verification_node import query_verification
from app.agents.spreadsheet_agent import spreadsheet_agent
# import main graph state
from app.state.main_graph_state import State

# import subgraph compiled graph
from app.workflow.product_subgraph_workflow import sub_graph

# Initialize stategraph
graph_builder = StateGraph(State)

# add nodes
graph_builder.add_node("ParserAgent", parser_agent)
graph_builder.add_node("IntentClassifier", intent_classifier_agent)
graph_builder.add_node("ProductOrchestrator", product_orchestrator)
graph_builder.add_node("GeneralOrchestrator", general_orchestrator)
graph_builder.add_node("QueryVerification", query_verification)
graph_builder.add_node("ProductSubgraph", sub_graph, return_state=True) # compiled subgraph
graph_builder.add_node("SpreadSheetAgent", spreadsheet_agent)


# Connect Nodes
graph_builder.add_conditional_edges(
    START,
    route_from_start,
    {
        "ParserAgent": "ParserAgent", 
        "IntentClassifier": "IntentClassifier"
    }
)
graph_builder.add_edge("ParserAgent", "IntentClassifier")

graph_builder.add_conditional_edges(
    "IntentClassifier",
    route_from_intent,
    {
        "ProductOrchestrator": "ProductOrchestrator",
        "GeneralOrchestrator": "GeneralOrchestrator"
    }
)

graph_builder.add_edge("GeneralOrchestrator", END)
graph_builder.add_edge("ProductOrchestrator", "QueryVerification")

graph_builder.add_conditional_edges(
    "QueryVerification",
    fanout_products_node,
    ["ProductSubgraph"]
)

# Add connection from ProductOrchestrator to ProductSubgraph
# graph_builder.add_edge("ProductOrchestrator", "ProductSubgraph")


graph_builder.add_edge("ProductSubgraph", "SpreadSheetAgent")
graph_builder.add_edge("SpreadSheetAgent", END)


# Set up memory
memory = InMemorySaver()

# Initialize graph
graph = graph_builder.compile(
    checkpointer=memory,
    name="MainGraph"
    )


# # Get workflow Image
# from IPython.display import Image, display
# import os

# try:
#     # Fix the file path to use forward slashes
#     with open("main_graph.png", "wb") as f:
#         f.write(graph.get_graph().draw_mermaid_png())
# except Exception as e:
#     # This requires some extra dependencies and is optional
#     print(str(e))



