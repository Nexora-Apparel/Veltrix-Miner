from pydantic import BaseModel


class LivenessResponse(BaseModel):
    status: str
    service: str
    version: str


class ReadinessResponse(BaseModel):
    status: str
    service: str
    version: str
    database: str
