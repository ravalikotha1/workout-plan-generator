"""Streamlit frontend for the Workout Plan Generator.
"""
import logging

import requests
import streamlit as st
from config import (
    EQUIPMENT_OPTIONS,
    EXPERIENCE_LEVELS,
    GENERATE_ENDPOINT,
    GOALS,
    SELECT_PLACEHOLDER,
)

logger = logging.getLogger(__name__)

# --- Page setup ------------------------------------------------
st.set_page_config(page_title="Workout Plan Generator", page_icon="🏋️")
st.title("Workout Plan Generator")


# --- Input widgets ------------------------------------------------------------

# st.selectbox(label, options) renders a dropdown. 
goal = st.selectbox("Fitness goal *", [SELECT_PLACEHOLDER] + GOALS)
experience = st.selectbox("Experience level *", [SELECT_PLACEHOLDER] + EXPERIENCE_LEVELS)
equipment = st.selectbox("Equipment access *", [SELECT_PLACEHOLDER] + EQUIPMENT_OPTIONS)

# st.slider(label, min_value, max_value, value) renders a draggable slider.
days = st.slider("Days per week", min_value=1, max_value=7, value=3)

# st.text_area(label, max_chars=...) renders a multi-line text box.
injuries = st.text_area(
    "Injuries or limitations (optional)",
    max_chars=500,
    placeholder="e.g. lower back pain, avoid overhead pressing",
)


# --- Client-side validation ----
submitted = st.button("Generate Plan")

if submitted:
    plan = None

    missing_fields = []
    if goal == SELECT_PLACEHOLDER:
        missing_fields.append("Fitness goal")
    if experience == SELECT_PLACEHOLDER:
        missing_fields.append("Experience level")
    if equipment == SELECT_PLACEHOLDER:
        missing_fields.append("Equipment access")
    if missing_fields:
        st.error(
            f"Please select a value for the following required fields: {', '.join(missing_fields)}"
        )
    else:
        # --- Build the request payload -------------------------------------------
        # Keys must match WorkoutRequest field names exactly.
        payload = {
            "goal": goal,
            "experience": experience,
            "equipment": equipment,
            "days": days,
            "injuries": injuries if injuries else None,
        }

        # --- Call the backend -----------------
        # `plan` holds the parsed response body

        try:
            with st.spinner("Generating your workout plan..."):
                response = requests.post(GENERATE_ENDPOINT, json=payload)

            if response.ok:
                plan = response.json()   
            elif response.status_code == 422:
                try:
                    detail = response.json().get("detail", response.text)
                except ValueError:
                  detail = response.text
                logger.warning("Validation error from backend: %s", detail)
                st.error("Something went wrong with your request. Please try later.")
            else:
                # Some other non-2xx (e.g. 500 from a failed Groq call,
                # surfaced by the backend's HTTPException handling).
                try:
                    detail = response.json().get("detail", response.text)
                except ValueError:
                    detail = response.text
                logger.error("Unexpected error from backend: %s", response.text)
                st.error("Something went wrong. Please try later.")
        except requests.exceptions.RequestException:
            logger.exception("Request to backend failed")
            st.error("Something went wrong. Please try later.")


# --- Render response ----------------------------------------------------------
if submitted and plan:

    if plan.get("disclaimer"):
        st.warning(plan["disclaimer"])

    tabs = st.tabs([f"Day {day['day_number']}" for day in plan["days"]])
    for tab, day in zip(tabs, plan["days"]):
        with tab:
            for exercise in day["exercises"]:
                st.markdown(f"exercise: {exercise['name']} sets: {exercise['sets']} reps: {exercise['reps']}")
    
