from pydantic import BaseModel, Field

class LoaderOutput(BaseModel):
    sale_data: list[dict] = Field(..., description="The sales data of the cars")
    model_specification: str = Field(..., description="The specification of the car model")
    class Config:
        json_schema_extra = {
            "model_specification": "银河E5 550",
            "sale_data": [{"2025WK1": 100}, {"2025WK2": 200}, {"2025WK3": 300}]
        }