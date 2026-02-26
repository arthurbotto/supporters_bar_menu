-- The job of this file is to reset all of our important database tables.
-- And add any data that is needed for the tests to run.
-- This is so that our tests, and application, are always operating from a fresh
-- database state, and that tests don't interfere with each other.

DROP TABLE IF EXISTS test_table;


CREATE TABLE test_table (id SERIAL PRIMARY KEY, name VARCHAR(255));


INSERT INTO test_table (name) VALUES ('first_record');
