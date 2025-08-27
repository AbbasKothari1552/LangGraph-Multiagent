from langgraph.graph import StateGraph, START, END

# import agents
from app.agents.search_agent import search_agent
from app.agents.product_aggregator_agent import product_aggregator
# from app.agents.scrape_agent import scrape_agent
# import scrape sub_graph
from app.workflow.scrape_subgraph_workflow import scrape_sub_graph

# import product subgraph state
from app.state.product_subgraph_state import SubGraphState

from app.conditional_edges import fanout_scrape_node

SubGraph_builder = StateGraph(SubGraphState)

# add nodes
SubGraph_builder.add_node("SearchAgent", search_agent)
SubGraph_builder.add_node("ScrapeSubgraph", scrape_sub_graph)
SubGraph_builder.add_node("ProductAggregator", product_aggregator)
# SubGraph_builder.add_node("ScraperAgent", scrape_agent)

# create workflow
SubGraph_builder.add_edge(START, "SearchAgent")

SubGraph_builder.add_conditional_edges(
    "SearchAgent",
    fanout_scrape_node,
    ["ScrapeSubgraph"]
)

# SubGraph_builder.add_edge("SearchAgent", "ScraperAgent")
SubGraph_builder.add_edge("ScrapeSubgraph", "ProductAggregator")
SubGraph_builder.add_edge("ProductAggregator", END)

# compile graph
sub_graph = SubGraph_builder.compile(
    name="ProductSubgraph"
)



# # Get workflow Image
# from IPython.display import Image, display
# import os

# try:
#     # Fix the invalid escape sequence by using raw string or forward slashes
#     with open("sub_graph.png", "wb") as f:
#         f.write(sub_graph.get_graph().draw_mermaid_png())
# except Exception as e:
#     # This requires some extra dependencies and is optional
#     print(str(e))