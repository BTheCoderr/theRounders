-- Allow the market-blend challenger to store locked pregame picks (forward test).
alter table public.rounders_predictions drop constraint if exists rounders_predictions_model_id_check;
alter table public.rounders_predictions add constraint rounders_predictions_model_id_check
  check (model_id = any (array['rounders-v1','power-v2','rpi-v2.1','rounders-v3','ensemble','power-v3','blend-v1']));
