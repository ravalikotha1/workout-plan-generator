import os

# URL of the FastAPI backend. Overridable via env var for deployment flexibility.
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

GENERATE_ENDPOINT = f"{BACKEND_URL}/generate-plan"

# Dropdown options — hardcoded here rather than shared with the backend
# (backend stays standalone). Must match the backend's enum values EXACTLY
# — same casing/wording — or Pydantic will reject the request with a 422.
GOALS = ["Build muscle", "Lose fat", "General fitness", "Improve endurance"]
EXPERIENCE_LEVELS = ["Beginner", "Intermediate", "Advanced"]
EQUIPMENT_OPTIONS = ["No equipment", "Home dumbbells", "Full gym"]
SELECT_PLACEHOLDER = "-- Select --"
