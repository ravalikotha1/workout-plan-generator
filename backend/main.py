"""FastAPI app — the single endpoint that ties prompt building, the Groq
call, and response parsing together.
"""
import logging

from fastapi import FastAPI, HTTPException

from .groq_client import PlanGenerationFailedError, generate_validated_plan
from .models import WorkoutRequest, WorkoutResponse
from .prompts import SYSTEM_PROMPT, build_user_prompt

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Workout Plan Generator")


@app.post("/generate-plan", response_model=WorkoutResponse)
def generate_plan(request: WorkoutRequest) -> WorkoutResponse:
    user_prompt = build_user_prompt(request)

    try:
        plan = generate_validated_plan(SYSTEM_PROMPT, user_prompt)
    except PlanGenerationFailedError:
        # Detailed per-attempt reasons were already logged inside
        # generate_validated_plan — only a generic, user-safe message
        # crosses the HTTP boundary.
        logger.error("Giving up on plan generation for this request")
        raise HTTPException(
            status_code=502,
            detail="Unable to generate your plan right now, please try again.",
        ) from None
    except Exception:
        logger.exception("Unexpected error generating plan")
        raise HTTPException(
            status_code=500,
            detail="Unable to generate your plan right now, please try again.",
        ) from None

    disclaimer = (
        "This plan is not medical advice. Consult a healthcare "
        "professional before starting any new exercise program, "
        "especially with an existing injury or condition."
        if request.injuries
        else None
    )
    return WorkoutResponse(**plan.model_dump(), disclaimer=disclaimer)
