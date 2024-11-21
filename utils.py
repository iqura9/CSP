from data import professors_info, rooms, times, weekdays

def is_professor_busy(professor, weekday, time, schedule):
    """
    Перевіряє, чи зайнятий викладач у заданий день та час.
    """
    return any(
        value[0] == professor
        for key, value in schedule.items()
        if key[1] == weekday and key[2] == time
    )

def is_professor_assigned_to_group_on_day(professor, group, weekday, schedule):
    """
    Перевіряє, чи викладач вже викладає цій групі в заданий день.
    """
    return any(
        value[0] == professor
        for key, value in schedule.items()
        if key[0] == group and key[1] == weekday
    )

def heuristic_sort_professors(professors_list):
    """
    Сортує список викладачів за евристикою (мінімум залишкових годин).
    """
    return sorted(
        professors_list,
        key=lambda prof: professors_info[prof]["max_hours"] - professors_info[prof]["current_hours"]
    )

def get_available_rooms(weekday, time, schedule):
    """
    Отримує список доступних аудиторій для заданого дня та часу.
    """
    available_rooms = []
    for room in rooms:
        room_occupied = any(
            value[2] == room
            for key, value in schedule.items()
            if key[1] == weekday and key[2] == time
        )
        if not room_occupied:
            available_rooms.append(room)
    return available_rooms