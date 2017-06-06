
# coding: utf-8

# In[9]:

import pandas as pd
import numpy as np
import mysql.connector
from mysql.connector import errorcode
import getpass as getpass


# ## CREATING DATABASE

# In[11]:

TABLES = {}
##################################################### ACCESSION LEVEL DATA ##########################
TABLES['DW201_ACCESSIONS'] = (
    "CREATE TABLE `DW201_ACCESSIONS` ("
    "  `ACCESS_NR` VARCHAR(15) NOT NULL COMMENT 'invention entries in derwent',"
    "  `ACCESS_COUNTRY_COUNT` INT NULL,"
    "  `ACCESS_PUBLN_COUNT` INT NULL,"
    "  `ACCESS_CITED_COUNT` INT NULL,"
    "  `ACCESS_CITED_INV_COUNT` INT NULL,"
    "  `ACCESS_CIT_AUTH_COUNT` INT NULL,"
    "  `ACCESS_CIT_LITER_COUNT` INT NULL,"
    "  `ACCESS_ID` BIGINT NOT NULL,"
    "  PRIMARY KEY (`ACCESS_ID`),"
    "  INDEX `ACCESS_ID`(`ACCESS_ID`),"
    "  UNIQUE KEY `ACCESS_NR_UNIQUE` (`ACCESS_NR` ASC)"
    ") ENGINE=InnoDB")

TABLES['DW203_ACCESS_ASSIG'] = (
    "CREATE TABLE `DW203_ACCESS_ASSIG` ("
    "  `ASSIG_ID` BIGINT NOT NULL,"
    "  `ACCESS_ID` BIGINT NOT NULL,"
    "  CONSTRAINT `DW203_fk_ACCESS_ID`" 
    "    FOREIGN KEY (`ACCESS_ID`)" #tableName_fk_fieldName FOR KEY field Name
    "    REFERENCES `DW201_ACCESSIONS` (`ACCESS_ID`)," #foreignTableName (foreignFieldName)
    "  CONSTRAINT `DW203_fk_ASSIG_ID`" 
    "    FOREIGN KEY (`ASSIG_ID`)" #tableName_fk_fieldName FOR KEY field Name
    "    REFERENCES `DW901_ASSIG_SUPPORT` (`ASSIG_ID`)" #foreignTableName (foreignFieldName)
    ") ENGINE=InnoDB")

#TO FILL ACCESS_ID AT THE END
TABLES['DW202_ACCESS_REL'] = (
    "CREATE TABLE `DW202_ACCESS_REL` ("
    "  `ACCESS_NR` VARCHAR(15) NOT NULL,"
    "  `ACCESS_ID` BIGINT NOT NULL,"
    "  `REL_TO_ACCESS_NR` VARCHAR(15) NOT NULL,"
    "  `REL_TO_ACCESS_ID` BIGINT NULL,"
    "  `REL_TYPE` VARCHAR(15) NOT NULL,"
    "  CONSTRAINT `DW202_fk_ACCESS_ID`" 
    "    FOREIGN KEY (`ACCESS_ID`)" #tableName_fk_fieldName FOR KEY field Name
    "    REFERENCES `DW201_ACCESSIONS` (`ACCESS_ID`)," #foreignTableName (foreignFieldName)
    "  CONSTRAINT `DW202_fk_REL_TO_ACCESS_ID`" 
    "    FOREIGN KEY (`REL_TO_ACCESS_ID`)" #tableName_fk_fieldName FOR KEY field Name
    "    REFERENCES `DW201_ACCESSIONS` (`ACCESS_ID`)" #foreignTableName (foreignFieldName)
    ") ENGINE=InnoDB")




########################################### PUBLICATION + APPLICATION DATA ##########################

TABLES['DW101_APPLN'] = (
    "CREATE TABLE `DW101_APPLN` ("
    "  `APPLN_NR_S` VARCHAR(15) NULL,"
    "  `APPLN_NR_L` VARCHAR(15) NOT NULL,"
    "  `APPLN_AUTH` CHAR(3) NULL,"
    "  `APPLN_DATE` DATE NULL,"
    "  `ACCESS_NR` VARCHAR(15) NOT NULL,"
    "  `APPLN_ID` BIGINT NOT NULL COMMENT 'defined by APPLN_NR_L+ACCESS_NR',"
    "  `ACCESS_ID` BIGINT NOT NULL,"
    "  `APPLN_TXT` VARCHAR(20) NULL COMMENT 'additional information on some appln',"
    "  PRIMARY KEY (`APPLN_ID`),"
    "  INDEX `ACCESS_NR`(`ACCESS_NR`),"
    "  INDEX `APPLN_NR_L`(`APPLN_NR_L`),"
    "  CONSTRAINT `DW101_fk_ACCESS_ID`" 
    "    FOREIGN KEY (`ACCESS_ID`)" #tableName_fk_fieldName FOR KEY field Name
    "    REFERENCES `DW201_ACCESSIONS` (`ACCESS_ID`)" #foreignTableName (foreignFieldName)
    ") ENGINE=InnoDB")

TABLES['DW102_PUBLN'] = (
    "CREATE TABLE `DW102_PUBLN` ("
    "  `PUBLN_NR` BIGINT NOT NULL,"
    "  `PUBLN_KIND` VARCHAR(3) NOT NULL,"
    "  `PUBLN_DATE` DATE NULL,"
    "  `PUBLN_TYPE` VARCHAR(25) NULL COMMENT 'basic (defines derwent patent family) / equiv.',"
    "  `PUBLN_AUTH` CHAR(3) NOT NULL,"
    "  `PUBLN_LAN` CHAR(3) NULL,"
    "  `ACCESS_NR` VARCHAR(15) NOT NULL,"
    "  `ACCESS_ID` BIGINT NOT NULL,"
    "  `PUBLN_ID` BIGINT NOT NULL COMMENT 'defined by PUBLN_NR+PUBLN_KIND+PUBLN_AUTH',"
    "  PRIMARY KEY (`PUBLN_ID`),"
    "  CONSTRAINT `DW102_fk_ACCESS_NR`" 
    "    FOREIGN KEY (`ACCESS_ID`)" #tableName_fk_fieldName FOR KEY field Name
    "    REFERENCES `DW201_ACCESSIONS` (`ACCESS_ID`)" #foreignTableName (foreignFieldName)
    ") ENGINE=InnoDB")

TABLES['DW102a_PUBLN_APPLN'] = (
    "CREATE TABLE `DW102a_PUBLN_APPLN` ("
    "  `PUBLN_NR` BIGINT NOT NULL,"
    "  `APPLN_ID` BIGINT NOT NULL,"
    "  `APPLN_NR_L` VARCHAR(15) NOT NULL,"
    "  `ACCESS_NR` VARCHAR(15) NOT NULL,"
    "  `ACCESS_ID` BIGINT NOT NULL,"
    "  `PUBLN_ID` BIGINT NOT NULL,"
    "  CONSTRAINT `DW102a_fk_APPLN_ID` FOREIGN KEY (`APPLN_ID`)" #tableName_fk_fieldName FOR KEY field Name
    "    REFERENCES `DW101_APPLN` (`APPLN_ID`)," #foreignTableName (foreignFieldName)
    "  CONSTRAINT `DW102a_fk_PUBLN_ID` FOREIGN KEY (`PUBLN_ID`)" #tableName_fk_fieldName FOR KEY field Name
    "    REFERENCES `DW102_PUBLN` (`PUBLN_ID`)," #foreignTableName (foreignFieldName)
    "  CONSTRAINT `DW102a_fk_ACCESS_ID`" 
    "    FOREIGN KEY (`ACCESS_ID`)" #tableName_fk_fieldName FOR KEY field Name
    "    REFERENCES `DW201_ACCESSIONS` (`ACCESS_ID`)" #foreignTableName (foreignFieldName)
    ") ENGINE=InnoDB")

