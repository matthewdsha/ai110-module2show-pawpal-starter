from datetime import date, time

from pawpal_system import (
    Constraint, ConstraintType, Frequency, Owner, Pet, Priority, Scheduler, Task
)

# --- Setup ---
owner = Owner(name="Jordan", email="jordan@example.com")

buddy = Pet(name="Buddy", species="Dog", breed="Labrador", age=3)
luna  = Pet(name="Luna",  species="Cat", breed="Siamese",  age=5)

owner.add_pet(buddy)
owner.add_pet(luna)

# Manually assign start_times that intentionally conflict:
#   Morning Walk  starts 08:00, runs 30 min -> ends 08:30
#   Feed Buddy    starts 08:15, runs 10 min -> ends 08:25  (overlaps 08:15-08:25)
#   Playtime      starts 09:00, runs 20 min -> ends 09:20  (no conflict)
#   Vet Checkup   starts 09:10, runs 60 min -> ends 10:10  (overlaps Playtime 09:10-09:20)
buddy.add_task(Task(
    name="Morning Walk",
    duration=30,
    priority=Priority.HIGH,
    description="Walk around the block twice",
    frequency=Frequency.DAILY,
    start_time=time(8, 0),
))

buddy.add_task(Task(
    name="Feed Buddy",
    duration=10,
    priority=Priority.HIGH,
    description="One cup of dry food",
    frequency=Frequency.DAILY,
    start_time=time(8, 15),   # <-- conflicts with Morning Walk (08:00-08:30)
))

luna.add_task(Task(
    name="Playtime",
    duration=20,
    priority=Priority.MEDIUM,
    description="Feather wand session",
    frequency=Frequency.DAILY,
    start_time=time(9, 0),
))

luna.add_task(Task(
    name="Vet Checkup",
    duration=60,
    priority=Priority.LOW,
    description="Annual wellness exam",
    frequency=Frequency.ONCE,
    start_time=time(9, 10),   # <-- conflicts with Playtime (09:00-09:20)
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

# --- Step 1: detect conflicts on manually-set (broken) times ---
print("=" * 44)
print("  STEP 1: detect_conflicts() BEFORE generate_plan()")
print("  (tasks have manually-set overlapping start_times)")
print("=" * 44)

warnings = scheduler.detect_conflicts()
if warnings:
    for w in warnings:
        print(f"  {w}")
else:
    print("  No conflicts detected.")

# --- Step 2: generate_plan() reassigns all start_times sequentially ---
print()
print("=" * 44)
print("  STEP 2: generate_plan() resolves the schedule")
print("=" * 44)

plan = scheduler.generate_plan()
plan.display()

# --- Step 3: detect_conflicts() again — should be clean ---
print("=" * 44)
print("  STEP 3: detect_conflicts() AFTER generate_plan()")
print("=" * 44)

warnings = scheduler.detect_conflicts()
if warnings:
    for w in warnings:
        print(f"  {w}")
else:
    print("  No conflicts detected.")
