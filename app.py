import streamlit as st
from datetime import date

from pawpal_system import Frequency, Owner, Pet, Priority, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

# ---------------------------------------------------------------------------
# Session state init — objects are created once and reused across reruns.
# The "not in" check is the standard Streamlit guard: skip creation if the
# object already exists in the session vault.
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
    pet_name  = st.text_input("Pet name")
    species   = st.selectbox("Species", ["Dog", "Cat", "Other"])
    breed     = st.text_input("Breed")
    age       = st.number_input("Age", min_value=0, max_value=30, value=1)
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
        task_name    = st.text_input("Task name")
        description  = st.text_input("Description (optional)")
        duration     = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
        priority     = st.selectbox("Priority", ["LOW", "MEDIUM", "HIGH"], index=1)
        frequency    = st.selectbox("Frequency", ["ONCE", "DAILY", "WEEKLY", "AS_NEEDED"])
        if st.form_submit_button("Add task"):
            target_pet = next(p for p in owner.pets if p.name == selected_pet_name)
            target_pet.add_task(Task(
                name=task_name,
                duration=int(duration),
                priority=Priority[priority],
                description=description,
                frequency=Frequency[frequency],
            ))
            st.success(f"Added '{task_name}' for {selected_pet_name}!")

    all_tasks = owner.get_all_tasks()
    if all_tasks:
        for task in all_tasks:
            pet_label = task.pet.name if task.pet else "unassigned"
            st.write(f"- [{task.priority.name}] **{task.name}** ({pet_label}) — {task.duration} min")
    else:
        st.info("No tasks yet. Add one above.")
else:
    st.info("Add a pet before adding tasks.")

# ---------------------------------------------------------------------------
# Schedule
# ---------------------------------------------------------------------------
st.divider()
st.subheader("Today's Schedule")

if st.button("Generate schedule"):
    scheduler.tasks = []  # clear stale references before reloading
    scheduler.load_tasks_from_owner(owner)
    st.session_state.plan = scheduler.generate_plan()

if "plan" in st.session_state:
    plan = st.session_state.plan
    for i, task in enumerate(plan.ordered_tasks, 1):
        pet_label = task.pet.name if task.pet else "unassigned"
        time_str  = task.start_time.strftime("%I:%M %p") if task.start_time else "--:--"
        status    = "[x]" if task.completed else "[ ]"
        st.write(f"{i}. {status} **{time_str}** — {task.name} ({pet_label}) | {task.duration} min | {task.priority.name}")

    with st.expander("Why this order?"):
        st.text(plan.explain_reasoning())
