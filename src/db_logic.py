import sqlite3
import os
from datetime import datetime as dt
from datetime import timedelta

from formats import (date_to_text,
                    time_to_text, text_to_time,)
from settings import filters_of_repeats

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.sqlite")
con = sqlite3.connect(DB_PATH)
cur = con.cursor()

date_now = dt.today()


def create_database():
    cur.executescript('''
    CREATE TABLE IF NOT EXISTS Types (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    description TEXT
    );

    CREATE TABLE IF NOT EXISTS Types_body (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    description TEXT
    );

    CREATE TABLE IF NOT EXISTS Trainings (
    id INTEGER PRIMARY KEY,
    date TEXT,
    type_body_id INTEGER NOT NULL,
    FOREIGN KEY(type_body_id) REFERENCES Types_body(id)
    );

    CREATE TABLE IF NOT EXISTS Exercises (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    time TEXT,
    type_body_id INTEGER NOT NULL,
    type_id INTEGER NOT NULL,
    FOREIGN KEY(type_id) REFERENCES Types(id),
    FOREIGN KEY(type_body_id) REFERENCES Types_body(id)
    );

    CREATE TABLE IF NOT EXISTS Repeats (
    id INTEGER PRIMARY KEY,
    weight INTEGER,
    count INTEGER NOT NULL,
    time TEXT,
    exercise_id INTEGER NOT NULL,
    training_id INTEGER NOT NULL,
    FOREIGN KEY(exercise_id) REFERENCES Exercises(id),
    FOREIGN KEY(training_id) REFERENCES Trainings(id)
    );

    CREATE TABLE IF NOT EXISTS Tasks (
    id INTEGER PRIMARY KEY UNIQUE,
    exercise_id INTEGER NOT NULL,
    weight INTEGER,
    count INTEGER NOT NULL,
    date TEXT,
    create_date TEXT,
    complete_date TEXT,
    FOREIGN KEY(exercise_id) REFERENCES Exercises(id)
    );
    ''')
    con.commit()


def fill_db():
    Types = [
        ('Жим', 'Толкание от себя'),
        ('Тяга', 'Тяга к себе'),
        ('Сгибания рук', 'Сгибания рук в зоне предплечья или запястья'),
        ('Сгибания ног', 'Сгибания ног в зоне колена или голеностопа'),
        ('Разгибания рук', 'Разгибания рук в зоне предплечья или запястья'),
        ('Разгибания ног', 'Разгибания ног в зоне колена или голеностопа'),
        ('Бег', 'Бег или ходьба по дорожке'),
        ('Лестница', 'Подъем по лестнице'),
        ('Присед', 'Приседания, выпады или прыжки'),
    ]
    Types_body = [
        ('Грудь', 'Грудные мыщцы, отвечающие за вывод рук от себя'),
        ('Спина', 'Мыщцы спины для подвода рук к себе'),
        ('Ноги', 'Квадрицепсы, бицепсы, икры ног'),
        ('Руки', 'Бицепс, трицепс, предплечье, плечи'),
        ('Торс', 'Пресс, плечи'),
    ]
    Exercises = [
        ('Жим лёжа', '0:00.00', 1, 1),
        ('Подтягивания', '0:00.00', 2, 2),
        ('Жим гантелей', '0:00.00', 1, 1)
    ]
    # Tasks = [
    #     (1, 75, 1, date_text, date_to_text(date_now))
    # ]
    cur.executemany('INSERT OR IGNORE INTO Types (name, description) VALUES(?, ?);', Types)
    cur.executemany('INSERT OR IGNORE INTO Types_body (name, description) VALUES(?, ?);', Types_body)
    cur.executemany('INSERT OR IGNORE INTO Exercises (name, time, type_body_id, type_id) VALUES(?, ?, ?, ?);', Exercises)
    # cur.executemany('INSERT OR IGNORE INTO Tasks (exercise_id, weight, count, date, create_date) VALUES(?, ?, ?, ?, ?);', Tasks)

    con.commit()


def get_info(type_training):
    return cur.execute(f'''
    SELECT id
    FROM Types_body
    WHERE name = '{type_training}';''')


def create_training(type_body):
    Trainings = [
        (date_to_text(date_now), type_body),
    ]
    cur.executemany('INSERT INTO Trainings (date, type_body_id) VALUES(?, ?);', Trainings)
    con.commit()


def get_trainings_with_repeats(filter_name, filter_id):  # date
    trainings = cur.execute(f"""
    SELECT Trainings.date, Types_body.name, Exercises.name, Repeats.count, Repeats.weight
    FROM Trainings, Repeats, Exercises, Types_body
    WHERE {filters_of_repeats[filter_name]} = {filter_id} AND Trainings.id = Repeats.training_id
                                                            AND Repeats.exercise_id = Exercises.id
                                                            AND Trainings.type_body_id = Types_body.id;""")
    return [list(i) for i in trainings]

