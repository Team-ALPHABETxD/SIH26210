from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, START, END

from .prompts import *
from .tools import *
from .states import *
from .debugger import AgentDebugger, debug_agent

load_dotenv()
llm = init_chat_model("groq:llama-3.1-8b-instant")


#  AGENTS 

def validator_agent(state: CropState) -> CropState:
    crop = state["crop_details"]

    if crop["disease_detect"] and not crop["crop_img"]:
        state["validated"] = {"flag": False, "reason": "Missing crop image"}
        return state

    res = llm.with_structured_output(Validation).invoke(
        validator_prompt(crop)
    )
    state["validated"] = res.dict()
    return state


def data_agent(state: CropState) -> CropState:
    crop = state["crop_details"]
    weather = get_weather_forecast(lat=crop["lat"], lon=crop["lon"])
    res = llm.with_structured_output(Weather).invoke(
        weather_summary_prompt(weather)
    )
    # Store both the LLM-generated summary and the raw forecast data
    weather_data = res.dict()
    weather_data["forecasts"] = weather 
    state["weather_details"] = weather_data
    return state

def soil_agent(state: CropState) -> CropState:
    crop = state["crop_details"]
    soil_data = analyse_soil_img(crop["soil_img"])
    state["soil_details"] = soil_data
    return state


def yeild_predict_agent(state: CropState) -> CropState:
    state["predicted_yeild"] = predict_yeild(state["crop_details"])
    return state


def disease_detect_agent(state: CropState) -> CropState:
    res = llm.with_structured_output(Disease).invoke(
        predict_disease_prompt(state)
    )
    state["disease_details"] = res.dict()
    return state


def revenue_estimate_agent(state: CropState) -> CropState:
    res = llm.with_structured_output(Revenue).invoke(
        estimate_revenue_prompt(state)
    )
    state["rev_strat_details"] = res.dict()
    return state


def planner_agent(state: CropState) -> CropState:
    res = llm.with_structured_output(Plan).invoke(
        planner_prompt(state)
    )
    state["plan"] = res.dict()
    return state


def control_agent(state: CropState) -> CropState:
    res = llm.with_structured_output(Control).invoke(
        disease_control_prompt(state)
    )
    state["control_strats"] = res.dict()
    return state


# CONDITIONS 

def validator_cond(state: CropState) -> bool:
    return state["validated"]["flag"]

def disease_cond(state: CropState) -> bool:
    return state["crop_details"]["disease_detect"]

def planner_cond(state: CropState) -> str:
    return state["plan"]["decision"]


# Graph

def build_graph(debugger: AgentDebugger):

    graph = StateGraph(CropState)

    graph.add_node(
        "validator_agent",
        debug_agent("validator_agent", debugger)(validator_agent)
    )
    graph.add_node(
        "data_agent",
        debug_agent("data_agent", debugger)(data_agent)
    )
    graph.add_node(
        "soil_agent",
        debug_agent("soil_agent", debugger)(soil_agent)
    )
    graph.add_node(
        "yeild_predict_agent",
        debug_agent("yeild_predict_agent", debugger)(yeild_predict_agent)
    )
    graph.add_node(
        "disease_detect_agent",
        debug_agent("disease_detect_agent", debugger)(disease_detect_agent)
    )
    graph.add_node(
        "revenue_estimate_agent",
        debug_agent("revenue_estimate_agent", debugger)(revenue_estimate_agent)
    )
    graph.add_node(
        "planner_agent",
        debug_agent("planner_agent", debugger)(planner_agent)
    )
    graph.add_node(
        "control_agent",
        debug_agent("control_agent", debugger)(control_agent)
    )

    graph.add_edge(START, "validator_agent")
    graph.add_conditional_edges(
        "validator_agent",
        validator_cond,
        {True: "data_agent", False: END}
    )
    graph.add_conditional_edges(
        "data_agent",
        disease_cond,
        {True: "disease_detect_agent", False: "soil_agent"}
    )
    graph.add_edge("soil_agent", "disease_detect_agent")
    graph.add_edge("disease_detect_agent", "revenue_estimate_agent")
    graph.add_edge("revenue_estimate_agent", "yeild_predict_agent")
    graph.add_edge("yeild_predict_agent", "planner_agent")
    graph.add_conditional_edges(
        "planner_agent",
        planner_cond,
        {
            "Sell": END,
            "Store": END,
            "Disease Control": "control_agent",
        },
    )

    return graph.compile()