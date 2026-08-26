CREATE TABLE Team (
    id_team BIGINT PRIMARY KEY,
    abbreviation VARCHAR(5),
    nickname VARCHAR(50),
    year_founded INT,
    year_active_till INT,
    city VARCHAR(50),
    arena VARCHAR(100),
    arena_capacity INT,
    owner VARCHAR(100),
    general_manager VARCHAR(100),
    head_coach VARCHAR(100),
    dleague_affiliation VARCHAR(100)
);

CREATE TABLE Player (
    id_player BIGINT PRIMARY KEY,
    full_name VARCHAR(100),
    is_active BOOLEAN,
    player_slug VARCHAR(100),
    birthdate DATE,
    school VARCHAR(100),
    country VARCHAR(50),
    last_affiliation VARCHAR(100),
    height NUMERIC(5,2),
    weight NUMERIC(6,2),
    season_exp INT,
    position VARCHAR(50),
    roster_status VARCHAR(30),
    games_played_current_season_flag CHAR(1),
    team_id BIGINT,
    from_year INT,
    to_year INT,
    dleague_flag CHAR(1),
    nba_flag CHAR(1),
    games_played_flag CHAR(1),
    draft_number VARCHAR(20),
    pts NUMERIC(5,2),
    ast NUMERIC(5,2),
    reb NUMERIC(5,2),
    all_star_appearances INT,
    pie NUMERIC(6,3),

    FOREIGN KEY (team_id) REFERENCES Team(id_team)
);

CREATE TABLE Draft (
    id_draft BIGINT PRIMARY KEY,
    year_draft INT,
    name_player VARCHAR(100),
    name_organization_from VARCHAR(100),
    type_organization_from VARCHAR(50),
    id_player BIGINT,
    id_team BIGINT,
    player_profile_flag INT,

    FOREIGN KEY (id_player) REFERENCES Player(id_player),
    FOREIGN KEY (id_team) REFERENCES Team(id_team)
);

CREATE TABLE Draft_Combine (
    year_combine INT,
    id_player BIGINT,
    height_wo_shoes NUMERIC(5,2),
    weight_lbs NUMERIC(6,2),
    reach_standing_inches NUMERIC(5,2),
    pct_body_fat NUMERIC(5,2),
    vertical_leap_standing_inches NUMERIC(5,2),
    time_lane_agility NUMERIC(5,2),
    time_three_quarter_court_sprint NUMERIC(5,2),
    reps_bench_press_135 INT,
    set_spot_15_corner_left_pct NUMERIC(5,2),
    set_spot_15_break_left_pct NUMERIC(5,2),
    set_spot_15_top_key_pct NUMERIC(5,2),
    set_spot_15_break_right_pct NUMERIC(5,2),

    PRIMARY KEY (year_combine, id_player),
    FOREIGN KEY (id_player) REFERENCES Player(id_player)
);

CREATE TABLE Game (
    game_id BIGINT PRIMARY KEY,
    season_id BIGINT,
    game_date DATE,
    team_id_home BIGINT,
    team_id_away BIGINT,
    wl_home CHAR(1),
    wl_away CHAR(1),
    min_home INT,
    min_away INT,
    fg_pct_home NUMERIC(5,3),
    fg_pct_away NUMERIC(5,3),
    fg3_pct_home NUMERIC(5,3),
    fg3_pct_away NUMERIC(5,3),
    ft_pct_home NUMERIC(5,3),
    ft_pct_away NUMERIC(5,3),
    reb_home INT,
    reb_away INT,
    ast_home INT,
    ast_away INT,
    stl_home INT,
    stl_away INT,
    blk_home INT,
    blk_away INT,
    tov_home INT,
    tov_away INT,
    pf_home INT,
    pf_away INT,
    pts_home INT,
    pts_away INT,

    FOREIGN KEY (team_id_home) REFERENCES Team(id_team),
    FOREIGN KEY (team_id_away) REFERENCES Team(id_team)
);

CREATE TABLE Player_Salary (
    slug_season VARCHAR(10),
    id_team BIGINT,
    id_player BIGINT,
    status_player VARCHAR(50),
    is_final_season BOOLEAN,
    is_waived BOOLEAN,
    is_on_roster BOOLEAN,
    is_non_guaranteed BOOLEAN,
    is_team_option BOOLEAN,
    is_player_option BOOLEAN,
    type_contract_detail VARCHAR(50),
    value NUMERIC(15,2),

    PRIMARY KEY (slug_season, id_team, id_player),
    FOREIGN KEY (id_team) REFERENCES Team(id_team),
    FOREIGN KEY (id_player) REFERENCES Player(id_player)
);

CREATE TABLE Team_Salary (
    id_team BIGINT,
    season VARCHAR(10),
    salary_value NUMERIC(15,2),

    PRIMARY KEY (id_team, season),
    FOREIGN KEY (id_team) REFERENCES Team(id_team)
);