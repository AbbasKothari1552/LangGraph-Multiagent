from langgraph.graph import StateGraph, START, END

# import scrape subgraph state
from app.state.scrape_subgraph_state import ScrapeSubGraphState

# import agent
from app.agents.scrape_agent import scrape_agent

# initialize StateGraph with State
SubGraph_builder = StateGraph(ScrapeSubGraphState)

# add nodes
SubGraph_builder.add_node("ScraperAgent", scrape_agent)

# create workflow
SubGraph_builder.add_edge(START, "ScraperAgent")
SubGraph_builder.add_edge("ScraperAgent", END)

# compile grpah
scrape_sub_graph = SubGraph_builder.compile(
    name="ScrapeAgentSubgraph"
)


# # Get workflow Image
# from IPython.display import Image, display
# import os

# try:
#     # Fix the invalid escape sequence by using raw string or forward slashes
#     with open("scrape_sub_graph.png", "wb") as f:
#         f.write(scrape_sub_graph.get_graph().draw_mermaid_png())
# except Exception as e:
#     # This requires some extra dependencies and is optional
#     print(str(e))


