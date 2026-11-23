-- Stripe billing records (TEST MODE ONLY). Written exclusively by the server's webhook and checkout routes.
create table if not exists public.rounders_customers (
  user_id uuid primary key references auth.users(id) on delete cascade,
  stripe_customer_id text not null unique check (stripe_customer_id ~ '^cus_[A-Za-z0-9]+$'),
  email text,
  created_at timestamptz not null default now()
);
create table if not exists public.rounders_subscriptions (
  stripe_subscription_id text primary key check (stripe_subscription_id ~ '^sub_[A-Za-z0-9]+$'),
  user_id uuid not null references auth.users(id) on delete cascade,
  stripe_customer_id text not null,
  plan text check (plan in ('pro','edge')),
  price_id text,
  status text not null check (status in ('incomplete','incomplete_expired','trialing','active','past_due','canceled','unpaid','paused')),
  current_period_end timestamptz,
  cancel_at_period_end boolean not null default false,
  canceled_at timestamptz,
  -- Guard: live-mode billing is not enabled. Remove only as a deliberate, reviewed launch step.
  livemode boolean not null default false check (livemode = false),
  updated_at timestamptz not null default now()
);
create index if not exists rounders_subscriptions_user on public.rounders_subscriptions (user_id);
create table if not exists public.rounders_stripe_events (
  id text primary key check (id ~ '^evt_[A-Za-z0-9]+$'),
  type text not null,
  livemode boolean not null default false check (livemode = false),
  received_at timestamptz not null default now()
);
alter table public.rounders_customers enable row level security;
alter table public.rounders_subscriptions enable row level security;
alter table public.rounders_stripe_events enable row level security;
revoke all on table public.rounders_customers, public.rounders_subscriptions, public.rounders_stripe_events from anon, authenticated;
grant select, insert, update on public.rounders_customers, public.rounders_subscriptions to service_role;
grant select, insert on public.rounders_stripe_events to service_role;
