# PawPal+ Project Reflection

## 1. System Design

Some core actions a usr should be able to perform are:
- Adding a pet
- Scheduling a walk
- View today's tasks
- Add constraints to a schedule

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

The initial UML design contains the classes as well as their relationships. It includes attributes and methods for each class, and the relationship shows how these classes interact. Like it shows an owner can own multiple pets, an owner manages 1 schedule, a schedule contains multiple tasks, etc..

The classes I told Claude to include were Pet, Task, Constraint, and Schedule. I also said providing an Owner class would be a good idea, and it came up with DailyPlan on its own. However, I liked the addition of DailyPlan, so I chose to keep it. I said Pet should contain resposibilities related to the pet itself and should be able to update the pet info. Task class is responsible for containing any info related to tasks, including duration and priority, as well as be able to update these things. Constraint class should contain info related to constraints, and its responsibility is that it should be able to update any constraint info. The Schedule class should contain the tasks that need to be done as well as constraints that will fit within the schedule. I assigned it the responsibility of being able to add/remove tasks and constraints as well as be able to generate the daily plan.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

I did make some changes based on AI feedback. I made a Priority and ConstraintType enum for simplicity. Priority and ConstraintType were strings before, but this caused them to be fraigile when comparing strings. Enum is meant to help with this. Schedule.date is now a date object instead of a string as this avoids a string comparison. Task.pet is now optional so now a task can be created before being assigned a pet. Owner.schedule was also added as a Owner -> Schedule relationship was missing. Both Schedule and Task had ways to mark a task completed, but now Schedule does it by just called a function in Task to mark it compeleted. These changes make more sense and add some simplicity and usefulness.
---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

Some constraints we consider are time, priority, and duration. We use these constraints to help build the schedule around what the owner wants and thinks what tasks are more important than others.

Of course, priority is most important due to the fact that the owner chooses how important a task may be. We then take into account time constraints. Some owners may not want any tasks too early, too late, or at a certain time. Considering these constraints next is important. We then take into account the duration of a task to help avoid any overlaps in the schedule.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

One tradeoff the schedule had to make was not using the most optimal scheduling algorithm. While we could've made it most optimal by considering the task set as a whole, I chose to follow a greedy scheduling algorithm where when one task ends, another begins. There are no gaps or any lookahead.

This is reasonable because a pet owner with multiple tasks doesn't need an optimal solution, they just need a predictable one. This type of schedule will make their lives much easier as they are using this app to assist them. This algorithm always produces a complete schedule, and it is easy to reason about when something looks wrong.
---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
