import operator 
from typing import Annotated, Any 

from typing_extensions import TypedDict 

from langgraph.graph import StateGraph, START, END

from dotenv import load_dotenv, find_dotenv 

load_dotenv(find_dotenv(), override=True)

class State(TypedDict): 
    aggregate: Annotated[list, operator.add]
    
class ReturnNodeValue: 
    def __init__(self, node_secret: str): 
        self._value=node_secret # private attribute
    
    def __call__(self, state: State) -> Any: # https://www.geeksforgeeks.org/__call__-in-python/
        import time
        time.sleep(1)
        print(f"Adding {self._value} to {state['aggregate']}")
        return {"aggregate": [self._value]}
    
# Python has a set of built-in methods and
# __call__
# is one of them. The
# __call__
# method enables Python programmers to write classes where the instances behave like functions and can be called like a function. 
# When the instance is called as a function; if this method is defined,
# x(arg1, arg2, ...)
# is a shorthand for
# x.__call__(arg1, arg2, ...)

workflow=StateGraph(State)

workflow.add_node("a", ReturnNodeValue("I am node: a")) 

workflow.add_edge(start_key=START, end_key="a" ) 

workflow.add_node("b", ReturnNodeValue("I am node: b")) 
workflow.add_node("c", ReturnNodeValue("I am node: c")) 
workflow.add_node('d', ReturnNodeValue("I am node: d"))

workflow.add_edge(start_key="a", end_key="b") 
workflow.add_edge(start_key="a", end_key="c") 
workflow.add_edge(start_key="b", end_key="d") 
workflow.add_edge(start_key="c", end_key="d")

workflow.add_edge(start_key="d", end_key=END)

graph=workflow.compile() 

graph.get_graph().draw_mermaid_png(output_file_path="async_graph.png")

if __name__ == "__main__": 
    print("Hello Async Graph")
    graph.invoke(input={"aggregate": []}, config={"thread_id": "id_1"})
    
    # The state after node "a" and just before node "b" and node "c" is, in both instances, ['I am node: a'] incdicating that 
    # the node "a" "split" into two and ran node "b" and node "c" asynchronously 