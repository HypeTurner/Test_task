import json
from datetime import datetime, timedelta
from collections import defaultdict

categories = ("M15", "M16", "M18", "W15", "W16", "W18")

def total_time(time_str_finish, time_str_start):
    """Общее время забега"""
    time_obj_finish = datetime.strptime(time_str_finish, "%H:%M:%S")
    time_obj_start = datetime.strptime(time_str_start, "%H:%M:%S")
    if time_obj_finish < time_obj_start:
        return time_obj_finish.hour * 3600 + 24 * 3600 - time_obj_start.hour * 3600 + time_obj_finish.minute * 60 - time_obj_start.minute * 60 + time_obj_finish.second - time_obj_start.second
    return time_obj_finish.hour * 3600 - time_obj_start.hour * 3600 + time_obj_finish.minute * 60 - time_obj_start.minute * 60 + time_obj_finish.second - time_obj_start.second


def load_to_json(category, results):
    """Выгрузка данных"""
    with open(f"{category}.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

def calculate_prizes(filename):
    """Запоминаем призы в категориях"""
    prizes = []
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                prizes.append(' '.join(line.strip().split()[2:]))
        return prizes
    except FileNotFoundError:
        print(f"Файл prizes_list_{filename} не найден")
        return []


def calculate_result():
    """"Расчёт призов спортсменам"""
    prizes = {category: calculate_prizes(f"Data\\prizes_list_{category.lower()}.txt") for category in categories}
    try:
        with open("Data\\race_data.json", encoding = 'utf-8') as f:
            race_data = json.load(f)
    except FileNotFoundError:
        print("Файл race_data.json не найден.")
        return 1

    results_by_category = defaultdict(list)

    for athlete in race_data:
        race_time = total_time(athlete["Время финиша"], athlete["Время старта"])
        if race_time is None: continue

        results_by_category[athlete["Категория"]].append({
            "Нагрудный номер": athlete["Нагрудный номер"],
            "Имя и Фамилия": athlete["Имя"] + " " + athlete["Фамилия"],
            "Время": str(timedelta(seconds=race_time)),
            "race_time_seconds": race_time,
            "bib_number": athlete["Нагрудный номер"]
        })

    for category, athletes in results_by_category.items():
        athletes.sort(key=lambda x: (x["race_time_seconds"], x["bib_number"]))
        for i, athlete in enumerate(athletes):
            place = i + 1
            prize = prizes[category][i] if i < len(prizes[category]) else None
            athlete["Место"] = place
            if prize is not None:
                athlete["Приз"] = prize
            del athlete["race_time_seconds"]
            del athlete["bib_number"]

        load_to_json(category, athletes)



def main():
    calculate_result()

if __name__ == "__main__":
	main()