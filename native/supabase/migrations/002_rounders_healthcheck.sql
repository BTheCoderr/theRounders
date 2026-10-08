-- Matches the database health check installed on the Rounders Supabase project.
create or replace function public.rounders_healthcheck()
returns boolean language sql stable security invoker
set search_path = ''
as $$
  select exists (
    select 1 from pg_catalog.pg_class where relname = 'model_projections'
  )
$$;
revoke all on function public.rounders_healthcheck() from public;
grant execute on function public.rounders_healthcheck() to anon, authenticated;