TABLES['DW103_PUBLN_DES_COUNTR'] = (
    "CREATE TABLE `DW103_PUBLN_DES_COUNTR` ("
    "  `PUBLN_ID` BIGINT NOT NULL,"
    "  `PUBLN_COUNTR` VARCHAR(3) NULL,"
    "  `PUBLN_GROUP` VARCHAR(10) NULL,"
    "  CONSTRAINT `DW103_fk_PUBLN_ID`" 
    "    FOREIGN KEY (`PUBLN_ID`)" #tableName_fk_fieldName FOR KEY field Name
    "    REFERENCES `DW102_PUBLN` (`PUBLN_ID`)" #foreignTableName (foreignFieldName)
    ") ENGINE=InnoDB")




################################## PEOPLE: ASSIGNEES + INVENTORS + AGENTS ####################################
TABLES['DW901_ASSIG_SUPPORT'] = (
    "CREATE TABLE `DW901_ASSIG_SUPPORT` ("
    "  `ASSIG_CODE` VARCHAR(15) NOT NULL COMMENT 'if doesnt exist - PUBLN_ID',"
    "  `ASSIG_TYPE` VARCHAR(20) NOT NULL,"
    "  `ASSIG_ID` BIGINT NOT NULL COMMENT 'defined by unique ASSIG_CODE+ASSIG_TYPE',"
    "  PRIMARY KEY (`ASSIG_ID`)"
    ") ENGINE=InnoDB")

#OK
TABLES['DW104_PUBLN_ASSIG'] = (
    "CREATE TABLE `DW104_PUBLN_ASSIG` ("
    "  `PUBLN_ID` BIGINT NOT NULL,"
    "  `ASSIG_ID` BIGINT NOT NULL,"
    "  CONSTRAINT `DW104_fk_PUBLN_ID`" 
    "    FOREIGN KEY (`PUBLN_ID`)" #tableName_fk_fieldName FOR KEY field Name
    "    REFERENCES `DW102_PUBLN` (`PUBLN_ID`)," #foreignTableName (foreignFieldName)
    "  CONSTRAINT `DW104_fk_ASSIG_ID`" 
    "    FOREIGN KEY (`ASSIG_ID`)" #tableName_fk_fieldName FOR KEY field Name
    "    REFERENCES `DW901_ASSIG_SUPPORT` (`ASSIG_ID`)" #foreignTableName (foreignFieldName)
    ") ENGINE=InnoDB")

#OK
TABLES['DW105_ASSIG'] = (
    "CREATE TABLE `DW105_ASSIG` ("
    "  `ASSIG_ID` BIGINT NOT NULL,"
    "  `ASSIG_TOTAL` VARCHAR(400) NULL,"
    "  `ASSIG_NAME_DWPI` VARCHAR(300) NULL,"
    "  `ASSIG_NAME_ORIG` VARCHAR(300) NULL,"
    "  `ASSIG_ADDRESS_TOTAL` VARCHAR(300) NULL,"
    "  `ASSIG_COUNTRY_CODE` VARCHAR(3) NULL,"
    "  `ASSIG_CITY` VARCHAR(3) NULL,"
    "  `ASSIG_LIMITATION` VARCHAR(3) NULL,"
    "  `ASSIG_LIMIT_TYPE` VARCHAR(10) NULL,"
    "  `ASSIG_RESIDENCE` VARCHAR(3) NULL,"
    "  `ASSIG_NATION` VARCHAR(3) NULL,"
    "  CONSTRAINT `DW105_fk_ASSIG_ID`" 
    "    FOREIGN KEY (`ASSIG_ID`)" #tableName_fk_fieldName FOR KEY field Name
    "    REFERENCES `DW901_ASSIG_SUPPORT` (`ASSIG_ID`)" #foreignTableName (foreignFieldName)
    ") ENGINE=InnoDB")

TABLES['DW106_PUBLN_INVENTOR'] = (
    "CREATE TABLE `DW106_PUBLN_INVENTOR` ("
    "  `INVENTOR_TOTAL` VARCHAR(400) NULL,"
    "  `INVENTOR_NAME_DWPI` VARCHAR(300) NULL,"
    "  `INVENTOR_NAME_ORIG` VARCHAR(300) NULL,"
    "  `INVENTOR_COUNTRY_CODE` VARCHAR(3) NULL,"
    "  `INVENTOR_CITY` VARCHAR(20) NULL,"
    "  `INVENTOR_ADDRESS_TOTAL` VARCHAR(300) NULL,"
    "  `INVENTOR_RESIDENCE` VARCHAR(3) NULL,"
    "  `INVENTOR_NATION` VARCHAR(3) NULL,"
    "  `PUBLN_ID` BIGINT NOT NULL,"
    "  `ACCESS_ID` BIGINT NOT NULL,"
    "  CONSTRAINT `DW106_fk_PUBLN_ID`" 
    "    FOREIGN KEY (`PUBLN_ID`)" #tableName_fk_fieldName FOR KEY field Name
    "    REFERENCES `DW102_PUBLN` (`PUBLN_ID`)," #foreignTableName (foreignFieldName)
    "  CONSTRAINT `DW106_fk_ACCESS_ID`" 
    "    FOREIGN KEY (`ACCESS_ID`)" #tableName_fk_fieldName FOR KEY field Name
    "    REFERENCES `DW201_ACCESSIONS` (`ACCESS_ID`)" #foreignTableName (foreignFieldName)
    ") ENGINE=InnoDB")

TABLES['DW107_AGENTS'] = (
    "CREATE TABLE `DW107_AGENTS` ("
    "  `AGENT_TOTAL` VARCHAR(400) NULL,"
    "  `AGENT_NAME_DWPI` VARCHAR(300) NULL,"
    "  `AGENT_NAME_ORIG` VARCHAR(300) NULL,"
    "  `AGENT_COUNTRY_CODE` VARCHAR(3) NULL,"
    "  `AGENT_CITY` VARCHAR(20) NULL,"
    "  `AGENT_ADDRESS_TOTAL` VARCHAR(300) NULL,"
    "  `AGENT_RESIDENCE` VARCHAR(3) NULL,"
    "  `AGENT_NATION` VARCHAR(3) NULL,"
    "  `PUBLN_ID` BIGINT NOT NULL,"
    "  `ACCESS_ID` BIGINT NOT NULL,"
    "  CONSTRAINT `DW107_fk_PUBLN_ID`" 
    "    FOREIGN KEY (`PUBLN_ID`)" #tableName_fk_fieldName FOR KEY field Name
    "    REFERENCES `DW102_PUBLN` (`PUBLN_ID`)," #foreignTableName (foreignFieldName)
    "  CONSTRAINT `DW107_fk_ACCESS_ID`" 
    "    FOREIGN KEY (`ACCESS_ID`)" #tableName_fk_fieldName FOR KEY field Name
    "    REFERENCES `DW201_ACCESSIONS` (`ACCESS_ID`)" #foreignTableName (foreignFieldName)
    ") ENGINE=InnoDB")




