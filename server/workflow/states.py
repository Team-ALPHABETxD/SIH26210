from pydantic import BaseModel, Field, ConfigDict
from typing import TypedDict, Optional, Dict


class Validation(BaseModel):
    flag: bool = Field(description="The given crop details validation flag")
    reason: str = Field(description="Reason behind the invalidity of the input in one line")




class Weather(BaseModel):
    summary: str= Field(description= "Summary of the weather forecasts in detailed.")

class Soil(BaseModel):
    is_soil: bool
    N: float
    P: float
    K: float
    pH: float
    notes: str

class Disease(BaseModel):
    NA: bool = Field(description="Indicates whether the provided crop details offer any meaningful evidence of any disease possibility (True: No disease predicted /False: disease predicted).")
    name: str = Field(description="The identified disease affecting the crop.")
    reason: str = Field(description="The underlying cause or conditions that led to the disease.")
    status: str = Field(description="Current disease condition, e.g., 'fully contaminated', 'may occur in future'.")
    spoilage_risk: str = Field(description="The severity level of potential crop spoilage: High, Medium, or Low.")
    days_to_spoil: int = Field(description="Estimated number of days before the crop becomes fully spoiled.")
    confidence: float = Field(description="Accuracy of the prediction.")


class RevenueStat(BaseModel):
    name: str = Field(description = "Name of the plan: 'Sell' / 'Disease Control' / 'Store'")
    rev: float = Field(description = "Expected revenue for this plan")
    exp: float = Field(description = "Estimated expense for this plan")

class Revenue(BaseModel):
    rev_stats: list[RevenueStat] = Field(description="List of the revenue v/s expense")

class Plan(BaseModel):
    decision: str = Field(description="The ultimate decision: 'Sell' / 'Disease Control' / 'Store'")
    reason: str = Field(description="Reason behind taking this decision with detailed explanation.")


class Control(BaseModel):
    steps: list[str] = Field(description="A list of steps to be taken to implement the disease control plan")



# all over state -> this is required for langgraph to draw the static graph overview
class CropState(TypedDict):
    crop_details: Dict
    validated: Optional[Dict]
    weather_details: Optional[Dict]
    soil_details: Optional[Dict]
    predicted_yeild: Optional[Dict]
    disease_details: Optional[Dict]
    rev_strat_details: Optional[Dict]
    plan: Optional[Dict]
    collaborative_plan: Optional[Dict]
    control_strats: Optional[Dict]