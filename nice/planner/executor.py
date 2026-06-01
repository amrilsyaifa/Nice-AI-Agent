from nice.planner.plan import ExecutionPlan
from nice.providers.registry import get_active_provider
from nice.tools.registry import TOOL_DEFINITIONS

EXECUTOR_PROMPT = """You are an AI engineer executing one step from a plan.

You have tools: read_file, write_file, run_command, list_directory.

Execute the given step using the appropriate tools.
Reply in the same language as the user's input.
When done, report what you did."""

def execute_step(step_description: str, goal: str) -> tuple[bool, str]:
    """
    Execute a single plan step.
    Returns: (success, output)
    """
    provider = get_active_provider()
    messages = [
        {"role": "system", "content": EXECUTOR_PROMPT},
        {
            "role": "user",
            "content": f"""Overall goal: {goal}

Step to execute now:
{step_description}

Execute this step now."""
        }
    ]

    try:
        result = provider.chat_sync(messages, tools=TOOL_DEFINITIONS)
        return True, result
    except Exception as e:
        return False, str(e)

def execute_plan(plan: ExecutionPlan) -> ExecutionPlan:
    """Execute all steps in the plan one by one."""
    print(f"\nStarting plan execution: {plan.goal}\n")

    for step in plan.steps:
        print(f"\n{'='*50}")
        print(f"{step}")
        print('='*50)

        step.mark_running()
        success, output = execute_step(step.description, plan.goal)

        if success:
            step.mark_done()
            print(f"\nDone: {output[:200]}...")
        else:
            step.mark_failed()
            print(f"\nFailed: {output}")
            choice = input("\nStep failed. Continue to next step? (y/n): ")
            if choice.lower() != "y":
                print("Execution stopped.")
                break

    return plan
