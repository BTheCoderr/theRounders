-- Rounders model history. Apply to the dedicated Rounders Supabase project.
create table if not exists public.model_projections (
  id text primary key,
  event_id text not null,
  sport text not null,
  away text not null,
  home text not null,
  created_at timestamptz not null default now(),
  model_version text not null,
  training_provider text not null,
  training_data_state text not null,
  projected_away double precision not null,
  projected_home double precision not null,
  fair_spread_home double precision not null,
  home_win_probability double precision not null check (home_win_probability between 0 and 100),
  confidence double precision not null check (confidence between 0 and 100),
  market jsonb,
  closing jsonb,
  final jsonb
);
create index if not exists model_projections_event_idx on public.model_projections(event_id);
create index if not exists model_projections_sport_created_idx on public.model_projections(sport,created_at desc);
alter table public.model_projections enable row level security;
-- Browser clients get no direct write policy. Rounders writes only through its server API.
