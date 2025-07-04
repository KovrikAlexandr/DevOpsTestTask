DO
$$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_catalog.pg_roles WHERE rolname = 'student'
   ) THEN
      CREATE ROLE student WITH LOGIN PASSWORD 'studentpass';
   END IF;
END
$$;

GRANT CONNECT ON DATABASE studentdb TO student;
GRANT USAGE ON SCHEMA public TO student;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO student;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO student;
