-- Team box totals from the scoreboard (field-goal/free-throw attempts etc.), when ESPN provides them.
-- Groundwork for a per-possession college basketball model; nullable, nothing reads it yet.
alter table public.rounders_games add column if not exists box jsonb;
