"""Unit tests for backend/groq_client.py.

parse_response needs no network access — test it with canned strings.
call_groq and generate_validated_plan are mocked (patching the Groq
client / call_groq itself) so tests don't hit the real API or need a key.
"""
from unittest.mock import MagicMock, patch

import pytest
from groq import AuthenticationError

from backend.groq_client import (
    MalformedPlanError,
    PlanGenerationFailedError,
    call_groq,
    generate_validated_plan,
    parse_response,
)
from backend.models import LLMPlanOutput


def test_parse_response_valid_json():
    raw = '{"days": [{"day_number": 1, "exercises": [{"name": "Push-up", "sets": 3, "reps": 10}]}]}'
    plan = parse_response(raw)
    assert isinstance(plan, LLMPlanOutput)
    assert plan.days[0].exercises[0].name == "Push-up"


def test_parse_response_empty_string_raises():
    with pytest.raises(MalformedPlanError):
        parse_response("")


def test_parse_response_invalid_json_raises():
    with pytest.raises(MalformedPlanError):
        parse_response("this is not json")


def test_parse_response_missing_fields_raises():
    with pytest.raises(MalformedPlanError):
        parse_response('{"unexpected": "shape"}')


@patch("backend.groq_client.client")
def test_call_groq_returns_text(mock_client: MagicMock):
    mock_client.chat.completions.create.return_value.choices = [
        MagicMock(message=MagicMock(content="fake response text"))
    ]

    result = call_groq("system prompt", "user prompt")

    assert result == "fake response text"


@patch("backend.groq_client.call_groq")
def test_generate_validated_plan_retries_on_malformed_json(mock_call_groq: MagicMock):
    # First two attempts return garbage, third returns a valid plan —
    # confirms the retry loop actually re-runs call_groq, not just parsing.
    valid = '{"days": [{"day_number": 1, "exercises": [{"name": "Push-up", "sets": 3, "reps": 10}]}]}'
    mock_call_groq.side_effect = ["not json", "{}", valid]

    plan = generate_validated_plan("system prompt", "user prompt")

    assert isinstance(plan, LLMPlanOutput)
    assert mock_call_groq.call_count == 3


@patch("backend.groq_client.call_groq")
def test_generate_validated_plan_gives_up_after_max_attempts(mock_call_groq: MagicMock):
    mock_call_groq.side_effect = AuthenticationError(
        message="bad key", response=MagicMock(), body=None
    )

    with pytest.raises(PlanGenerationFailedError):
        generate_validated_plan("system prompt", "user prompt", max_attempts=3)

    assert mock_call_groq.call_count == 3
