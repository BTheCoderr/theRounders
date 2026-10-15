-- Track monthly completion independently from daily run receipts.
-- Allows gradual, restart-safe backfill without hammering a public provider.
create table if not exists public.rounders_history_months (
 sport text not null check (sport in ('NBA','NFL','NHL','MLB')),
 year_month text not null check(year_month ~ '^(19|20)[0-9]{2}(0[1-9]|1[0-2])$'),
 source text not null check(source='espn-scoreboard'),
 imported_games integer not null check(imported_games>=0),
 fetched_at timestamptz not null default now(),
 primary key(sport,year_month,source)
);
alter table public.rounders_history_months enable row level security;
revoke all on public.rounders_history_months from anon,authenticated;
grant select,insert,update on public.rounders_history_months to service_role;
