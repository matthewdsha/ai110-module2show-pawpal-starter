from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta
from enum import Enum
from itertools import combinations


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
    last_completed: date | None = None
    due_date: date | None = None  # set on spawned recurring tasks; None means "due immediately"

    def update_name(self, name: str) -> None:
        """Rename this task."""
        self.name = name

    def update_duration(self, duration: int) -> None:
        """Update how long this task takes in minutes."""
        self.duration = duration

    def update_priority(self, priority: Priority) -> None:
        """Change the scheduling priority of this task."""
        self.priority = priority

    def mark_completed(self, on_date: date | None = None) -> None:
        """Mark this task as done and record when, so weekly/daily recurrence can reset."""
        self.completed = True
        self.last_completed = on_date


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
    conflicts: list[str] = field(default_factory=list)

    def display(self) -> None:
        """Print the day's scheduled tasks with times and completion status."""
        print(f"Daily Plan - {len(self.ordered_tasks)} task(s)")
        print("-" * 40)
        for i, task in enumerate(self.ordered_tasks, 1):
            pet_name = task.pet.name if task.pet else "unassigned"
            status = "[x]" if task.completed else "[ ]"
            time_str = task.start_time.strftime("%I:%M %p") if task.start_time else "--:--"
            print(f"{i}. {status} {time_str}  {task.name} ({pet_name}) | {task.duration} min | {task.priority.name}")
        if self.conflicts:
            print()
            print("  [!] Conflicts detected:")
            for c in self.conflicts:
                print(f"    - {c}")
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
        # Task is a mutable dataclass (no __hash__), so we key the set on object
        # identity with id() — same semantics as the original list `in` check,
        # but O(1) per lookup instead of O(n).
        seen = {id(t) for t in self.tasks}
        for pet in owner.pets:
            for task in pet.tasks:
                if id(task) not in seen:
                    self.tasks.append(task)
                    seen.add(id(task))

    def add_task(self, task: Task) -> None:
        """Add a single task directly to the scheduler."""
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove a task from the scheduler."""
        self.tasks.remove(task)

    def mark_completed(self, task: Task) -> Task | None:
        """Mark task done, then spawn the next occurrence for recurring tasks.

        Uses timedelta to compute the exact next due date:
          - DAILY  -> today + timedelta(days=1)
          - WEEKLY -> today + timedelta(weeks=1)
          - ONCE / AS_NEEDED -> no new task; returns None
        """
        task.mark_completed(on_date=self.date)
        recurrence_delta = {
            Frequency.DAILY: timedelta(days=1),
            Frequency.WEEKLY: timedelta(weeks=1),
        }
        delta = recurrence_delta.get(task.frequency)
        if delta is not None:
            return self._spawn_next_occurrence(task, self.date + delta)
        return None

    def _spawn_next_occurrence(self, task: Task, due_date: date) -> Task:
        """Create a fresh, incomplete copy of task scheduled for due_date."""
        next_task = Task(
            name=task.name,
            duration=task.duration,
            priority=task.priority,
            description=task.description,
            frequency=task.frequency,
            due_date=due_date,
        )
        if task.pet:
            task.pet.add_task(next_task)  # wires next_task.pet and appends to pet.tasks
        self.tasks.append(next_task)
        return next_task

    def add_constraint(self, constraint: Constraint) -> None:
        """Register a scheduling constraint."""
        self.constraints.append(constraint)

    def remove_constraint(self, constraint: Constraint) -> None:
        """Remove a previously registered constraint."""
        self.constraints.remove(constraint)

    def _is_due_today(self, task: Task) -> bool:
        """Return True if this task should appear in today's plan based on its frequency."""
        # Spawned recurring tasks have an explicit due_date; include them on or after that date.
        if task.due_date is not None:
            return task.due_date <= self.date
        if task.frequency == Frequency.DAILY:
            return True
        if task.frequency == Frequency.ONCE:
            return not task.completed
        if task.frequency == Frequency.WEEKLY:
            return task.last_completed is None or (self.date - task.last_completed).days >= 7
        if task.frequency == Frequency.AS_NEEDED:
            return False
        return not task.completed

    def get_pending_tasks(self) -> list[Task]:
        """Return tasks that are incomplete and due today based on their recurrence frequency."""
        return [t for t in self.tasks if not t.completed and self._is_due_today(t)]

    def sort_by_time(self) -> list[Task]:
        """Return all tasks sorted chronologically by start_time.

        Uses a lambda key so Python's sorted() compares time objects directly.
        Tasks with no start_time assigned yet sort to the end via time.max.
        """
        return sorted(
            self.tasks,
            key=lambda t: t.start_time if t.start_time is not None else time.max,
        )

    def detect_conflicts(self) -> list[str]:
        """Check all scheduled tasks for pairwise time overlaps.

        Two tasks conflict when their windows overlap:
            A.start < B.end  AND  B.start < A.end
        Only tasks that already have a start_time are considered.
        Returns a list of human-readable warning strings; never raises.
        """
        scheduled = [t for t in self.tasks if t.start_time is not None]
        warnings: list[str] = []
        for a, b in combinations(scheduled, 2):
            # Integer minutes avoids creating datetime objects for every pair.
            a_start = a.start_time.hour * 60 + a.start_time.minute
            a_end   = a_start + a.duration
            b_start = b.start_time.hour * 60 + b.start_time.minute
            b_end   = b_start + b.duration
            if a_start < b_end and b_start < a_end:
                warnings.append(
                    f"WARNING: '{a.name}' ({a.start_time.strftime('%I:%M %p')}, "
                    f"{a.duration} min) overlaps "
                    f"'{b.name}' ({b.start_time.strftime('%I:%M %p')}, {b.duration} min)"
                )
        return warnings

    def filter_by_pet_name(self, name: str) -> list[Task]:
        """Return tasks whose pet's name matches name (case-insensitive)."""
        return [t for t in self.tasks if t.pet and t.pet.name.lower() == name.lower()]

    def get_tasks_for_pet(self, pet: Pet) -> list[Task]:
        """Return all tasks belonging to a specific pet."""
        return [t for t in self.tasks if t.pet == pet]

    def get_tasks_by_priority(self, priority: Priority) -> list[Task]:
        """Return all tasks matching a given priority level."""
        return [t for t in self.tasks if t.priority == priority]

    def get_tasks_by_status(self, completed: bool) -> list[Task]:
        """Return tasks filtered by completion status."""
        return [t for t in self.tasks if t.completed == completed]

    def generate_plan(self) -> DailyPlan:
        """Schedule pending tasks and detect constraint violations."""
        pending = self.get_pending_tasks()

        # Multi-key sort: priority (high→low), then duration (short→long), then name for determinism
        sorted_tasks = sorted(
            pending,
            key=lambda t: (-t.priority.value, t.duration, t.name),
        )

        # Resolve the start time — NO_TASKS_BEFORE wins over the 08:00 default.
        # next() short-circuits at the first match instead of walking every constraint.
        no_before = next(
            (c for c in self.constraints if c.type == ConstraintType.NO_TASKS_BEFORE), None
        )
        h, m = map(int, no_before.value.split(":")) if no_before else (8, 0)
        current = datetime.combine(self.date, time(h, m))
        for task in sorted_tasks:
            if task.start_time is None:
                task.start_time = current.time()
            current += timedelta(minutes=task.duration)

        # --- Conflict detection ---
        conflicts: list[str] = []

        for c in self.constraints:
            if c.type == ConstraintType.NO_TASKS_AFTER:
                end_hour, end_minute = map(int, c.value.split(":"))
                cutoff = datetime.combine(self.date, time(end_hour, end_minute))
                for task in sorted_tasks:
                    task_end = datetime.combine(self.date, task.start_time) + timedelta(minutes=task.duration)
                    if task_end > cutoff:
                        conflicts.append(
                            f"'{task.name}' ends at {task_end.strftime('%I:%M %p')}, past cutoff {c.value}"
                        )

            elif c.type == ConstraintType.TIME_BLOCK:
                # value format: "HH:MM-HH:MM"
                block_start_str, block_end_str = c.value.split("-")
                bsh, bsm = map(int, block_start_str.split(":"))
                beh, bem = map(int, block_end_str.split(":"))
                block_start = datetime.combine(self.date, time(bsh, bsm))
                block_end = datetime.combine(self.date, time(beh, bem))
                for task in sorted_tasks:
                    task_start_dt = datetime.combine(self.date, task.start_time)
                    task_end_dt = task_start_dt + timedelta(minutes=task.duration)
                    if task_start_dt < block_end and task_end_dt > block_start:
                        conflicts.append(
                            f"'{task.name}' overlaps blocked window {c.value}"
                        )

            elif c.type == ConstraintType.MAX_DURATION:
                max_mins = int(c.value)
                total = sum(t.duration for t in sorted_tasks)
                if total > max_mins:
                    conflicts.append(
                        f"Total scheduled time ({total} min) exceeds max allowed ({max_mins} min)"
                    )

        # --- Reasoning text ---
        lines = [f"Plan for {self.date} - {len(sorted_tasks)} pending task(s):"]
        lines.append("  Sorted by: priority (high to low), duration (short to long)")
        for i, task in enumerate(sorted_tasks, 1):
            pet_name = task.pet.name if task.pet else "unassigned"
            time_str = task.start_time.strftime("%I:%M %p")
            lines.append(
                f"  {i}. {time_str}  {task.name} ({pet_name}) - {task.priority.name}, {task.duration} min"
            )
        if self.constraints:
            lines.append("Constraints applied:")
            for c in self.constraints:
                lines.append(f"  - {c.name} ({c.type.value}): {c.value}")
        if conflicts:
            lines.append("Conflicts:")
            for conflict in conflicts:
                lines.append(f"  [!] {conflict}")

        return DailyPlan(ordered_tasks=sorted_tasks, reasoning="\n".join(lines), conflicts=conflicts)
