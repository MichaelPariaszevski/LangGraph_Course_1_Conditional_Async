import operator
from typing import Annotated, Any, Sequence

from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(), override=True)


class State(TypedDict):
    aggregate: Annotated[list, operator.add]
    which: str


class ReturnNodeValue:
    def __init__(self, node_secret: str):
        self._value = node_secret  # private attribute

    def __call__(
        self, state: State
    ) -> Any:  # https://www.geeksforgeeks.org/__call__-in-python/
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


def route_bc_or_cd(state: State) -> Sequence[str]:
    if state["which"] == "cd":
        return ["c", "d"]
    return ["b", "c"]


workflow = StateGraph(State)

workflow.set_entry_point(key="a")

workflow.add_node("a", ReturnNodeValue("I am node: a"))
workflow.add_edge(start_key=START, end_key="a")
workflow.add_node("b", ReturnNodeValue("I am node: b"))
workflow.add_node("c", ReturnNodeValue("I am node: c"))
workflow.add_node("d", ReturnNodeValue("I am node: d"))
workflow.add_node("e", ReturnNodeValue("I am node: e"))

intermediates = ["b", "c", "d"]

workflow.add_conditional_edges(
    source="a", path=route_bc_or_cd, path_map=intermediates
)  # Even though the function route_bc_or_cd only returns ["c", "d"] or ["b", "c"], here, path_map is needed to make the graph illustration more readable

for node in intermediates:
    workflow.add_edge(start_key=node, end_key="e")

workflow.add_edge(start_key="e", end_key=END)

graph = workflow.compile()

graph.get_graph().draw_mermaid_png(output_file_path="conditional_async_graph.png")

if __name__ == "__main__":
    print("Hello Async Graph")
    graph.invoke(
        input={"aggregate": [], "which": ""}, config={"thread_id": "id_1"}
    )  # Node a, then node b and c (asynchronously), then node e
    print("-" * 100)
    graph.invoke(
        input={"aggregate": [], "which": "cd"}, config={"thread_id": "id_1"}
    )  # Node a, then node c and d (asynchronously), then node e
    print("-" * 100)

    example_state = State(aggregate=["example_list"], which="example_str")

    print(example_state)

    graph.invoke(input=example_state, config={"thread_id": "id_1"})  # this also works

    # The state after node "a" and just before node "b" and node "c" is, in both instances, ['I am node: a'] incdicating that
    # the node "a" "split" into two and ran node "b" and node "c" asynchronously
    
    # To make working with asynchronous nodes easier each node that is executed asynchronously should update/modify a different attribute in the State class
