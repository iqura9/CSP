import random

groups = ["ТТП-41", "ТТП-42"]
rooms = ["А39", "А41", "А43"]
times = ["8:40-10:10", "10:35-12:10", "12:20-13:55"]
professors_info = {
    "Проф. Нікітченко Микола Степанович": {"office": "601", "subjects": ["формальні моделі програмування", "мови програмування та мови специфікацій", "формальні методи розробки програм", "логіка предикатів на різних рівнях абстракції", "абстрактна обчислювальність"], "max_hours": 3, "current_hours": 0},
    "Проф. Дорошенко Анатолій Юхимович": {"office": "602", "subjects": ["кластерні паралельні обчислення", "grid-технології і «хмарні» системи", "агентно-орієнтовані технології та засоби інтелектуалізації програмування", "крупномасшабні прикладні обчислення (метеорологія, екологія)", "автоматизація наукових досліджень"], "max_hours": 3, "current_hours": 0},
    "Проф. Шкільняк Степан Степанович": {"office": "608", "subjects": ["логіко-математичні засоби специфікацій програм", "математична логіка"], "max_hours": 3, "current_hours": 0},
    "Доц. Волохов Віктор Миколайович": {"office": "610", "subjects": ["системне програмування", "теорія та технології баз даних", "комп'ютерні мережі", "безпека інформації в комп'ютерних мережах"], "max_hours": 3, "current_hours": 0},
    "Доц. Зубенко Віталій Володимирович": {"office": "605", "subjects": ["основи інформатики та програмування", "програмні логіки", "інформаційне моделювання", "дистанційне навчання"], "max_hours": 3, "current_hours": 0},
    "Доц. Панченко Тарас Володимирович": {"office": "611", "subjects": ["композиційні методи", "інтернет-технології", "бази даних"], "max_hours": 3, "current_hours": 0},
    "Доц. Омельчук Людмила Леонідівна": {"office": "610", "subjects": ["формальні методи розробки програм", "технології програмування"], "max_hours": 3, "current_hours": 0},
    "Доц. Ткаченко Олексій Миколайович": {"office": "603", "subjects": ["технології програмування", "формальні методи розробки ПЗ", "освітні ІТ"], "max_hours": 3, "current_hours": 0},
    "Доц. Русіна Наталія Геннадіївна": {"office": "605", "subjects": ["формування інформатичних компетентностей", "розробка інформаційних систем для дистанційного навчання", "тестовий інструментарій", "дослідження методів специфікації та верифікації програмних систем"], "max_hours": 3, "current_hours": 0},
    "Асис. Криволап Андрій Володимирович": {"office": "612", "subjects": ["формальні методи", "верифікація програмного забезпечення", "програмні логіки", "теорія категорій"], "max_hours": 3, "current_hours": 0},
    "Асис. Белова Анна Сергіївна": {"office": "603", "subjects": [], "max_hours": 3, "current_hours": 0},
    "Асис. Поліщук Наталія Володимирівна": {"office": "603", "subjects": [], "max_hours": 3, "current_hours": 0},
    "Асис. Шишацька Олена Володимирівна": {"office": "604", "subjects": ["формальна розробка програм", "програмні алгебри", "багатозначні логіки"], "max_hours": 3, "current_hours": 0},
    "Асис. Свистунов Антон Олександрович": {"office": "606", "subjects": ["хмарні обчислення", "розподілені системи", "архітектура програмних систем", "технології програмування"], "max_hours": 3, "current_hours": 0}
}
# Дні тижня
weekdays = ["Понеділок", "Вівторок", "Середа", "Четвер", "Пʼятниця"]

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

def assign_professor_to_schedule(group, weekday, time, schedule):
    """
    Призначає викладача до розкладу для заданої групи, дня та часу.
    """
    available_professors = get_available_professors(weekday, time, group, schedule)
    if not available_professors:
        return False  # Немає доступних викладачів
    available_professors = heuristic_sort_professors(available_professors)
    for professor in available_professors:
        subjects = professors_info[professor]["subjects"]
        if subjects:
            subject = random.choice(subjects)
            available_rooms = get_available_rooms(weekday, time, schedule)
            if available_rooms:
                room = random.choice(available_rooms)
                # Призначення розкладу
                schedule[(group, weekday, time)] = (professor, subject, room)
                professors_info[professor]["current_hours"] += 1
                return True  # Успішно призначено
    return False  # Не вдалося призначити

def csp_algorithm():
    schedule = {}
    for group in groups:
        for weekday in weekdays:
            for time in times:
                assigned = assign_professor_to_schedule(group, weekday, time, schedule)
                if not assigned:
                    # Якщо не вдалося призначити викладача
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

schedule = csp_algorithm()
print_schedule(schedule)
