"""Unit tests for backend/prompts.py.
"""
from backend.models import EquipmentAccess, ExperienceLevel, FitnessGoal, WorkoutRequest
from backend.prompts import build_user_prompt


def test_user_prompt_includes_all_fields():
    request = WorkoutRequest(
        goal=FitnessGoal.LOSE_FAT,
        experience=ExperienceLevel.INTERMEDIATE,
        equipment=EquipmentAccess.DUMBBELLS,
        days=4,
    )
    prompt = build_user_prompt(request)

    assert "Lose fat" in prompt
    assert "Intermediate" in prompt
    assert "Home dumbbells" in prompt
    assert "Days: 4" in prompt


def test_user_prompt_isolates_injuries_constraint():
    request = WorkoutRequest(
        goal=FitnessGoal.GENERAL_FITNESS,
        experience=ExperienceLevel.ADVANCED,
        equipment=EquipmentAccess.NONE,
        days=2,
        injuries="lower back pain",
    )
    prompt = build_user_prompt(request)

    assert "Injuries: lower back pain" in prompt


def test_user_prompt_handles_no_injuries():
    request = WorkoutRequest(
        goal=FitnessGoal.IMPROVE_ENDURANCE,
        experience=ExperienceLevel.BEGINNER,
        equipment=EquipmentAccess.FULL_GYM,
        days=5,
    )
    prompt = build_user_prompt(request)

    assert "Injuries: No injuries reported" in prompt


def test_user_prompt_reinforces_day_count():
    request = WorkoutRequest(
        goal=FitnessGoal.BUILD_MUSCLE,
        experience=ExperienceLevel.BEGINNER,
        equipment=EquipmentAccess.FULL_GYM,
        days=6,
    )
    prompt = build_user_prompt(request)

    assert "Generate exactly 6 days." in prompt
