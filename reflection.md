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

The AI tools were useful throughout this entire project. It was helpful for design, debugging, refactoring, and understanding parts of the code and features. I used it to help me develop an idea of how I wanted to project to look, and then it gave me an outline. Afterward, I developed the project and used the AI to help me test and debug it. Afterward, I had it review the code for correctness and refactoring to see if any improvements could be made. It made this task a lot easier as it felt I had a super fast assistant to help me with anything I needed.

Good prompts I used included very specific instructions, including what exactly I wanted from it. As long as I included features I wanted and key words on what to do, the AI would do it very quickly and easily. Saying things like "identify", "develop", and "verify" as a few examples helped a lot when it came to telling the AI what exactly I wanted.

The plan feature for the UML diagram helped a lot. We were able to collaborate to develop a diagram I was happy with, and the AI suggested a lot of useful ideas on what to include.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

When I noticed it developed code that did not work properly or looked too complex. Of course, sometimes the algorithms will require some sort of complexity in order to work, but I tried to make it more simplified as readability is also important. When I realized there was a bug in the code when a conflict were occur due to overlapping times, I asked the AI to suggest a fix. After viewing it, I chose not to accept as it not only did not fix the issue right away, but it also made the system more complex.

I mostly verify and evaluate AI suggestion based on its reasoning and how well it actually completes the task. If there is some complexity, that is ok as that can be worked around. Ensuring the code does what it is meant to do correctly is most important as the customer experience will be most important, and we want things to be correct for them.

Sometimes I needed to refresh the chat and start a new one as the AI would get too tunnel-visioned on an incorrect solution it came up with. It would try to edit the solution that did not work at all, and it fell deeper into that rabbit hole.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

I tested quite a few behaviors. I check adding owners, pets, and tasks as well as checking the schedule. These are the core features, and these MUST be working properly at a bare minimum. Afterward, I took a look at conflict and testing for different types of conflict as well as adding schedule restraints.

These tests are very important as they are core behaviors for the app. Customers use this app for these features, and I need to ensure they work properly. If customers were not able to add a new pet or task, that would lead to issues as a schedule would just generate as empty. Or if conflicts did not work, then that means the schedule would be incorrect, and this would confuse the customer. Testing these behaviors allows me to verify the app is working and shows the features work properly as expected.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

I am pretty confident overall that the schedule works correctly. I spent quite a bit of my time testing conflicts, adding multiple pets, and overlapping tasks. It seems to generate a schedule that works well and has reasoning on why it works. There could always be some lingering bugs or edge cases though, so it does not have my full confidence.

Maybe some edge cases I could test for are maybe negative values, weird task time intervals (like ones that go past midnight), and daylight savings. These are just some very obscure edge cases I came up with that could be fun to tackle in the future.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

I felt developing the UML diagram and seeing the outline and code being developed after went well. It felt extremely satisfying to see it go from diagram to actual code, and I thought it was really cool. I feel most satisfied with this as well as seeing a lot of the core features of the app working.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

For starters, I would definitely want to improve the actual look of the app. Of course, we were mainly focusing on function and features, so I would hope to maybe decrease the complexity of my code a little. The code works, but some parts of it can be a little complex or long.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

One important thing I learned about designing systems was that they all need to work well together. If one part of the system doesn't work, then the rest would not function well. For instance in this app, all parts of the system needed to work together. Generating a schedule requires tasks, and adding tasks requires having pets added, and adding pets require an owner. I need to ensure all parts work together and make sense.

Working with AI on this project has also taught me that it is important to get the core design right, and AI helps me realize solutions that may work better than my own. Sometimes it will not always have the best solution, but it allows for a fresh perspective on it. Being the "lead architect" when collaborating with the AI tools was extremely fun and showed me where I need to improve on when it comes to system design and such.