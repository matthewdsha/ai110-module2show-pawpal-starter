import streamlit as st
from datetime import date, time

from pawpal_system import (
    Constraint, ConstraintType, Frequency, Owner, Pet, Priority, Scheduler, Task,
)

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

# ---------------------------------------------------------------------------
# Session state init
# ---------------------------------------------------------------------------
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="", email="")
if "scheduler" not in st.session_state:
    st.session_state.scheduler = Scheduler(date=date.today())

owner: Owner = st.session_state.owner
scheduler: Scheduler = st.session_state.scheduler

# ---------------------------------------------------------------------------
# Owner
# ---------------------------------------------------------------------------
st.subheader("Owner")
with st.form("owner_form"):
    name = st.text_input("Name", value=owner.name)
    email = st.text_input("Email", value=owner.email)
    if st.form_submit_button("Save owner"):
        owner.name = name
        owner.email = email
        st.success(f"Owner saved: {owner.name}")

# ---------------------------------------------------------------------------
# Pets
# ---------------------------------------------------------------------------
st.subheader("Pets")
with st.form("pet_form"):
    pet_name = st.text_input("Pet name")
    species  = st.selectbox("Species", ["Dog", "Cat", "Other"])
    breed    = st.text_input("Breed")
    age      = st.number_input("Age", min_value=0, max_value=30, value=1)
    if st.form_submit_button("Add pet"):
        owner.add_pet(Pet(name=pet_name, species=species, breed=breed, age=int(age)))
        st.success(f"Added {pet_name}!")

if owner.pets:
    for pet in owner.pets:
        st.write(f"- **{pet.name}** ({pet.species}, {pet.breed}, age {pet.age})")
else:
    st.info("No pets yet. Add one above.")