def get_trainings():
    trainings = cur.execute("""
    SELECT Trainings.id, Trainings.date, Types_body.name
    FROM Trainings, Types_body
    WHERE Trainings.type_body_id = Types_body.id;""")
    return [list(i) for i in trainings]

def create_type(type_var, name, description):
    strings = ('Types', 'Types_body')
    Types = [
        (name, description),
    ]
    cur.executemany(f'INSERT INTO {strings[type_var]} (name, description) VALUES(?, ?);', Types)
    con.commit()


def create_exercise(name, time_var, type_body, type_exercise):
    Exercises = [
        (name, time_var, type_body, type_exercise),
    ]
    cur.executemany('INSERT INTO Exercises (name, time, type_body_id, type_id) VALUES(?, ?, ?);', Exercises)
    con.commit()


def get_exercises(filter_name, filter_id):
    exercises = cur.execute(f'''
    SELECT Exercises.id, Exercises.name, time, Types.name, Types_body.name
    FROM Exercises, Types_body, Types
    WHERE {filters_of_repeats[filter_name]} = {filter_id}   AND Exercises.type_body_id = Types_body.id
                                                            AND Exercises.type_id = Types.id;''')
    return [list(i) for i in exercises]

def get_exercises_and_repeats(training_id):
    exercises = cur.execute(f'''
    SELECT Repeats.id, Repeats.weight, Repeats.count, Exercises.name
    FROM Repeats, Exercises
    WHERE training_id = {training_id} AND Repeats.exercise_id = Exercises.id
    ORDER BY Exercises.name;''')
    return [list(i) for i in exercises]

def add_time_to_exercise(exercise_id, time_delta):
    cur.execute('''
    SELECT time
    FROM Exercises
    WHERE id = ?
    ''', (exercise_id,))
    time_var = text_to_time(cur.fetchone()[0])

    time_var += timedelta(hours=time_delta.hour, minutes=time_delta.minute, seconds=time_delta.second)
    cur.execute('''
    UPDATE Exercises
    SET time = ? WHERE id = ?
    ''', (time_to_text(time_var), exercise_id))
    con.commit()


def create_repeat(weight, count, time_var, exercise_id, training_id):
    Repeat = [
        (weight, count, time_var, exercise_id, training_id),
    ]
    cur.executemany('INSERT INTO Repeats (weight, count, time, exercise_id, training_id) VALUES(?, ?, ?, ?, ?);', Repeat)
    con.commit()


def get_repeats(filter_name, filter_id):
    repeats = cur.execute(f'''
    SELECT
        Exercises.name,
        Repeats.weight,
        Repeats.count,
        Repeats.time,
        Repeats.id,
        Types.name,
        Types_body.name
    FROM Repeats
    JOIN Trainings ON Repeats.training_id = Trainings.id
    JOIN Exercises ON Repeats.exercise_id = Exercises.id
    JOIN Types_body ON Exercises.type_body_id = Types_body.id
    JOIN Types ON Exercises.type_id = Types.id
    WHERE {filters_of_repeats[filter_name]} = ?
    ''', (filter_id,))
    return [list(i) for i in repeats]


def create_task(exercise_id, weight, count, date_var):
    Repeat = [
        (exercise_id, weight, count, date_var, date_to_text(date_now)),
    ]
    cur.executemany('INSERT INTO Tasks (exercise_id, weight, count, date, create_date) VALUES(?, ?, ?, ?, ?);', Repeat)
    con.commit()


def get_tasks():  # dates  filter_name, filter_id
    tasks = cur.execute('''
    SELECT Tasks.id, Exercises.name, Tasks.weight, Tasks.count, Tasks.date, Tasks.create_date, Tasks.complete_date, Types.name, Types_body.name
    FROM Tasks
    JOIN Exercises ON Tasks.exercise_id = Exercises.id
    JOIN Types_body ON Exercises.type_body_id = Types_body.id
    JOIN Types ON Exercises.type_id = Types.id;''')
    return [list(i) for i in tasks]

def get_types_body():
    types_body = cur.execute('''SELECT name FROM Types_body ORDER BY id''')
    return types_body

def get_exercises_names():
    exercises_names = cur.execute('''SELECT name FROM Exercises ORDER BY id''')
    return exercises_names

# create_database()
# fill_db()

# create_training(2)
# create_repeat(0, 10, "1:14.0", 2, 1)
# create_repeat(0, 7, "0:56.0", 2, 1)
# create_repeat(0, 3, "0:31.0", 2, 1)

# create_training(1)
# create_repeat(15, 12, "0:40.0", 3, 2)
# create_repeat(20, 12, "0:56.0", 3, 2)
# create_repeat(25, 4, "0:36.0", 3, 2)

# create_task(1, 12, 2, "01.01.2027")
# add_time_to_exercise(1, time(hour=1, minute=1, second=5))

# print(get_exercises_names())
# print(get_exercises(2, 1))
# print(get_repeats(1, 1))
# print(get_exercises(2, 1))
# print(get_trainings())
# print(get_tasks())

# con.close()
