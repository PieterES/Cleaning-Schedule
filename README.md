# Cleaning-Schedule
A much too complicated system to assign the cleaning schedule for 15 roommates

As it was my task to create the cleaning schedule, I came to the conclusion that it was a constrained problem that I could solve easily with a small algorithm. We get the dates of the coming sundays and mondays of the amount of coming weeks we want, separate the roommates into teams of 5 and create a roster.

# Rules:

Everybody does the toilets once every 15 weeks.
If you had a certain task the previous week, you won't have that the next week
Everyone has the same amount of shifts
Everyone has a shift every 3 weeks

We also keep track who did a task last week so people don't have a task so that when we create a new roster or when the 15th week is reached, people don't have tasks two weeks in a row.
However, we cannot ensure that everyone has a shift every 3 weeks if we create a roster bigger than 15 weeks as we also want to change teams.

# Tasks:

Living room: 2 people
Hallway: 2 people
Toilets: 1 person

# Export:

We can also export it as csv, docx table or excel so we can easily use it (docx doesn't save the last entry)
