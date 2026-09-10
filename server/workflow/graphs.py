import json

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, START, END

from .prompts import *
from .tools import *
from .states import *
from .debugger import AgentDebugger, debug_agent

load_dotenv()
llm = init_chat_model("groq:openai/gpt-oss-20b")


def structured_invoke(model, schema, prompt):
    try:
        return model.with_structured_output(schema).invoke(prompt)
    except Exception:
        try:
            response = model.invoke(prompt)
            content = getattr(response, "content", None)
            if content is None:
                content = str(response)

            if isinstance(content, str):
                raw = content.strip()
                if raw.startswith("```"):
                    raw = raw.strip("`\n ")
                    if raw.lower().startswith("json"):
                        raw = raw[4:].lstrip()
                try:
                    data = json.loads(raw)
                except json.JSONDecodeError:
                    data = raw
            else:
                data = content

            if isinstance(data, str):
                cleaned = data.strip()
                if not cleaned or cleaned.lower() in {"none", "null", "na", "n/a"}:
                    try:
                        return schema.model_validate({})
                    except Exception:
                        field_names = list(getattr(schema, "model_fields", {}).keys())
                        fallback = {}
                        for field_name in field_names:
                            field_type = getattr(schema.model_fields[field_name], "annotation", None)
                            if field_type is bool:
                                fallback[field_name] = False
                            elif field_type in (int, float):
                                fallback[field_name] = 0
                            elif field_type is str:
                                fallback[field_name] = ""
                            elif field_type is list:
                                fallback[field_name] = []
                            else:
                                fallback[field_name] = None
                        return schema.model_validate(fallback)
                try:
                    return schema.model_validate_json(cleaned)
                except Exception:
                    try:
                        return schema.model_validate_json(json.dumps(data))
                    except Exception:
                        field_names = list(getattr(schema, "model_fields", {}).keys())
                        if len(field_names) == 1:
                            field_name = field_names[0]
                            return schema.model_validate({field_name: cleaned})
                        return schema.model_validate({})

            if isinstance(data, dict):
                return schema.model_validate(data)

            if isinstance(data, list):
                return schema.model_validate({"rev_stats": data}) if schema.__name__ == "Revenue" else schema.model_validate({})

            raise TypeError(f"Unable to parse structured output: {type(data).__name__}: {data}")
        except Exception:
            field_names = list(getattr(schema, "model_fields", {}).keys())
            fallback = {}
            for field_name in field_names:
                field_type = getattr(schema.model_fields[field_name], "annotation", None)
                if field_type is bool:
                    fallback[field_name] = False
                elif field_type in (int, float):
                    fallback[field_name] = 0
                elif field_type is str:
                    fallback[field_name] = ""
                elif field_type is list:
                    fallback[field_name] = []
                else:
                    fallback[field_name] = None
            return schema.model_validate(fallback)


#  AGENTS 

def validator_agent(state: CropState) -> CropState:
    crop = state["crop_details"]

    if crop["disease_detect"] and not crop["crop_img"]:
        state["validated"] = {"flag": False, "reason": "Missing crop image"}
        return state

    res = structured_invoke(llm, Validation, validator_prompt(crop))
    state["validated"] = res.model_dump()
    return state


def data_agent(state: CropState) -> CropState:
    crop = state["crop_details"]
    weather = get_weather_forecast(lat=crop["lat"], lon=crop["lon"])
    res = structured_invoke(llm, Weather, weather_summary_prompt(weather))
    # Store both the LLM-generated summary and the raw forecast data
    weather_data = res.model_dump()
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
    res = structured_invoke(llm, Disease, predict_disease_prompt(state))
    state["disease_details"] = res.model_dump()
    return state


def revenue_estimate_agent(state: CropState) -> CropState:
    res = structured_invoke(llm, Revenue, estimate_revenue_prompt(state))
    state["rev_strat_details"] = res.model_dump()
    return state


def planner_agent(state: CropState) -> CropState:
    res = structured_invoke(llm, Plan, planner_prompt(state))
    state["plan"] = res.model_dump()
    return state


def control_agent(state: CropState) -> CropState:
    res = structured_invoke(llm, Control, disease_control_prompt(state))
    state["control_strats"] = res.model_dump()
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