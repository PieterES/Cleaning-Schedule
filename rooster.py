import numpy as np
import random
import pandas as pd
import csv
from datetime import datetime, timedelta
import locale
import copy
from docx import Document

# Create a new Document
doc = Document()

# If we want to print or export the roster
EXPORT = True
PRINT = True

# If we want to remove the people that were assigned last week when we reach week 15 and reassign everyone
REMOVE = True

# Amount of weeks for the roster
roster_length = 60

# Define tasks and their requirements
tasks = {
    'Woonkamer': 2,
    'Gang': 2,
    'Toiletten': 1,
}

# List of roommates that were assigned last week
names_to_remove = [
    'Milena',
    'Sanne',
    'Joren',
    'Bastiaan',
    'Anouk'
]
# List of roommate names
roommates = [
    'Milena',
    'Sanne',
    'Joren',
    'Bastiaan',
    'Anouk',
    'Pieter',
    'Alex',
    'Irene',
    'Noa',
    'Caspar',
    'Susana',
    'Jelle',
    'Margriet',
    'Lodewijk',
    'Mathis'
]

# Add a table to the document
table = doc.add_table(rows=1, cols=4)

# Add headers to the table
hdr_cells = table.rows[0].cells
hdr_cells[0].text = 'Datum'
hdr_cells[1].text = 'Woonkamer'
hdr_cells[2].text = 'Gang'
hdr_cells[3].text = 'Toiletten'

def create_dates(roster_length):
    """
    Creates the dates of the sunday and monday of the coming weeks depending on roster_length
    :return: dates
    """
    # Set the locale to Dutch for month name
    locale.setlocale(locale.LC_TIME, 'nl_NL.UTF-8')

    # Get the current date
    current_date = datetime.now()

    # Create all the dates of the next sundays and mondays
    dates = []
    for _ in range(roster_length):
        days_until_sunday = (6 - current_date.weekday() + 7) % 7

        next_sunday = current_date + timedelta(days=days_until_sunday)
        next_monday = next_sunday + timedelta(days=1)

        formatted_sunday = next_sunday.strftime("%d")
        formatted_monday = next_monday.strftime("/" + "%d")
        dates.append(formatted_sunday + formatted_monday + " " + next_monday.strftime("%B"))

        current_date = next_sunday + timedelta(days=7)
    return dates

def create_output(weeks_with_tasks, dates):
    """
    Merges the tasks and dates so we can create the roster and either print or export is as excel or csv
    :param weeks_with_tasks: All the tasks for the coming weeks
    :param dates: All the dates for the coming weeks
    :return: Matched dates and weeks
    """
    # Create list of dictionaries
    data = []
    for i, team_with_tasks in enumerate(weeks_with_tasks):
        date = dates[i]
        woonkamer = ', '.join(team_with_tasks['tasks']['Woonkamer'])
        gang = ', '.join(team_with_tasks['tasks']['Gang'])
        wc = ', '.join(team_with_tasks['tasks']['Toiletten'])
        data.append({'Datum': date, 'Woonkamer': woonkamer, 'Gang': gang, 'Toiletten': wc})
    print(data)
    if PRINT:
        for d in data:
            print(d)

    if EXPORT:
        for row_data in data:
            row_cells = table.add_row().cells
            for i, key in enumerate(row_data.keys()):
                row_cells[i].text = row_data[key]
        doc.save('date_table.docx')
        # Create DataFrame
        df = pd.DataFrame(data)
        #
        # # Export to Excel
        df.to_excel("tasks.xlsx", index=False)
        #
        # # Export to CSV
        with open("tasks.csv", "w", newline="") as csvfile:
            fieldnames = ['Datum', 'Woonkamer', 'Gang', 'Toiletten']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            writer.writerows(data)

def create_teams(roommates, names_to_remove):
    """
    Separates all the roommates into teams, these teams will be the same for the coming 15 weeks
    After that the teams will switch.
    :param roommates: All the names of the roommates
    :return: roommates separated into teams
    """
    names_per_team = len(roommates) // 3
    random.shuffle(roommates)

    if REMOVE:
        results_list = [name for name in roommates if name not in names_to_remove]
        team1 = results_list[:5]
        results_list = [name for name in roommates if name not in team1]
        random.shuffle(results_list)
        team2 = results_list[:5]
        team3 = results_list[5:]

    # Separate the names into 3 teams
    else:
        team1 = roommates[:names_per_team]
        team2 = roommates[names_per_team:2 * names_per_team]
        team3 = roommates[2 * names_per_team:]

    teams = [roommates[:names_per_team], roommates[names_per_team:2*names_per_team], roommates[2 * names_per_team:]]

    return teams

