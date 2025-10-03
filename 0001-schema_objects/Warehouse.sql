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
CREATE WAREHOUSE IF NOT EXISTS {{env}}_EDW_WHS
    WITH WAREHOUSE_TYPE = 'standard'
    WAREHOUSE_SIZE = 'x_small'
    MIN_CLUSTER_COUNT = 2
    MAX_CLUSTER_COUNT = 4
    SCALING_POLICY = 'ECONOMY'
    AUTO_SUSPEND = 60
    INITIALLY_SUSPENDED = TRUE
    AUTO_RESUME = TRUE
	COMMENT = 'Utilised for loading the tables into enterprise data platform from various data sources';

GRANT USAGE ON WAREHOUSE {{env}}_EDW_WHS
  TO ROLE sfg_{{env}}_data_engineer;
  
ALTER WAREHOUSE  {{env}}_EDW_WHS SET RESOURCE_CONSTRAINT=STANDARD_GEN_2,
STATEMENT_TIMEOUT_IN_SECONDS=7200;

USE ROLE ACCOUNTADMIN;

 CREATE OR REPLACE RESOURCE MONITOR {{env}}_EDW_REPORTING_WHS_MONITOR
    WITH CREDIT_QUOTA = 100
    FREQUENCY = MONTHLY -- Can also be DAILY, WEEKLY, YEARLY, or NEVER (for a one-time quota)
    START_TIMESTAMP = IMMEDIATELY
    TRIGGERS ON 75 PERCENT DO NOTIFY
             ON 90 PERCENT DO SUSPEND
             ON 100 PERCENT DO SUSPEND_IMMEDIATE; 
             
ALTER WAREHOUSE {{env}}_EDW_WHS
    SET RESOURCE_MONITOR = "{{env}}_EDW_REPORTING_WHS_MONITOR";

ALTER WAREHOUSE {{env}}_EDW_WHS SET TAG environment_tag = {{env}};






  



  
