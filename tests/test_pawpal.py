from datetime import date, time, timedelta

from pawpal_system import (
    Constraint,
    ConstraintType,
    Frequency,
    Owner,
    Pet,
    Priority,
    Scheduler,
    Task,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_pet(name="Buddy") -> Pet:
    return Pet(name=name, species="Dog", breed="Labrador", age=3)


def make_task(name="Walk", duration=30, priority=Priority.MEDIUM,
              frequency=Frequency.ONCE) -> Task:
    return Task(name=name, duration=duration, priority=priority,
                frequency=frequency)


def make_scheduler(day: date | None = None) -> Scheduler:
    return Scheduler(date=day or date(2026, 6, 25))


# ===========================================================================
# 1. Recurrence spawning
# ===========================================================================

class TestRecurrenceSpawning:
    """mark_completed must spawn the correct follow-up task for recurring tasks."""

    def test_daily_spawns_next_day(self):
        today = date(2026, 6, 25)
        scheduler = make_scheduler(today)
        pet = make_pet()
        task = make_task(frequency=Frequency.DAILY)
        pet.add_task(task)
        scheduler.add_task(task)

        next_task = scheduler.mark_completed(task)

        assert next_task is not None
        assert next_task.due_date == today + timedelta(days=1)

    def test_weekly_spawns_seven_days_later(self):
        today = date(2026, 6, 25)
        scheduler = make_scheduler(today)
        pet = make_pet()
        task = make_task(frequency=Frequency.WEEKLY)
        pet.add_task(task)
        scheduler.add_task(task)

        next_task = scheduler.mark_completed(task)

        assert next_task is not None
        assert next_task.due_date == today + timedelta(weeks=1)

    def test_once_does_not_spawn(self):
        scheduler = make_scheduler()
        task = make_task(frequency=Frequency.ONCE)
        scheduler.add_task(task)

        result = scheduler.mark_completed(task)

        assert result is None

    def test_as_needed_does_not_spawn(self):
        scheduler = make_scheduler()
        task = make_task(frequency=Frequency.AS_NEEDED)
        scheduler.add_task(task)

        result = scheduler.mark_completed(task)

        assert result is None

    def test_spawned_task_added_to_pet(self):
        scheduler = make_scheduler()
        pet = make_pet()
        task = make_task(frequency=Frequency.DAILY)
        pet.add_task(task)
        scheduler.add_task(task)

        next_task = scheduler.mark_completed(task)

        assert next_task in pet.tasks
        assert next_task.pet is pet

    def test_spawned_task_added_to_scheduler(self):
        scheduler = make_scheduler()
        pet = make_pet()
        task = make_task(frequency=Frequency.DAILY)
        pet.add_task(task)
        scheduler.add_task(task)

        next_task = scheduler.mark_completed(task)

        assert next_task in scheduler.tasks

    def test_spawned_task_inherits_properties(self):
        scheduler = make_scheduler()
        pet = make_pet()
        task = make_task(name="Evening Run", duration=45,
                         priority=Priority.HIGH, frequency=Frequency.DAILY)
        pet.add_task(task)
        scheduler.add_task(task)

        next_task = scheduler.mark_completed(task)

        assert next_task.name == task.name
        assert next_task.duration == task.duration
        assert next_task.priority == task.priority
        assert next_task.frequency == task.frequency
        assert not next_task.completed

    def test_original_task_marked_completed_after_spawn(self):
        scheduler = make_scheduler()
        task = make_task(frequency=Frequency.DAILY)
        scheduler.add_task(task)
        scheduler.mark_completed(task)

        assert task.completed is True
        assert task.last_completed == scheduler.date


# ===========================================================================
# 2. generate_plan — ordering & time assignment
# ===========================================================================

class TestGeneratePlan:
    """generate_plan must sort tasks and assign sequential start times."""

    def test_high_priority_before_medium(self):
        scheduler = make_scheduler()
        med = make_task(name="Feed", duration=10, priority=Priority.MEDIUM)
        high = make_task(name="Walk", duration=10, priority=Priority.HIGH)
        scheduler.add_task(med)
        scheduler.add_task(high)

        plan = scheduler.generate_plan()

        assert plan.ordered_tasks[0] is high
        assert plan.ordered_tasks[1] is med

    def test_same_priority_shorter_first(self):
        scheduler = make_scheduler()
        long_task = make_task(name="Bath", duration=60, priority=Priority.MEDIUM)
        short_task = make_task(name="Feed", duration=10, priority=Priority.MEDIUM)
        scheduler.add_task(long_task)
        scheduler.add_task(short_task)

        plan = scheduler.generate_plan()

        assert plan.ordered_tasks[0] is short_task
        assert plan.ordered_tasks[1] is long_task

    def test_same_priority_duration_alphabetical_tiebreak(self):
        scheduler = make_scheduler()
        z_task = make_task(name="Zzz", duration=10, priority=Priority.LOW)
        a_task = make_task(name="Aaa", duration=10, priority=Priority.LOW)
        scheduler.add_task(z_task)
        scheduler.add_task(a_task)

        plan = scheduler.generate_plan()

        assert plan.ordered_tasks[0] is a_task
        assert plan.ordered_tasks[1] is z_task

    def test_start_times_are_sequential(self):
        scheduler = make_scheduler()
        t1 = make_task(name="A", duration=30, priority=Priority.HIGH)
        t2 = make_task(name="B", duration=20, priority=Priority.MEDIUM)
        scheduler.add_task(t1)
        scheduler.add_task(t2)

        plan = scheduler.generate_plan()

        # Default start is 08:00; t1 takes 30 min → t2 starts at 08:30
        assert plan.ordered_tasks[0].start_time == time(8, 0)
        assert plan.ordered_tasks[1].start_time == time(8, 30)

    def test_no_tasks_before_constraint_shifts_start(self):
        scheduler = make_scheduler()
        scheduler.add_constraint(Constraint(
            name="Late Start", type=ConstraintType.NO_TASKS_BEFORE, value="10:00"
        ))
        task = make_task(name="Feed", duration=15, priority=Priority.HIGH)
        scheduler.add_task(task)

        plan = scheduler.generate_plan()

        assert plan.ordered_tasks[0].start_time == time(10, 0)

    def test_empty_scheduler_returns_empty_plan(self):
        scheduler = make_scheduler()
        plan = scheduler.generate_plan()

        assert plan.ordered_tasks == []
        assert plan.conflicts == []

    def test_plan_reasoning_is_non_empty(self):
        scheduler = make_scheduler()
        scheduler.add_task(make_task())

        plan = scheduler.generate_plan()

        assert len(plan.reasoning) > 0


# ===========================================================================
# 3. Constraint conflict detection
# ===========================================================================

class TestConstraintConflicts:
    """generate_plan must surface violations in DailyPlan.conflicts."""

    def test_no_tasks_after_flags_overrun(self):
        scheduler = make_scheduler()
        scheduler.add_constraint(Constraint(
            name="Cutoff", type=ConstraintType.NO_TASKS_AFTER, value="08:30"
        ))
        # Task starts at 08:00 (default) and runs 60 min → ends 09:00
        scheduler.add_task(make_task(name="Long Walk", duration=60,
                                     priority=Priority.HIGH))

        plan = scheduler.generate_plan()

        assert any("Long Walk" in c for c in plan.conflicts)

    def test_no_tasks_after_no_false_positive(self):
        scheduler = make_scheduler()
        scheduler.add_constraint(Constraint(
            name="Cutoff", type=ConstraintType.NO_TASKS_AFTER, value="09:00"
        ))
        # Task starts 08:00, runs 30 min → ends 08:30, within cutoff
        scheduler.add_task(make_task(name="Short Walk", duration=30,
                                     priority=Priority.HIGH))

        plan = scheduler.generate_plan()

        assert plan.conflicts == []

    def test_time_block_flags_overlap(self):
        scheduler = make_scheduler()
        # Block 08:00–09:00; task is scheduled at 08:00 by default
        scheduler.add_constraint(Constraint(
            name="Blocked", type=ConstraintType.TIME_BLOCK, value="08:00-09:00"
        ))
        scheduler.add_task(make_task(name="Feed", duration=30,
                                     priority=Priority.HIGH))

        plan = scheduler.generate_plan()

        assert any("Feed" in c for c in plan.conflicts)

    def test_time_block_no_false_positive(self):
        scheduler = make_scheduler()
        # Block 12:00–13:00; task ends before block
        scheduler.add_constraint(Constraint(
            name="Lunch Block", type=ConstraintType.TIME_BLOCK, value="12:00-13:00"
        ))
        scheduler.add_task(make_task(name="Morning Feed", duration=15,
                                     priority=Priority.HIGH))

        plan = scheduler.generate_plan()

        assert plan.conflicts == []

    def test_max_duration_flags_excess(self):
        scheduler = make_scheduler()
        scheduler.add_constraint(Constraint(
            name="Max Time", type=ConstraintType.MAX_DURATION, value="20"
        ))
        scheduler.add_task(make_task(name="Walk", duration=30,
                                     priority=Priority.HIGH))

        plan = scheduler.generate_plan()

        assert any("exceeds" in c for c in plan.conflicts)

    def test_max_duration_no_false_positive(self):
        scheduler = make_scheduler()
        scheduler.add_constraint(Constraint(
            name="Max Time", type=ConstraintType.MAX_DURATION, value="60"
        ))
        scheduler.add_task(make_task(name="Walk", duration=30,
                                     priority=Priority.HIGH))

        plan = scheduler.generate_plan()

        assert plan.conflicts == []

    def test_detect_conflicts_overlapping_tasks(self):
        scheduler = make_scheduler()
        t1 = make_task(name="Walk", duration=60)
        t2 = make_task(name="Feed", duration=30)
        t1.start_time = time(8, 0)
        t2.start_time = time(8, 30)  # starts during t1
        scheduler.add_task(t1)
        scheduler.add_task(t2)

        warnings = scheduler.detect_conflicts()

        assert len(warnings) == 1
        assert "Walk" in warnings[0]
        assert "Feed" in warnings[0]

    def test_detect_conflicts_boundary_is_not_overlap(self):
        """Tasks that share only an endpoint must NOT be flagged."""
        scheduler = make_scheduler()
        t1 = make_task(name="Walk", duration=30)
        t2 = make_task(name="Feed", duration=30)
        t1.start_time = time(8, 0)   # ends exactly at 08:30
        t2.start_time = time(8, 30)  # starts exactly at 08:30
        scheduler.add_task(t1)
        scheduler.add_task(t2)

        warnings = scheduler.detect_conflicts()

        assert warnings == []

    def test_detect_conflicts_no_start_time_skipped(self):
        scheduler = make_scheduler()
        t1 = make_task(name="Walk", duration=30)
        t2 = make_task(name="Feed", duration=30)
        # Neither has a start_time; detect_conflicts should return nothing
        scheduler.add_task(t1)
        scheduler.add_task(t2)

        warnings = scheduler.detect_conflicts()

        assert warnings == []


# ===========================================================================
# 4. _is_due_today — recurrence gating
# ===========================================================================

class TestIsDueToday:
    """Scheduler.get_pending_tasks must respect each Frequency rule."""

    def test_daily_task_always_due(self):
        scheduler = make_scheduler()
        task = make_task(frequency=Frequency.DAILY)
        scheduler.add_task(task)

        assert task in scheduler.get_pending_tasks()

    def test_once_task_due_when_not_completed(self):
        scheduler = make_scheduler()
        task = make_task(frequency=Frequency.ONCE)
        scheduler.add_task(task)

        assert task in scheduler.get_pending_tasks()

    def test_once_task_not_due_after_completed(self):
        scheduler = make_scheduler()
        task = make_task(frequency=Frequency.ONCE)
        task.mark_completed()
        scheduler.add_task(task)

        assert task not in scheduler.get_pending_tasks()

    def test_as_needed_never_due(self):
        scheduler = make_scheduler()
        task = make_task(frequency=Frequency.AS_NEEDED)
        scheduler.add_task(task)

        assert task not in scheduler.get_pending_tasks()

    def test_weekly_due_when_never_completed(self):
        scheduler = make_scheduler()
        task = make_task(frequency=Frequency.WEEKLY)
        scheduler.add_task(task)

        assert task in scheduler.get_pending_tasks()

    def test_weekly_due_when_seven_days_elapsed(self):
        today = date(2026, 6, 25)
        scheduler = make_scheduler(today)
        task = make_task(frequency=Frequency.WEEKLY)
        task.last_completed = today - timedelta(days=7)
        scheduler.add_task(task)

        assert task in scheduler.get_pending_tasks()

    def test_weekly_not_due_when_completed_recently(self):
        today = date(2026, 6, 25)
        scheduler = make_scheduler(today)
        task = make_task(frequency=Frequency.WEEKLY)
        task.last_completed = today - timedelta(days=3)
        scheduler.add_task(task)

        assert task not in scheduler.get_pending_tasks()

    def test_spawned_task_not_due_before_due_date(self):
        today = date(2026, 6, 25)
        scheduler = make_scheduler(today)
        task = make_task(frequency=Frequency.DAILY)
        task.due_date = today + timedelta(days=1)
        scheduler.add_task(task)

        assert task not in scheduler.get_pending_tasks()

    def test_spawned_task_due_on_due_date(self):
        today = date(2026, 6, 25)
        scheduler = make_scheduler(today)
        task = make_task(frequency=Frequency.DAILY)
        task.due_date = today
        scheduler.add_task(task)

        assert task in scheduler.get_pending_tasks()


# ===========================================================================
# 5. Pet↔Task wiring & Owner aggregation
# ===========================================================================

class TestPetTaskWiring:
    """add_task/remove_task back-references and Owner aggregation."""

    def test_add_task_sets_back_reference(self):
        pet = make_pet()
        task = make_task()
        pet.add_task(task)

        assert task.pet is pet

    def test_add_task_appends_to_pet_tasks(self):
        pet = make_pet()
        task = make_task()
        pet.add_task(task)

        assert task in pet.tasks

    def test_remove_task_removes_from_list(self):
        pet = make_pet()
        task = make_task()
        pet.add_task(task)
        pet.remove_task(task)

        assert task not in pet.tasks

    def test_get_pending_tasks_excludes_completed(self):
        pet = make_pet()
        done = make_task(name="Done")
        done.mark_completed()
        pending = make_task(name="Pending")
        pet.add_task(done)
        pet.add_task(pending)

        result = pet.get_pending_tasks()

        assert done not in result
        assert pending in result

    def test_owner_get_all_tasks_aggregates_pets(self):
        owner = Owner(name="Alice", email="a@example.com")
        pet1, pet2 = make_pet("Buddy"), make_pet("Luna")
        t1, t2 = make_task("Feed Buddy"), make_task("Feed Luna")
        pet1.add_task(t1)
        pet2.add_task(t2)
        owner.add_pet(pet1)
        owner.add_pet(pet2)

        all_tasks = owner.get_all_tasks()

        assert t1 in all_tasks
        assert t2 in all_tasks
        assert len(all_tasks) == 2

    def test_owner_get_all_pending_excludes_done(self):
        owner = Owner(name="Alice", email="a@example.com")
        pet = make_pet()
        done = make_task(name="Done")
        done.mark_completed()
        pending = make_task(name="Pending")
        pet.add_task(done)
        pet.add_task(pending)
        owner.add_pet(pet)

        result = owner.get_all_pending_tasks()

        assert done not in result
        assert pending in result

    def test_filter_by_pet_name_case_insensitive(self):
        scheduler = make_scheduler()
        pet = make_pet("Buddy")
        task = make_task()
        pet.add_task(task)
        scheduler.add_task(task)

        assert task in scheduler.filter_by_pet_name("buddy")
        assert task in scheduler.filter_by_pet_name("BUDDY")
        assert task in scheduler.filter_by_pet_name("Buddy")

    def test_load_tasks_from_owner_skips_duplicates(self):
        scheduler = make_scheduler()
        owner = Owner(name="Alice", email="a@example.com")
        pet = make_pet()
        task = make_task()
        pet.add_task(task)
        owner.add_pet(pet)

        scheduler.load_tasks_from_owner(owner)
        scheduler.load_tasks_from_owner(owner)  # second call must be a no-op

        assert scheduler.tasks.count(task) == 1
