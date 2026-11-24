-- Rounders: NBA, NFL, college basketball (NCAAM), college football (NCAAF), NHL and MLB.
-- Widens every sport CHECK constraint; no data changes.
do $$
declare t text;
begin
 foreach t in array array['rounders_games','rounders_ingestion_runs','rounders_model_runs','rounders_model_comparisons',
  'rounders_history_months','rounders_team_registry','rounders_predictions','rounders_backtests']
 loop
  execute format('alter table public.%I drop constraint if exists %I',t,t||'_sport_check');
  execute format('alter table public.%I add constraint %I check (sport in (''NBA'',''NFL'',''NCAAM'',''NCAAF'',''NHL'',''MLB''))',t,t||'_sport_check');
 end loop;
end $$;
