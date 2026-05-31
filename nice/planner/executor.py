from nice.planner.plan import ExecutionPlan
from nice.providers.registry import get_active_provider
from nice.tools.registry import TOOL_DEFINITIONS

EXECUTOR_PROMPT = """Kamu adalah AI engineer yang mengeksekusi satu langkah dari sebuah plan.

Kamu punya tools: read_file, write_file, run_command, list_directory.

Eksekusi langkah yang diberikan menggunakan tools yang sesuai.
Jawab dalam Bahasa Indonesia.
Setelah selesai, laporkan apa yang sudah dilakukan."""

def execute_step(step_description: str, goal: str) -> tuple[bool, str]:
    """
    Eksekusi satu step dari plan.
    Return: (success, output)
    """
    provider = get_active_provider()
    messages = [
        {"role": "system", "content": EXECUTOR_PROMPT},
        {
            "role": "user",
            "content": f"""
            Goal keseluruhan: {goal}

            Langkah yang harus dikerjakan sekarang:
            {step_description}

            Eksekusi langkah ini sekarang."""
        }
    ]

    try:
        result = provider.chat_sync(messages, tools=TOOL_DEFINITIONS)
        return True, result
    except Exception as e:
        return False, str(e)
    
def execute_plan(plan: ExecutionPlan) -> ExecutionPlan:
    """Eksekusi semua step dalam plan satu per satu."""
    print(f"\n🚀 Memulai eksekusi plan: {plan.goal}\n")

    for step in plan.steps:
        print(f"\n{'='*50}")
        print(f"⚡ {step}")
        print('='*50)

        step.mark_running()
        success, output = execute_step(step.description, plan.goal)

        if success:
            step.mark_done()
            print(f"\n✅ Selesai: {output[:200]}...")
        else:
            step.mark_failed()
            print(f"\n❌ Gagal: {output}")
            # Tanya user mau lanjut atau stop
            choice = input("\nStep gagal. Lanjut ke step berikutnya? (y/n): ")
            if choice.lower() != "y":
                print("🛑 Eksekusi dihentikan.")
                break
    return plan
        