import json

from nice.planner.plan import ExecutionPlan
from nice.providers.registry import get_active_provider

PLANNER_PROMPT = """You are an AI engineer that creates execution plans.

Your task: break down a goal into concrete, actionable steps.

IMPORTANT — your response must be EXACTLY this JSON format:
{
  "steps": [
    "first concrete step",
    "second concrete step",
    "third concrete step"
  ]
}

Rules:
- Maximum 6 steps
- Each step must be specific and actionable
- No explanations outside the JSON
- Response ONLY JSON, no other text"""


def create_plan(
    goal: str, feedback: str = None, previous_steps: list[str] = None, project_context: str = None
) -> ExecutionPlan:
    """Ask the LLM to break down a goal into steps."""
    provider = get_active_provider()

    system = PLANNER_PROMPT
    if project_context:
        system += f"\n\n## Project Context\n\n{project_context}"

    content = f"Create a plan for: {goal}"
    if feedback and previous_steps:
        steps_str = "\n".join(f"{i + 1}. {s}" for i, s in enumerate(previous_steps))
        content += f"\n\nPrevious plan:\n{steps_str}\n\nUser feedback: {feedback}\n\nCreate a revised plan."

    messages = [{"role": "system", "content": system}, {"role": "user", "content": content}]

    response = provider.chat_sync(messages)

    try:
        clean = response.strip()
        if "```" in clean:
            clean = clean.split("```")[1]
            if clean.startswith("json"):
                clean = clean[4:]

        data = json.loads(clean.strip())
        steps = data.get("steps", [])
    except json.JSONDecodeError:
        print("Warning: response was not valid JSON, parsing manually...")
        steps = [
            line.strip().lstrip("0123456789.-) ")
            for line in response.split("\n")
            if line.strip() and len(line.strip()) > 5
        ][:6]

    plan = ExecutionPlan(goal=goal)
    for step in steps:
        if step:
            plan.add_step(step)
    return plan
