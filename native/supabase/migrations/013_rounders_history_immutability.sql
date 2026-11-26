-- Harden migration 012 without changing locked predictions or ensemble functions.
create or replace function public.rounders_adjusted_forecasts_freeze()
returns trigger language plpgsql set search_path = '' as $$
begin
  if tg_op <> 'UPDATE' then raise exception 'adjusted forecasts cannot be removed'; end if;
  if (to_jsonb(new) - array['final_home','final_away','winner_correct','brier','margin_error','graded_at'])
     is distinct from
     (to_jsonb(old) - array['final_home','final_away','winner_correct','brier','margin_error','graded_at'])
  then raise exception 'adjusted forecasts are immutable'; end if;
  if old.graded_at is not null then raise exception 'adjusted forecast already graded'; end if;
  if new.graded_at is null then raise exception 'grading must be finalized in one update'; end if;
  return new;
end $$;
drop trigger if exists rounders_adjusted_forecasts_freeze on public.rounders_adjusted_forecasts;
create trigger rounders_adjusted_forecasts_freeze before update or delete on public.rounders_adjusted_forecasts
for each row execute function public.rounders_adjusted_forecasts_freeze();

create or replace function public.rounders_reject_history_mutation()
returns trigger language plpgsql set search_path = '' as $$
begin
  raise exception 'historical records are append-only';
end $$;
drop trigger if exists rounders_odds_immutable on public.rounders_odds_snapshots;
create trigger rounders_odds_immutable before update or delete on public.rounders_odds_snapshots
for each row execute function public.rounders_reject_history_mutation();
drop trigger if exists rounders_odds_no_truncate on public.rounders_odds_snapshots;
create trigger rounders_odds_no_truncate before truncate on public.rounders_odds_snapshots
for each statement execute function public.rounders_reject_history_mutation();
drop trigger if exists rounders_forecasts_no_truncate on public.rounders_adjusted_forecasts;
create trigger rounders_forecasts_no_truncate before truncate on public.rounders_adjusted_forecasts
for each statement execute function public.rounders_reject_history_mutation();
