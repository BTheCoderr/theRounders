-- Rounders: live odds snapshots, injuries, player impact, injury-adjusted forecasts and
-- provider spend tracking. Additive only: existing tables and locked predictions are untouched.
-- All tables are server-only (RLS on, no policies); the service role writes them.

-- 1) Consensus market line per game per capture. Opening = first capture, closing = last
--    capture before the start time (see view). Rows are never updated.
create table if not exists public.rounders_odds_snapshots (
  id bigint generated always as identity primary key,
  sport text not null check (sport in ('NBA','NFL','NCAAM','NCAAF','NHL','MLB')),
  provider text not null default 'the-odds-api',
  odds_event_id text not null,
  espn_event_id text,
  starts_at timestamptz not null,
  home text not null,
  away text not null,
  captured_at timestamptz not null default now(),
  books integer not null check (books > 0),
  spread_home numeric,            -- median home spread across books
  total numeric,                  -- median total across books
  home_win_prob numeric check (home_win_prob is null or (home_win_prob > 0 and home_win_prob < 1)), -- vig-free moneyline, averaged across books
  quotes jsonb not null default '[]'::jsonb,  -- per-book prices at capture (powers the line shop without extra API calls)
  unique (provider, odds_event_id, captured_at)
);
create index if not exists rounders_odds_snapshots_event on public.rounders_odds_snapshots (sport, espn_event_id, captured_at);
create index if not exists rounders_odds_snapshots_start on public.rounders_odds_snapshots (sport, starts_at);
alter table public.rounders_odds_snapshots enable row level security;

create or replace view public.rounders_odds_open_close with (security_invoker = true) as
select s.sport, s.provider, s.odds_event_id, max(s.espn_event_id) as espn_event_id, min(s.starts_at) as starts_at,
  (array_agg(s.spread_home order by s.captured_at asc))[1]  as open_spread_home,
  (array_agg(s.total order by s.captured_at asc))[1]        as open_total,
  (array_agg(s.home_win_prob order by s.captured_at asc))[1] as open_home_win_prob,
  min(s.captured_at) as opened_at,
  (array_agg(s.spread_home order by s.captured_at desc))[1] as close_spread_home,
  (array_agg(s.total order by s.captured_at desc))[1]       as close_total,
  (array_agg(s.home_win_prob order by s.captured_at desc))[1] as close_home_win_prob,
  max(s.captured_at) as closed_at,
  count(*) as captures
from public.rounders_odds_snapshots s
where s.captured_at < s.starts_at
group by s.sport, s.provider, s.odds_event_id;

-- 2) Injury report history: a row whenever a player's status or note changes.
create table if not exists public.rounders_injury_reports (
  id bigint generated always as identity primary key,
  sport text not null check (sport in ('NBA','NFL')),
  provider text not null default 'balldontlie',
  player_id text not null,
  player_name text not null,
  team text,
  position text,
  status text not null,
  description text,
  return_date text,
  reported_at timestamptz,
  first_seen_at timestamptz not null default now(),
  last_seen_at timestamptz not null default now(),  -- refreshed each fetch while the player stays listed
  report_hash text not null,
  unique (sport, provider, player_id, report_hash)
);
create index if not exists rounders_injury_reports_team on public.rounders_injury_reports (sport, team, first_seen_at desc);
alter table public.rounders_injury_reports enable row level security;

-- 2b) Per-game player minutes and plus-minus (NBA box scores), stored incrementally.
create table if not exists public.rounders_player_games (
  sport text not null check (sport in ('NBA','NFL')),
  provider text not null default 'balldontlie',
  game_date date not null,
  game_id text not null,
  player_id text not null,
  player_name text not null,
  team text not null,
  minutes numeric not null,
  plus_minus numeric,
  primary key (sport, provider, game_id, player_id)
);
create index if not exists rounders_player_games_date on public.rounders_player_games (sport, game_date);
alter table public.rounders_player_games enable row level security;

