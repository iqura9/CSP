import random
from data import professors_info, groups, times, weekdays
from utils import (
    is_professor_busy,
    is_professor_assigned_to_group_on_day,
    heuristic_sort_professors,
    get_available_rooms,
)


def get_available_professors(weekday, time, group, schedule):
    """
    Отримує список доступних викладачів для заданого дня, часу та групи.
    """
    available_professors = []
    for professor, info in professors_info.items():
        if info["subjects"]:
            if not is_professor_busy(professor, weekday, time, schedule):
                if info["current_hours"] < info["max_hours"]:
                    if not is_professor_assigned_to_group_on_day(professor, group, weekday, schedule):
                        available_professors.append(professor)
    return available_professors


def assign_professor_to_schedule(group, weekday, time, schedule):
    """
    Призначає викладача до розкладу для заданої групи, дня та часу.
    """
    available_professors = get_available_professors(weekday, time, group, schedule)
    if not available_professors:
        return False
    available_professors = heuristic_sort_professors(available_professors)
    for professor in available_professors:
        subjects = professors_info[professor]["subjects"]
        if subjects:
            subject = random.choice(subjects)
            available_rooms = get_available_rooms(weekday, time, schedule)
            if available_rooms:
                room = random.choice(available_rooms)
                schedule[(group, weekday, time)] = (professor, subject, room)
                professors_info[professor]["current_hours"] += 1
                return True 
    return False

def csp_algorithm():
    schedule = {}
    for group in groups:
        for weekday in weekdays:
            for time in times:
                assigned = assign_professor_to_schedule(group, weekday, time, schedule)
                if not assigned:
                    schedule[(group, weekday, time)] = ("Вільно", "Немає предмету", "Немає аудиторії")
    return schedule

def print_schedule(schedule):
    for weekday in weekdays:
        print(f"\n{weekday}:")
        for group in groups:
            print(f"\nГрупа: {group}")
            for time in times:
                key = (group, weekday, time)
                if key in schedule:
                    professor, subject, room = schedule[key]
                    if professor != "Вільно":
                        office = professors_info[professor]["office"]
                        print(f"  Час: {time}, Викладач: {professor}, Предмет: {subject}, Аудиторія: {room}, Кабінет: {office}")
                    else:
                        print(f"  Час: {time}, Вікно в розкладі")
                else:
                    print(f"  Час: {time}, Немає даних")

