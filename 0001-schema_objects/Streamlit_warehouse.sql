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

/*
CREATE TAG environment_tag;
ALTER WAREHOUSE {{env}}_ENT_ELT_WHS SET TAG environment_tag = '{{env}}';

Tags will come in Governance DB 
*/







  



  
