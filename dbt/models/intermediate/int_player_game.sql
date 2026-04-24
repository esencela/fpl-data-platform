{{ config(
    alias='player_game',
    materialized='incremental',
    incremental_strategy='delete+insert',
    unique_key=['player_game_key']
)}}

with combined as (
    select 
        *,
        'fpl' as source
    from {{ ref('stg_fpl__player_game') }}
    union all
    select
        *,
        'vaastav' as source
    from {{ ref('stg_vaastav__player_game') }}
),

-- If rows clash, prioritise by source
prioritised as (
    select
        *,
        row_number() over (
            partition by season, fixture_season_id, player_season_id
            order by case
                when source = 'fpl' then 1
                else 2
            end
        ) as r
    from combined
),

-- Add composite keys for later joins
keys_added as (
    select
        concat(season, '_', fixture_season_id, '_', player_season_id) as player_game_key,
        concat(season, '_', fixture_season_id) as fixture_key,
        concat(season, '_', player_season_id) as player_season_key,
        *
    from prioritised
),

-- A fixture in the 2020 season has duplicated player_game data, only select data from max gameweek_id
fixture_deduped as (
    select
        g.*
    from keys_added as g
    inner join {{ ref('int_fixtures') }} as f
        on g.season = f.season
        and g.fixture_season_id = f.fpl_fixture_season_id
        and g.gameweek_id = f.gameweek_id
),

-- Join player_season table and add position for reconstructing defensive contributions
position_added as (
    select
        game.*,
        player.position
    from fixture_deduped as game
    left join {{ ref('int_player_season') }} as player
        on game.player_season_key = player.player_season_key
),

-- Remove managers included in raw data
managers_removed as (
    select
        *
    from position_added
    where position is not null
),

-- Reconstruct defensive contributions for historic seasons that contain defensive features, else null
defcons_reconstructed as (
    select 
        *,
        case
            when tackles is not null
                or clearances_blocks_interceptions is not null
                or recoveries is not null
            then
                case
                    when position = 'GKP' then 0
                    else
                        tackles +
                        clearances_blocks_interceptions +
                        case 
                            when position = 'MID' or position = 'FWD' then recoveries
                            else 0
                        end
                    end
            else null
        end as defcons_reconstructed
    from managers_removed
),

-- Join fixtures table and add team_season_key for imputing whether a player started
team_added as (
    select
        player_game.*,
        case
            when was_home then fixture.home_team_season_key
            else fixture.away_team_season_key
        end as team_season_key
    from defcons_reconstructed as player_game
    left join {{ ref('int_fixtures') }} as fixture
        on player_game.fixture_key = fixture.fixture_key
),

-- 'starts' column for 2023 season is all zeroes, set null to impute 'starts' downstream
cleaned_starts as (
    select
        *,
        case
            when season = 2023 then null
            else starts
        end as starts_cleaned
    from team_added
),

-- Add minute ranking of players split by fixture and team to impute whether a player starts
minute_ranked as (
    select
        *,
        row_number() over (
            partition by fixture_key, team_season_key
            order by minutes desc
        ) as minute_rank
    from cleaned_starts
),

-- Naively impute starts (0 or 1) by ranking the 11 players with the most minutes for each team in the fixture
starts_imputed as (
    select
        *,
        case
            when minute_rank <= 11 then 1
            else 0
        end as starts_imputed,
        case 
            when starts_cleaned is null then 1
            else 0
        end as missing_starts_flag
    from minute_ranked
),

-- Only certain fixtures in the 2023 season have expected metrics, others are represented as 0
fixture_has_expected as (
    select
        fixture_key,
        max(case when expected_goals > 0 then 1 else 0 end) as has_expected
    from starts_imputed
    group by fixture_key
),

-- Join fixtures table and add whether fixture has expected metrics
player_has_expected as (
    select 
        p.*,
        x.has_expected
    from starts_imputed as p
    left join fixture_has_expected as x
        on p.fixture_key = x.fixture_key
),

-- Set 0 values in 2023 fixtures without expected metrics to null
-- Signals whether player has 0 expected metrics or data is not available
expected_cleaned as (
    select
        *,
        case 
            when season != 2023 then expected_goals
            when has_expected = 1 then expected_goals
            else null
        end as xg_clean,
        case 
            when season != 2023 then expected_assists
            when has_expected = 1 then expected_assists
            else null
        end as xa_clean,
        case 
            when season != 2023 then expected_goal_involvements
            when has_expected = 1 then expected_goal_involvements
            else null
        end as xgi_clean,
        case 
            when season != 2023 then expected_goals_conceded
            when has_expected = 1 then expected_goals_conceded
            else null
        end as xgc_clean
    from player_has_expected
)

select 
    -- Identifiers
    player_game_key,
    fixture_key,
    player_season_key,
    player_season_id as fpl_player_season_id,
    season,
    fixture_season_id as fpl_fixture_season_id,

    -- Fixture info
    gameweek_id,
    was_home as at_home,
    
    -- Core stats
    minutes,
    case
        when missing_starts_flag = 1 then starts_imputed
        else starts_cleaned
    end as starts,
    goals_scored,
    assists,
    clean_sheets,
    goals_conceded,
    own_goals,
    
    -- Penalties
    penalties_saved,
    penalties_missed,

    -- Discipline
    yellow_cards,
    red_cards,

    -- Defensive
    clearances_blocks_interceptions,
    recoveries,
    tackles,
    defcons_reconstructed as defensive_contributions,
    saves,

    -- FPL metrics
    total_points,
    bonus,
    bps,
    influence,
    creativity,
    threat,
    ict_index,
    
    -- Expected metrics
    xg_clean as expected_goals,
    xa_clean as expected_assists,
    xgi_clean as expected_goal_involvements,
    xgc_clean as expected_goals_conceded, 

    -- Transfer and cost info
    cost,
    selected,
    transfers_in,
    transfers_out,
    transfers_in - transfers_out as transfers_balance,

    -- Metadata
    missing_starts_flag,
    position

from expected_cleaned