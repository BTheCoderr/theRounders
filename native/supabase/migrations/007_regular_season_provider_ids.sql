-- Versioned, lossless cleanup of the original score-only archive.
-- Existing rows remain explicitly unclassified, not re-labeled as regular season.
alter table public.rounders_games
 add column if not exists provider_event_id text,
 add column if not exists home_team_id text,
 add column if not exists away_team_id text,
 add column if not exists season_phase text not null default 'unknown'
   check (season_phase in ('regular','preseason','postseason','exhibition','unknown')),
 add column if not exists provider_season integer,
 add column if not exists verified_at timestamptz;
create unique index if not exists rounders_games_provider_event_unique
 on public.rounders_games(source,sport,provider_event_id)
 where provider_event_id is not null;
create index if not exists rounders_games_regular_sport_date
 on public.rounders_games(sport,occurred_at desc)
 where season_phase='regular' and home_team_id is not null and away_team_id is not null;
alter table public.rounders_history_months
 add column if not exists ingestion_revision integer not null default 0,
 add column if not exists excluded_games integer not null default 0 check (excluded_games>=0);
-- Stable ESPN IDs prevent renamed clubs appearing as separate teams in training.
create table if not exists public.rounders_team_registry (
 sport text not null check (sport in ('NBA','NFL','NHL','MLB')),
 provider text not null check (provider='espn-scoreboard'),
 provider_team_id text not null,
 canonical_name text not null check (length(canonical_name) between 1 and 100),
 updated_at timestamptz not null default now(),
 primary key(sport,provider,provider_team_id)
);
alter table public.rounders_team_registry enable row level security;
revoke all on public.rounders_team_registry from anon,authenticated;
grant select,insert,update on public.rounders_team_registry to service_role;