################################################## PRIORITY + RELATEDS + CITATIONS ############################
#OK, BUT UPATE AT END EXTRACTION WITH APPLN_ID
TABLES['DW108_PUBLN_PRIORITY'] = (
    "CREATE TABLE `DW108_PUBLN_PRIORITY` ("
    "  `PRIO_NR_L` VARCHAR(15) NULL,"
    "  `PRIO_NR_S` VARCHAR(15) NULL,"
    "  `PRIO_AUTH` CHAR(3) NULL,"
    "  `PRIO_DATE` DATE NULL,"
    "  `PUBLN_ID` BIGINT NOT NULL,"
    "  `ACCESS_ID` BIGINT NOT NULL,"
    "  `PRIO_APPLN_ID` BIGINT NULL COMMENT 'only if exists in this DB',"
    "  `PRIO_CODE` VARCHAR(5) NULL,"
    "  CONSTRAINT `DW108_fk_PUBLN_ID`" 
    "    FOREIGN KEY (`PUBLN_ID`)" #tableName_fk_fieldName FOR KEY field Name
    "    REFERENCES `DW102_PUBLN` (`PUBLN_ID`)," #foreignTableName (foreignFieldName)
    "  CONSTRAINT `DW108_fk_APPLN_ID` FOREIGN KEY (`PRIO_APPLN_ID`)" #tableName_fk_fieldName FOR KEY field Name
    "    REFERENCES `DW101_APPLN` (`APPLN_ID`)," #foreignTableName (foreignFieldName)
    "  CONSTRAINT `DW108_fk_ACCESS_ID`" 
    "    FOREIGN KEY (`ACCESS_ID`)" #tableName_fk_fieldName FOR KEY field Name
    "    REFERENCES `DW201_ACCESSIONS` (`ACCESS_ID`)" #foreignTableName (foreignFieldName)
    ") ENGINE=InnoDB")

TABLES['DW109_PUBLN_CIT_TO'] = (
    "CREATE TABLE `DW109_PUBLN_CIT_TO` ("
    "  `PUBLN_ID` BIGINT NOT NULL,"
    "  `ACCESS_ID` BIGINT NOT NULL,"
    "  `CITED_PUBLN_NR` BIGINT NOT NULL,"
    "  `CITED_PUBLN_KIND` VARCHAR(3) NULL,"
    "  `CITED_PUBLN_AUTH` CHAR(3) NULL,"
    "  `CITED_ACCESS_NR` VARCHAR(15) NULL,"
    "  `CITED_PUBLN_DATE` DATE NULL,"
    "  `CITED_PUBLN_ID` BIGINT NULL,"
    "  `CITED_ACCESS_ID` BIGINT NULL,"
    "  CONSTRAINT `DW109_fk_PUBLN_ID`" 
    "    FOREIGN KEY (`PUBLN_ID`)" #tableName_fk_fieldName FOR KEY field Name
    "    REFERENCES `DW102_PUBLN` (`PUBLN_ID`)," #foreignTableName (foreignFieldName)
    "  CONSTRAINT `DW109_fk_CITED_PUBLN_ID`" 
    "    FOREIGN KEY (`CITED_PUBLN_ID`)" #tableName_fk_fieldName FOR KEY field Name
    "    REFERENCES `DW102_PUBLN` (`PUBLN_ID`)," #foreignTableName (foreignFieldName)
    "  CONSTRAINT `DW109_fk_CITED_ACCESS_ID`" 
    "    FOREIGN KEY (`CITED_ACCESS_ID`)" #tableName_fk_fieldName FOR KEY field Name
    "    REFERENCES `DW201_ACCESSIONS` (`ACCESS_ID`)" #foreignTableName (foreignFieldName)
    ") ENGINE=InnoDB")

TABLES['DW110_PUBLN_CIT_BY'] = (
    "CREATE TABLE `DW110_PUBLN_CIT_BY` ("
    "  `PUBLN_ID` BIGINT NOT NULL,"
    "  `ACCESS_ID` BIGINT NOT NULL,"
    "  `CITBY_PUBLN_NR` BIGINT NULL,"
    "  `CITBY_PUBLN_KIND` VARCHAR(3) NULL,"   
    "  `CITBY_PUBLN_AUTH` CHAR(3) NOT NULL,"
    "  `CITBY_ACCESS_NR` VARCHAR(15) NULL,"
    "  `CITBY_PUBLN_DATE` DATE NULL,"
    "  `CITBY_ACCESS_ID` BIGINT NULL,"
    "  `CITBY_PUBLN_ID` BIGINT NULL,"
    "  CONSTRAINT `DW110_fk_PUBLN_ID`" 
    "    FOREIGN KEY (`PUBLN_ID`)" #tableName_fk_fieldName FOR KEY field Name
    "    REFERENCES `DW102_PUBLN` (`PUBLN_ID`)," #foreignTableName (foreignFieldName)
    "  CONSTRAINT `DW110_fk_CITBY_PUBLN_ID`" 
    "    FOREIGN KEY (`CITBY_PUBLN_ID`)" #tableName_fk_fieldName FOR KEY field Name
    "    REFERENCES `DW102_PUBLN` (`PUBLN_ID`)," #foreignTableName (foreignFieldName)
    "  CONSTRAINT `DW110_fk_CITBY_ACCESS_ID`" 
    "    FOREIGN KEY (`CITBY_ACCESS_ID`)" #tableName_fk_fieldName FOR KEY field Name
    "    REFERENCES `DW201_ACCESSIONS` (`ACCESS_ID`)" #foreignTableName (foreignFieldName)
    ") ENGINE=InnoDB")

#OK, BUT UPATE AT END EXTRACTION WITH PUBLN_ID
TABLES['DW111_PUBLN_REL'] = (
    "CREATE TABLE `DW111_PUBLN_REL` ("
    "  `PUBLN_ID` BIGINT NOT NULL,"
    "  `RELATED_PUBLN_NR` BIGINT NULL,"
    "  `RELATED_PUBLN_KIND` VARCHAR(3) NULL,"
    "  `RELATED_PUBLN_ID` BIGINT NULL,"
    "  `RELATED_PUBLN_AUTH` CHAR(3) NOT NULL,"
    "  `RELATION_TXT` VARCHAR(20) NULL,"
    "  CONSTRAINT `DW111_fk_PUBLN_ID`" 
    "    FOREIGN KEY (`PUBLN_ID`)" #tableName_fk_fieldName FOR KEY field Name
    "    REFERENCES `DW102_PUBLN` (`PUBLN_ID`)," #foreignTableName (foreignFieldName)
    "  CONSTRAINT `DW111_fk_RELATED_PUBLN_ID`" 
    "    FOREIGN KEY (`RELATED_PUBLN_ID`)" #tableName_fk_fieldName FOR KEY field Name
    "    REFERENCES `DW102_PUBLN` (`PUBLN_ID`)" #foreignTableName (foreignFieldName)
    ") ENGINE=InnoDB")

