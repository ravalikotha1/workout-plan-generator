"""Unit tests for backend/models.py — Pydantic validation at the boundary.

Boilerplate (imports, ValidationError pattern) is filled in. Fill in the
actual assertions — they depend on the response schema you're designing.
"""
import pytest
from pydantic import ValidationError

from backend.models import (
    EquipmentAccess,
    Exercise,
    ExperienceLevel,
    FitnessGoal,
    LLMPlanOutput,
    WorkoutRequest,
    WorkoutResponse,
)


def test_valid_request_accepted():
    request = WorkoutRequest(
        goal=FitnessGoal.BUILD_MUSCLE,
        experience=ExperienceLevel.BEGINNER,
        equipment=EquipmentAccess.FULL_GYM,
        days=3,
    )
    assert request.days == 3
    assert request.injuries is None


def test_days_out_of_range_rejected():
    with pytest.raises(ValidationError):
        WorkoutRequest(
            goal=FitnessGoal.BUILD_MUSCLE,
            experience=ExperienceLevel.BEGINNER,
            equipment=EquipmentAccess.FULL_GYM,
            days=8,  # above the ge=1, le=7 bound
        )


def test_invalid_goal_value_rejected():
    with pytest.raises(ValidationError):
        WorkoutRequest(
            goal="Not a real goal",
            experience=ExperienceLevel.BEGINNER,
            equipment=EquipmentAccess.FULL_GYM,
            days=3,
        )


def test_valid_llm_plan_output_accepted():
    plan = LLMPlanOutput.model_validate(
        {
            "days": [
                {
                    "day_number": 1,
                    "exercises": [{"name": "Push-up", "sets": 3, "reps": 10}],
                }
            ]
        }
    )
    assert plan.days[0].day_number == 1
    assert plan.days[0].exercises[0].name == "Push-up"


def test_llm_plan_output_missing_exercises_rejected():
    with pytest.raises(ValidationError):
        LLMPlanOutput.model_validate({"days": [{"day_number": 1}]})


def test_llm_plan_output_empty_days_rejected():
    with pytest.raises(ValidationError):
        LLMPlanOutput.model_validate({"days": []})  # violates min_length=1


def test_day_number_out_of_range_rejected():
    with pytest.raises(ValidationError):
        LLMPlanOutput.model_validate(
            {
                "days": [
                    {
                        "day_number": 8,  # above the ge=1, le=7 bound
                        "exercises": [{"name": "Push-up", "sets": 3, "reps": 10}],
                    }
                ]
            }
        )


def test_workout_response_disclaimer_defaults_to_none():
    exercise = Exercise(name="Push-up", sets=3, reps=10)
    response = WorkoutResponse(days=[{"day_number": 1, "exercises": [exercise]}])
    assert response.disclaimer is None


def test_workout_response_accepts_disclaimer():
    response = WorkoutResponse(
        days=[{"day_number": 1, "exercises": [{"name": "Push-up", "sets": 3, "reps": 10}]}],
        disclaimer="This plan is not medical advice.",
    )
    assert response.disclaimer == "This plan is not medical advice."
