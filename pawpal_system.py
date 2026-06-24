from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta
from enum import Enum


class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3


class Frequency(Enum):
    ONCE = "once"
    DAILY = "daily"
    WEEKLY = "weekly"
    AS_NEEDED = "as_needed"


class ConstraintType(Enum):
    TIME_BLOCK = "time_block"
    MAX_DURATION = "max_duration"
    NO_TASKS_BEFORE = "no_tasks_before"
    NO_TASKS_AFTER = "no_tasks_after"


@dataclass
class Pet:
    name: str
    species: str
    breed: str
    age: int
    tasks: list[Task] = field(default_factory=list)

    def update_info(self, name: str, species: str, breed: str, age: int) -> None:
        """Replace all pet profile fields with new values."""
        self.name = name
        self.species = species
        self.breed = breed
        self.age = age

    def add_task(self, task: Task) -> None:
        """Attach a task to this pet and set the task's back-reference."""
        task.pet = self
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove a task from this pet's task list."""
        self.tasks.remove(task)

    def get_pending_tasks(self) -> list[Task]:
        """Return all tasks that have not been marked completed."""
        return [t for t in self.tasks if not t.completed]


@dataclass
class Task:
    name: str
    duration: int  # minutes
    priority: Priority
    description: str = ""
    frequency: Frequency = Frequency.ONCE
    pet: Pet | None = None
    completed: bool = False
    start_time: time | None = None

    def update_name(self, name: str) -> None:
        """Rename this task."""
        self.name = name

    def update_duration(self, duration: int) -> None:
        """Update how long this task takes in minutes."""
        self.duration = duration

    def update_priority(self, priority: Priority) -> None:
        """Change the scheduling priority of this task."""
        self.priority = priority

    def mark_completed(self) -> None:
        """Mark this task as done."""
        self.completed = True


@dataclass
class Constraint:
    name: str
    type: ConstraintType
    value: str

    def update_name(self, name: str) -> None:
        """Rename this constraint."""
        self.name = name

    def update_type(self, type: ConstraintType) -> None:
        """Change what kind of constraint this is."""
        self.type = type

    def update_value(self, value: str) -> None:
        """Update the constraint's value (e.g. a time string like '08:00')."""
        self.value = value


@dataclass
class DailyPlan:
    ordered_tasks: list[Task] = field(default_factory=list)
    reasoning: str = ""

    def display(self) -> None:
        """Print the day's scheduled tasks with times and completion status."""
        print(f"Daily Plan - {len(self.ordered_tasks)} task(s)")
        print("-" * 40)
        for i, task in enumerate(self.ordered_tasks, 1):
            pet_name = task.pet.name if task.pet else "unassigned"
            status = "[x]" if task.completed else "[ ]"
            time_str = task.start_time.strftime("%I:%M %p") if task.start_time else "--:--"
            print(f"{i}. {status} {time_str}  {task.name} ({pet_name}) | {task.duration} min | {task.priority.name}")
        print()

    def explain_reasoning(self) -> str:
        """Return the text explanation of how the plan was ordered."""
        return self.reasoning


@dataclass
class Owner:
    name: str
    email: str
    pets: list[Pet] = field(default_factory=list)
    scheduler: Scheduler | None = None

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's roster."""
        self.pets.append(pet)

    def remove_pet(self, pet: Pet) -> None:
        """Remove a pet from this owner's roster."""
        self.pets.remove(pet)

    def get_all_tasks(self) -> list[Task]:
        """Return every task across all of this owner's pets."""
        return [task for pet in self.pets for task in pet.tasks]

    def get_all_pending_tasks(self) -> list[Task]:
        """Return incomplete tasks across all of this owner's pets."""
        return [task for pet in self.pets for task in pet.get_pending_tasks()]


class Scheduler:
    def __init__(self, date: date) -> None:
        self.date = date
        self.tasks: list[Task] = []
        self.constraints: list[Constraint] = []

    def load_tasks_from_owner(self, owner: Owner) -> None:
        """Pull in all tasks from every pet the owner has, skipping duplicates."""
        for pet in owner.pets:
            for task in pet.tasks:
                if task not in self.tasks:
                    self.tasks.append(task)

    def add_task(self, task: Task) -> None:
        """Add a single task directly to the scheduler."""
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove a task from the scheduler."""
        self.tasks.remove(task)

    def mark_completed(self, task: Task) -> None:
        """Delegate completion to the task itself."""
        task.mark_completed()

    def add_constraint(self, constraint: Constraint) -> None:
        """Register a scheduling constraint."""
        self.constraints.append(constraint)

    def remove_constraint(self, constraint: Constraint) -> None:
        """Remove a previously registered constraint."""
        self.constraints.remove(constraint)

    def get_pending_tasks(self) -> list[Task]:
        """Return all tasks that have not been completed."""
        return [t for t in self.tasks if not t.completed]

    def generate_plan(self) -> DailyPlan:
        """Sort pending tasks by priority and assign sequential start times."""
        pending = self.get_pending_tasks()
        sorted_tasks = sorted(pending, key=lambda t: t.priority.value, reverse=True)

        # Default start time is 08:00; NO_TASKS_BEFORE constraint overrides it
        start_hour, start_minute = 8, 0
        for c in self.constraints:
            if c.type == ConstraintType.NO_TASKS_BEFORE:
                start_hour, start_minute = map(int, c.value.split(":"))

        current = datetime.combine(self.date, time(start_hour, start_minute))
        for task in sorted_tasks:
            task.start_time = current.time()
            current += timedelta(minutes=task.duration)

        lines = [f"Plan for {self.date} - {len(sorted_tasks)} pending task(s):"]
        for i, task in enumerate(sorted_tasks, 1):
            pet_name = task.pet.name if task.pet else "unassigned"
            time_str = task.start_time.strftime("%I:%M %p")
            lines.append(f"  {i}. {time_str}  {task.name} ({pet_name}) - {task.priority.name}, {task.duration} min")

        if self.constraints:
            lines.append("Constraints applied:")
            for c in self.constraints:
                lines.append(f"  - {c.name} ({c.type.value}): {c.value}")

        return DailyPlan(ordered_tasks=sorted_tasks, reasoning="\n".join(lines))
