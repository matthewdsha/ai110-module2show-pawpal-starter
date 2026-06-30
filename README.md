# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

```
# e.g.:
# Daily plan for Biscuit (Golden Retriever):
#   08:00 — Morning walk (30 min) [priority: high]
#   09:00 — Feeding (10 min) [priority: high]
#   ...
```

========================================
       TODAY'S SCHEDULE
========================================
Daily Plan - 4 task(s)
----------------------------------------
1. [ ] 08:00 AM  Morning Walk (Buddy) | 30 min | HIGH
2. [ ] 08:30 AM  Feed Buddy (Buddy) | 10 min | HIGH
3. [ ] 08:40 AM  Playtime (Luna) | 20 min | MEDIUM
4. [ ] 09:00 AM  Vet Checkup (Luna) | 60 min | LOW

Plan for 2026-06-23 - 4 pending task(s):
  1. 08:00 AM  Morning Walk (Buddy) - HIGH, 30 min
  2. 08:30 AM  Feed Buddy (Buddy) - HIGH, 10 min
  3. 08:40 AM  Playtime (Luna) - MEDIUM, 20 min
  4. 09:00 AM  Vet Checkup (Luna) - LOW, 60 min
Constraints applied:
  - No early tasks (no_tasks_before): 08:00

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
python -m pytest

The suite covers task sorting, recurrence spawning and due-date gating, conflict and constraint detection, and pet-to-task wiring.

I would say my confidence level would be 4/5 stars. The tests cover a lot of topics, which gives me a lot of confidence in the system's reliability. However, after reviewing, I realized htere was not much testing for the display of the daily plan or any constraint updates. While a lot of the system was tested, there are a few outliers still missing.

Sample test output:

rootdir: C:\Users\matth\ai110-module2show-pawpal-starter
plugins: anyio-4.14.0
collected 41 items                                                                                                                                                             

tests\test_pawpal.py .........................................                                                                                                           [100%]

============================================================================= 41 passed in 0.08s ==============================================================================

## 📐 Smarter Scheduling

> Fill in once you've implemented scheduling logic.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | Scheduler.sort_by_time(), Scheduler.generate_plan() | Sorts based off time, priority, and duration (in generate_plan) |
| Filtering | Scheduler.get_pending_tasks(), Scheduler.filter_by_pet_name(), Scheduler.get_tasks_for_pet(), Scheduler.get_tasks_by_priority(), Scheduler.get_tasks_by_status() | Several methods filter the scheduler's task list using pet names, priority level, or completion |
| Conflict handling | Scheduler.detect_conflicts(), Scheduler.generate_plan() | checks every pair of time-assigned tasks for overlap and checks constraints in generate_plan |
| Recurring tasks | Scheduler.is_due_today(), Scheduler.mark_complete(), Scheduler.spawn_next_occurrence() | is_due_today influences what appears in each day's plan, checks for daily and weekly tasks as well as repeating tasks |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. Enter and save owner name and email
2. Add a pet profile (name, species, breed, age)
3. Add a task for the pet with duration, priority, frequency, and optional start time
4. Optionally add more tasks or another pet task
5. Add a scheduling constraint such as NO_TASKS_AFTER, NO_TASKS_BEFORE, TIME_BLOCK, or MAX_DURATION
6. Click “Generate schedule”
7. Review the generated plan and any conflict or constraint warnings

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->

## Features:
Add pets with profile details
Add pet tasks with duration, priority, frequency, optional start time, and description
Track recurring tasks for daily and weekly schedules
Select pending tasks due today based on recurrence rules
Sort tasks by priority, then duration, then name
Assign start times sequentially beginning at 8:00 AM or after a NO_TASKS_BEFORE constraint
Detect overlapping task time windows
Enforce constraints
Filter tasks by pet, priority, or completion status
Display schedule chronologically with assigned times