# ---------------------------------------------------------------------------
# Tasks
# ---------------------------------------------------------------------------
st.subheader("Tasks")
if owner.pets:
    with st.form("task_form"):
        selected_pet_name = st.selectbox("For which pet?", [p.name for p in owner.pets])
        task_name   = st.text_input("Task name")
        description = st.text_input("Description (optional)")
        duration    = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
        priority    = st.selectbox("Priority", ["LOW", "MEDIUM", "HIGH"], index=1)
        frequency   = st.selectbox("Frequency", ["ONCE", "DAILY", "WEEKLY", "AS_NEEDED"])
        col_chk, col_time = st.columns([1, 2])
        with col_chk:
            set_time = st.checkbox("Set start time")
        with col_time:
            task_time = st.time_input("Start time", value=time(8, 0))
        if st.form_submit_button("Add task"):
            target_pet = next(p for p in owner.pets if p.name == selected_pet_name)
            target_pet.add_task(Task(
                name=task_name,
                duration=int(duration),
                priority=Priority[priority],
                description=description,
                frequency=Frequency[frequency],
                start_time=task_time if set_time else None,
            ))
            st.success(f"Added '{task_name}' for {selected_pet_name}!")

    # Sync scheduler so filter/sort methods reflect current tasks.
    scheduler.tasks = []
    scheduler.load_tasks_from_owner(owner)

    if scheduler.tasks:
        col1, col2, col3 = st.columns(3)
        with col1:
            pet_filter      = st.selectbox("Filter by pet",      ["All"] + [p.name for p in owner.pets])
        with col2:
            priority_filter = st.selectbox("Filter by priority", ["All", "HIGH", "MEDIUM", "LOW"])
        with col3:
            status_filter   = st.selectbox("Status",             ["All", "Pending", "Done"])

        if pet_filter != "All":
            visible = scheduler.filter_by_pet_name(pet_filter)
        elif priority_filter != "All":
            visible = scheduler.get_tasks_by_priority(Priority[priority_filter])
        elif status_filter == "Pending":
            visible = scheduler.get_tasks_by_status(completed=False)
        elif status_filter == "Done":
            visible = scheduler.get_tasks_by_status(completed=True)
        else:
            visible = scheduler.tasks

        st.dataframe(
            [
                {
                    "Pet":            t.pet.name if t.pet else "—",
                    "Task":           t.name,
                    "Priority":       t.priority.name,
                    "Duration (min)": t.duration,
                    "Frequency":      t.frequency.value,
                    "Start Time":     t.start_time.strftime("%I:%M %p") if t.start_time else "auto",
                    "Done":           "✓" if t.completed else "",
                }
                for t in visible
            ],
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No tasks yet. Add one above.")
else:
    st.info("Add a pet before adding tasks.")

# ---------------------------------------------------------------------------
# Constraints
# ---------------------------------------------------------------------------
st.divider()
st.subheader("Scheduling Constraints")
# Type selector outside the form so changing it re-renders the value inputs immediately.
c_type = st.selectbox("Constraint type", ["NO_TASKS_AFTER", "NO_TASKS_BEFORE", "TIME_BLOCK", "MAX_DURATION"])

with st.form("constraint_form"):
    c_name = st.text_input("Constraint name")

    if c_type in ("NO_TASKS_AFTER", "NO_TASKS_BEFORE"):
        c_time = st.time_input("Time", value=time(8, 0))
    elif c_type == "TIME_BLOCK":
        col_a, col_b = st.columns(2)
        with col_a:
            block_start = st.time_input("Block start", value=time(12, 0))
        with col_b:
            block_end = st.time_input("Block end", value=time(13, 0))
    else:  # MAX_DURATION
        max_mins = st.number_input("Max total minutes", min_value=1, max_value=480, value=120)

    if st.form_submit_button("Add constraint"):
        if not c_name:
            st.error("Name is required.")
        else:
            if c_type in ("NO_TASKS_AFTER", "NO_TASKS_BEFORE"):
                c_value = c_time.strftime("%H:%M")
            elif c_type == "TIME_BLOCK":
                c_value = f"{block_start.strftime('%H:%M')}-{block_end.strftime('%H:%M')}"
            else:
                c_value = str(int(max_mins))
            scheduler.add_constraint(Constraint(name=c_name, type=ConstraintType[c_type], value=c_value))
            st.success(f"Constraint '{c_name}' added.")

if scheduler.constraints:
    st.dataframe(
        [{"Name": c.name, "Type": c.type.value, "Value": c.value} for c in scheduler.constraints],
        use_container_width=True,
        hide_index=True,
    )
else:
    st.info("No constraints yet. Add one above to enforce time limits or blocked windows.")

# ---------------------------------------------------------------------------
# Schedule
# ---------------------------------------------------------------------------
st.divider()
st.subheader("Today's Schedule")

if st.button("Generate schedule"):
    scheduler.tasks = []
    scheduler.load_tasks_from_owner(owner)
    # detect_conflicts must run before generate_plan, which overwrites manual start_times.
    st.session_state.overlap_warnings = scheduler.detect_conflicts()
    st.session_state.plan             = scheduler.generate_plan()

if "plan" in st.session_state:
    plan             = st.session_state.plan
    overlap_warnings = st.session_state.get("overlap_warnings", [])
    all_conflicts    = plan.conflicts + overlap_warnings

    if all_conflicts:
        st.error(f"⚠️ {len(all_conflicts)} conflict(s) detected — review before confirming your schedule:")
        for conflict in all_conflicts:
            st.warning(conflict)
    else:
        st.success("No conflicts — your schedule looks good!")

    # sort_by_time gives a chronological view of every task that has an assigned time.
    timed_tasks = [t for t in scheduler.sort_by_time() if t.start_time is not None]
    st.dataframe(
        [
            {
                "Time":           t.start_time.strftime("%I:%M %p"),
                "Task":           t.name,
                "Pet":            t.pet.name if t.pet else "—",
                "Duration (min)": t.duration,
                "Priority":       t.priority.name,
                "Done":           "✓" if t.completed else "",
            }
            for t in timed_tasks
        ],
        use_container_width=True,
        hide_index=True,
    )

    with st.expander("Why this order?"):
        st.text(plan.explain_reasoning())
