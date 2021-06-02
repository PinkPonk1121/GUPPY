CREATE TABLE IF NOT EXISTS petstat(
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
);

CREATE TABLE IF NOT EXISTS userpet(
    UserID integer PRIMARY KEY,
    UserLevel integer DEFAULT 1,
    Pet1 integer,
    Pet2 integer,
    Pet3 integer,
    Pet4 integer,
    Pet5 integer,
);

CREATE TABLE IF NOT EXISTS petlist(
    species text PRIMARY KEY,
    ele_type text NOT NULL,
    tier integer DEFAULT 1,
    nextevo integer,
    hp int NOT NULL,
    atk integer NOT NULL,
    defend integer NOT NULL,
    speed integer NOT NULL,
    mana integer NOT NULL,
);