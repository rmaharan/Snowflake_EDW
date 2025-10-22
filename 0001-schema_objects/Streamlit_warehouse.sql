/***************************************************************************************************       
Asset:        Warehouse and Resource Monitor
Version:      v1     
****************************************************************************************************

Simple Data Pipeline
1. Create Warehouse
2. Grant usage
3. Create Resource Monitor
****************************************************************************************************/
--!jinja------

USE ROLE SYSADMIN;
CREATE WAREHOUSE IF NOT EXISTS {{env}}_STREAMLIT_WHS
    WITH WAREHOUSE_TYPE = 'STANDARD'
    WAREHOUSE_SIZE = 'X-SMALL'
    MIN_CLUSTER_COUNT = 2
    MAX_CLUSTER_COUNT = 4
    SCALING_POLICY = 'ECONOMY'
    AUTO_SUSPEND = 60
    INITIALLY_SUSPENDED = TRUE
    AUTO_RESUME = TRUE
	COMMENT = 'UTILISED FOR CREATING STREMLIT APP FOR MONITORING DASHBOARDS';

-- We need to understand the naming convention proposed 
/*
GRANT USAGE ON WAREHOUSE {{env}}_ENT_ELT_WHS
  TO ROLE sfg_{{env}}_data_engineer;
*/

-- Gen 2 Comes with a premium so we don't do this or statement timeout
/*
ALTER WAREHOUSE  {{env}}_EDW_WHS SET RESOURCE_CONSTRAINT=STANDARD_GEN_2,
STATEMENT_TIMEOUT_IN_SECONDS=7200;
*/

USE ROLE ACCOUNTADMIN;

 CREATE OR REPLACE RESOURCE MONITOR {{env}}_STREAMLIT_WHS_MONITOR
    WITH CREDIT_QUOTA = 200
    FREQUENCY = MONTHLY --
    START_TIMESTAMP = IMMEDIATELY
    NOTIFY_USERS = () -- Decide who to Support 
    TRIGGERS
    ON 50 PERCENT DO NOTIFY
    ON 75 PERCENT DO NOTIFY
    ON 80 PERCENT DO NOTIFY
    ON 90 PERCENT DO NOTIFY;
              
ALTER WAREHOUSE {{env}}_STREAMLIT_WHS
    SET RESOURCE_MONITOR = "{{env}}_STREAMLIT_WHS_MONITOR";

CREATE DATABASE {{env}}_STREAMLIT_DB;
CREATE SCHEMA L80_INTEGRATION;


CREATE OR REPLACE SECRET MYPAT
    TYPE = PASSWORD
    USERNAME='RMAHARAN1'
    PASSWORD= 'ABC';

    SHOW SECRETS;
    
CREATE OR REPLACE API INTEGRATION git_STREAMLIT_integration
  API_PROVIDER = git_https_api
  API_ALLOWED_PREFIXES = ('https://github.com/rmaharan/Snowflake_EDW')
  ALLOWED_AUTHENTICATION_SECRETS=(MYPAT)
  ENABLED = TRUE;
  
SHOW INTEGRATIONS;
  
CREATE OR REPLACE GIT REPOSITORY git_STREAMLIT_integration_extensions
  API_INTEGRATION = git_snow_integration
  GIT_CREDENTIALS = MYPAT
  ORIGIN = 'https://github.com/rmaharan/Snowflake_EDW';

GRANT OWNERSHIP ON INTEGRATION git_STREAMLIT_integration TO ROLE sfg_dev_data_engineer;
GRANT OWNERSHIP ON GIT REPOSITORY git_STREAMLIT_integration_extensions TO ROLE sfg_dev_data_engineer;
GRANT usage ON schema l80_integration TO ROLE sfg_dev_data_engineer;

GRANT ROLE sfg_dev_data_engineer TO USER RMAHARAN1;
USE ROLE sfg_dev_data_engineer;

LS @git_STREAMLIT_integration_extensions/branches/main/0001-schema_objects/Warehouse.sql;
LS @git_STREAMLIT_integration_extensions/branches/snowdev/;

ALTER GIT REPOSITORY git_snow_integration_extensions FETCH;
execute immediate from @git_snow_integration_extensions/branches/snowdev/0001-schema_objects/Streamlit_warehouse.sql USING (env=> 'DEV');


USE DATABASE DEV_STREAMLIT_DB;
CREATE SCHEMA STREAMLT;
GRANT CREATE STREAMLIT ON SCHEMA STREAMLT TO ROLE ACCOUNTADMIN;

GRANT usage ON schema STREAMLT TO ROLE sfg_dev_data_engineer;
GRANT CREATE STREAMLIT ON SCHEMA STREAMLT TO ROLE sfg_dev_data_engineer;
GRANT ROLE sfg_dev_data_engineer TO USER RMAHARAN1;
USE ROLE sfg_dev_data_engineer;







  



  




  



  
