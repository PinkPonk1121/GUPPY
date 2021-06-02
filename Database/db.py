from os.path import isfile
import sqlite3

DB_PATH = "C:/Users/Pink/PycharmProjects/GUPPY/Database/db/database.db"
BUILD_PATH = "Database/db/build.sql"

cxn = sqlite3.connect(DB_PATH, check_same_thread=False)
cur = cxn.cursor()


def with_commit(func):
    def inner(*args, **kwargs):
        func(*args, **kwargs)
        commit()

    return inner


@with_commit
def build():
    if isfile(BUILD_PATH):
        scriptexec(BUILD_PATH)


def commit():
    cxn.commit()


def close():
    cxn.close()


def field(command, *values):
    cur.execute(command, tuple(values))
    fetch = cur.fetchone()
    if fetch is not None:
        return fetch[0]


def record(command, *values):
    cur.execute(command, tuple(values))
    return cur.fetchone()


def records(command, *values):
    cur.execute(command, tuple(values))
    return cur.fetchall()


def column(command, *values):
    cur.execute(command, tuple(values))
    return [item[0] for item in cur.fetchall()]


def execute(command, *values):
    cur.execute(command, tuple(values))


def multiexec(command, valueset):
    cur.executemany(command, valueset)


def scriptexec(path):
    with open(path, "r", encoding="utf-8") as script:
        cur.executescript(script.read())

petstats_table = '''CREATE TABLE IF NOT EXISTS petstat(
    PetID varchar PRIMARY KEY,
    name text,
    species text NOT NULL,
    hp int NOT NULL,
    atk integer NOT NULL,
    defend integer NOT NULL,
    speed integer NOT NULL,
    mana integer NOT NULL,
    ele_type text NOT NULL,
    level integer DEFAULT 1,
    tier integer DEFAULT 1,
    exp integer DEFAULT 0,
    hunger integer DEFAULT 50,
    fun integer DEFAULT 50,
    skill1 text,
    skill2 text
)'''

users_table = '''CREATE TABLE IF NOT EXISTS userpet(
    UserID integer PRIMARY KEY,
    UserLevel integer DEFAULT 1,
    Pet1 integer,
    Pet2 integer,
    Pet3 integer,
    Pet4 integer,
    Pet5 integer
)'''

all_pet_table = '''CREATE TABLE IF NOT EXISTS petlist(
    species text PRIMARY KEY,
    ele_type text NOT NULL,
    tier integer DEFAULT 1,
    nextevo integer,
    hp int NOT NULL,
    atk integer NOT NULL,
    defend integer NOT NULL,
    speed integer NOT NULL,
    mana integer NOT NULL,
    pic text NOT NULL
)'''


cur.execute(petstats_table)
cur.execute(users_table)
cur.execute(all_pet_table)
