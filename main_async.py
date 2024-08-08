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
        print(f"Adding {self._value} to {state["aggregate"]}")
        return {"aggregate": [self._value]}
    
# Python has a set of built-in methods and
# __call__
# is one of them. The
# __call__
# method enables Python programmers to write classes where the instances behave like functions and can be called like a function. When the instance is called as a function; if this method is defined,
# x(arg1, arg2, ...)
# is a shorthand for
# x.__call__(arg1, arg2, ...)

workflow=StateGraph(State)

if __name__ == "__main__": 
    print("Hello Async Graph")