TABLES['DW112_LITER_CIT'] = (
    "CREATE TABLE `DW112_LITER_CIT` ("
    "  `PUBLN_ID` BIGINT NOT NULL,"
    "  `LITER_TOTAL` VARCHAR(5000) NOT NULL,"
    "  CONSTRAINT `DW112_fk_PUBLN_ID`" 
    "    FOREIGN KEY (`PUBLN_ID`)" #tableName_fk_fieldName FOR KEY field Name
    "    REFERENCES `DW102_PUBLN` (`PUBLN_ID`)" #foreignTableName (foreignFieldName)
    ") ENGINE=InnoDB")






################################################# CLAIM + TITLE #####################################

TABLES['DW113_PUBLN_TIT']=(
    "CREATE TABLE `DW113_PUBLN_TIT` ("
    "  `PUBLN_ID` BIGINT NOT NULL,"
    "  `PUBLN_TIT` VARCHAR(5000) NOT NULL,"
    "  `IS_ENHANCED` CHAR(1) NOT NULL,"
    "  CONSTRAINT `DW113_fk_PUBLN_ID`" 
    "    FOREIGN KEY (`PUBLN_ID`)" #tableName_fk_fieldName FOR KEY field Name
    "    REFERENCES `DW102_PUBLN` (`PUBLN_ID`)" #foreignTableName (foreignFieldName)
    ") ENGINE=InnoDB")

TABLES['DW114_PUBLN_CLAIM'] = (
    "CREATE TABLE `DW114_PUBLN_CLAIM` ("
    "  `PUBLN_ID` BIGINT NOT NULL,"
    "  `ACCESS_ID` BIGINT NOT NULL,"
    "  `CLAIM_TOTAL` VARCHAR(7000) NOT NULL,"
    "  CONSTRAINT `DW114_fk_PUBLN_ID`" 
    "    FOREIGN KEY (`PUBLN_ID`)" #tableName_fk_fieldName FOR KEY field Name
    "    REFERENCES `DW102_PUBLN` (`PUBLN_ID`)," #foreignTableName (foreignFieldName)
    "  CONSTRAINT `DW114_fk_ACCESS_ID`" 
    "    FOREIGN KEY (`ACCESS_ID`)" #tableName_fk_fieldName FOR KEY field Name
    "    REFERENCES `DW201_ACCESSIONS` (`ACCESS_ID`)" #foreignTableName (foreignFieldName)
    ") ENGINE=InnoDB")

TABLES['DW115_TITLE_TERMS'] = (
    "CREATE TABLE `DW115_TITLE_TERMS` ("
    "  `PUBLN_ID` BIGINT NOT NULL,"
    "  `ACCESS_ID` BIGINT NOT NULL,"
    "  `TITLE_TERM` VARCHAR(25) NOT NULL,"
    "  CONSTRAINT `DW115_fk_PUBLN_ID`" 
    "    FOREIGN KEY (`PUBLN_ID`)" #tableName_fk_fieldName FOR KEY field Name
    "    REFERENCES `DW102_PUBLN` (`PUBLN_ID`)," #foreignTableName (foreignFieldName)
    "  CONSTRAINT `DW115_fk_ACCESS_ID`" 
    "    FOREIGN KEY (`ACCESS_ID`)" #tableName_fk_fieldName FOR KEY field Name
    "    REFERENCES `DW201_ACCESSIONS` (`ACCESS_ID`)" #foreignTableName (foreignFieldName)
    ") ENGINE=InnoDB")




################################################# CLASSIFICATIONS #####################################

TABLES['DW116_IPC_CLASS'] = (
    "CREATE TABLE `DW116_IPC_CLASS` ("
    "  `PUBLN_ID` BIGINT NOT NULL,"
    "  `ACCESS_ID` BIGINT NOT NULL,"
    "  `IPC_CLASS` VARCHAR(25) NULL,"
    "  `IPC_VERSION` DATE NULL,"
    "  `IPC_ACTION_DATE` DATE NULL,"
    "  `IPC_CLASS_LEVEL` VARCHAR(25) NULL,"
    "  `IPC_SCOPE` VARCHAR(25) NULL,"
    "  `IPC_LEVEL` VARCHAR(25) NULL,"
    "  `IPC_APPLIED` VARCHAR(25) NULL,"
    "  `IPC_OFFICE` VARCHAR(25) NULL,"
    "  `IPC_TYPE` VARCHAR(25) NULL,"
    "  `IPC_RANK` VARCHAR(25) NULL,"
    "  CONSTRAINT `DW116_fk_PUBLN_ID`" 
    "    FOREIGN KEY (`PUBLN_ID`)" #tableName_fk_fieldName FOR KEY field Name
    "    REFERENCES `DW102_PUBLN` (`PUBLN_ID`)," #foreignTableName (foreignFieldName)
    "  CONSTRAINT `DW116_fk_ACCESS_ID`" 
    "    FOREIGN KEY (`ACCESS_ID`)" #tableName_fk_fieldName FOR KEY field Name
    "    REFERENCES `DW201_ACCESSIONS` (`ACCESS_ID`)" #foreignTableName (foreignFieldName)
    ") ENGINE=InnoDB")

TABLES['DW117_CPC_CLASS'] = (
    "CREATE TABLE `DW117_CPC_CLASS` ("
    "  `PUBLN_ID` BIGINT NOT NULL,"
    "  `ACCESS_ID` BIGINT NOT NULL,"
    "  `CPC_CLASS` VARCHAR(25) NULL,"
    "  `CPC_VERSION` DATE NULL,"
    "  `CPC_ACTION_DATE` DATE NULL,"
    "  `CPC_CLASS_LEVEL` VARCHAR(25) NULL,"
    "  `CPC_SCOPE` VARCHAR(25) NULL,"
    "  `CPC_LEVEL` VARCHAR(25) NULL,"
    "  `CPC_APPLIED` VARCHAR(25) NULL,"
    "  `CPC_OFFICE` VARCHAR(25) NULL,"
    "  `CPC_TYPE` VARCHAR(25) NULL,"
    "  `CPC_RANK` VARCHAR(25) NULL,"
    "  CONSTRAINT `DW117_fk_PUBLN_ID`" 
    "    FOREIGN KEY (`PUBLN_ID`)" #tableName_fk_fieldName FOR KEY field Name
    "    REFERENCES `DW102_PUBLN` (`PUBLN_ID`)," #foreignTableName (foreignFieldName)
    "  CONSTRAINT `DW117_fk_ACCESS_ID`" 
    "    FOREIGN KEY (`ACCESS_ID`)" #tableName_fk_fieldName FOR KEY field Name
    "    REFERENCES `DW201_ACCESSIONS` (`ACCESS_ID`)" #foreignTableName (foreignFieldName)
    ") ENGINE=InnoDB")

