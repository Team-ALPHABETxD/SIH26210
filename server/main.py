from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict, Field

from workflow.graphs import build_graph


class CropDetails(BaseModel):
	model_config = ConfigDict(extra="allow")

	item: str = Field(alias="Item")
	average_rain_fall_mm_per_year: float
	avg_temp: float
	crop_img: str | None = None
	current_date: str
	disease_detect: bool = False
	growth: str
	lat: float
	lon: float
	pesticides_tonnes: float
	soil_img: str
	sowing_date: str
	storage_availability: str


class ReportRequest(BaseModel):
	temp: float
	humidity: float
	moisture: float
	dryness: float
	crop_details: CropDetails


class SensorData(BaseModel):
	device_id: str = "esp32-1"
	temp: float
	humidity: float
	moisture: float
	dryness: float


app = FastAPI(title="Krisy Crop Report API")
app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=False,
	allow_methods=["*"],
	allow_headers=["*"],
)

latest_sensor_data: dict[str, SensorData] = {}


@app.post("/sensor-data")
def receive_sensor_data(sensor_data: SensorData) -> dict[str, Any]:
	latest_sensor_data[sensor_data.device_id] = sensor_data
	return {
		"message": "Sensor data received",
		"data": sensor_data.model_dump(),
	}


@app.get("/sensor-data/{device_id}")
def get_sensor_data(device_id: str) -> dict[str, Any]:
	sensor_data = latest_sensor_data.get(device_id)
	if sensor_data is None:
		raise HTTPException(status_code=404, detail="No sensor data found")
	return sensor_data.model_dump()


@app.post("/generate-report")
def generate_report(request: ReportRequest) -> dict[str, Any]:
	try:
		from workflow.debugger import AgentDebugger

		graph = build_graph(AgentDebugger())
		crop_details = request.crop_details.model_dump(by_alias=True)
		crop_details["sensor_data"] = {
			"temp": request.temp,
			"humidity": request.humidity,
			"moisture": request.moisture,
			"dryness": request.dryness,
		}
		state = graph.invoke({"crop_details": crop_details})
		return state
	except Exception as exc:
		raise HTTPException(status_code=500, detail=f"Report generation failed: {exc}") from exc
