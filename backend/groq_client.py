"""Groq API call + response parsing.
"""
import json
import logging

from groq import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    AuthenticationError,
    Groq,
    RateLimitError,
)
from pydantic import ValidationError

from .config import GROQ_API_KEY, GROQ_MODEL
from .models import LLMPlanOutput

logger = logging.getLogger(__name__)

client = Groq(api_key=GROQ_API_KEY)


def call_groq(system_prompt: str, user_prompt: str) -> str:
    #Send the prompts to Groq and return the raw text response.
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0, response_format={"type": "json_object"}
    )
    return response.choices[0].message.content


class MalformedPlanError(Exception):
    """Raised when Groq's response is empty, not valid JSON, or doesn't
    match LLMPlanOutput. main.py catches this specifically — see your
    retry design: this is the exception that should trigger a retry."""


def parse_response(raw_response: str) -> LLMPlanOutput:
    """Parse and validate the LLM's raw text into LLMPlanOutput."""
    # (design-bearing): empty/whitespace-only check.
    if not raw_response or not raw_response.strip():
        raise MalformedPlanError("Groq returned an empty response")

    # (design-bearing): parse as JSON, catching json.JSONDecodeError
    # and re-raising as MalformedPlanError 
    try:
        data = json.loads(raw_response)
    except json.JSONDecodeError as e:
        raise MalformedPlanError("Malformed JSON response from Groq") from e

    # (design-bearing): validate against LLMPlanOutput, catching
    # pydantic.ValidationError and re-raising as MalformedPlanError.
   
    try:
        return LLMPlanOutput.model_validate(data)
    except ValidationError as e:
        raise MalformedPlanError("Invalid workout plan structure") from e


class PlanGenerationFailedError(Exception):
    """Raised when generate_validated_plan exhausts all attempts without
    producing a valid LLMPlanOutput — whether from repeated API failures,
    repeated malformed responses, or a mix of both. main.py catches only
    this one exception and turns it into a generic 502; the specific
    reason for each failed attempt is logged here, not passed along."""


def generate_validated_plan(
    system_prompt: str, user_prompt: str, max_attempts: int = 3
) -> LLMPlanOutput:
    """Call Groq and validate its response, retrying on failure.

    Both failure modes — the API call itself failing, and Groq responding
    with malformed/invalid JSON — share one budget of `max_attempts` total
    attempts. Each attempt re-runs call_groq from scratch (retrying just
    parse_response on the same raw text can never produce a different
    result, since it's a pure function of already-fixed input).
    """
    for attempt in range(1, max_attempts + 1):
        try:
            raw = call_groq(system_prompt, user_prompt)
        except AuthenticationError:
            logger.error(
                "Groq authentication failed — check API key (attempt %s/%s)",
                attempt, max_attempts,
            )
            continue
        except RateLimitError:
            logger.error(
                "Groq rate limit exceeded (attempt %s/%s)", attempt, max_attempts
            )
            continue
        except APIConnectionError:
            logger.error(
                "Could not connect to Groq (attempt %s/%s)", attempt, max_attempts
            )
            continue
        except APITimeoutError:
            logger.error(
                "Groq request timed out (attempt %s/%s)", attempt, max_attempts
            )
            continue
        except APIStatusError as e:
            logger.error(
                "Groq API returned status %s (attempt %s/%s)",
                e.status_code, attempt, max_attempts,
            )
            continue

        try:
            return parse_response(raw)
        except MalformedPlanError as e:
            logger.warning(
                "Malformed plan from Groq (attempt %s/%s): %s",
                attempt, max_attempts, e,
            )
            continue

    raise PlanGenerationFailedError(
        f"Failed to generate a valid plan after {max_attempts} attempts"
    )