TABLES['DW118_ECLA_CLASS'] = (
    "CREATE TABLE `DW118_ECLA_CLASS` ("
    "  `PUBLN_ID` BIGINT NOT NULL,"
    "  `ACCESS_ID` BIGINT NOT NULL,"
    "  `ECLA_CLASS` VARCHAR(25) NULL,"
    "  `ECLA_TYPE` VARCHAR(25) NULL,"
    "  CONSTRAINT `DW118_fk_PUBLN_ID`" 
    "    FOREIGN KEY (`PUBLN_ID`)" #tableName_fk_fieldName FOR KEY field Name
    "    REFERENCES `DW102_PUBLN` (`PUBLN_ID`)," #foreignTableName (foreignFieldName)
    "  CONSTRAINT `DW118_fk_ACCESS_ID`" 
    "    FOREIGN KEY (`ACCESS_ID`)" #tableName_fk_fieldName FOR KEY field Name
    "    REFERENCES `DW201_ACCESSIONS` (`ACCESS_ID`)" #foreignTableName (foreignFieldName)
    ") ENGINE=InnoDB")

TABLES['DW119_DWPI_CLASS'] = (
    "CREATE TABLE `DW119_DWPI_CLASS` ("
    "  `PUBLN_ID` BIGINT NOT NULL,"
    "  `ACCESS_ID` BIGINT NOT NULL,"
    "  `DWPI_CLASS` VARCHAR(25) NULL,"
    "  `DWPI_SECTION` VARCHAR(25) NULL,"
    "  `DWPI_FAMILY` VARCHAR(25) NULL,"
    "  CONSTRAINT `DW119_fk_PUBLN_ID`" 
    "    FOREIGN KEY (`PUBLN_ID`)" #tableName_fk_fieldName FOR KEY field Name
    "    REFERENCES `DW102_PUBLN` (`PUBLN_ID`)," #foreignTableName (foreignFieldName)
    "  CONSTRAINT `DW119_fk_ACCESS_ID`" 
    "    FOREIGN KEY (`ACCESS_ID`)" #tableName_fk_fieldName FOR KEY field Name
    "    REFERENCES `DW201_ACCESSIONS` (`ACCESS_ID`)" #foreignTableName (foreignFieldName)
    ") ENGINE=InnoDB")

TABLES['DW120_MANUAL_CLASS'] = (
    "CREATE TABLE `DW120_MANUAL_CLASS` ("
    "  `PUBLN_ID` BIGINT NOT NULL,"
    "  `ACCESS_ID` BIGINT NOT NULL,"
    "  `MANUAL_CLASS` VARCHAR(25) NULL,"
    "  `MANUAL_SECTION` VARCHAR(25) NULL,"
    "  `MANUAL_FAMILY` VARCHAR(25) NULL,"
    "  CONSTRAINT `DW120_fk_PUBLN_ID`" 
    "    FOREIGN KEY (`PUBLN_ID`)" #tableName_fk_fieldName FOR KEY field Name
    "    REFERENCES `DW102_PUBLN` (`PUBLN_ID`)," #foreignTableName (foreignFieldName)
    "  CONSTRAINT `DW120_fk_ACCESS_ID`" 
    "    FOREIGN KEY (`ACCESS_ID`)" #tableName_fk_fieldName FOR KEY field Name
    "    REFERENCES `DW201_ACCESSIONS` (`ACCESS_ID`)" #foreignTableName (foreignFieldName)
    ") ENGINE=InnoDB")

TABLES['DW121_USPC_CLASS'] = (
    "CREATE TABLE `DW121_USPC_CLASS` ("
    "  `PUBLN_ID` BIGINT NOT NULL,"
    "  `ACCESS_ID` BIGINT NOT NULL,"
    "  `USPC_TYPE` VARCHAR(25) NULL,"
    "  `USPC_MAIN` VARCHAR(25) NULL,"
    "  `USPC_SUB` VARCHAR(25) NULL,"
    "  CONSTRAINT `DW121_fk_PUBLN_ID`" 
    "    FOREIGN KEY (`PUBLN_ID`)" #tableName_fk_fieldName FOR KEY field Name
    "    REFERENCES `DW102_PUBLN` (`PUBLN_ID`)," #foreignTableName (foreignFieldName)
    "  CONSTRAINT `DW121_fk_ACCESS_ID`" 
    "    FOREIGN KEY (`ACCESS_ID`)" #tableName_fk_fieldName FOR KEY field Name
    "    REFERENCES `DW201_ACCESSIONS` (`ACCESS_ID`)" #foreignTableName (foreignFieldName)
    ") ENGINE=InnoDB")

TABLES['DW122_JPPC_CLASS'] = (
    "CREATE TABLE `DW122_JPPC_CLASS` ("
    "  `PUBLN_ID` BIGINT NOT NULL,"
    "  `ACCESS_ID` BIGINT NOT NULL,"
    "  `JPPC_MAIN` VARCHAR(25) NULL,"
    "  `JPPC_TYPE` VARCHAR(25) NULL,"
    "  `JPPC_RANK` VARCHAR(25) NULL,"
    "  CONSTRAINT `DW122_fk_PUBLN_ID`" 
    "    FOREIGN KEY (`PUBLN_ID`)" #tableName_fk_fieldName FOR KEY field Name
    "    REFERENCES `DW102_PUBLN` (`PUBLN_ID`)," #foreignTableName (foreignFieldName)
    "  CONSTRAINT `DW122_fk_ACCESS_ID`" 
    "    FOREIGN KEY (`ACCESS_ID`)" #tableName_fk_fieldName FOR KEY field Name
    "    REFERENCES `DW201_ACCESSIONS` (`ACCESS_ID`)" #foreignTableName (foreignFieldName)
    ") ENGINE=InnoDB")

TABLES['DW123_JP_FCLASS'] = (
    "CREATE TABLE `DW123_JP_FCLASS` ("
    "  `PUBLN_ID` BIGINT NOT NULL,"
    "  `ACCESS_ID` BIGINT NOT NULL,"
    "  `JP_FTHEME` VARCHAR(25) NULL,"
    "  `JP_FTERM` VARCHAR(25) NULL,"
    "  CONSTRAINT `DW123_fk_PUBLN_ID`" 
    "    FOREIGN KEY (`PUBLN_ID`)" #tableName_fk_fieldName FOR KEY field Name
    "    REFERENCES `DW102_PUBLN` (`PUBLN_ID`)," #foreignTableName (foreignFieldName)
    "  CONSTRAINT `DW123_fk_ACCESS_ID`" 
    "    FOREIGN KEY (`ACCESS_ID`)" #tableName_fk_fieldName FOR KEY field Name
    "    REFERENCES `DW201_ACCESSIONS` (`ACCESS_ID`)" #foreignTableName (foreignFieldName)
    ") ENGINE=InnoDB")





################################################# ABSTRACTS #####################################

TABLES['DW124_ABSTRACT_ORIG'] = (
    "CREATE TABLE `DW124_ABSTRACT_ORIG` ("
    "  `PUBLN_ID` BIGINT NOT NULL,"
    "  `ACCESS_ID` BIGINT NOT NULL,"
    "  `ABSTRACT_TOTAL` VARCHAR(7000) NOT NULL COMMENT 'only French and English extracted',"
    "  `ABS_LANG` VARCHAR(2) NOT NULL,"
    "  CONSTRAINT `DW124_fk_PUBLN_ID`" 
    "    FOREIGN KEY (`PUBLN_ID`)" #tableName_fk_fieldName FOR KEY field Name
    "    REFERENCES `DW102_PUBLN` (`PUBLN_ID`)," #foreignTableName (foreignFieldName)
    "  CONSTRAINT `DW124_fk_ACCESS_ID`" 
    "    FOREIGN KEY (`ACCESS_ID`)" #tableName_fk_fieldName FOR KEY field Name
    "    REFERENCES `DW201_ACCESSIONS` (`ACCESS_ID`)" #foreignTableName (foreignFieldName)
    ") ENGINE=InnoDB")

