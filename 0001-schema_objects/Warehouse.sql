/***************************************************************************************************       
Asset:        Warehouse and Resource Monitor
Version:      v1     
****************************************************************************************************

Simple Data Pipeline
1. Create Warehouse
2. Grant usage
3.Create Resource Monitor
****************************************************************************************************/
--!jinja

USE ROLE SYSADMIN;
CREATE WAREHOUSE IF NOT EXISTS "{{env}}_EDW_WHS"
    WITH WAREHOUSE_TYPE = STANDARD
    WAREHOUSE_SIZE = XSMALL
    MIN_CLUSTER_COUNT = 2
    MAX_CLUSTER_COUNT = 4
    SCALING_POLICY = STANDARD
    AUTO_SUSPEND = 60
    INITIALLY_SUSPENDED = TRUE
    AUTO_RESUME = TRUE
	COMMENT = 'Utilised for loading the tables into enterprise data platform from various data sources';

GRANT USAGE ON WAREHOUSE "{{env}}_EDW_WHS"
  TO ROLE "sfg_{{env}}_data_engineer";

  



  
