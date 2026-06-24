from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class Pet:
    name: str
    species: str
    breed: str
    age: int

    def update_info(self, name: str, species: str, breed: str, age: int) -> None:
        pass


@dataclass
class Task:
    name: str
    duration: int  # minutes
    priority: str
    pet: Pet
    completed: bool = False

    def update_name(self, name: str) -> None:
        pass

    def update_duration(self, duration: int) -> None:
        pass

    def update_priority(self, priority: str) -> None:
        pass

    def mark_completed(self) -> None:
        pass


@dataclass
class Constraint:
    name: str
    type: str
    value: str

    def update_name(self, name: str) -> None:
        pass


@dataclass
class DailyPlan:
    ordered_tasks: list[Task] = field(default_factory=list)
    reasoning: str = ""

    def display(self) -> None:
        pass

    def explain_reasoning(self) -> str:
        pass


@dataclass
class Owner:
    name: str
    email: str
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        pass

    def remove_pet(self, pet: Pet) -> None:
        pass


class Schedule:
    def __init__(self, date: str) -> None:
        self.date = date
        self.tasks: list[Task] = []
        self.constraints: list[Constraint] = []

    def add_task(self, task: Task) -> None:
        pass

    def remove_task(self, task: Task) -> None:
        pass

    def mark_completed(self, task: Task) -> None:
        pass

    def add_constraint(self, constraint: Constraint) -> None:
        pass

    def remove_constraint(self, constraint: Constraint) -> None:
        pass

    def generate_plan(self) -> DailyPlan:
        pass