TABLES['DW125_ABSTRACT_NOVELTY'] = (
    "CREATE TABLE `DW125_ABSTRACT_NOVELTY` ("
    "  `PUBLN_ID` BIGINT NOT NULL,"
    "  `ACCESS_ID` BIGINT NOT NULL,"
    "  `ABSTRACT_NOVELTY` VARCHAR(7000) NOT NULL,"
    "  `IS_ALERT` VARCHAR(3) NOT NULL COMMENT 'yes=shorter Abstract until 1999/ DOC=longer / no=longer after 1999',"
    "  CONSTRAINT `DW125_fk_PUBLN_ID`" 
    "    FOREIGN KEY (`PUBLN_ID`)" #tableName_fk_fieldName FOR KEY field Name
    "    REFERENCES `DW102_PUBLN` (`PUBLN_ID`)," #foreignTableName (foreignFieldName)
    "  CONSTRAINT `DW125_fk_ACCESS_ID`" 
    "    FOREIGN KEY (`ACCESS_ID`)" #tableName_fk_fieldName FOR KEY field Name
    "    REFERENCES `DW201_ACCESSIONS` (`ACCESS_ID`)" #foreignTableName (foreignFieldName)
    ") ENGINE=InnoDB")

TABLES['DW126_ABSTRACT_USE'] = (
    "CREATE TABLE `DW126_ABSTRACT_USE` ("
    "  `PUBLN_ID` BIGINT NOT NULL,"
    "  `ACCESS_ID` BIGINT NOT NULL,"
    "  `ABSTRACT_USE` VARCHAR(7000) NOT NULL,"
    "  `IS_ALERT` VARCHAR(3) NOT NULL COMMENT 'yes=shorter Abstract until 1999/ DOC=longer / no=longer after 1999',"
    "  CONSTRAINT `DW126_fk_PUBLN_ID`" 
    "    FOREIGN KEY (`PUBLN_ID`)" #tableName_fk_fieldName FOR KEY field Name
    "    REFERENCES `DW102_PUBLN` (`PUBLN_ID`)," #foreignTableName (foreignFieldName)
    "  CONSTRAINT `DW126_fk_ACCESS_ID`" 
    "    FOREIGN KEY (`ACCESS_ID`)" #tableName_fk_fieldName FOR KEY field Name
    "    REFERENCES `DW201_ACCESSIONS` (`ACCESS_ID`)" #foreignTableName (foreignFieldName)
    ") ENGINE=InnoDB")

TABLES['DW127_ABSTRACT_DESCRIPTION'] = (
    "CREATE TABLE `DW127_ABSTRACT_DESCRIPTION` ("
    "  `PUBLN_ID` BIGINT NOT NULL,"
    "  `ACCESS_ID` BIGINT NOT NULL,"
    "  `ABSTRACT_DESCRIPTION` VARCHAR(7000) NOT NULL,"
    "  `IS_ALERT` VARCHAR(3) NOT NULL COMMENT 'yes=shorter Abstract until 1999/ DOC=longer / no=longer after 1999',"
    "  CONSTRAINT `DW127_fk_PUBLN_ID`" 
    "    FOREIGN KEY (`PUBLN_ID`)" #tableName_fk_fieldName FOR KEY field Name
    "    REFERENCES `DW102_PUBLN` (`PUBLN_ID`)," #foreignTableName (foreignFieldName)
    "  CONSTRAINT `DW127_fk_ACCESS_ID`" 
    "    FOREIGN KEY (`ACCESS_ID`)" #tableName_fk_fieldName FOR KEY field Name
    "    REFERENCES `DW201_ACCESSIONS` (`ACCESS_ID`)" #foreignTableName (foreignFieldName)
    ") ENGINE=InnoDB")

TABLES['DW128_ABSTRACT_ADVANTAGE'] = (
    "CREATE TABLE `DW128_ABSTRACT_ADVANTAGE` ("
    "  `PUBLN_ID` BIGINT NOT NULL,"
    "  `ACCESS_ID` BIGINT NOT NULL,"
    "  `ABSTRACT_ADVANTAGE` VARCHAR(7000) NOT NULL,"
    "  `IS_ALERT` VARCHAR(3) NOT NULL COMMENT 'yes=shorter Abstract until 1999/ DOC=longer / no=longer after 1999',"
    "  CONSTRAINT `DW128_fk_PUBLN_ID`" 
    "    FOREIGN KEY (`PUBLN_ID`)" #tableName_fk_fieldName FOR KEY field Name
    "    REFERENCES `DW102_PUBLN` (`PUBLN_ID`)," #foreignTableName (foreignFieldName)
    "  CONSTRAINT `DW128_fk_ACCESS_ID`" 
    "    FOREIGN KEY (`ACCESS_ID`)" #tableName_fk_fieldName FOR KEY field Name
    "    REFERENCES `DW201_ACCESSIONS` (`ACCESS_ID`)" #foreignTableName (foreignFieldName)
    ") ENGINE=InnoDB")

TABLES['DW129_ABSTRACT_DRAWINGS'] = (
    "CREATE TABLE `DW129_ABSTRACT_DRAWINGS` ("
    "  `PUBLN_ID` BIGINT NOT NULL,"
    "  `ACCESS_ID` BIGINT NOT NULL,"
    "  `ABSTRACT_DRAWINGS` VARCHAR(7000) NOT NULL,"
    "  `IS_ALERT` VARCHAR(3) NOT NULL,"
    "  CONSTRAINT `DW129_fk_PUBLN_ID`" 
    "    FOREIGN KEY (`PUBLN_ID`)" #tableName_fk_fieldName FOR KEY field Name
    "    REFERENCES `DW102_PUBLN` (`PUBLN_ID`)," #foreignTableName (foreignFieldName)
    "  CONSTRAINT `DW129_fk_ACCESS_ID`" 
    "    FOREIGN KEY (`ACCESS_ID`)" #tableName_fk_fieldName FOR KEY field Name
    "    REFERENCES `DW201_ACCESSIONS` (`ACCESS_ID`)" #foreignTableName (foreignFieldName)
    ") ENGINE=InnoDB")


TABLES['DW130_ABSTRACT_OTHER_DOC'] = (
    "CREATE TABLE `DW130_ABSTRACT_OTHER_DOC` ("
    "  `PUBLN_ID` BIGINT NOT NULL,"
    "  `ACCESS_ID` BIGINT NOT NULL,"
    "  `ABSTRACT_OTHER_DOC` VARCHAR(7000) NOT NULL,"
    "  CONSTRAINT `DW130_fk_PUBLN_ID`" 
    "    FOREIGN KEY (`PUBLN_ID`)" #tableName_fk_fieldName FOR KEY field Name
    "    REFERENCES `DW102_PUBLN` (`PUBLN_ID`)," #foreignTableName (foreignFieldName)
    "  CONSTRAINT `DW130_fk_ACCESS_ID`" 
    "    FOREIGN KEY (`ACCESS_ID`)" #tableName_fk_fieldName FOR KEY field Name
    "    REFERENCES `DW201_ACCESSIONS` (`ACCESS_ID`)" #foreignTableName (foreignFieldName)
    ") ENGINE=InnoDB")


