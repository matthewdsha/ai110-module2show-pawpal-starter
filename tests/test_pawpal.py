from pawpal_system import Pet, Priority, Task


def test_mark_completed_changes_status():
    task = Task(name="Morning Walk", duration=30, priority=Priority.HIGH)
    assert task.completed is False
    task.mark_completed()
    assert task.completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet(name="Buddy", species="Dog", breed="Labrador", age=3)
    assert len(pet.tasks) == 0
    pet.add_task(Task(name="Feed Buddy", duration=10, priority=Priority.HIGH))
    assert len(pet.tasks) == 1
