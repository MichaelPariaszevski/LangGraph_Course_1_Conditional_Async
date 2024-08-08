from typing import TypedDict 

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver # ModuleNotFoundError: No module named 'langgraph.checkpoint.sqlite'

class State(TypedDict): 
    input: str 
    user_feedback: str
    
def step_1(state: State) -> None: 
    print("---Step 1---")
    
def human_feedback(state: State) -> None: 
    print("---Human Feedback---") 
    
def step_3(state: State) -> None: 
    print("---Step 3---") 
    
workflow=StateGraph(State)

workflow.set_entry_point("step_1")

workflow.add_node("step_1", step_1) 

workflow.add_node("human_feedback", human_feedback) 

workflow.add_node("step_3", step_3) 

workflow.add_edge("step_1", "human_feedback") 

workflow.add_edge("human_feedback", "step_3") 

workflow.add_edge("step_3", END) 

memory=SqliteSaver.from_conn_string("checkpoints.sqlite")

graph=workflow.compile(checkpointer=memory, interrupt_before=["human_feedback"])

graph.get_graph().draw_mermaid_png(output_file_path="memorysaver_interrupts_graph.png")

if __name__ == "__main__": 
    thread={"configurable": {"thread_id": "145"}} # Essentially a session id
    
    initial_input={"input": "hello world"} 
    
    for event in graph.stream(initial_input, thread, stream_mode="values"): 
        print(event)
    
    print(graph.get_state(thread).next)
    
    user_input=input("Tell me how you want to update the state: ")
    
    graph.update_state(thread, values={"user_feedback": user_input}, as_node="human_feedback") # user_feedback is defined in our GraphState
    
    print("---State After Update---") 
    print(graph.get_state(thread))
    
    for event_2 in graph.stream(None, thread, stream_mode="values"): 
        print(event_2)