CREATE TABLE IF NOT EXISTS game_types (
    type_id SERIAL PRIMARY KEY,
    name VARCHAR(50),
    description text DEFAULT "No Description has been provided"
);

CREATE TABLE IF NOT EXISTS card_squares (
    square_id SERIAL PRIMARY KEY,
    square TEXT NOT NULL,
    type_id INT NOT NULL REFERENCES game_types(type_id)
);

CREATE TABLE IF NOT EXISTS games (
    game_id SERIAL PRIMARY KEY,
    type_id INT NOT NULL REFERENCES game_types(type_id),
    game_start timestamp(0) with time zone NOT NULL,
    game_length interval(0) NOT NULL,
    game_owner INT NOT NULL
);

CREATE TABLE IF NOT EXISTS player_info (
    internal_id SERIAL PRIMARY KEY,
    discord_id INT NOT NULL,
    game_id INT NOT NULL REFERENCES games(game_id),
    card_squares INT[5][5],
    card_status BIT(25)
);