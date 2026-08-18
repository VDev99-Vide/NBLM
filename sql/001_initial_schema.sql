-- NBLM — Notebook Quản Gia AI
-- Neon Postgres schema v1

create extension if not exists "uuid-ossp";
create extension if not exists pgcrypto;

-- Notebooks
create table notebooks (
  id uuid primary key default uuid_generate_v4(),
  name text not null,
  description text,
  icon text,
  color text default '#6366f1',
  sort_order int default 0,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

-- Entries (multi-block JSONB)
create table entries (
  id uuid primary key default uuid_generate_v4(),
  notebook_id uuid references notebooks(id) on delete cascade,
  title text not null default '',
  blocks jsonb not null default '[]'::jsonb,
  tags text[] default '{}',
  is_pinned boolean default false,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

-- Attachments
create table attachments (
  id uuid primary key default uuid_generate_v4(),
  entry_id uuid references entries(id) on delete cascade,
  block_index int,
  file_name text not null,
  mime_type text,
  size_bytes bigint,
  r2_key text,
  public_url text,
  created_at timestamptz default now()
);

-- Stored Credentials (encrypted)
create table stored_credentials (
  id uuid primary key default uuid_generate_v4(),
  label text not null,
  category text default 'api_key',
  encrypted_value text not null,
  iv text not null,
  notes text,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

-- AI Sessions
create table ai_sessions (
  id uuid primary key default uuid_generate_v4(),
  messages jsonb default '[]'::jsonb,
  model_used text,
  provider_used text,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

-- API Providers
create table api_providers (
  id uuid primary key default uuid_generate_v4(),
  name text unique not null,
  display_name text,
  base_url text not null,
  api_protocol text default 'openai-completions',
  chat_model text,
  vision_model text,
  priority int default 50,
  is_active boolean default true,
  encrypted_api_key text,
  iv text,
  error_count int default 0,
  cooldown_until timestamptz,
  created_at timestamptz default now()
);

-- Audit Log
create table audit_log (
  id uuid primary key default uuid_generate_v4(),
  action text not null,
  entity_type text,
  entity_id uuid,
  details jsonb,
  created_at timestamptz default now()
);

-- Indexes
create index idx_entries_notebook on entries(notebook_id);
create index idx_entries_tags on entries using gin(tags);
create index idx_attachments_entry on attachments(entry_id);
create index idx_audit_created on audit_log(created_at desc);

-- Seed default notebook
insert into notebooks (name, description, icon, color)
values ('Sổ tay chính', 'Notebook mặc định', '📒', '#6366f1')
on conflict do nothing;

-- Seed xkiro provider placeholder
insert into api_providers (name, display_name, base_url, api_protocol, chat_model, vision_model, priority, encrypted_api_key, iv)
values ('xkiro', 'XKiro Primary', 'https://api.xkiro.com/v1', 'openai-completions', 'deepseek-v4', 'qwen-vl-max', 100, 'PLACEHOLDER', 'PLACEHOLDER')
on conflict (name) do nothing;
