use role accountadmin;
create database DEV_EDW_DB;
USE DATABASE DEV_EDW_DB;
create schema L80_INTEGRATIONS;
USE SCHEMA L80_INTEGRATIONS;

CREATE OR REPLACE SECRET MYPAT
    TYPE = PASSWORD
    USERNAME='RMAHARAN1'
    PASSWORD= 'pat';

    SHOW SECRETS;
    
CREATE OR REPLACE API INTEGRATION git_snow_integration
  API_PROVIDER = git_https_api
  API_ALLOWED_PREFIXES = ('https://github.com/rmaharan/Snowflake_EDW')
  ALLOWED_AUTHENTICATION_SECRETS=(MYPAT)
  ENABLED = TRUE;
  
  SHOW INTEGRATIONS;
  
CREATE OR REPLACE GIT REPOSITORY git_snow_integration_extensions
  API_INTEGRATION = git_snow_integration
  GIT_CREDENTIALS = MYPAT
  ORIGIN = 'https://github.com/rmaharan/Snowflake_EDW';

GRANT OWNERSHIP ON INTEGRATION git_snow_integration TO ROLE sfg_dev_data_engineer;
GRANT OWNERSHIP ON GIT REPOSITORY git_snow_integration_extensions TO ROLE sfg_dev_data_engineer;
GRANT usage ON schema l80_integrations TO ROLE sfg_dev_data_engineer;

GRANT ROLE sfg_dev_data_engineer TO USER RMAHARAN1;
USE ROLE sfg_dev_data_engineer;

LS @git_snow_integration_extensions/branches/main/0001-schema_objects/Warehouse.sql;
LS @git_snow_integration_extensions/branches/snowdev/;

ALTER GIT REPOSITORY git_snow_integration_extensions FETCH;
execute immediate from @git_snow_integration_extensions/branches/snowdev/0001-schema_objects/Warehouse.sql USING (env=> 'DEV');

Wed, 1 Oct 2025 04:05:54 GMT
CREATE or replace TAG environment_tag;

drop warehouse dev_edw_whs;

