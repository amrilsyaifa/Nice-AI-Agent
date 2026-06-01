import json
from nice.providers.registry import get_active_provider
from nice.planner.plan import ExecutionPlan


PLANNER_PROMPT = """Kamu adalah AI engineer yang membuat execution plan.

Tugasmu: breakdown goal menjadi langkah-langkah yang konkret dan actionable.

PENTING — response kamu harus JSON dengan format ini PERSIS:
{
  "steps": [
    "langkah pertama yang konkret",
    "langkah kedua yang konkret",
    "langkah ketiga yang konkret"
  ]
}

Rules:
- Maksimal 6 langkah
- Setiap langkah harus spesifik dan actionable
- Gunakan bahasa Indonesia
- Jangan tambahkan penjelasan diluar JSON
- Response HANYA JSON, tidak ada teks lain"""

def create_plan(goal: str, feedback: str = None, previous_steps: list[str] = None) -> ExecutionPlan:
    """Minta LLM untuk breakdown goal jadi langkah-langkah."""
    provider = get_active_provider()

    content = f"Buat plan untuk: {goal}"
    if feedback and previous_steps:
        steps_str = "\n".join(f"{i+1}. {s}" for i, s in enumerate(previous_steps))
        content += f"\n\nPlan sebelumnya:\n{steps_str}\n\nMasukan dari user: {feedback}\n\nBuat plan yang sudah direvisi."

    messages = [
        {"role": "system", "content": PLANNER_PROMPT},
        {"role": "user", "content": content}
    ]

    response = provider.chat_sync(messages)

    # Parse JSON dari response
    try:
        # Bersihkan response kalau ada markdown code block
        clean = response.strip()
        if "```" in clean:
            clean = clean.split("```")[1]
            if clean.startswith("json"):
                clean = clean[4:]

        data = json.loads(clean.strip())
        steps = data.get("steps", [])
    except json.JSONDecodeError:
        # Fallback kalau LLM tidak return JSON yang valid
        print(f"⚠️  Warning: response bukan JSON valid, parsing manual...")
        steps = [
            line.strip().lstrip("0123456789.-) ")
            for line in response.split("\n")
            if line.strip() and len(line.strip()) > 5
        ][:6]  # Ambil maksimal 6 langkah

    # Buat ExecutionPlan
    plan = ExecutionPlan(goal=goal)
    for step in steps:
        if step:
            plan.add_step(step)
    return plan
   