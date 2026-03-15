--
-- PostgreSQL database dump
--

\restrict bd9LFG7UAizr86MvABeXZYoPvCrYQCWmq8YZHUnkEWICkgaRW3S5xg9ZcBvIaHp

-- Dumped from database version 16.13
-- Dumped by pg_dump version 16.13

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: analytics_cache; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.analytics_cache (
    id integer NOT NULL,
    key character varying(255) NOT NULL,
    data json NOT NULL
);


ALTER TABLE public.analytics_cache OWNER TO postgres;

--
-- Name: analytics_cache_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.analytics_cache_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.analytics_cache_id_seq OWNER TO postgres;

--
-- Name: analytics_cache_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.analytics_cache_id_seq OWNED BY public.analytics_cache.id;


--
-- Name: test_results; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.test_results (
    id integer NOT NULL,
    session_id character varying(255) NOT NULL,
    user_id integer NOT NULL,
    accuracy double precision NOT NULL,
    loss double precision NOT NULL,
    predictions json NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.test_results OWNER TO postgres;

--
-- Name: test_results_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.test_results_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.test_results_id_seq OWNER TO postgres;

--
-- Name: test_results_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.test_results_id_seq OWNED BY public.test_results.id;


--
-- Name: training_history; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.training_history (
    id integer NOT NULL,
    epoch integer NOT NULL,
    val_accuracy double precision NOT NULL,
    val_loss double precision NOT NULL,
    train_accuracy double precision NOT NULL,
    train_loss double precision NOT NULL
);


ALTER TABLE public.training_history OWNER TO postgres;

--
-- Name: training_history_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.training_history_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.training_history_id_seq OWNER TO postgres;

--
-- Name: training_history_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.training_history_id_seq OWNED BY public.training_history.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id integer NOT NULL,
    username character varying(255) NOT NULL,
    hashed_password character varying(255) NOT NULL,
    first_name character varying(255) NOT NULL,
    last_name character varying(255) NOT NULL,
    role character varying(50) NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: analytics_cache id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.analytics_cache ALTER COLUMN id SET DEFAULT nextval('public.analytics_cache_id_seq'::regclass);


--
-- Name: test_results id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.test_results ALTER COLUMN id SET DEFAULT nextval('public.test_results_id_seq'::regclass);


--
-- Name: training_history id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.training_history ALTER COLUMN id SET DEFAULT nextval('public.training_history_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: analytics_cache; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.analytics_cache (id, key, data) FROM stdin;
\.


--
-- Data for Name: test_results; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.test_results (id, session_id, user_id, accuracy, loss, predictions, created_at) FROM stdin;
1	d23259b1-e82a-477b-b8dd-fdb2093e0d0d	5	0	0.0818471580458352	[{"index": 0, "true_label": 0, "predicted_label": 1, "correct": false, "confidence": 0.078747}, {"index": 1, "true_label": 1, "predicted_label": 6, "correct": false, "confidence": 0.078256}, {"index": 2, "true_label": 2, "predicted_label": 1, "correct": false, "confidence": 0.078554}, {"index": 3, "true_label": 3, "predicted_label": 1, "correct": false, "confidence": 0.078546}, {"index": 4, "true_label": 4, "predicted_label": 6, "correct": false, "confidence": 0.078833}]	2026-03-15 11:08:43.471112+00
2	82f5976c-e7ec-4b46-99fc-343783e6b31e	5	0	0.0818471580458352	[{"index": 0, "true_label": 0, "predicted_label": 1, "correct": false, "confidence": 0.078747}, {"index": 1, "true_label": 1, "predicted_label": 6, "correct": false, "confidence": 0.078256}, {"index": 2, "true_label": 2, "predicted_label": 1, "correct": false, "confidence": 0.078554}, {"index": 3, "true_label": 3, "predicted_label": 1, "correct": false, "confidence": 0.078546}, {"index": 4, "true_label": 4, "predicted_label": 6, "correct": false, "confidence": 0.078833}]	2026-03-15 11:15:18.059725+00
\.


--
-- Data for Name: training_history; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.training_history (id, epoch, val_accuracy, val_loss, train_accuracy, train_loss) FROM stdin;
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (id, username, hashed_password, first_name, last_name, role, created_at) FROM stdin;
1	admin	$2b$12$GhnzaMN0osZmSekFiCHqOeDhEdj4eaInhAnAThN.XKmoVvIoddOQu	Admin	Admin	admin	2026-03-15 10:28:22.931636+00
2	login	$2b$12$zBUGspVAd3ifKYn0vM2le.XfmKqUvMrH/h/j1v1TGmoSKY5f2zZEi	Admin	Test	admin	2026-03-15 10:28:51.778379+00
3	loglog	$2b$12$2H46DqMylCBlpRrH1J45gOg6P2DHueEcLWymxPAjpytFu.cDyQEcS	Артем	Морфов	user	2026-03-15 10:29:12.154932+00
4	logloglog	$2b$12$Ihc6f0jsdFSS5A9WqCxAOuo3jXZScpOj8luSi1rQbLlQDQLuoh.fq	Admin	Test	admin	2026-03-15 11:04:08.276489+00
5	user	$2b$12$q.M6mG0voOSAMqfnOE3vO.gd7AlHZIL0YOUuMpJaLvGuvobAQ38jy	Иван	иван	user	2026-03-15 11:04:21.675262+00
6	username11	$2b$12$qV73Wa.RDh9Gt08kqx4j5ujwm5NhmOdY9WqFlpTIjyk6eoIwcg4xS	Иван	Иванов	user	2026-03-15 11:14:58.957744+00
\.


--
-- Name: analytics_cache_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.analytics_cache_id_seq', 1, false);


--
-- Name: test_results_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.test_results_id_seq', 2, true);


--
-- Name: training_history_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.training_history_id_seq', 1, false);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.users_id_seq', 6, true);


--
-- Name: analytics_cache analytics_cache_key_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.analytics_cache
    ADD CONSTRAINT analytics_cache_key_key UNIQUE (key);


--
-- Name: analytics_cache analytics_cache_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.analytics_cache
    ADD CONSTRAINT analytics_cache_pkey PRIMARY KEY (id);


--
-- Name: test_results test_results_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.test_results
    ADD CONSTRAINT test_results_pkey PRIMARY KEY (id);


--
-- Name: training_history training_history_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.training_history
    ADD CONSTRAINT training_history_pkey PRIMARY KEY (id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: users users_username_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_username_key UNIQUE (username);


--
-- Name: test_results test_results_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.test_results
    ADD CONSTRAINT test_results_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- PostgreSQL database dump complete
--

\unrestrict bd9LFG7UAizr86MvABeXZYoPvCrYQCWmq8YZHUnkEWICkgaRW3S5xg9ZcBvIaHp