def assign(teams, dates, rooster_lengte, names_to_remove):
    """
    Assigns the teams to tasks.
    Rules:
    Everybody does the toilets once every 15 weeks.
    If you had a certain task the previous week, you won't have that the next week
    Everyone has the same amount of shifts
    Everyone has a shift every 3 weeks

    :param teams: All the roommates separated into 3 teams
    :param dates: All the dates that need to be filled in
    :param rooster_lengte: The length of the roster
    :return: Roommates assigned to tasks for all the necessary weeks

    The only thing that can happen that if we reach week 15, we reassign eveyrone, we only keep track of the last time
    so then it is possible that people have shifts after 2 weeks instead of 3. Otherwise the teams will never switch
    """

    # Need to keep track of who did the toilets the last time as we can place them last as they are the least constrained
    toilet_person = None

    # Keeps track of all the current teams and previous teams, necessary for knowing who did what in previous weeks
    teams_with_tasks = []
    previous_teams_with_tasks = []
    previous_team_with_tasks = None
    # For the amount of weeks
    for week in range(rooster_lengte // len(teams)):

        # If week = 5, so a full roster has been created, we reassign everyone to new teams, begin from scratch
        if week % 5 == 0:
            roommates = []
            for subteam in teams:
                roommates.extend(subteam)
            if previous_team_with_tasks:
                if REMOVE:
                    names_to_remove = previous_teams_with_tasks[-1]['team']
            teams = create_teams(roommates, names_to_remove)

            toilet_person = None

            previous_teams_with_tasks = []
            previous_team_with_tasks = None
        for team_index, team in enumerate(teams):
            # When we begin from scratch, we need new information for the first 3 weeks
            if week % 5 == 0:

                # Set the current and previous teams to nothing
                team_with_tasks = {'team': copy.deepcopy(team), 'tasks': {}}
                previous_team_with_tasks = {'team': set(), 'tasks': {}, 'toilet_person': {}}

                # For each task, we get the task and the required people
                for task, required_people in tasks.items():

                    # Initialize lists
                    team_with_tasks['tasks'][task] = []
                    previous_team_with_tasks['tasks'][task] = []

                    # For each person we need per task
                    for _ in range(required_people):

                        # First week so we don't need to keep to constraints, just take the first person and put them somewhere
                        person = team_with_tasks['team'].pop()
                        team_with_tasks['tasks'][task].append(person)
                        previous_team_with_tasks['team'].add(person)
                        previous_team_with_tasks['tasks'][task].append(person)

                        # We do need to keep track of who did the toilet. We can go through tasks and then toilet, but this is more readable
                        if task == 'Toiletten':
                            previous_team_with_tasks['toilet_person'] = person

                # Add the team to current and previous teams
                # Current team for output, previous for keeping track
                teams_with_tasks.append(team_with_tasks)
                previous_teams_with_tasks.append(previous_team_with_tasks)

            else:
                # We get the previous team and associated tasks using the team_index which will reset to 0 after 3 weeks
                previous_team_with_tasks = previous_teams_with_tasks[team_index]
                team_with_tasks = {'team': copy.deepcopy(team), 'tasks': {}}

                # We check who did the toilets the last time, as they can be assigned to both 'Woonkamer' and 'Gang'.
                # We put them at the front of the array, as we work backwards and we want to select them last.
                toilet_person = previous_team_with_tasks['toilet_person']
                team_with_tasks['team'].remove(toilet_person)
                team_with_tasks['team'].insert(0, toilet_person)

                # Initialize lists for each task
                team_with_tasks['tasks']['Woonkamer'] = []
                team_with_tasks['tasks']['Gang'] = []
                team_with_tasks['tasks']['Toiletten'] = []

                # For each task and required people
                for task, required_people in tasks.items():

                    for _ in range(required_people):

                        # We select the last person in the list, which is never the toilet person
                        person = team_with_tasks['team'][-1]

                        # Check if the person already did toilets in the previous 15 weeks and toilets are not full
                        if person not in previous_team_with_tasks['tasks']['Toiletten'] and len(team_with_tasks['tasks']['Toiletten']) < 1:
                            person = team_with_tasks['team'].pop()

                            # If the person is in another group
                            if person in previous_team_with_tasks['tasks']['Gang']:
                                previous_team_with_tasks['tasks']['Gang'].remove(person)
                            if person in previous_team_with_tasks['tasks']['Woonkamer']:
                                previous_team_with_tasks['tasks']['Woonkamer'].remove(person)

                            # Assign that person to the toilet
                            team_with_tasks['tasks']['Toiletten'].append(person)
                            previous_team_with_tasks['tasks']['Toiletten'].append(person)
                            toilet_person = person
                            previous_team_with_tasks['toilet_person'] = toilet_person

                        # If the person did do toilets, but not woonkamer in the previous week and woonkamer is not full
                        elif person not in previous_team_with_tasks['tasks']['Woonkamer'] and len(team_with_tasks['tasks']['Woonkamer']) < 2:
                            person = team_with_tasks['team'].pop()

                            # We remove that person from the 'Gang' task for the previous tasks of next week
                            # We do not remove that person from toilets as we don't want to assign someone more often to toilets than once every 15 weeks
                            if person in previous_team_with_tasks['tasks']['Gang']:
                                previous_team_with_tasks['tasks']['Gang'].remove(person)
                            team_with_tasks['tasks']['Woonkamer'].append(person)
                            previous_team_with_tasks['tasks']['Woonkamer'].append(person)

                        # If the person did do toilets and did woonkamer last week or woonkamer is already full, we assign it to gang
                        elif person not in previous_team_with_tasks['tasks']['Gang'] and len(team_with_tasks['tasks']['Gang']) < 2:
                            person = team_with_tasks['team'].pop()

                            # Remove from woonkamer similar to logic above
                            if person in previous_team_with_tasks['tasks']['Woonkamer']:
                                previous_team_with_tasks['tasks']['Woonkamer'].remove(person)

                            team_with_tasks['tasks']['Gang'].append(person)
                            previous_team_with_tasks['tasks']['Gang'].append(person)

                # Add the team with the tasks to the total teams with tasks.
                teams_with_tasks.append(team_with_tasks)

    return teams_with_tasks

def main():
    dates = create_dates(roster_length)
    teams = create_teams(roommates, names_to_remove)
    weeks_with_tasks = assign(teams, dates, roster_length, names_to_remove)
    if EXPORT or PRINT:
        create_output(weeks_with_tasks, dates)


if __name__ == "__main__":
    main()
