from datetime import date

from pawpal_system import (
    Constraint, ConstraintType, Frequency, Owner, Pet, Priority, Scheduler, Task
)

# --- Setup ---
owner = Owner(name="Jordan", email="jordan@example.com")

buddy = Pet(name="Buddy", species="Dog", breed="Labrador", age=3)
luna  = Pet(name="Luna",  species="Cat", breed="Siamese",  age=5)

owner.add_pet(buddy)
owner.add_pet(luna)

# --- Tasks ---
buddy.add_task(Task(
    name="Morning Walk",
    duration=30,
    priority=Priority.HIGH,
    description="Walk around the block twice",
    frequency=Frequency.DAILY,
))

buddy.add_task(Task(
    name="Feed Buddy",
    duration=10,
    priority=Priority.HIGH,
    description="One cup of dry food",
    frequency=Frequency.DAILY,
))

luna.add_task(Task(
    name="Playtime",
    duration=20,
    priority=Priority.MEDIUM,
    description="Feather wand session",
    frequency=Frequency.DAILY,
))

luna.add_task(Task(
    name="Vet Checkup",
    duration=60,
    priority=Priority.LOW,
    description="Annual wellness exam",
    frequency=Frequency.ONCE,
))

# --- Scheduler ---
scheduler = Scheduler(date=date.today())
scheduler.load_tasks_from_owner(owner)

scheduler.add_constraint(Constraint(
    name="No early tasks",
    type=ConstraintType.NO_TASKS_BEFORE,
    value="08:00",
))

owner.scheduler = scheduler

# --- Output ---
plan = scheduler.generate_plan()

print("=" * 40)
print("       TODAY'S SCHEDULE")
print("=" * 40)
plan.display()
print(plan.explain_reasoning())
