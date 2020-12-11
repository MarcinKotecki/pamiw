-- Adminer 4.7.7 PostgreSQL dump

CREATE TABLE "public"."users" (
    "firstname" text NOT NULL,
    "lastname" text NOT NULL,
    "login" text NOT NULL,
    "email" text NOT NULL,
    "password" text NOT NULL,
    "address" text NOT NULL,
    CONSTRAINT "users_login" PRIMARY KEY ("login")
) WITH (oids = false);

CREATE TABLE "public"."packages" (
    "uuid" text NOT NULL,
    "sender" text NOT NULL,
    "receiver" text NOT NULL,
    "machine" text NOT NULL,
    "size" text NOT NULL,
    "status" text NOT NULL,
    CONSTRAINT "packages_uuid" UNIQUE ("uuid"),
    CONSTRAINT "packages_sender_fkey" FOREIGN KEY (sender) REFERENCES users(login) NOT DEFERRABLE
) WITH (oids = false);

CREATE SEQUENCE sessions_id_seq INCREMENT 1 MINVALUE 1 MAXVALUE 2147483647 START 3 CACHE 1;

CREATE TABLE "public"."sessions" (
    "id" integer DEFAULT nextval('sessions_id_seq') NOT NULL,
    "session_id" character varying(255),
    "data" bytea,
    "expiry" timestamp,
    CONSTRAINT "sessions_pkey" PRIMARY KEY ("id"),
    CONSTRAINT "sessions_session_id_key" UNIQUE ("session_id")
) WITH (oids = false);

-- 2020-12-09 14:14:37.972408+00
