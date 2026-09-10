"""Pydantic schemas for the workout plan generator API."""
from enum import Enum
from pydantic import BaseModel, Field

# --- LLM input schema ---------------------------------------------------
# What streamlit provides to FastAPI: the request body for the /generate endpoint. 
# This is a Pydantic model, so FastAPI will validate it automatically and return a 422, if the request body doesn't match the schema. 
class FitnessGoal(str, Enum):
    BUILD_MUSCLE = "Build muscle"
    LOSE_FAT = "Lose fat"
    GENERAL_FITNESS = "General fitness"
    IMPROVE_ENDURANCE = "Improve endurance"


class ExperienceLevel(str, Enum):
    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    ADVANCED = "Advanced"


class EquipmentAccess(str, Enum):
    NONE = "No equipment"
    DUMBBELLS = "Home dumbbells"
    FULL_GYM = "Full gym"


class WorkoutRequest(BaseModel):
    goal: FitnessGoal
    experience: ExperienceLevel
    equipment: EquipmentAccess
    days: int = Field(ge=1, le=7)
    injuries: str | None = None


# --- LLM output schema ---------------------------------------------------
# What llm returns as JSON. 

class Exercise(BaseModel):
    name: str
    sets: int
    reps: int


class DayPlan(BaseModel):
    day_number: int = Field(ge=1, le=7)
    exercises: list[Exercise]


class LLMPlanOutput(BaseModel):
    days: list[DayPlan] = Field(min_length=1, max_length=7)


# --- API response schema --------------------------------------------------
# What FastAPI returns to Streamlit: LLMPlanOutput's fields plus `disclaimer`

class WorkoutResponse(LLMPlanOutput):
    disclaimer: str | None = None