-- 3) Player impact: points of team margin per game above a replacement player.
create table if not exists public.rounders_player_impact (
  sport text not null check (sport in ('NBA','NFL')),
  provider text not null default 'balldontlie',
  player_id text not null,
  player_name text not null,
  team text,
  position text,
  season integer not null,
  games integer not null,
  minutes_share numeric,
  impact numeric not null,           -- margin points per game vs replacement (positive = valuable)
  method text not null,              -- e.g. 'nba-pm-regressed-v1', 'nfl-position-prior-v1'
  computed_at timestamptz not null default now(),
  primary key (sport, provider, player_id, season)
);
alter table public.rounders_player_impact enable row level security;

-- 4) Injury-adjusted forecasts: stored separately, append-only, never replacing locked picks.
create table if not exists public.rounders_adjusted_forecasts (
  id bigint generated always as identity primary key,
  sport text not null check (sport in ('NBA','NFL')),
  provider_event_id text not null,
  base_prediction_id bigint not null references public.rounders_predictions(id),
  model_id text not null check (model_id in ('injury-v4')),
  model_version text not null,
  forecast_at timestamptz not null default now(),
  starts_at timestamptz not null,
  base_margin numeric not null,
  injury_adjustment numeric not null,
  projected_margin numeric not null,
  home_win_probability numeric not null check (home_win_probability > 0 and home_win_probability < 1),
  inputs jsonb not null,             -- players, statuses, impacts and report timestamps used
  final_home integer, final_away integer, winner_correct boolean, brier numeric, margin_error numeric,
  graded_at timestamptz,
  check (forecast_at < starts_at)
);
create index if not exists rounders_adjusted_forecasts_event on public.rounders_adjusted_forecasts (sport, provider_event_id, forecast_at);
alter table public.rounders_adjusted_forecasts enable row level security;

create or replace function public.rounders_adjusted_forecasts_freeze()
returns trigger language plpgsql set search_path = '' as $$
begin
  -- Only grading columns may change, once.
  if (new.provider_event_id, new.base_prediction_id, new.model_version, new.forecast_at, new.starts_at,
      new.base_margin, new.injury_adjustment, new.projected_margin, new.home_win_probability, new.inputs)
     is distinct from
     (old.provider_event_id, old.base_prediction_id, old.model_version, old.forecast_at, old.starts_at,
      old.base_margin, old.injury_adjustment, old.projected_margin, old.home_win_probability, old.inputs)
  then raise exception 'adjusted forecasts are immutable';
  end if;
  if old.graded_at is not null then raise exception 'adjusted forecast already graded'; end if;
  return new;
end $$;
drop trigger if exists rounders_adjusted_forecasts_freeze on public.rounders_adjusted_forecasts;
create trigger rounders_adjusted_forecasts_freeze before update on public.rounders_adjusted_forecasts
  for each row execute function public.rounders_adjusted_forecasts_freeze();

-- 5) Paid-provider usage per UTC day, for budgets and the kill switch.
create table if not exists public.rounders_provider_usage (
  provider text not null,
  day date not null,
  requests integer not null default 0,
  credits integer not null default 0,
  last_remaining integer,
  blocked integer not null default 0,
  updated_at timestamptz not null default now(),
  primary key (provider, day)
);
alter table public.rounders_provider_usage enable row level security;

-- Atomic usage increment (avoids lost updates when jobs overlap).
create or replace function public.rounders_record_usage(p_provider text, p_credits integer, p_remaining integer, p_blocked integer default 0)
returns void language sql security definer set search_path = '' as $$
  insert into public.rounders_provider_usage (provider, day, requests, credits, last_remaining, blocked)
  values (p_provider, (now() at time zone 'utc')::date, case when p_blocked>0 then 0 else 1 end, greatest(p_credits,0), p_remaining, p_blocked)
  on conflict (provider, day) do update set
    requests = public.rounders_provider_usage.requests + excluded.requests,
    credits = public.rounders_provider_usage.credits + excluded.credits,
    last_remaining = coalesce(excluded.last_remaining, public.rounders_provider_usage.last_remaining),
    blocked = public.rounders_provider_usage.blocked + excluded.blocked,
    updated_at = now();
$$;
revoke all on function public.rounders_record_usage(text, integer, integer, integer) from public, anon, authenticated;
