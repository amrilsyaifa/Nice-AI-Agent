from dataclasses import dataclass, field
from enum import Enum


class StepStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"


@dataclass
class Step:
    number: int
    description: str
    status: StepStatus = StepStatus.PENDING

    def mark_done(self):
        self.status = StepStatus.DONE

    def mark_failed(self):
        self.status = StepStatus.FAILED

    def mark_running(self):
        self.status = StepStatus.RUNNING

    def status_icon(self):
        icons = {
            StepStatus.PENDING: "[ ]",
            StepStatus.RUNNING: "[→]",
            StepStatus.DONE: "[✅]",
            StepStatus.FAILED: "[❌]",
        }

        return icons[self.status]

    def __str__(self):
        return f"{self.status_icon()} Step {self.number}: {self.description}"


@dataclass
class ExecutionPlan:
    goal: str
    steps: list[Step] = field(default_factory=list)

    def add_step(self, description: str):
        step = Step(number=len(self.steps) + 1, description=description)
        self.steps.append(step)

    def pending_steps(self) -> list[Step]:
        return [step for step in self.steps if step.status == StepStatus.PENDING]

    def is_complete(self) -> bool:
        return all(step.status == StepStatus.DONE for step in self.steps)

    def display(self):
        print(f"\n📋 Plan: {self.goal}")
        print("-" * 50)
        for step in self.steps:
            print(f"  {step}")
        print()