TABLES['DW131_ABSTRACT_TECH_FOCUS'] = (
    "CREATE TABLE `DW131_ABSTRACT_TECH_FOCUS` ("
    "  `PUBLN_ID` BIGINT NOT NULL,"
    "  `ACCESS_ID` BIGINT NOT NULL,"
    "  `TECH_AREA` VARCHAR(25) NULL,"
    "  `ABSTRACT_TECH_FOCUS` VARCHAR(7000) NOT NULL,"
    "  CONSTRAINT `DW131_fk_PUBLN_ID`" 
    "    FOREIGN KEY (`PUBLN_ID`)" #tableName_fk_fieldName FOR KEY field Name
    "    REFERENCES `DW102_PUBLN` (`PUBLN_ID`)," #foreignTableName (foreignFieldName)
    "  CONSTRAINT `DW131_fk_ACCESS_ID`" 
    "    FOREIGN KEY (`ACCESS_ID`)" #tableName_fk_fieldName FOR KEY field Name
    "    REFERENCES `DW201_ACCESSIONS` (`ACCESS_ID`)" #foreignTableName (foreignFieldName)
    ") ENGINE=InnoDB")

TABLES['DW132_ABSTRACT_EXTENSION'] = (
    "CREATE TABLE `DW132_ABSTRACT_EXTENSION` ("
    "  `PUBLN_ID` BIGINT NOT NULL,"
    "  `ACCESS_ID` BIGINT NOT NULL,"
    "  `ABSTRACT_EXTENSION` VARCHAR(7000) NOT NULL,"
    "  CONSTRAINT `DW132_fk_PUBLN_ID`" 
    "    FOREIGN KEY (`PUBLN_ID`)" #tableName_fk_fieldName FOR KEY field Name
    "    REFERENCES `DW102_PUBLN` (`PUBLN_ID`)," #foreignTableName (foreignFieldName)
    "  CONSTRAINT `DW132_fk_ACCESS_ID`" 
    "    FOREIGN KEY (`ACCESS_ID`)" #tableName_fk_fieldName FOR KEY field Name
    "    REFERENCES `DW201_ACCESSIONS` (`ACCESS_ID`)" #foreignTableName (foreignFieldName)
    ") ENGINE=InnoDB")

TABLES['DW133_ABSTRACT_MECH_ACTION'] = (
    "CREATE TABLE `DW133_ABSTRACT_MECH_ACTION` ("
    "  `PUBLN_ID` BIGINT NOT NULL,"
    "  `ACCESS_ID` BIGINT NOT NULL,"
    "  `ABSTRACT_MECH_ACTION` VARCHAR(7000) NOT NULL,"
    "  `IS_ALERT` VARCHAR(3) NOT NULL COMMENT 'yes=shorter Abstract until 1999/ DOC=longer / no=longer after 1999',"
    "  CONSTRAINT `DW133_fk_PUBLN_ID`" 
    "    FOREIGN KEY (`PUBLN_ID`)" #tableName_fk_fieldName FOR KEY field Name
    "    REFERENCES `DW102_PUBLN` (`PUBLN_ID`)," #foreignTableName (foreignFieldName)
    "  CONSTRAINT `DW133_fk_ACCESS_ID`" 
    "    FOREIGN KEY (`ACCESS_ID`)" #tableName_fk_fieldName FOR KEY field Name
    "    REFERENCES `DW201_ACCESSIONS` (`ACCESS_ID`)" #foreignTableName (foreignFieldName)
    ") ENGINE=InnoDB")

TABLES['DW134_ABSTRACT_ACTIVITY'] = (
    "CREATE TABLE `DW134_ABSTRACT_ACTIVITY` ("
    "  `PUBLN_ID` BIGINT NOT NULL,"
    "  `ACCESS_ID` BIGINT NOT NULL,"
    "  `ABSTRACT_ACTIVITY` VARCHAR(7000) NOT NULL,"
    "  `IS_ALERT` VARCHAR(3) NOT NULL COMMENT 'yes=shorter Abstract until 1999/ DOC=longer / no=longer after 1999',"
    "  CONSTRAINT `DW134_fk_PUBLN_ID`" 
    "    FOREIGN KEY (`PUBLN_ID`)" #tableName_fk_fieldName FOR KEY field Name
    "    REFERENCES `DW102_PUBLN` (`PUBLN_ID`)," #foreignTableName (foreignFieldName)
    "  CONSTRAINT `DW134_fk_ACCESS_ID`" 
    "    FOREIGN KEY (`ACCESS_ID`)" #tableName_fk_fieldName FOR KEY field Name
    "    REFERENCES `DW201_ACCESSIONS` (`ACCESS_ID`)" #foreignTableName (foreignFieldName)
    ") ENGINE=InnoDB")




##################################### INDEXING + LINK CODES ######################################

TABLES['DW140_POLYMER_INDEXING'] = (
    "CREATE TABLE `DW140_POLYMER_INDEXING` ("
    "  `PUBLN_ID` BIGINT NOT NULL,"
    "  `ACCESS_ID` BIGINT NOT NULL,"
    "  `PARA_NUM` INT NULL COMMENT 'paragraph number',"
    "  `STC_NUM` INT NULL COMMENT 'sentence number',"
    "  `TIME_RNG` VARCHAR(10) NULL COMMENT 'attribute of the sentence',"
    "  `APPLIED` VARCHAR(5) NULL COMMENT 'attribute of the term',"
    "  `TERM_TYPE` VARCHAR(10) NULL COMMENT 'code/scn=Specific Compound Number/drc',"
    "  `TERM` VARCHAR(10) NULL,"
    "  CONSTRAINT `DW140_fk_PUBLN_ID`" 
    "    FOREIGN KEY (`PUBLN_ID`)" #tableName_fk_fieldName FOR KEY field Name
    "    REFERENCES `DW102_PUBLN` (`PUBLN_ID`)," #foreignTableName (foreignFieldName)
    "  CONSTRAINT `DW140_fk_ACCESS_ID`" 
    "    FOREIGN KEY (`ACCESS_ID`)" #tableName_fk_fieldName FOR KEY field Name
    "    REFERENCES `DW201_ACCESSIONS` (`ACCESS_ID`)" #foreignTableName (foreignFieldName)
    ") ENGINE=InnoDB")

TABLES['DW141_KEYWORD_INDEXING'] = (
    "CREATE TABLE `DW141_KEYWORD_INDEXING` ("
    "  `PUBLN_ID` BIGINT NOT NULL,"
    "  `ACCESS_ID` BIGINT NOT NULL,"
    "  `PARA_NUM` INT NULL COMMENT 'paragraph number',"
    "  `STC_NUM` INT NULL COMMENT 'sentence number',"
    "  `RELEVANCE` VARCHAR(10) NULL COMMENT 'attribute of the sentence',"
    "  `APPLIED` VARCHAR(5) NULL COMMENT 'attribute of the term',"
    "  `TERM_TYPE` VARCHAR(10) NULL COMMENT 'code/scn=Specific Compound Number/drc',"
    "  `ROLE` VARCHAR(25) NULL COMMENT 'role',"
    "  `TERM` VARCHAR(10) NULL,"
    "  CONSTRAINT `DW141_fk_PUBLN_ID`" 
    "    FOREIGN KEY (`PUBLN_ID`)" #tableName_fk_fieldName FOR KEY field Name
    "    REFERENCES `DW102_PUBLN` (`PUBLN_ID`)," #foreignTableName (foreignFieldName)
    "  CONSTRAINT `DW141_fk_ACCESS_ID`" 
    "    FOREIGN KEY (`ACCESS_ID`)" #tableName_fk_fieldName FOR KEY field Name
    "    REFERENCES `DW201_ACCESSIONS` (`ACCESS_ID`)" #foreignTableName (foreignFieldName)
    ") ENGINE=InnoDB")

