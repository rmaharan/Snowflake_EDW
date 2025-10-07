USE ROLE ACCOUNTADMIN;
CREATE DATABASE doc_ai_db;
CREATE SCHEMA doc_ai_db.doc_ai_schema;
CREATE ROLE doc_ai_role;
GRANT DATABASE ROLE SNOWFLAKE.DOCUMENT_INTELLIGENCE_CREATOR TO ROLE doc_ai_role;
GRANT USAGE, OPERATE ON WAREHOUSE EDW_DEV_WH TO ROLE doc_ai_role;
GRANT USAGE ON DATABASE doc_ai_db TO ROLE doc_ai_role;
GRANT USAGE ON SCHEMA doc_ai_db.doc_ai_schema TO ROLE doc_ai_role;

--Grant the create stage privilege on the schema to the doc_ai_role role to store the documents for extraction:
GRANT CREATE STAGE ON SCHEMA doc_ai_db.doc_ai_schema TO ROLE doc_ai_role;

--Grant the privileges to create model builds (instances of the DOCUMENT_INTELLIGENCE class) to the doc_ai_role role:
GRANT CREATE SNOWFLAKE.ML.DOCUMENT_INTELLIGENCE ON SCHEMA doc_ai_db.doc_ai_schema TO ROLE doc_ai_role;
GRANT CREATE MODEL ON SCHEMA doc_ai_db.doc_ai_schema TO ROLE doc_ai_role;

GRANT CREATE MODEL ON SCHEMA doc_ai_db.doc_ai_schema TO  accountadmin;

--Grant the privileges required to create a processing pipeline using streams and tasks to the doc_ai_role role:
GRANT CREATE STREAM, CREATE TABLE, CREATE TASK, CREATE VIEW ON SCHEMA doc_ai_db.doc_ai_schema TO ROLE doc_ai_role;
GRANT EXECUTE TASK ON ACCOUNT TO ROLE doc_ai_role;

GRANT ROLE doc_ai_role TO USER RMAHARAN1;
