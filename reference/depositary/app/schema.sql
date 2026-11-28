-- SPDX-License-Identifier: EUPL-1.2
-- Register of the reference depositary (prototype). Idempotent.

CREATE TABLE IF NOT EXISTS acceptors (
  id          text PRIMARY KEY,
  name        text NOT NULL,
  jwk         jsonb NOT NULL,
  kid         text NOT NULL UNIQUE,
  created_at  timestamptz NOT NULL DEFAULT now()
);

-- Demo only: private key of the built-in demo acceptor. A real acceptor keeps
-- its private key in its own system; the depositary never sees it.
CREATE TABLE IF NOT EXISTS demo_keys (
  acceptor_id text PRIMARY KEY REFERENCES acceptors(id),
  private_pem text NOT NULL
);

-- Holder account (партида): pseudonymous, no personal data.
CREATE TABLE IF NOT EXISTS accounts (
  ref         text PRIMARY KEY,
  last_seq    integer NOT NULL DEFAULT -1,
  last_hash   text NOT NULL DEFAULT '',
  created_at  timestamptz NOT NULL DEFAULT now()
);

-- Passkeys: only public key, credential id and counter (spec 7.2).
CREATE TABLE IF NOT EXISTS credentials (
  id          text PRIMARY KEY,
  account_ref text NOT NULL REFERENCES accounts(ref),
  public_key  bytea NOT NULL,
  sign_count  bigint NOT NULL DEFAULT 0,
  created_at  timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS entitlements (
  id          text PRIMARY KEY,
  account_ref text NOT NULL REFERENCES accounts(ref),
  doc         jsonb NOT NULL,
  form        text NOT NULL,
  unit        text NOT NULL,
  balance     numeric(14,2) NOT NULL CHECK (balance >= 0),
  divisible   boolean NOT NULL,
  goods_scheme text NOT NULL,
  goods_code  text NOT NULL,
  valid_until timestamptz,
  status      text NOT NULL,
  created_at  timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS entitlements_account ON entitlements(account_ref);

-- Append-only event log; per account a hash chain (spec 6.1).
CREATE TABLE IF NOT EXISTS events (
  event_id    text PRIMARY KEY,
  account_ref text NOT NULL REFERENCES accounts(ref),
  seq         integer NOT NULL,
  doc         jsonb NOT NULL,
  hash        text NOT NULL,
  UNIQUE (account_ref, seq)
);

-- Idempotency of redeem: one row per redemption-request nonce.
CREATE TABLE IF NOT EXISTS redemptions (
  nonce       text PRIMARY KEY,
  event_id    text NOT NULL REFERENCES events(event_id),
  acceptor_id text NOT NULL,
  result      jsonb NOT NULL,
  created_at  timestamptz NOT NULL DEFAULT now()
);

-- Short-lived WebAuthn ceremonies.
CREATE TABLE IF NOT EXISTS sessions (
  id          text PRIMARY KEY,
  kind        text NOT NULL,
  account_ref text,
  challenge   bytea NOT NULL,
  data        jsonb NOT NULL DEFAULT '{}'::jsonb,
  expires_at  timestamptz NOT NULL
);

CREATE OR REPLACE FUNCTION forbid_change() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN RAISE EXCEPTION 'event log is append-only'; END $$;
DROP TRIGGER IF EXISTS events_append_only ON events;
CREATE TRIGGER events_append_only BEFORE UPDATE OR DELETE ON events
  FOR EACH ROW EXECUTE FUNCTION forbid_change();