TABLES['DW142_CHEMICAL_CODES'] = (
    "CREATE TABLE `DW142_CHEMICAL_CODES` ("
    "  `PUBLN_ID` BIGINT NOT NULL,"
    "  `ACCESS_ID` BIGINT NOT NULL,"
    "  `SUBJECT` VARCHAR(20) COMMENT 'paragraph number',"
    "  `CARD_NUM` INT NULL COMMENT 'sentence number',"
    "  `TIME_RNG` VARCHAR(10) NULL COMMENT 'attribute of the sentence',"
    "  `ROLE` VARCHAR(25) NULL COMMENT 'role',"
    "  `MARKUSH` VARCHAR(10) NULL,"
    "  `REGISTRY` VARCHAR(10) NULL,"
    "  `APPLIED` VARCHAR(5) NULL COMMENT 'attribute of the term',"
    "  `TERM_TYPE` VARCHAR(10) NULL COMMENT 'code/scn=Specific Compound Number/drc',"
    "  `CODE` VARCHAR(10) NULL,"
    "  CONSTRAINT `DW142_fk_PUBLN_ID`" 
    "    FOREIGN KEY (`PUBLN_ID`)" #tableName_fk_fieldName FOR KEY field Name
    "    REFERENCES `DW102_PUBLN` (`PUBLN_ID`)," #foreignTableName (foreignFieldName)
    "  CONSTRAINT `DW142_fk_ACCESS_ID`" 
    "    FOREIGN KEY (`ACCESS_ID`)" #tableName_fk_fieldName FOR KEY field Name
    "    REFERENCES `DW201_ACCESSIONS` (`ACCESS_ID`)" #foreignTableName (foreignFieldName)
    ") ENGINE=InnoDB")

TABLES['DW143_CHEMICAL_UNLINK_CODES'] = (
    "CREATE TABLE `DW143_CHEMICAL_UNLINK_CODES` ("
    "  `PUBLN_ID` BIGINT NOT NULL,"
    "  `ACCESS_ID` BIGINT NOT NULL,"
    "  `ROLE` VARCHAR(25) NULL COMMENT 'role',"
    "  `APPLIED` VARCHAR(5) NULL COMMENT 'attribute of the term',"
    "  `TERM_TYPE` VARCHAR(10) NULL COMMENT 'code/scn=Specific Compound Number/drc',"
    "  `CODE` VARCHAR(10) NULL,"
    "  CONSTRAINT `DW143_fk_PUBLN_ID`" 
    "    FOREIGN KEY (`PUBLN_ID`)" #tableName_fk_fieldName FOR KEY field Name
    "    REFERENCES `DW102_PUBLN` (`PUBLN_ID`)," #foreignTableName (foreignFieldName)
    "  CONSTRAINT `DW143_fk_ACCESS_ID`" 
    "    FOREIGN KEY (`ACCESS_ID`)" #tableName_fk_fieldName FOR KEY field Name
    "    REFERENCES `DW201_ACCESSIONS` (`ACCESS_ID`)" #foreignTableName (foreignFieldName)
    ") ENGINE=InnoDB")

TABLES['DW144_POLYMER_CODES'] = (
    "CREATE TABLE `DW144_POLYMER_CODES` ("
    "  `PUBLN_ID` BIGINT NOT NULL,"
    "  `ACCESS_ID` BIGINT NOT NULL,"
    "  `CARD_NUM` INT NULL COMMENT 'sentence number',"
    "  `TIME_RNG` VARCHAR(10) NULL COMMENT 'attribute of the sentence',"
    "  `CODE` VARCHAR(10) NULL,"
    "  CONSTRAINT `DW144_fk_PUBLN_ID`" 
    "    FOREIGN KEY (`PUBLN_ID`)" #tableName_fk_fieldName FOR KEY field Name
    "    REFERENCES `DW102_PUBLN` (`PUBLN_ID`)," #foreignTableName (foreignFieldName)
    "  CONSTRAINT `DW144_fk_ACCESS_ID`" 
    "    FOREIGN KEY (`ACCESS_ID`)" #tableName_fk_fieldName FOR KEY field Name
    "    REFERENCES `DW201_ACCESSIONS` (`ACCESS_ID`)" #foreignTableName (foreignFieldName)
    ") ENGINE=InnoDB")

TABLES['DW145_POLYMER_SERIAL_KEYS'] = (
    "CREATE TABLE `DW145_POLYMER_SERIAL_KEYS` ("
    "  `PUBLN_ID` BIGINT NOT NULL,"
    "  `ACCESS_ID` BIGINT NOT NULL,"
    "  `SERIAL_KEY` VARCHAR(10) NULL,"
    "  CONSTRAINT `DW145_fk_PUBLN_ID`" 
    "    FOREIGN KEY (`PUBLN_ID`)" #tableName_fk_fieldName FOR KEY field Name
    "    REFERENCES `DW102_PUBLN` (`PUBLN_ID`)," #foreignTableName (foreignFieldName)
    "  CONSTRAINT `DW145_fk_ACCESS_ID`" 
    "    FOREIGN KEY (`ACCESS_ID`)" #tableName_fk_fieldName FOR KEY field Name
    "    REFERENCES `DW201_ACCESSIONS` (`ACCESS_ID`)" #foreignTableName (foreignFieldName)
    ") ENGINE=InnoDB")


# In[11]:

DB_NAME = raw_input("DB name e.g.: DERWENT_2015: ")
usr=raw_input("MySQL user: ")
pwd=getpass.getpass("MySQL password: ")


# In[ ]:

for i in range(5):  #REPETITION DUE TO ORDERING IN TABLE CREATION. TABLES WITH FOREIGN KEYS WILL NOT BE GENERATED UNTIL PRIMARY KEYS ARE.
    cnx = mysql.connector.connect(user=usr,password=pwd)
    cursor = cnx.cursor()

####################


    def create_database(cursor):
        try:
            cursor.execute(
            "CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(DB_NAME))
        except mysql.connector.Error as err:
            print("Failed creating database: {}".format(err))
            exit(1)

        
    try:
        cnx.database = DB_NAME  
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_BAD_DB_ERROR:
            create_database(cursor)
            cnx.database = DB_NAME
        else:
            print(err)
            exit(1)


###########################################


    for name, ddl in TABLES.items():
        try:
            #print("Creating table {}: ".format(name), end='')     #THIS LINE ONLY WORKS ON PYTHON 3
            cursor.execute(ddl)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                print("already exists.")
            else:
                print(err.msg)
        else:
            print("OK")

    cursor.close()
    cnx.close()
    


# In[ ]:



