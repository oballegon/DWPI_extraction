
# coding: utf-8

# <script>
#   function code_toggle() {
#     if (code_shown){
#       $('div.input').hide('500');
#       $('#toggleButton').val('Show Code')
#     } else {
#       $('div.input').show('500');
#       $('#toggleButton').val('Hide Code')
#     }
#     code_shown = !code_shown
#   }
# 
#   $( document ).ready(function(){
#     code_shown=false;
#     $('div.input').hide()
#   });
# </script>
# <form action="javascript:code_toggle()"><input type="submit" id="toggleButton" value="Show Code"></form>

# In[4]:

import tarfile
import os
import getpass as getpass                                                                                                                                                           
import xml.etree.ElementTree as ET
from lxml import etree
import mysql.connector
from mysql.connector import errorcode
from datetime import datetime
import csv
import stat
import pickle
import calendar
import sys
import db_creation 


# ## Initialization
# This generates a directory for the ID dictionaries as well as the empty pickle files if desired (yes/no). Answer is required. If yes, previous pickle files will be erased and the ID's linking already-extracted patents will be lost. Only hit yes if extracting the ENTIRE data_st or in controlled tests.
# 
# The paths to the data and log are also defined here.

# In[30]:

# This generates a directory for the ID dictionaries as well as the empty pickle files if desired (yes/no)

#path="./zip2" #path to directory where data is located (year folders)
#outpath="./" #path where the temporary extraction is performed

#path to directory where data is located (year folders)
path="/your/path/to/data" #path to directory where data is located (year folders)
#path to directory where extraction is performed and LOG saved
outpath="/your/path/to/extraction" 
#path to storing the pickles with the unique identifiers for future reference
dict_dir="your/path/to/pickles"

if os.path.exists(dict_dir):
    pass
else:
    os.mkdir(dict_dir)
    
new_id=raw_input("Generate NEW ID's (extract full db) - yes/no: ")
if new_id=="yes":
    empty_dict={}
    pickle.dump(empty_dict,open(dict_dir+"/access.p","w"))
    pickle.dump(empty_dict,open(dict_dir+"/appln.p","w"))
    pickle.dump(empty_dict,open(dict_dir+"/publn.p","w"))
    pickle.dump(empty_dict,open(dict_dir+"/assig.p","w"))
    pickle.dump(empty_dict,open(dict_dir+"/unexplored_fields.p","w"))
elif new_id=="no":
    pass
else:
    print("ERROR")
    sys.exit(0)


# This is a function that removes DS_Store when working with OSX, in case the directory has been visited. Generally, it won't be needed

# In[31]:

#this is a function that removes DS_Store when working with OSX, in case the directory has been visited. Generally not needed
def del_ds(path):
    ds="/.DS_Store"
    pth=path+ds
    try: 
        os.remove(pth)
    except OSError:
        pass


# ## Dictionary
# This defines the various possibilities for introducing/updating tables.

# In[32]:

INSERTS = {}

INSERTS['publn'] = (
    "INSERT INTO DW102_PUBLN" #table name
    "(PUBLN_ID,PUBLN_NR,PUBLN_KIND,PUBLN_DATE,PUBLN_TYPE,PUBLN_AUTH,PUBLN_LAN,ACCESS_NR,ACCESS_ID)" #columns
    "VALUE (%(publn_id)s,%(publn_nr)s,%(publn_kind)s,%(publn_date)s,%(publn_type)s,%(publn_auth)s,%(publn_lang)s,%(access_nr)s,%(access_id)s)") #information - can be coded as dict

INSERTS['access'] = (
    "INSERT INTO DW201_ACCESSIONS" #table name
    "(ACCESS_ID,ACCESS_NR,ACCESS_COUNTRY_COUNT,ACCESS_PUBLN_COUNT,ACCESS_CITED_COUNT,ACCESS_CITED_INV_COUNT,ACCESS_CIT_AUTH_COUNT,ACCESS_CIT_LITER_COUNT)" #columns
    "VALUE (%(access_id)s,%(access_nr)s,%(country_count)s,%(publn_count)s,%(cit_count)s,%(invent_count)s,%(auth_count)s,%(liter_count)s)") #information - can be coded as dict

#THIS TABLE NEEDS TO BE UPDATED LATER
INSERTS['access_rel'] = (
    "INSERT INTO DW202_ACCESS_REL" #table name
    "(ACCESS_NR,ACCESS_ID,REL_TO_ACCESS_NR,REL_TYPE)" #columns
    "VALUE (%(access_nr)s,%(access_id)s,%(rel_access_nr)s,%(rel_type)s)") #information - can be coded as dict

INSERTS["appln"] = (
    "INSERT INTO DW101_APPLN"
    "(APPLN_NR_S,APPLN_NR_L,APPLN_AUTH,APPLN_DATE,ACCESS_NR,ACCESS_ID,APPLN_TXT, APPLN_ID)"
    "VALUE (%(appln_s)s,%(appln_l)s,%(appln_auth)s,%(appln_date)s,%(access_nr)s,%(access_id)s,%(appln_txt)s,%(appln_id)s)")

INSERTS["publn_appln"]=(
    "INSERT INTO DW102a_PUBLN_APPLN"
    "(PUBLN_NR,PUBLN_ID,ACCESS_NR,ACCESS_ID,APPLN_NR_L,APPLN_ID)"
    "VALUE (%(publn_nr)s,%(publn_id)s,%(access_nr)s,%(access_id)s,%(appln_nr_l)s,%(appln_id)s)")

INSERTS['publn_des_countr'] = (
    "INSERT INTO DW103_PUBLN_DES_COUNTR" #table name
    "(PUBLN_ID,PUBLN_GROUP,PUBLN_COUNTR)" #columns
    "VALUE (%(publn_id)s,%(pub_gr)s,%(pub_countr)s)") #information - can be coded as dict




################################## PEOPLE: ASSIGNEES + INVENTORS + AGENTS ####################################

INSERTS['assig_access'] = (
    "INSERT INTO DW203_ACCESS_ASSIG" #table name
    "(ACCESS_ID,ASSIG_ID)" #columns
    "VALUE (%(access_id)s,%(assig_id)s)") #information - can be coded as dict

INSERTS['inventors'] = (
    "INSERT INTO DW106_PUBLN_INVENTOR" #table name
    "(PUBLN_ID,INVENTOR_TOTAL,INVENTOR_NAME_DWPI,INVENTOR_NAME_ORIG,INVENTOR_ADDRESS_TOTAL,INVENTOR_COUNTRY_CODE,INVENTOR_CITY,INVENTOR_RESIDENCE,INVENTOR_NATION,ACCESS_ID)" #columns
    "VALUE (%(publn_id)s,%(assig_total)s,%(assig_name_dwpi)s,%(assig_name_orig)s,%(assig_address_tot)s,%(assig_cc)s,%(assig_city)s,%(resid)s,%(nation)s,%(access_id)s)") #information - can be coded as dict

INSERTS['agents'] = (
    "INSERT INTO DW107_AGENTS" #table name
    "(PUBLN_ID,AGENT_TOTAL,AGENT_NAME_DWPI,AGENT_NAME_ORIG,AGENT_ADDRESS_TOTAL,AGENT_COUNTRY_CODE,AGENT_CITY,AGENT_RESIDENCE,AGENT_NATION,ACCESS_ID)" #columns
    "VALUE (%(publn_id)s,%(assig_total)s,%(assig_name_dwpi)s,%(assig_name_orig)s,%(assig_address_tot)s,%(assig_cc)s,%(assig_city)s,%(resid)s,%(nation)s,%(access_id)s)") #information - can be coded as dict

INSERTS['assignees'] = (
    "INSERT INTO DW901_ASSIG_SUPPORT" #table name
    "(ASSIG_CODE,ASSIG_TYPE,ASSIG_ID)" #columns
    "VALUE (%(assig_code)s,%(assig_type)s,%(assig_id)s)") #information - can be coded as dict

INSERTS['assig_publn'] = (
    "INSERT INTO DW104_PUBLN_ASSIG" #table name
    "(PUBLN_ID,ASSIG_ID)" #columns
    "VALUE (%(publn_id)s,%(assig_id)s)") #information - can be coded as dict

INSERTS['assig_data'] = (
    "INSERT INTO DW105_ASSIG" #table name
    "(ASSIG_ID,ASSIG_TOTAL,ASSIG_NAME_DWPI,ASSIG_NAME_ORIG,ASSIG_ADDRESS_TOTAL,ASSIG_COUNTRY_CODE,ASSIG_CITY,ASSIG_LIMITATION,ASSIG_LIMIT_TYPE,ASSIG_RESIDENCE,ASSIG_NATION)" #columns
    "VALUE (%(assig_id)s,%(assig_total)s,%(assig_name_dwpi)s,%(assig_name_orig)s,%(assig_address_tot)s,%(assig_cc)s,%(assig_city)s,%(limitation)s,%(limitation_type)s,%(resid)s,%(nation)s)") #information - can be coded as dict




################################################## PRIORITY + RELATEDS + CITATIONS ############################

INSERTS["priorities"] = (
    "INSERT INTO DW108_PUBLN_PRIORITY"
    "(PRIO_NR_S,PRIO_NR_L,PRIO_AUTH,PRIO_DATE,ACCESS_ID,PUBLN_ID,PRIO_CODE)"
    "VALUE (%(appln_s)s,%(appln_l)s,%(appln_auth)s,%(appln_date)s,%(access_id)s,%(publn_id)s,%(priority_code)s)")

INSERTS['citations'] = (
    "INSERT INTO DW109_PUBLN_CIT_TO" #table name
    "(PUBLN_ID,ACCESS_ID,CITED_PUBLN_NR,CITED_PUBLN_DATE,CITED_PUBLN_KIND,CITED_PUBLN_AUTH,CITED_ACCESS_NR)" #columns
    "VALUE (%(publn_id)s,%(access_id)s,%(cit_publn_nr)s,%(cit_publn_date)s,%(cit_publn_kind)s,%(cit_publn_auth)s,%(cit_access_nr)s)") #information - can be coded as dict

INSERTS['citings'] = (
    "INSERT INTO DW110_PUBLN_CIT_BY" #table name
    "(PUBLN_ID,ACCESS_ID,CITBY_PUBLN_NR,CITBY_PUBLN_DATE,CITBY_PUBLN_KIND,CITBY_PUBLN_AUTH,CITBY_ACCESS_NR)" #columns
    "VALUE (%(publn_id)s,%(access_id)s,%(cit_publn_nr)s,%(cit_publn_date)s,%(cit_publn_kind)s,%(cit_publn_auth)s,%(cit_access_nr)s)") #information - can be coded as dict

INSERTS['publn_rel'] = (
    "INSERT INTO DW111_PUBLN_REL" #table name
    "(RELATED_PUBLN_KIND,RELATED_PUBLN_AUTH,RELATED_PUBLN_NR,PUBLN_ID,RELATION_TXT)" #columns
    "VALUE (%(rel_publn_kind)s,%(rel_publn_auth)s,%(rel_publn_nr)s,%(publn_id)s,%(description)s)") #information - can be coded as dict

INSERTS["literature"] = (
    "INSERT INTO DW112_LITER_CIT"
    "(PUBLN_ID,LITER_TOTAL)"
    "VALUE (%(publn_id)s,%(liter_tot)s)")



################################################# CLAIM + TITLE #####################################


INSERTS["claims"] = (
    "INSERT INTO DW114_PUBLN_CLAIM"
    "(PUBLN_ID, ACCESS_ID, CLAIM_TOTAL)"
    "VALUE (%(publn_id)s,%(access_id)s,%(publn_claim)s)")

INSERTS["tit_terms"] = (
    "INSERT INTO DW115_TITLE_TERMS"
    "(PUBLN_ID, ACCESS_ID, TITLE_TERM)"
    "VALUE (%(publn_id)s,%(access_id)s,%(tit_term)s)")

INSERTS["publn_tit"] = (
    "INSERT INTO DW113_PUBLN_TIT"
    "(PUBLN_ID,PUBLN_TIT,IS_ENHANCED)"
    "VALUE (%(publn_id)s,%(publn_tit)s,%(is_enhanced)s)")



################################################# CLASSIFICATIONS #####################################

INSERTS["Ipc"] = (
    "INSERT INTO DW116_IPC_CLASS"
    "(PUBLN_ID, ACCESS_ID, IPC_CLASS,IPC_VERSION,IPC_CLASS_LEVEL,IPC_SCOPE,IPC_LEVEL,IPC_APPLIED,IPC_OFFICE,IPC_TYPE,IPC_RANK,IPC_ACTION_DATE)"
    "VALUE (%(publn_id)s,%(access_id)s,%(ipc_class)s,%(ipc_version)s,%(ipc_class_level)s,%(ipc_scope)s,%(ipc_level)s,%(ipc_applied)s,%(ipc_office)s,%(ipc_type)s,%(ipc_rank)s,%(action_date)s)")

INSERTS["Cpc"] = (
    "INSERT INTO DW117_CPC_CLASS"
    "(PUBLN_ID, ACCESS_ID, CPC_CLASS,CPC_VERSION,CPC_CLASS_LEVEL,CPC_SCOPE,CPC_LEVEL,CPC_APPLIED,CPC_OFFICE,CPC_TYPE,CPC_RANK,CPC_ACTION_DATE)"
    "VALUE (%(publn_id)s,%(access_id)s,%(ipc_class)s,%(ipc_version)s,%(ipc_class_level)s,%(ipc_scope)s,%(ipc_level)s,%(ipc_applied)s,%(ipc_office)s,%(ipc_type)s,%(ipc_rank)s,%(action_date)s)")

INSERTS["ecla"] = (
    "INSERT INTO DW118_ECLA_CLASS"
    "(PUBLN_ID, ACCESS_ID, ECLA_CLASS,ECLA_TYPE)"
    "VALUE (%(publn_id)s,%(access_id)s,%(ecla_class)s,%(ecla_type)s)")

INSERTS["dwpi"] = (
    "INSERT INTO DW119_DWPI_CLASS"
    "(PUBLN_ID, ACCESS_ID, DWPI_CLASS,DWPI_SECTION,DWPI_FAMILY)"
    "VALUE (%(publn_id)s,%(access_id)s,%(ecla_class)s,%(ecla_type)s,%(family)s)")

INSERTS["manual"] = (
    "INSERT INTO DW120_MANUAL_CLASS"
    "(PUBLN_ID, ACCESS_ID, MANUAL_CLASS,MANUAL_SECTION,MANUAL_FAMILY)"
    "VALUE (%(publn_id)s,%(access_id)s,%(ecla_class)s,%(ecla_type)s,%(family)s)")

INSERTS["uspc"] = (
    "INSERT INTO DW121_USPC_CLASS"
    "(PUBLN_ID, ACCESS_ID, USPC_TYPE,USPC_MAIN,USPC_SUB)"
    "VALUE (%(publn_id)s,%(access_id)s,%(us_type)s,%(main)s,%(sub)s)")

INSERTS["jppc"] = (
    "INSERT INTO DW122_JPPC_CLASS"
    "(PUBLN_ID, ACCESS_ID, JPPC_MAIN,JPPC_TYPE,JPPC_RANK)"
    "VALUE (%(publn_id)s,%(access_id)s,%(main)s,%(type)s,%(rank)s)")

INSERTS["jp_fclass"] = (
    "INSERT INTO DW123_JP_FCLASS"
    "(PUBLN_ID, ACCESS_ID, JP_FTHEME,JP_FTERM)"
    "VALUE (%(publn_id)s,%(access_id)s,%(theme)s,%(term)s)")




################################################# ABSTRACTS #####################################

INSERTS["abstracts"] = (
    "INSERT INTO DW124_ABSTRACT_ORIG"
    "(PUBLN_ID, ACCESS_ID, ABSTRACT_TOTAL, ABS_LANG)"
    "VALUE (%(publn_id)s,%(access_id)s,%(abstract)s,%(lang)s)")

INSERTS["abstract_novelty"] = (
    "INSERT INTO DW125_ABSTRACT_NOVELTY"
    "(PUBLN_ID, ACCESS_ID, ABSTRACT_NOVELTY, IS_ALERT)"
    "VALUE (%(publn_id)s,%(access_id)s,%(novelty)s,%(alert)s)")

INSERTS["abstract_use"] = (
    "INSERT INTO DW126_ABSTRACT_USE"
    "(PUBLN_ID, ACCESS_ID, ABSTRACT_USE, IS_ALERT)"
    "VALUE (%(publn_id)s,%(access_id)s,%(novelty)s,%(alert)s)")

INSERTS["abstract_description"] = (
    "INSERT INTO DW127_ABSTRACT_DESCRIPTION"
    "(PUBLN_ID, ACCESS_ID, ABSTRACT_DESCRIPTION, IS_ALERT)"
    "VALUE (%(publn_id)s,%(access_id)s,%(novelty)s,%(alert)s)")

INSERTS["abstract_advantage"] = (
    "INSERT INTO DW128_ABSTRACT_ADVANTAGE"
    "(PUBLN_ID, ACCESS_ID, ABSTRACT_ADVANTAGE, IS_ALERT)"
    "VALUE (%(publn_id)s,%(access_id)s,%(novelty)s,%(alert)s)")

INSERTS["abstract_drawings"] = (
    "INSERT INTO DW129_ABSTRACT_DRAWINGS"
    "(PUBLN_ID, ACCESS_ID, ABSTRACT_DRAWINGS, IS_ALERT)"
    "VALUE (%(publn_id)s,%(access_id)s,%(novelty)s,%(alert)s)")

INSERTS["abstract_preferred"] = (
    "INSERT INTO DW130_ABSTRACT_OTHER_DOC"
    "(PUBLN_ID, ACCESS_ID, ABSTRACT_OTHER_DOC)"
    "VALUE (%(publn_id)s,%(access_id)s,%(novelty)s)")

INSERTS["abstract_tech_focus"] = (
    "INSERT INTO DW131_ABSTRACT_TECH_FOCUS"
    "(PUBLN_ID, ACCESS_ID, ABSTRACT_TECH_FOCUS,TECH_AREA)"
    "VALUE (%(publn_id)s,%(access_id)s,%(novelty)s,%(area)s)")

INSERTS["abstract_extension"] = (
    "INSERT INTO DW132_ABSTRACT_EXTENSION"
    "(PUBLN_ID, ACCESS_ID, ABSTRACT_EXTENSION)"
    "VALUE (%(publn_id)s,%(access_id)s,%(novelty)s)")

INSERTS["abstract_mech_action"] = (
    "INSERT INTO DW133_ABSTRACT_MECH_ACTION"
    "(PUBLN_ID, ACCESS_ID, ABSTRACT_MECH_ACTION, IS_ALERT)"
    "VALUE (%(publn_id)s,%(access_id)s,%(novelty)s,%(alert)s)")

INSERTS["abstract_activity"] = (
    "INSERT INTO DW134_ABSTRACT_ACTIVITY"
    "(PUBLN_ID, ACCESS_ID, ABSTRACT_ACTIVITY, IS_ALERT)"
    "VALUE (%(publn_id)s,%(access_id)s,%(novelty)s,%(alert)s)")

##################################### INDEXING + LINK CODES ######################################
INSERTS["polymer_terms"] = (
    "INSERT INTO DW140_POLYMER_INDEXING"
    "(PUBLN_ID, ACCESS_ID,PARA_NUM,STC_NUM,TIME_RNG,APPLIED,TERM_TYPE,TERM)"
    "VALUE (%(publn_id)s,%(access_id)s,%(para_num)s,%(sen_num)s,%(time_rng)s,%(applied)s,%(term_type)s,%(term)s)")

INSERTS["keywords"] = (
    "INSERT INTO DW141_KEYWORD_INDEXING"
    "(PUBLN_ID, ACCESS_ID,PARA_NUM,STC_NUM,RELEVANCE,APPLIED,TERM_TYPE,TERM,ROLE)"
    "VALUE (%(publn_id)s,%(access_id)s,%(para_num)s,%(sen_num)s,%(relevance)s,%(applied)s,%(term_type)s,%(term)s,%(role)s)")

INSERTS["chemical_codes"] = (
    "INSERT INTO DW142_CHEMICAL_CODES"
    "(PUBLN_ID, ACCESS_ID,SUBJECT,CARD_NUM,TIME_RNG,MARKUSH,REGISTRY,ROLE,APPLIED,TERM_TYPE,CODE)"
    "VALUE (%(publn_id)s,%(access_id)s,%(subject)s,%(card_n)s,%(time_rng)s,%(markush)s,%(registry)s,%(role)s,%(application)s,%(term_type)s,%(term)s)")

INSERTS["chemical_uncodes"] = (
    "INSERT INTO DW143_CHEMICAL_UNLINK_CODES"
    "(PUBLN_ID, ACCESS_ID,ROLE,APPLIED,TERM_TYPE,CODE)"
    "VALUE (%(publn_id)s,%(access_id)s,%(role)s,%(applied)s,%(term_type)s,%(term)s)")

INSERTS["polymer_code"] = (
    "INSERT INTO DW144_POLYMER_CODES"
    "(PUBLN_ID, ACCESS_ID,CARD_NUM,TIME_RNG,CODE)"
    "VALUE (%(publn_id)s,%(access_id)s,%(num_card)s,%(time_rng)s,%(code)s)")

INSERTS["polymer_serial"] = (
    "INSERT INTO DW145_POLYMER_SERIAL_KEYS"
    "(PUBLN_ID, ACCESS_ID,SERIAL_KEY)"
    "VALUE (%(publn_id)s,%(access_id)s,%(code)s)")


# In[33]:

#we just obtain the database and user we defined in the db_creation script
db_name=db_creation.DB_NAME
usr=db_creation.usr
pwd=db_creation.pwd


# In[35]:

def give_date(item,publn_id): #this function returns a date statement when it is an Element of the Tree
    date=None
    try:
        dt=item.find(".//{*}date").text
        fmt="%Y-%m-%d"
        if dt==None:
            date=None
        else:
            dat=datetime.strptime(dt,fmt)
            date=datetime.date(dat)
    except AttributeError:
        date=None
    except ValueError:
        if dt=="--":
            date=None
        else:
            dat=datetime.strptime(dt[:7],fmt[:5])
            _, monthdays = calendar.monthrange(dat.year, dat.month)
            if monthdays<dat.day:
                dt=datetime(dat.year,dat.month,monthdays)
                date=datetime.date(dt)
                write_log(name,i,j,"date Modified publn_id",publn_id,"KO")
    return(date)


def give_version(item,txt,publn_id): #this function returns a date statement when it is part of the Attributes of an Element
    date=None
    try:
        dt=item.attrib[zz+txt]
        fmt="%Y-%m-%d"
        if dt==None:
            date=None
        else:
            dat=datetime.strptime(dt,fmt)
            date=datetime.date(dat)
    except (AttributeError, KeyError):
        date=None
    except ValueError:
        if dt=="--":
            date=None
        else:
            dat=datetime.strptime(dt[:7],fmt[:5])
            _, monthdays = calendar.monthrange(dat.year, dat.month)
            if monthdays<dat.day:
                dt=datetime(dat.year,dat.month,monthdays)
                date=datetime.date(dt)
                write_log(name,i,j,"date Modified publn_id",publn_id,"KO")
    return(date)


# ## LOG-FILE function and characteristics
# 
# The following functions define the LOG-FILE which tracks all the extractions and dumps to MySQL and the "clearing" of OK fields when several extractions have taken place. File name, columns defined here.

# In[36]:

#some definitions:
log="derwent_ext_log.csv" #full path of the LOG where records will be stored
nl="\n" #just a newline definition
cm="," #just a comma definition
head="file_name,file,full_name,folder,tar_file,status,comments,oknok\n" #header of the document


#file=name of the file it is working on, should always be "name"
#folder= i from the first loop, coinciding with the years. should always be "i"
#tarfile= j from the second loop. Tarfile from which "file" is being extracted should always be "j"
#status=text strings
#comments=text strings
def write_log(filee,folder,tarfile,status,comments,oknok): 
    y_f=filee[9:-4]
    fil=filee[14:-4]
    
    if os.path.exists(log):
        with open(log,"a") as f:
            f.write(y_f+cm+fil+cm+filee+cm+folder+cm+tarfile+cm+status+cm+comments+cm+oknok+nl)

    else:
        f=open(log,"w")
        f.write(head)
        f.write(y_f+cm+fil+cm+filee+cm+folder+cm+tarfile+cm+status+cm+comments+cm+oknok+nl)
        f.close()
        #os.chmod(log,0777)
        
def clean_log():
    infile = open(log, 'r')
    output = open("copy.csv", 'w')
    writer = csv.writer(output)
    for row in csv.reader(infile):
        if row[7]!="ok":
            writer.writerow(row)
    infile.close()
    output.close()
    os.remove(log)
    os.rename("copy.csv",log)
    #os.chmod(log,0777)


# ## MISC
# These two misc. functions provide the Namespace and those elements of the tree we haven't parsed (finds unknowns)

# In[37]:


def parse_and_get_ns(filee):
    events = "start", "start-ns"
    root = None
    ns = {}
    for event, elem in ET.iterparse(filee, events):
        if event == "start-ns":
            if elem[0] in ns and ns[elem[0]] != elem[1]:
                raise KeyError("Duplicate prefix with different URI found.")
            ns[elem[0]] = "{%s}" % elem[1]
        elif event == "start":
            if root is None:
                root = elem
    return ET.ElementTree(root), ns

def get_unknowns(patent):
    global dict_fields
    tag_list=["accessions",
              "assignees",
              "literatureCitations",
              "publications",
              "applications",
              "priorities",
              "agents",
              "inventors",
              "titles",
              "titleEnhanced",
              "claimed",
              "relateds",
              "classificationIpcCurrent",
              "classificationIpc",
              "classificationCpcCurrent",
              "classificationCpc",
              "classificationEclaCurrent",
              "classificationJpCurrent",
              "classificationUsCurrent",
              "classificationDwpi",
              "abstracts",
              "abstractEnhanced",
              "abstractDocumentationImgRefs",
              "abstractImageRefs",
              "patentCitations",
              "keywordIndexing",
              "chemicalLinkCodes",
              "chemicalUnlinkCodes",
              "polymerIndexing",
              "polymerCodes",
              "abstractDocumentation",
              "citingPatents",
              "manualCodesChemical",
              "manualCodesEngineering",
              "manualCodesElectrical"]
    for child in patent:
        if child.tag[len(zz):] in tag_list:
            pass
        else:
            dict_fields[child.tag[len(zz):]]="not yet exported"


# #### From here on, each of the functions parses and writes on a variable the elements of the Tree that we are interested on. 

# ## Classifications
# 
# IPC and CPC classifications have two branches on the data "ipcClassification" and "ipcClassificationCurrent". From each of them we obtain different information which we summarize in one single table for IPC and one for CPC.
# 
# The rest of the classifications are more straightforward. These all come from the patent offices.

# In[38]:

def get_ipc(patent,publn_id,access_id,cl_typ):
    global data_Ipc
    global data_Cpc
    cl_typ_low=cl_typ.lower()
    ipcC=patent.find("./{*}classification"+cl_typ+"Current")
    ipcnC=patent.find("./{*}classification"+cl_typ)
    rank_dict={}
    type_dict={}
    if ipcnC==None:
        pass
    else:
        for ipc in ipcnC.iterfind("./{*}"+cl_typ_low):
            try:
                ipc_cod=ipc.text
            except (AttributeError, KeyError):
                ipc_cod=None
            try:
                typ=ipc.attrib[zz+"type"]
            except (AttributeError, KeyError):
                typ=None
            try:
                rank=ipc.attrib[zz+"rank"]
            except (AttributeError, KeyError):
                rank=None
            rank_dict[ipc_cod]=rank
            type_dict[ipc_cod]=typ
            
            if ipcC==None:
                data={}
                data={
                    "publn_id":publn_id,
                    "access_id":access_id,
                    "ipc_class":ipc_cod,
                    "ipc_version":None,
                    "ipc_class_level":None,
                    "ipc_scope":None,
                    "ipc_level":None,
                    "ipc_applied":None,
                    "ipc_office":None,
                    "ipc_type":typ,
                    "ipc_rank":rank,
                    "action_date":None
                }
                if cl_typ=="Ipc":
                    data_Ipc.append(data)
                else:
                    data_Cpc.append(data)
                #foo,status,comment,oknok=insert_to(cl_typ,data)
                #write_log(name,i,j,status,comment,oknok)
                
            else:
                continue
    if ipcC==None:
        pass       
    else:
        for ipc in ipcC.iterfind("./{*}"+cl_typ_low):
            try:
                ipc_code=ipc.text
            except (AttributeError, KeyError):
                ipc_code=None
            ipc_version=give_version(ipc,"version",publn_id)
            ipc_action=give_version(ipc,"actionDate",publn_id)
            try:
                class_level=ipc.attrib[zz+"classLevel"]
            except (AttributeError, KeyError):
                class_level=None
            try:
                scope=ipc.attrib[zz+"scope"]
            except (AttributeError, KeyError):
                scope=None
            try:
                level=ipc.attrib[zz+"level"]
            except (AttributeError, KeyError):
                level=None
            try:
                applied=ipc.attrib[zz+"applied"]
            except (AttributeError, KeyError):
                applied=None
            try:
                office=ipc.attrib[zz+"office"]
            except (AttributeError, KeyError):
                office=None
            try:
                rank=rank_dict[ipc_code]
            except KeyError:
                rank=None
            try:
                typp=type_dict[ipc_code]
            except KeyError:
                typp=None
            
            data={}
            data={
                "publn_id":publn_id,
                "access_id":access_id,
                "ipc_class":ipc_code,
                "ipc_version":ipc_version,
                "ipc_class_level":class_level,
                "ipc_scope":scope,
                "ipc_level":level,
                "ipc_applied":applied,
                "ipc_office":office,
                "ipc_type":typp,
                "ipc_rank":rank,
                "action_date":ipc_action
            }
            if cl_typ=="Ipc":
                data_Ipc.append(data)
            else:
                data_Cpc.append(data)
            #foo,status,comment,oknok=insert_to(cl_typ,data)
            #write_log(name,i,j,status,comment,oknok)

def get_ecla(patent,publn_id,access_id):
    global data_ecla
    ec=patent.find("./{*}classificationEclaCurrent")
    if ec==None:
        pass
    else:
        for child in ec:
            try:
                ecla_class=child.text
            except AttributeError:
                ecla_class=None
            try:
                ecla_type=child.tag[len(zz):]
            except (AttributeError,KeyError):
                ecla_type=None
            data={}
            data={
                "publn_id":publn_id,
                "access_id":access_id,
                "ecla_type":ecla_type,
                "ecla_class":ecla_class
            }
            data_ecla.append(data)
            #foo,status,comment,oknok=insert_to("ecla",data)
            #write_log(name,i,j,status,comment,oknok)
            
def get_dwpi(patent,publn_id,access_id):
    global data_dwpi
    ec=patent.find("./{*}classificationDwpi")
    if ec==None:
        pass
    else:
        for child_class in ec:
            for child in child_class:
                ecla_class=child.text
                family=child.tag[len(zz)+5:]
                ecla_type=child.attrib[zz+"section"]
                data={}
                data={
                    "publn_id":publn_id,
                    "access_id":access_id,
                    "ecla_type":ecla_type,
                    "family":family,
                    "ecla_class":ecla_class
                }
                data_dwpi.append(data)
                #foo,status,comment,oknok=insert_to("dwpi",data)
                #write_log(name,i,j,status,comment,oknok)  

            
def get_uspc(patent,publn_id,access_id):
    global data_uspc
    ec=patent.find("./{*}classificationUsCurrent")
    if ec==None:
        pass
    else:
        for uspc in patent.iterfind("./{*}classificationUsCurrent/{*}uspc"):
            try:
                us_type=uspc.attrib[zz+"type"]
            except KeyError:
                us_type=None
            try:
                main=uspc.find("./{*}mainclass").text
            except AttributeError:
                main=None
            try:
                sub=uspc.find("./{*}subclass").text
            except AttributeError:
                sub=None

            data={}
            data={
                "publn_id":publn_id,
                "access_id":access_id,
                "us_type":us_type,
                "main":main,
                "sub":sub
            }
            data_uspc.append(data)
            #foo,status,comment,oknok=insert_to("uspc",data)
            #write_log(name,i,j,status,comment,oknok)
                
                
def get_jppc(patent,publn_id,access_id):
    global data_jppc
    global data_jp_fclass
    ec=patent.find("./{*}classificationJpCurrent")
    if ec==None:
        pass
    else:
        for uspc in patent.iterfind("./{*}classificationJpCurrent/{*}jppc"):
            try:
                main=uspc.text
            except AttributeError:
                main=None
            try:
                typ=uspc.attrib[zz+"type"]
            except KeyError:
                typ=None
            try:
                rank=uspc.attrib[zz+"rank"]
            except KeyError:
                rank=None
            data={}
            data={
                "publn_id":publn_id,
                "access_id":access_id,
                "main":main,
                "type":typ,
                "rank":rank
            }
            data_jppc.append(data)
            #foo,status,comment,oknok=insert_to("jppc",data)
            #write_log(name,i,j,status,comment,oknok) 
            
            
        for fclass in patent.iterfind("./{*}classificationJpCurrent/{*}fClass"):
            try:
                theme=fclass.find("./{*}theme").text
            except AttributeError:
                theme=None
            try:
                term=fclass.find("./{*}fTerm").text
            except AttributeError:
                term=None

            data={}
            data={
                "publn_id":publn_id,
                "access_id":access_id,
                "theme":theme,
                "term":term
            }
            data_jp_fclass.append(data)
            #foo,status,comment,oknok=insert_to("jp_fclass",data)
            #write_log(name,i,j,status,comment,oknok) 


# ## ABSTRACT
# 
# Abstract classification is not trivial. There are three main fields: abstracts, abstractEnhanced and abstractDocumentation. The last two contain expanded information (Novelty, Use, Advantage...) which is usually present in both, when they coexist. Thus, we generate one table for "abstracts" (in general) and one for each of the attributes that we find under "abstractEnhanced" and "abstractDocumentation". This is what adds value in the DWPI.
# 
# Additionally, abstractEnhanced has different subtrees which we take into account (dates are approximate; * stands for novelty, use, etc. ):
# In 1990's data, we observe a subElement "abstractCoreAscii" with further children named "alert*"
# In 2010's data, we observe TWO subElements "abstractCoreAscii" + "abstractCore", with furhter children named "*Ascii" or "*" respectively. These two subelements contain the same information in different formats.
# AbstractEnhancedCore covers the following:
# - novelty
# - use
# - description
# - advantage
# - activity
# - mechanism of action
# - description of drawings
# 
# Official documentation states: "During 1999/2000, important changes were introduced to the structure and content of these abstracts. The abstracts are still written in plain English, removing unnecessary wordiness and legal jargon found in the original, but now contain more detail than before. As well as containing improved technical content, the abstracts also make use of several informative paragraph headings, which make the description of the invention easier to read. The new abstracts began to be produced by Derwent in February 1999."
# 
# AbstractEnhanced also have two subElements called <b>TechFocus</b> and <b>Extension</b> which we include in separate tables.
# - TechFocus provides technology specific areas, preferred methods and materials and headings which are easy to scan.
# - Extension provides a wider disclosure (inventions not covered in claim), Specific Substances, Examples, Definitions,  and administration (dose for chemical compounds).
# 
# We extract only Ascii information, since it's parsed in a more easy-to-read way in the xml files, and raise the exception for the "alert" cases.
# 
# "abstractDocumentation", in the observed cases, has the same information than the previous, and adds a field called "preferredDoc" which we extract as a separate table. For the "alertAbstracts", according to the documentation, it provides an extended abstract, which is not extracted here (only if the other are missing while this one isn't).

# In[39]:

def get_abstract(patent,publn_id,access_id):
    global data_abstracts
    global data_abstract_novelty
    global data_abstract_use
    global data_abstract_advantage
    global data_abstract_description
    global data_abstract_drawings
    global data_abstract_preferred
    global data_abstract_tech_focus
    global data_abstract_extension
    global data_abstract_mech_action
    global data_abstract_activity
    abst=patent.find("./{*}abstracts")
    abstE=patent.find("./{*}abstractEnhanced")
    abstD=patent.find("./{*}abstractDocumentation")
    if abst==None:
        pass
    else:
        abstracten=abst.find("./{*}abstract[@"+zz+'lang="en"]')
        if abstracten==None:
            abstractfr=abst.find("./{*}abstract[@"+zz+'lang="fr"]')
            if abstractfr==None:
                pass
            else:
                lang="fr"
                abstxt="".join(abstractfr.itertext())
                data={}
                data={
                    "publn_id":publn_id,
                    "access_id":access_id,
                    "abstract":abstxt,
                    "lang":lang
                }
                data_abstracts.append(data)
                #foo,status,comment,oknok=insert_to("abstracts",data)
                #write_log(name,i,j,status,comment,oknok)
                                      
        else:
            lang="en"
            abstxt="".join(abstracten.itertext())
            data={}
            data={
                "publn_id":publn_id,
                "access_id":access_id,
                "abstract":abstxt,
                "lang":lang
            }
            data_abstracts.append(data)
            #foo,status,comment,oknok=insert_to("abstracts",data)                
            #write_log(name,i,j,status,comment,oknok)
                
    if abstE==None:
        pass
    else:
        absAscii=abstE.find("./{*}abstractCoreAscii")
        #absnoAscii=asbtE.find("./{*}abstractCore")
################################################ NOVELTY #########################
        try:
            alert="no"
            novelt=absAscii.find("./{*}noveltyAscii")
            novelty="".join(novelt.itertext())
            data={}
            data={
                "publn_id":publn_id,
                "access_id":access_id,
                "novelty":novelty,
                "alert":alert
            }
            data_abstract_novelty.append(data)
            #foo,status,comment,oknok=insert_to("abstract_novelty",data)
            #write_log(name,i,j,status,comment,oknok)
        except AttributeError:
            try:
                alert="yes"
                novelt=absAscii.find("./{*}alertAscii/{*}firstSectionAlertAscii")
                novelty="".join(novelt.itertext())
                data={}
                data={
                    "publn_id":publn_id,
                    "access_id":access_id,
                    "novelty":novelty,
                    "alert":alert
                }
                data_abstract_novelty.append(data)
                #foo,status,comment,oknok=insert_to("abstract_novelty",data)
                #write_log(name,i,j,status,comment,oknok)
            except AttributeError:
                try:
                    alert="DOC"
                    novelt=abstD.find("./{*}firstSectionDoc")
                    novelty="".join(novelt.itertext())
                    data={}
                    data={
                        "publn_id":publn_id,
                        "access_id":access_id,
                        "novelty":novelty,
                        "alert":alert
                    }
                    data_abstract_novelty.append(data)
                    #foo,status,comment,oknok=insert_to("abstract_novelty",data)
                    #write_log(name,i,j,status,comment,oknok)
                except AttributeError:
                    pass
            
################################# USE ##############################
        try:
            alert="no"
            novelt=absAscii.find("./{*}useAscii")
            novelty="".join(novelt.itertext())
            data={}
            data={
                "publn_id":publn_id,
                "access_id":access_id,
                "novelty":novelty,
                "alert":alert
            }
            data_abstract_use.append(data)
            #foo,status,comment,oknok=insert_to("abstract_use",data)
            #write_log(name,i,j,status,comment,oknok)
        except AttributeError:
            try:
                alert="yes"
                novelt=absAscii.find("./{*}alertAscii/{*}useAlertAscii")
                novelty="".join(novelt.itertext())
                data={}
                data={
                    "publn_id":publn_id,
                    "access_id":access_id,
                    "novelty":novelty,
                    "alert":alert
                }
                data_abstract_use.append(data)
                #foo,status,comment,oknok=insert_to("abstract_use",data)
                #write_log(name,i,j,status,comment,oknok)
            except AttributeError:
                try:
                    alert="DOC"
                    novelt=abstD.find("./{*}useDoc")
                    novelty="".join(novelt.itertext())
                    data={}
                    data={
                        "publn_id":publn_id,
                        "access_id":access_id,
                        "novelty":novelty,
                        "alert":alert
                    }
                    data_abstract_use.append(data)
                    #foo,status,comment,oknok=insert_to("abstract_novelty",data)
                    #write_log(name,i,j,status,comment,oknok)
                except AttributeError:
                    pass
            
################################# ADVANTAGE ##############################
        try:
            alert="no"
            novelt=absAscii.find("./{*}advantageAscii")
            novelty="".join(novelt.itertext())
            data={}
            data={
                "publn_id":publn_id,
                "access_id":access_id,
                "novelty":novelty,
                "alert":alert
            }
            data_abstract_advantage.append(data)
            #foo,status,comment,oknok=insert_to("abstract_advantage",data)
            #write_log(name,i,j,status,comment,oknok)
        except AttributeError:
            try:
                alert="yes"
                novelt=absAscii.find("./{*}alertAscii/{*}advantageAlertAscii")
                novelty="".join(novelt.itertext())
                data={}
                data={
                    "publn_id":publn_id,
                    "access_id":access_id,
                    "novelty":novelty,
                    "alert":alert
                }
                data_abstract_advantage.append(data)
                #foo,status,comment,oknok=insert_to("abstract_advantage",data)
                #write_log(name,i,j,status,comment,oknok)
            except AttributeError:
                try:
                    alert="DOC"
                    novelt=abstD.find("./{*}advantageDoc")
                    novelty="".join(novelt.itertext())
                    data={}
                    data={
                        "publn_id":publn_id,
                        "access_id":access_id,
                        "novelty":novelty,
                        "alert":alert
                    }
                    data_abstract_advantage.append(data)
                    #foo,status,comment,oknok=insert_to("abstract_novelty",data)
                    #write_log(name,i,j,status,comment,oknok)
                except AttributeError:
                    pass
                
################################# ACTIVITY ##############################
        try:
            alert="no"
            novelt=absAscii.find("./{*}activityAscii")
            novelty="".join(novelt.itertext())
            data={}
            data={
                "publn_id":publn_id,
                "access_id":access_id,
                "novelty":novelty,
                "alert":alert
            }
            data_abstract_activity.append(data)
            #foo,status,comment,oknok=insert_to("abstract_activity",data)
            #write_log(name,i,j,status,comment,oknok)
        except AttributeError:
            try:
                alert="yes"
                novelt=absAscii.find("./{*}alertAscii/{*}activityAlertAscii")
                novelty="".join(novelt.itertext())
                data={}
                data={
                    "publn_id":publn_id,
                    "access_id":access_id,
                    "novelty":novelty,
                    "alert":alert
                }
                data_abstract_activity.append(data)
                #foo,status,comment,oknok=insert_to("abstract_activity",data)
                #write_log(name,i,j,status,comment,oknok)
            except AttributeError:
                try:
                    alert="DOC"
                    novelt=abstD.find("./{*}activityDoc")
                    novelty="".join(novelt.itertext())
                    data={}
                    data={
                        "publn_id":publn_id,
                        "access_id":access_id,
                        "novelty":novelty,
                        "alert":alert
                    }
                    data_abstract_activity.append(data)
                    #foo,status,comment,oknok=insert_to("abstract_activity",data)
                    #write_log(name,i,j,status,comment,oknok)
                except AttributeError:
                    pass
################################# MECHANISM OF ACTION ##############################
        try:
            alert="no"
            novelt=absAscii.find("./{*}mechanismOfActionAscii")
            novelty="".join(novelt.itertext())
            data={}
            data={
                "publn_id":publn_id,
                "access_id":access_id,
                "novelty":novelty,
                "alert":alert
            }
            data_abstract_mech_action.append(data)
            #foo,status,comment,oknok=insert_to("abstract_mech_action",data)
            #write_log(name,i,j,status,comment,oknok)
        except AttributeError:
            try:
                alert="yes"
                novelt=absAscii.find("./{*}alertAscii/{*}mechanismOfActionAlertAscii")
                novelty="".join(novelt.itertext())
                data={}
                data={
                    "publn_id":publn_id,
                    "access_id":access_id,
                    "novelty":novelty,
                    "alert":alert
                }
                data_abstract_mech_action.append(data)
                #foo,status,comment,oknok=insert_to("abstract_mech_action",data)
                #write_log(name,i,j,status,comment,oknok)
            except AttributeError:
                try:
                    alert="DOC"
                    novelt=abstD.find("./{*}mechanismOfActionDoc")
                    novelty="".join(novelt.itertext())
                    data={}
                    data={
                        "publn_id":publn_id,
                        "access_id":access_id,
                        "novelty":novelty,
                        "alert":alert
                    }
                    data_abstract_mech_action.append(data)
                    #foo,status,comment,oknok=insert_to("abstract_mech_action",data)
                    #write_log(name,i,j,status,comment,oknok)
                except AttributeError:
                    pass
            
################################# DRAWINGS ##############################
        try:
            alert="no"
            novelt=absAscii.find("./{*}descriptionOfDrawingsAscii")
            novelty="".join(novelt.itertext())
            data={}
            data={
                "publn_id":publn_id,
                "access_id":access_id,
                "novelty":novelty,
                "alert":alert
            }
            data_abstract_drawings.append(data)
            #foo,status,comment,oknok=insert_to("abstract_drawings",data)
            #write_log(name,i,j,status,comment,oknok)
        except AttributeError:
            try:
                alert="yes"
                novelt=absAscii.find("./{*}alertAscii/{*}descriptionOfDrawingsAlertAscii")
                novelty="".join(novelt.itertext())
                data={}
                data={
                    "publn_id":publn_id,
                    "access_id":access_id,
                    "novelty":novelty,
                    "alert":alert
                }
                data_abstract_drawings.append(data)
                #foo,status,comment,oknok=insert_to("abstract_drawings",data)
                #write_log(name,i,j,status,comment,oknok)
            except AttributeError:
                pass

            
################################# DESCRIPTION ##############################
        try:
            alert="no"
            novelt=absAscii.find("./{*}descriptionAscii")
            novelty="".join(novelt.itertext())
            data={}
            data={
                "publn_id":publn_id,
                "access_id":access_id,
                "novelty":novelty,
                "alert":alert
            }
            data_abstract_description.append(data)
            #foo,status,comment,oknok=insert_to("abstract_description",data)
            #write_log(name,i,j,status,comment,oknok)
        except AttributeError:
            try:
                alert="yes"
                novelt=absAscii.find("./{*}alertAscii/{*}descriptionAlertAscii")
                novelty="".join(novelt.itertext())
                data={}
                data={
                    "publn_id":publn_id,
                    "access_id":access_id,
                    "novelty":novelty,
                    "alert":alert
                }
                data_abstract_description.append(data)
                #foo,status,comment,oknok=insert_to("abstract_description",data)
                #write_log(name,i,j,status,comment,oknok)
            except AttributeError:
                try:
                    alert="DOC"
                    novelt=abstD.find("./{*}descriptionDoc")
                    novelty="".join(novelt.itertext())
                    data={}
                    data={
                        "publn_id":publn_id,
                        "access_id":access_id,
                        "novelty":novelty,
                        "alert":alert
                    }
                    data_abstract_description.append(data)
                    #foo,status,comment,oknok=insert_to("abstract_novelty",data)
                    #write_log(name,i,j,status,comment,oknok)
                except AttributeError:
                    pass
                
################################# TECH FOCUS ##############################

        absTF=abstE.find("./{*}abstractTechFocusAscii")
        if absTF==None:
            pass
        else:
            for areaTF in absTF:
                try:
                    area=areaTF.attrib[zz+"heading"]
                except KeyError:
                    area=None
                try:
                    novelty="".join(areaTF.itertext())
                    data={}
                    data={
                        "publn_id":publn_id,
                        "access_id":access_id,
                        "novelty":novelty,
                        "area":area
                    }
                    data_abstract_tech_focus.append(data)
                    #foo,status,comment,oknok=insert_to("abstract_drawings",data)
                    #write_log(name,i,j,status,comment,oknok)
                except AttributeError:
                    pass
################################# EXTENSION ##############################

        absEX=abstE.find("./{*}abstractExtensionAscii")
        if absEX==None:
            pass
        else:
            for example in absEX:
                ext_type=example.tag[len(zz):-5]
                try:
                    novelty="".join(example.itertext())
                    data={}
                    data={
                        "publn_id":publn_id,
                        "access_id":access_id,
                        "novelty":novelty,
                        "extension_type":ext_type
                    }
                    data_abstract_extension.append(data)
                    #foo,status,comment,oknok=insert_to("abstract_drawings",data)
                    #write_log(name,i,j,status,comment,oknok)
                except AttributeError:
                    pass
                
                
########################################## OTHER DOCUMENTATION #########################
    if abstD==None:
        pass
    else:
        for subclass in abstD:
            extracted=["descriptionDoc","useDoc","advantageDoc","noveltyDoc","mechanismOfActionDoc","activityDoc"]
            if subclass.tag[len(zz):] in extracted:
                pass
            else:
                try:
                    novelty="".join(subclass.itertext())
                    data={}
                    data={
                        "publn_id":publn_id,
                        "access_id":access_id,
                        "novelty":novelty
                        }
                    data_abstract_preferred.append(data)
                    #foo,status,comment,oknok=insert_to("abstract_novelty",data)
                    #write_log(name,i,j,status,comment,oknok)
                except AttributeError:
                    pass


# ## Title and claim
# There are two sorts of titles <b>Titles</b> and <b>TitlesEnhanced</b>. Whenever titleEnhanced is available, we provide it. DWPI provides the enhancment with this features (advantages over the original title):
# - In English
# - Rewritten to cover: <b>Scope</b>, <b>Use</b>, <b>Novelty</b>
# - Title terms automated generation.
# 
# However:
# - titleEnhanced is not the title on the patent
# - Original title only extracted if available in English or French
# 
# Claims only extracted if in English or French.

# In[40]:

def get_tit(patent,publn_id,access_id):
    global data_publn_tit
    global data_tit_terms
    tit=patent.find("./{*}titles")
    titE=patent.find("./{*}titleEnhanced")
    if titE==None:
        if tit==None:
            pass
        else:
            try:
                title=tit.find("./{*}title[@"+zz+'lang="en"]').text
            except AttributeError:
                title=None
            if title==None:
                try:
                    title=tit.find("./{*}title[@"+zz+'lang="fr"]').text
                except AttributeError:
                    title=None
                if title==None:
                    pass
                else:
                    is_enhanced="n"
                
                    data={}
                    data={
                        "publn_id":publn_id,
                        "publn_tit":title,
                        "is_enhanced":is_enhanced
                    }
                    data_publn_tit.append(data)
                    #foo,status,comment,oknok=insert_to("publn_tit",data)
                    #write_log(name,i,j,status,comment,oknok)
                
            else:
                is_enhanced="n"
                
                data={}
                data={
                    "publn_id":publn_id,
                    "publn_tit":title,
                    "is_enhanced":is_enhanced
                }
                data_publn_tit.append(data)
                #foo,status,comment,oknok=insert_to("publn_tit",data)
                #write_log(name,i,j,status,comment,oknok)
                
    else:
        title=""
        for titlepart in titE.iterfind("./{*}titleAscii[@"+zz+'lang="en"]/{*}titlePartAscii'):
            title=title+titlepart.text
        
        is_enhanced="y"
                        
        data={}
        data={
            "publn_id":publn_id,
            "publn_tit":title,
            "is_enhanced":is_enhanced,            
        }
        
        tit_terms=titE.find("./{*}titleAscii/{*}titleTerms/{*}titleTermsStandard")
        if tit_terms==None:
            pass
        else:
            for term in tit_terms.iterfind("./{*}titleTerm"):
                tit_term=term.text
                data2={}
                data2={
                    "publn_id":publn_id,
                    "access_id":access_id,
                    "tit_term":tit_term            
                }
                data_tit_terms.append(data2)
                #foo,status,comment,oknok=insert_to("tit_terms",data2)
                #write_log(name,i,j,status,comment,oknok)
            
            
        data_publn_tit.append(data)
        #foo,status,comment,oknok=insert_to("publn_tit",data)
        #write_log(name,i,j,status,comment,oknok)

        
def get_claims(patent,publn_id,access_id):
    global data_claims
    claim=patent.find("./{*}claimed/{*}claims[@"+zz+'lang="en"]/{*}claim')
    claimfr=patent.find("./{*}claimed/{*}claims[@"+zz+'lang="fr"]/{*}claim')
    if claim==None:
        if claimfr==None:
            pass
        else:
            claimtxt="".join(claimfr.itertext())
            data={}
            data={
                "publn_id":publn_id,
                "access_id":access_id,
                "publn_claim":claimtxt
            }
            data_claims.append(data)
            #foo,status,comment,oknok=insert_to("claims",data)
            #write_log(name,i,j,status,comment,oknok)
            
    else:
        claimtxt="".join(claim.itertext())
        data={}
        data={
            "publn_id":publn_id,
            "access_id":access_id,
            "publn_claim":claimtxt
        }
        data_claims.append(data)
        #foo,status,comment,oknok=insert_to("claims",data)
        #write_log(name,i,j,status,comment,oknok)



# ## Codes (chemicalLink, chemicalUnlink, Polymer and manual)
# *Codes different from ManualCodes and Indexing, which are provided by DWPI experts.
# 
# These codes, however, provide markush structures (i.e. structures having generic or variable components) which are widely used in chemical and pharmaceutical patents to protect a series of related compounds within a single invention. Pharmaceutical companies typically use Markush structures in patents to obtain strong protection of potential new drugs.
# 
# Read more about Markush here: https://www.ncbi.nlm.nih.gov/pubmed/27123583
# 
# Meaning of each code and it's classification is beyond this extraction, and can be found here: http://ip-science.thomsonreuters.com/m/pdfs/mgr/chemindguide.pdf
# 
# Manual Codes are alphanumeric codes that appear similar to Chemical Codes. Each Manual Code represents a term in a hierarchical controlled term vocabulary. While the Chemical Codes are designed to determine if certain chemical structures are present among the thousands or millions of compounds claimed or disclosed in a chemical patent, Manual Codes are most useful for general classification of patented compounds, reactions, and uses. Manual codes are, thus:
# - Three kinds: <b>Electrical</b>, <b>Chemical</b>, <b>Engineering</b>
# - hierarchical
# - intellectually applied based on patent content and specialist's knowledge
# - novelty of invention and applications
# 
# 
# There are different kinds of codes accross time periods, as explained in the documents linked above: punchCards (pre 1981 week 27) vs. keySeries.
# Also different "code types": SCN (Specific Compound Numbers), code (cardRecord, inherited from old nomenclature), dcr.

# In[41]:

def get_chem_codes(patent,publn_id,access_id):
    global data_chem_codes
    chco=patent.find("./{*}chemicalLinkCodes")
    if chco==None:
        pass
    else:
        for subh in patent.iterfind("./{*}chemicalLinkCodes/{*}chemicalCodeSubheading"):
            try:
                subject=subh.attrib[zz+"subject"]
            except KeyError:
                subject=None
            for card in subh.iterfind("./{*}cardRecord"):
                try:
                    num_c=card.attrib[zz+"no"]
                except KeyError:
                    num_c=None
                try:
                    tr=card.attrib[zz+"timeRange"]
                except KeyError:
                    tr=None
                try:
                    markush=card.attrib[zz+"markush"]
                except KeyError:
                    markush=None
                try:
                    reg=card.attrib[zz+"registry"]
                except KeyError:
                    reg=None
                
                cod=card.find("./{*}chemicalCodes")
                scns=card.find("./{*}specificCompoundNumbers")
                dcr=card.find("./{*}dcrNumbers")
                
                if cod==None:
                    pass
                else:
                    for code in cod.iterfind("./{*}code"):
                        term_type="code"
                        try:                                
                            app=code.attrib[zz+"applied"]
                        except KeyError:
                            app=None
                        try:                                
                            role=code.attrib[zz+"role"]
                        except KeyError:
                            role=None
                        try:
                            term=code.text
                        except AttributeError:
                            term=None
                            
                        data={}
                        data={
                            "publn_id":publn_id,
                            "access_id":access_id,
                            "subject":subject,
                            "card_n":num_c,
                            "time_rng":tr,
                            "markush":markush,
                            "registry":reg,
                            "term_type":term_type,
                            "application":app,
                            "role":role,
                            "term":term
                        }
                        data_chemical_codes.append(data)
                        #foo,status,comment,oknok=insert_to("chemical_codes",data)                
                        #write_log(name,i,j,status,comment,oknok)
                        
                if scns==None:
                    pass
                else:
                    for code in cod.iterfind("./{*}scnsDerwent/{*}scnDerwent"):
                        term_type="scn"
                        try:                                
                            app=code.attrib[zz+"applied"]
                        except KeyError:
                            app=None
                        try:                                
                            role=code.attrib[zz+"role"]
                        except KeyError:
                            role=None
                        try:
                            term=code.text
                        except AttributeError:
                            term=None
                            
                        data={}
                        data={
                            "publn_id":publn_id,
                            "access_id":access_id,
                            "subject":subj,
                            "card_n":num_c,
                            "time_rng":tr,
                            "markush":markush,
                            "registry":reg,
                            "term_type":term_type,
                            "application":app,
                            "role":role,
                            "term":term
                        }
                        data_chemical_codes.append(data)
                        #foo,status,comment,oknok=insert_to("chemical_codes",data)                
                        #write_log(name,i,j,status,comment,oknok)
                if dcr==None:
                    pass
                else:
                    for code in cod.iterfind("./{*}dcrNumbers"):
                        term_type="dcr"
                        try:                                
                            app=code.attrib[zz+"applied"]
                        except KeyError:
                            app=None
                        try:                                
                            role=code.attrib[zz+"role"]
                        except KeyError:
                            role=None
                        try:
                            term=code.text
                        except AttributeError:
                            term=None
                            
                        data={}
                        data={
                            "publn_id":publn_id,
                            "access_id":access_id,
                            "subject":subj,
                            "card_n":num_c,
                            "time_rng":tr,
                            "markush":markush,
                            "registry":reg,
                            "term_type":term_type,
                            "application":app,
                            "role":role,
                            "term":term
                        }
                        data_chemical_codes.append(data)
                        #foo,status,comment,oknok=insert_to("chemical_codes",data)                
                        #write_log(name,i,j,status,comment,oknok)

def get_chem_un_codes(patent,publn_id,access_id):
    global data_chemical_uncodes
    chunl=patent.find("./{*}chemicalUnlinkCodes")
    if chunl==None:
        pass
    else:
        for unlinks in chunl:
            cod_type=unlinks.tag[len(zz)+6:-7]
            for code in unlinks:
                try:                                
                    app=code.attrib[zz+"applied"]
                except KeyError:
                    app=None
                try:                                
                    role=code.attrib[zz+"role"]
                except KeyError:
                    role=None
                try:
                    term=code.text
                except AttributeError:
                    term=None
                data={}
                data={
                    "publn_id":publn_id,
                    "access_id":access_id,
                    "term_type":cod_type,
                    "applied":app,
                    "role":role,
                    "term":term
                    
                }
                data_chemical_uncodes.append(data)
                #foo,status,comment,oknok=insert_to("chemical_uncodes",data)                
                #write_log(name,i,j,status,comment,oknok)
                
def get_polymer_codes(patent,publn_id,access_id):
    global data_polymer_code
    global data_polymer_serial
    polyc=patent.find("./{*}polymerCodes")
    
    if polyc==None:
        pass
    else:
        pc=polyc.find("./{*}multiPunchCard")
        ks=polyc.find("./{*}keySerials")
        if pc==None:
            pass
        else:
            for multi in polyc.iterfind("./{*}multiPunchCard"):
                try:
                    num=multi.attrib[zz+"no"]
                except KeyError:
                    num_c=None
                try:
                    tr=multi.attrib[zz+"timeRange"]
                except KeyError:
                    tr=None
                for code in multi:
                    term=code.text
                    data={}
                    data={
                        "publn_id":publn_id,
                        "access_id":access_id,
                        "num_card":num,
                        "time_rng":tr,
                        "code":term
                    }
                    data_polymer_code.append(data)
                    #foo,status,comment,oknok=insert_to("polymer_code",data)                
                    #write_log(name,i,j,status,comment,oknok)
        if ks==None:
            pass
        else:
            for serial in ks:
                try:
                    term=serial.text
                except AttributeError:
                    term=None
                data={}
                data={
                    "publn_id":publn_id,
                    "access_id":access_id,
                    "code":term
                  }
                data_polymer_serial.append(data)
                #foo,status,comment,oknok=insert_to("polymer_serial",data)                
                #write_log(name,i,j,status,comment,oknok)
                
                
def get_manual(patent,publn_id,access_id):
    global data_manual
    for fam in ["Chemical","Engineering","Electrical"]:
        ec=patent.find("./{*}manualCodes"+fam)
        if ec==None:
            pass
        else:
            for child2 in ec:
                ecla_type=child2.attrib[zz+"section"]
                for child3 in child2:
                    ecla_class=child3.text
        
                    data={}
                    data={
                        "publn_id":publn_id,
                        "access_id":access_id,
                        "ecla_type":ecla_type,
                        "family":fam,
                        "ecla_class":ecla_class
                     }
                data_manual.append(data)
                #foo,status,comment,oknok=insert_to("manual",data)
                #write_log(name,i,j,status,comment,oknok)



# ## Indexing
# Also generated by Derwent, similar to codes but extends in order to:
# - define specific novelties of chemical structures
# - separate into chemical fragments that translate to chem codes
# - hierarchical
# - includes formulae and activity coding
# - covers all chem compounds listed in a document.
# 
# Polymer Indexing organized by paragraphs -> sentences -> phrases ->terms
# 
# Keyworkd indexing is used in the industry for search. Before a patent is assigned Chemical Codes, it is entered into the DWPI database with indexing terms that can be assigned more quickly than the Chemical Codes.

# In[42]:

def get_pol_indexing(patent,publn_id,access_id):
    global data_polymer_terms
    polix=patent.find("./{*}polymerIndexing")
    if polix==None:
        pass
    else:
        for para in polix.iterfind("./{*}polymerPara"):
            try:
                num=para.attrib[zz+"no"]
            except KeyError:
                num=None
            for sent in para.iterfind("./{*}polymerSentence"):
                try:
                    tr=sent.attrib[zz+"timeRange"]
                except KeyError:
                    tr=None
                try:
                    num_s=sent.attrib[zz+"no"]
                except KeyError:
                    num_s=None
                for phrase in sent.iterfind("./{*}polymerPhrase"):
                    trm=phrase.find("./{*}polymerTerms")
                    scns=phrase.find("./{*}scnsDerwent")
                    drc=phrase.find("./{*}drcNumbers")
                    if trm==None:
                        pass
                    else:
                        for terms in phrase.iterfind("./{*}polymerTerms/{*}term"):
                            term_type="term"
                            try:
                                app=terms.attrib[zz+"applied"]
                            except KeyError:
                                app=None
                            try:
                                term=terms.text
                            except AttributeError:
                                term=None
                                
                            data={}
                            data={
                                "publn_id":publn_id,
                                "access_id":access_id,
                                "para_num":num,
                                "sen_num":num_s,
                                "time_rng":tr,
                                "term":term,
                                "applied":app,
                                "term_type":term_type
                            }
                            data_polymer_terms.append(data)
                            #foo,status,comment,oknok=insert_to("polymer_terms",data)
                            #write_log(name,i,j,status,comment,oknok)
                        
                    if scns==None:
                        pass
                    else:
                        for terms in phrase.iterfind("./{*}scnsDerwent/scnDerwent"):
                            term_type="scnDerwent"
                            try:
                                app=terms.attrib[zz+"applied"]
                            except KeyError:
                                app=None
                            try:
                                term=terms.text
                            except AttributeError:
                                term=None
                                
                            data={}
                            data={
                                "publn_id":publn_id,
                                "access_id":access_id,
                                "para_num":num,
                                "sen_num":num_s,
                                "time_rng":tr,
                                "term":term,
                                "applied":app,
                                "term_type":term_type
                            }
                            data_polymer_terms.append(data)
                            #foo,status,comment,oknok=insert_to("polymer_terms",data)                
                            #write_log(name,i,j,status,comment,oknok)
                                
                                
                    if trm==None:
                        pass
                    else:
                        for terms in phrase.iterfind("./{*}dcrNumbers/dcrNumber"):
                            term_type="drcNum"
                            try:
                                app=terms.attrib[zz+"applied"]
                            except KeyError:
                                app=None
                            try:
                                term=terms.text
                            except AttributeError:
                                term=None
                                
                            data={}
                            data={
                                "publn_id":publn_id,
                                "access_id":access_id,
                                "para_num":num,
                                "sen_num":num_s,
                                "time_rng":tr,
                                "term":term,
                                "applied":app,
                                "term_type":term_type
                            }
                            data_polymer_terms.append(data)
                            #foo,status,comment,oknok=insert_to("polymer_terms",data)                
                            #write_log(name,i,j,status,comment,oknok)
                                    
def get_kw_indexing(patent,publn_id,access_id):
    global data_keywords
    kwix=patent.find("./{*}keywordIndexing")
    if kwix==None:
        pass
    else:
        for kwd in kwix.iterfind("./{*}keywords"):
            for link in kwd.iterfind("./{*}keywordsLinked"):
                for para in link.iterfind("./{*}keywordPara"):
                    try:
                        num=para.attrib[zz+"no"]
                    except KeyError:
                        num=None
                    for stc in para.iterfind("./{*}keywordSentence"):
                        try:
                            num_s=stc.attrib[zz+"no"]
                        except KeyError:
                            num_s=None
                        try:
                            rel=stc.attrib[zz+"relevance"]
                        except KeyError:
                            rel=None
                        for child in stc:
                            try:
                                term_type=child.tag[len(zz):len(zz)+3]
                            except:
                                term_type=None
                            try:
                                role=child.attrib[zz+"role"]
                            except KeyError:
                                role=None
                            try:
                                applied=child.attrib[zz+"applied"]
                            except KeyError:
                                applied=None
                            try:
                                term=child.text
                            except AttributeError:
                                term=None
                            
                            data={}
                            data={
                                "publn_id":publn_id,
                                "access_id":access_id,
                                "para_num":num,
                                "sen_num":num_s,
                                "relevance":rel,
                                "role":role,
                                "term":term,
                                "applied":applied,
                                "term_type":term_type
                            }
                            data_keywords.append(data)
                            #foo,status,comment,oknok=insert_to("keywords",data)                
                            #write_log(name,i,j,status,comment,oknok)
                    


# ## Citations and relations.

# In[43]:

def get_citations(patent,publn_id,access_id):
    pan="pan"
    date=None
    global data_citations
    cit=patent.find("./{*}patentCitations/{*}patCitation")
    if cit==None:
        pass
    else:
        for pub in patent.iterfind("./{*}patentCitations/{*}patCitation"):
            try:
                publn_nr=pub.find("./{*}documentId/{*}number").text
            except AttributeError:
                publn_nr=None
            try:
                publn_auth=pub.find("./{*}documentId/{*}countryCode").text
            except AttributeError:
                publn_auth=None
            try:
                publn_kind=pub.find("./{*}documentId/{*}kindCode").text
            except AttributeError:
                publn_kind=None
            try:
                caccess_nr=pub.attrib[zz+pan]
            except KeyError:
                caccess_nr=None
            try:
                dat=pub.find("./{*}documentId/{*}kindCode").text
                date=give_date(pub,publn_id)
            except AttributeError:
                date=None
    
            data={}
            data={
                "cit_publn_nr":publn_nr,
                "cit_publn_auth":publn_auth,
                "cit_publn_kind":publn_kind,
                "access_id":access_id,
                "publn_id":publn_id,
                "cit_access_nr":caccess_nr,
                "cit_publn_date":date
            }
    
            data_citations.append(data)
            #foo,status,comment,oknok=insert_to("citations",data)
            #write_log(name,i,j,status,comment,oknok)

def get_citings(patent,publn_id,access_id):
    sta="status" #required definition for calling Xpath purposes
    pan="pan"
    date=None
    global data_citings
    cit=patent.find("./{*}citingPatents/{*}citingPatent")
    if cit==None:
        pass
    else:
        for pub in patent.iterfind("./{*}citingPatents/{*}citingPatent"):
            try:
                publn_nr=pub.find("./{*}documentId/{*}number").text
            except AttributeError:
                publn_nr=None
            try:
                publn_auth=pub.find("./{*}documentId/{*}countryCode").text
            except AttributeError:
                publn_auth=None
            try:
                publn_kind=pub.find("./{*}documentId/{*}kindCode").text
            except AttributeError:
                publn_kind=None
            try:
                caccess_nr=pub.attrib[zz+pan]
            except KeyError:
                caccess_nr=None
            try:
                dat=pub.find("./{*}documentId/{*}kindCode").text
                date=give_date(pub,publn_id)
            except AttributeError:
                date=None

    
            data={}
            data={
                "cit_publn_nr":publn_nr,
                "cit_publn_auth":publn_auth,
                "cit_publn_kind":publn_kind,
                "access_id":access_id,
                "cit_access_nr":caccess_nr,
                "publn_id":publn_id,
                "cit_publn_date":date
            }
    
            data_citings.append(data)
            #foo,status,comment,oknok=insert_to("citings",data)
            #write_log(name,i,j,status,comment,oknok)

def get_literature(patent,publn_id,access_id):
    global data_literature
    
    cit=patent.find("./{*}literatureCitations/{*}litCitation")
    if cit==None:
        pass
    else:
        for pub in patent.iterfind("./{*}literatureCitations/{*}litCitation"):
            literature_total=pub.find("./{*}litCitationTotal").text
    
            data={}
            data={
                "publn_id":publn_id,
                "liter_tot":literature_total
            }
            data_literature.append(data)
            #foo,status,comment,oknok=insert_to("literature",data)
            #write_log(name,i,j,status,comment,oknok)
            
def get_relateds(patent,publn_id):
    sta="status" #required definition for calling Xpath purposes
    lan="lang"
    date=None
    
    rl=patent.find("./{*}relateds/{*}related")
    if rl==None:
        pass
    else:
        for pub in patent.iterfind("./{*}relateds/{*}related"):
            data={}
            try:
                rel_publn_nr=pub.find("./{*}documentId/{*}number").text
            except AttributeError:
                rel_publn_nr=None
            try:
                rel_publn_auth=pub.find("./{*}documentId/{*}countryCode").text
            except AttributeError:
                rel_publn_auth=None
            try:
                rel_publn_kind=pub.find(".//{*}kindCode").text
            except AttributeError:
                rel_publn_kind=None
            try:
                rel_desc=pub.find("./{*}textDescription").text
            except AttributeError:
                rel_desc=None
    
            data={
                "publn_id":publn_id,
                "rel_publn_nr":rel_publn_nr,
                "rel_publn_auth":rel_publn_auth,
                "rel_publn_kind":rel_publn_kind,
                "description":rel_desc
            }
            data_publn_rel.append(data)
    
            #foo,status,comment,oknok=insert_to("publn_rel",data)
            #write_log(name,i,j,status,comment,oknok)


# # PARSER   
# This is the main function of the programm, which takes the extracted xml file and parses it, returning all the id's and data that will be an input to MySQL tables. It is structured in a way that follows one function per TreeElement, so that all tabular data is generated independently in a transactional form, and can then be run into any other database with only rewriting the "insert" functions. 

# In[47]:

def parser(name):
    global ac_id
    global pu_id
    parser=etree.XMLParser(ns_clean=True)
    tree=etree.parse(name,parser)
    for tsip in tree.findall(".//{*}tsip"):
        access_id,access_nr=get_access(tsip)
        ac_id=ac_id+1
        for patent in tsip.iterfind("{*}memberPatents/{*}patent"):
            publn_id,publn_nr=get_publn(patent,access_nr,access_id)
            pu_id=pu_id+1
            get_appln(patent,access_id,access_nr,publn_id,publn_nr)
            get_designated_states(patent,publn_id)
            get_assignees(patent,publn_id,access_id)
            get_relateds(patent,publn_id)
            get_inventors(patent,publn_id,access_id)
            get_agents(patent,publn_id,access_id)
            get_priorities(patent,publn_id,access_id)
            get_tit(patent,publn_id,access_id)
            get_claims(patent,publn_id,access_id)
            get_literature(patent,publn_id,access_id)
            get_citations(patent,publn_id,access_id)
            get_citings(patent,publn_id,access_id)
            get_ipc(patent,publn_id,access_id,"Ipc")
            get_ipc(patent,publn_id,access_id,"Cpc")
            get_ecla(patent,publn_id,access_id)
            get_dwpi(patent,publn_id,access_id)
            get_manual(patent,publn_id,access_id)
            get_uspc(patent,publn_id,access_id)
            get_jppc(patent,publn_id,access_id)
            get_abstract(patent,publn_id,access_id)
            get_pol_indexing(patent,publn_id,access_id)
            get_kw_indexing(patent,publn_id,access_id)
            get_chem_codes(patent,publn_id,access_id)
            get_chem_un_codes(patent,publn_id,access_id)
            get_polymer_codes(patent,publn_id,access_id)
            get_unknowns(patent)


# ## Main tables: PUBLICATIONS, APPLICATIONS, ACCESSIONS
# These three are the central elements of the Database. Accessions define each DWPI invention. Each patent family is grouped into one Accession number with all the patents that relate to the same invention. Inside each Accession or invention, there are a number of publications.
# 
# Derwent defines two types of publications inside each accession. In the xml tree, they are rooted as "patent". 
# - basic : first publication containing an invention which DERWENT received first. Not necessarily priority filing
# - equivalent : any subsequent family member with the same invention.
# 
# Experts add to the family the non-convention equivalents that do not have priority information too.
# 
# Applications correspond to these publications: One publication can have several applications (relateds, CIP, etc.) and one application can have sevarl publications (e.g. different kind codes). Thus, we generate an ID which helps relate the different tables.
# 
# Publications are uniquely defined by 3 elements: Publication Number + Publication Kind + Publication Authority
# Applications are uniquely defined by Application Number Long + Accession Number
# Accession Numbers are unique.

# In[48]:

def get_publn(patent,access_nr,access_id):
    sta="status" #required definition for calling Xpath purposes
    lan="lang"
    date=None
    global pu_id
    global dict_publn
    global data_publn
    pub=patent.find("{*}publications/{*}publication")
    publn_nr=pub.find(".//{*}number").text
    publn_auth=pub.find("./{*}documentId/{*}countryCode").text
    publn_kind=pub.find(".//{*}kindCode").text
    pub_unique=(publn_nr,publn_kind,publn_auth)
    publn_type=pub.attrib[zz+sta][5:]
    publn_lang=pub.attrib[zz+lan]
    
    
    try:
        publn_id=dict_publn[pub_unique]
    except KeyError:
        publn_id=pu_id
        publn_date=give_date(pub,publn_id)
        
        data={}
        data={
            "publn_nr":publn_nr,
            "publn_id":publn_id,
            "publn_auth":publn_auth,
            "publn_kind":publn_kind,
            "publn_type":publn_type,
            "publn_lang":publn_lang,
            "publn_date":publn_date,
            "access_nr":access_nr,
            "access_id":access_id
        }
        
        data_publn.append(data)
        dict_publn[pub_unique]=publn_id
    #publn_id,status,comment,oknok=insert_to("publn",data)
    #write_log(name,i,j,status,comment,oknok)
    return(publn_id,publn_nr)

def get_access(tsip):
    data={}
    global dict_access
    global data_access_rel
    global data_access
    access_nr=tsip.find(".//{*}accession[@"+zz+'type="pan"]').text
    aces=tsip.find("{*}invention")
    try:
        access_id=dict_access[access_nr]
    except KeyError:
        dict_access[access_nr]=ac_id
        access_id=ac_id
        try:
            country_count=aces.find(".//{*}metaData/{*}patentCounts").attrib[zz+"countryCount"]
        except AttributeError:
            country_count=None
        try:
            publn_count=aces.find(".//{*}metaData/{*}patentCounts").attrib[zz+"publicationCount"]
        except AttributeError:
            publn_count=None
        try:
            cit_count=aces.find(".//{*}metaData/{*}citedCounts[@"+zz+'per="TOTAL"]').attrib[zz+"citedPatents"]
        except AttributeError:
            cit_count=None
        try:
            inventions_count=aces.find(".//{*}metaData/{*}citedCounts[@"+zz+'per="TOTAL"]').attrib[zz+"citedInventions"]
        except AttributeError:
            inventions_count=None
        try:
            auth_count=aces.find(".//{*}metaData/{*}citedCounts[@"+zz+'per="TOTAL"]').attrib[zz+"citedAuthorities"]
        except AttributeError:
            auth_count=None
        try:
            liter_count=aces.find(".//{*}metaData/{*}citedCounts[@"+zz+'per="TOTAL"]').attrib[zz+"citedLiterature"]
        except AttributeError:
            liter_count=None

        data={
            "access_nr":access_nr,
            "auth_count":auth_count,
            "publn_count":publn_count,
            "cit_count":cit_count,
            "liter_count":liter_count,
            "country_count":country_count,
            "invent_count":inventions_count,
            "access_id":access_id
        }
        
        data_access.append(data)
    #access_id,status,comment,oknok=insert_to("access",data)
    #write_log(name,i,j,status,comment,oknok)
    
    
        data={}
        for accss in tsip.iterfind("{*}invention/{*}accessions/{*}accession"):
            acc_type=accss.attrib[zz+"type"]
            if acc_type=="pan":
                pass
            else:
                rel_accss=accss.text
                rel_type=accss.attrib[zz+"type"]
                data={
                    "access_nr":access_nr,
                    "access_id":access_id,
                    "rel_access_nr":rel_accss,
                    "rel_type":rel_type
                }
                
                data_access_rel.append(data)
            #foo,status,comment,oknok=insert_to("access_rel",data)
            #write_log(name,i,j,status,comment,oknok)
    return(access_id,access_nr)
    
def get_appln(patent,access_id,access_nr,publn_id,publn_nr):
    appln=None
    global ap_id
    global dict_appln
    global data_appln
    global data_publn_appln

    appl=patent.find(".//{*}application")
    data={}
    if appl==None:
        pass
    else:
        for appln in patent.iterfind("./{*}applications/{*}application"):
            try:
                appln_s=appln.find("{*}applicationId/{*}number[@"+zz+"form='dwpi']").text
            except AttributeError:
                appln_s=None
            try:
                appln_l=appln.find("{*}applicationId/{*}number[@"+zz+"form='tsip']").text
            except AttributeError:
                appln_l=None
            try:
                appln_auth=appln.find("{*}applicationId/{*}countryCode").text
            except AttributeError:
                appln_auth=None
            try:
                appln_date=give_date(appln,publn_id)
            except AttributeError:
                appln_date=None
            try:
                appln_txt=appln.find("{*}textDescription").text
            except AttributeError:
                appln_txt=None
                
            if appln_l==None:
                print("APPLN_LONG IS NONE")
            else:
                pass

            appln_unique=(appln_l,access_nr)
            try:
                appln_id=dict_appln[appln_unique]
            except KeyError:
                appln_id=ap_id
            
                data={
                    "appln_s":appln_s,
                    "appln_l":appln_l,
                    "appln_auth":appln_auth,
                    "appln_date":appln_date,
                    "access_id":access_id,
                    "access_nr":access_nr,
                    "appln_txt":appln_txt,
                    "appln_id":appln_id
                }
                dict_appln[appln_unique]=appln_id
                data_appln.append(data)
            
            ap_id=ap_id+1    
                
            data={}
            data={
                "appln_id":appln_id,
                "publn_id":publn_id,
                "appln_nr_l":appln_l,
                "publn_nr":publn_nr,
                "access_id":access_id,
                "access_nr":access_nr
            }
            data_publn_appln.append(data)

def publn_appln(appln_id,publn_id,appln_l,publn_nr,access_id,access_nr):
    data={}
    
    data={
        "appln_id":appln_id,
        "publn_id":publn_id,
        "appln_nr_l":appln_l,
        "publn_nr":publn_nr,
        "access_id":access_id,
        "access_nr":access_nr
    }
    
    foo,status,comment,oknok=insert_to("publn_appln",data)
    try:
        write_log(name,i,j,status,comment,oknok)
    except IOError:
        pass


# ## DESIGNATED STATES, ASSIGNEES
# 
# <b>Designated states</b> shows under which countries (states) a publication is protected as well as the "route" which can be:
# - national (filling in each country)
# - international (filling PCT at WIPO)
# - regional (by using EPC at EPO)
# 
# <b>Assignees</b> are the applicants on one publication. They are not necessarily the same as inventors or agents. DWPI adds and classifies a 4-letter code to assignees which are thus uniquely identified. Over 21,000 organizations worldwide that patent frequently. Since there are some exceptions to this (individuals, russian... ) we uniquely identify assignees by: ASSIGNEE CODE + ASSIGNEE CODE TYPE.
# In the case where the assignee has not been identified by derwent, we assign the publication ID as an Assignee Code. This might rise two problems:
# - Same assignees in two different publications is not identified as one. This cannot be easily resolved without a thorough disambiguation.
# - Multiple assignees in one publication are not identified. This can be easily resolved with a different definition of unicity.
# 

# In[49]:

def get_designated_states(patent,publn_id):
    global data_des_countr
    grp="group"
    pubs=patent.find("{*}publications/{*}publication/{*}designatedStates/{*}route")
    if pubs==None:
        pass
    else:
        for pub in patent.iterfind("./{*}publications/{*}publication/{*}designatedStates/{*}route"):
            group=pub.attrib[zz+grp]
    
            for country in pub.iterfind("./{*}countryCode"):
                des_countr=country.text
    
                data={}
                data={
                    "publn_id":publn_id,
                    "pub_gr":group,
                    "pub_countr":des_countr
                }
                data_publn_des_countr.append(data)
                #foo,status,comment,oknok=insert_to("publn_des_countr",data)
                #write_log(name,i,j,status,comment,oknok)
    
def get_assignees(patent,publn_id,access_id):
    ct="codeType"
    global as_id
    global data_assig
    global dict_assig
    ass=patent.find("./{*}assignees")
    if ass==None:
        pass
    else:
        for assignees in ass.iterfind("./{*}assignee"):
            assigC=assignees.find("./{*}assigneeCode")
            if assigC==None:
                assig_code=publn_id
                cod_type="none/PUBLN_ID"
            else:
                assig_code=assigC.text
                cod_type=assigC.attrib[zz+ct][5:]
                if assig_code==None:
                    assig_code=publn_id
                else:
                    continue
                if cod_type==None:
                    cod_type="none/PUBLN_ID"
                else:
                    continue
            
            assig_unique=()
            assig_unique=(assig_code,cod_type)
            
            try:
                assig_id=dict_assig[assig_unique]
            except KeyError:
                data={}
                assig_id=as_id
                data={}
                data={
                    "assig_code":assig_code,
                    "assig_type":cod_type,
                    "assig_id":assig_id
                }
                #print(assig_id)
                dict_assig[assig_unique]=assig_id
                data_assig.append(data)
                get_assig_data(assignees,assig_id)
                
            get_assig_publn(assig_id,publn_id)
            get_assig_access(assig_id,access_id)
            
            as_id=as_id+1
    
            #assig_id,status,comment,oknok=insert_to("assignees",data)
            #if assig_id==None:
                #assig_id,status,comment,oknok=find_assig_id(assig_code,cod_type)
                #write_log(name,i,j,status,comment,oknok)
                #get_publn_assig(assig_id,publn_id)
                #get_access_assig(assig_id,access_id)
            #else:
                #get_publn_assig(assig_id,publn_id)
                #get_access_assig(assig_id,access_id)
                #get_assig_total(assignees,assig_id)

def get_assig_publn(assig_id,publn_id):
    global data_assig_publn
    #print("subfunct",assig_id)
    data={}
    data={
        "publn_id":publn_id,
        "assig_id":assig_id
    }
    
    data_assig_publn.append(data)
    #foo,status,comment,oknok=insert_to("assig_publn",data)
    #write_log(name,i,j,status,comment,oknok)

def get_assig_access(assig_id,access_id):
    global data_assig_access
    data={}
    data={
        "access_id":access_id,
        "assig_id":assig_id
    }
    
    data_assig_access.append(data)
    #foo,status,comment,oknok=insert_to("assig_access",data)
    #write_log(name,i,j,status,comment,oknok)
    
def get_assig_data(assignee,assig_id):
    global data_assig_data
    data={}
    form="form"
    
    try:
        assig_tot=assignee.find("./{*}assigneeTotal").text
    except AttributeError:
        assig_tot=None
    try:
        assig_name_dwpi=assignee.find("./{*}name/{*}nameTotal[@"+zz+'form="dwpi"]').text
    except AttributeError:
        assig_name_dwpi=None
    try:
        assig_name_orig=assignee.find("./{*}name/{*}nameTotal[@"+zz+'form="original"]').text
    except AttributeError:
        assig_name_orig=None
    try:
        assig_address_tot=assignee.find("./{*}address/{*}addressTotal").text
    except AttributeError:
        assig_address_tot=None
    try:
        assig_cc=assignee.find("./{*}address/{*}countryCode").text
    except AttributeError:
        assig_cc=None
    try:
        assig_city=assignee.find("./{*}address/{*}city").text
    except AttributeError:
        assig_city=None
    try:
        resid=assignee.find("./{*}residence").text
    except AttributeError:
        resid=None
    try:
        nation=assignee.find("./{*}nationality").text
    except AttributeError:
        nation=None
    try:
        limit=assignee.find("./{*}limitation").text
        limit_type=assignee.find("./{*}limitation").attrib[zz+"type"]
    except AttributeError:
        limit=None
        limit_type=None
    
    
    data={}
    data={
        "assig_id":assig_id,
        "assig_total":assig_tot,
        "assig_name_dwpi":assig_name_dwpi,
        "assig_name_orig":assig_name_orig,
        "assig_address_tot":assig_address_tot,
        "assig_cc":assig_cc,
        "assig_city":assig_city,
        "limitation":limit,
        "limitation_type":limit_type,
        "resid":resid,
        "nation":nation
    }
    
    data_assig_data.append(data)
    #foo,status,comment,oknok=insert_to("assig_data",data)
    #write_log(name,i,j,status,comment,oknok)



# ## INVENTORS, PRIORITIES & AGENTS
# 
# <b>Inventors</b> and <b>Agents</b> cannot be uniquely identified without proper disambiguation, so they are extracted "as-is". They follow a similar structure to assignees, but without the code identifiers. When available, both the "original" name and the "derwent" correction are used. Allegedly, the derwent correction should correct errors and misspelled, incorrect names, but we find duplicated data in several records with the only difference of a comma or a dot.
# 
# <b>Priorities</b> are the priority filings of the corrresponding patent family (invention). They might or might not have an APPLN_ID or PUBLN_ID assigned, since they are not necessarily catalogued in DWPI (specially for the oldest records, where priority publications happened prior to the begining of our registry).
# 

# In[50]:

def get_inventors(patent,publn_id,access_id):
    inv=patent.find("./{*}inventors")
    if inv==None:
        pass
    else:
        for inventor in patent.iterfind("./{*}inventors/{*}inventor"):
            get_inventor(inventor,publn_id,access_id)
        
def get_inventor(inventor,publn_id,access_id):
    global data_inventors
    data={}
    form="form"
    
    try:
        assig_tot=inventor.find("./{*}inventorTotal").text
    except AttributeError:
        assig_tot=None
    try:
        assig_name_dwpi=inventor.find("./{*}name/{*}nameTotal[@"+zz+'form="dwpi"]').text
    except AttributeError:
        assig_name_dwpi=None
    try:
        assig_name_orig=inventor.find("./{*}name/{*}nameTotal[@"+zz+'form="original"]').text
    except AttributeError:
        assig_name_orig=None
    try:
        assig_address_tot=inventor.find("./{*}address/{*}addressTotal").text
    except AttributeError:
        assig_address_tot=None
    try:
        assig_cc=inventor.find("./{*}address/{*}countryCode").text
    except AttributeError:
        assig_cc=None
    try:
        assig_city=inventor.find("./{*}address/{*}city").text
    except AttributeError:
        assig_city=None
    try:
        resid=inventor.find("./{*}residence").text
    except AttributeError:
        resid=None
    try:
        nation=inventor.find("./{*}nationality").text
    except AttributeError:
        nation=None

    
    
    data={}
    data={
        "publn_id":publn_id,
        "assig_total":assig_tot,
        "assig_name_dwpi":assig_name_dwpi,
        "assig_name_orig":assig_name_orig,
        "assig_address_tot":assig_address_tot,
        "assig_cc":assig_cc,
        "assig_city":assig_city,
        "resid":resid,
        "nation":nation,
        "access_id":access_id
    }
    
    data_inventors.append(data)
    #foo,status,comment,oknok=insert_to("inventors",data)
    #write_log(name,i,j,status,comment,oknok)

def get_agents(patent,publn_id,access_id):
    age=patent.find("./{*}agents")
    if age==None:
        pass
    else:
        for agent in patent.iterfind("./{*}agents/{*}agent"):
            get_agent(agent,publn_id,access_id)
            
def get_agent(agent,publn_id,access_id):
    global data_agents
    data={}
    form="form"
    
    try:
        assig_tot=agent.find("./{*}agentTotal").text
    except AttributeError:
        assig_tot=None
    try:
        assig_name_dwpi=agent.find("./{*}name/{*}nameTotal[@"+zz+'form="dwpi"]').text
    except AttributeError:
        assig_name_dwpi=None
    try:
        assig_name_orig=agent.find("./{*}name/{*}nameTotal[@"+zz+'form="original"]').text
    except AttributeError:
        assig_name_orig=None
    try:
        assig_address_tot=agent.find("./{*}address/{*}addressTotal").text
    except AttributeError:
        assig_address_tot=None
    try:
        assig_cc=agent.find("./{*}address/{*}countryCode").text
    except AttributeError:
        assig_cc=None
    try:
        assig_city=agent.find("./{*}address/{*}city").text
    except AttributeError:
        assig_city=None
    try:
        resid=agent.find("./{*}residence").text
    except AttributeError:
        resid=None
    try:
        nation=agent.find("./{*}nationality").text
    except AttributeError:
        nation=None
    
    data={}
    data={
        "publn_id":publn_id,
        "assig_total":assig_tot,
        "assig_name_dwpi":assig_name_dwpi,
        "assig_name_orig":assig_name_orig,
        "assig_address_tot":assig_address_tot,
        "assig_cc":assig_cc,
        "assig_city":assig_city,
        "resid":resid,
        "nation":nation,
        "access_id":access_id
    }
    
    data_agents.append(data)
    #foo,status,comment,oknok=insert_to("agents",data)
    #write_log(name,i,j,status,comment,oknok)
    
def get_priorities(patent,publn_id,access_id):
    global data_priorities
    appln=None
    appl=patent.find(".//{*}priorities")
    data={}
    if appl==None:
        pass
    else:
        for appln in patent.iterfind("./{*}priorities/{*}priority"):
            try:
                pri_code=appln.attrib[zz+"priorityCode"]
            except AttributeError:
                pri_code=None
            try:
                appln_s=appln.find("{*}applicationId/{*}number[@"+zz+"form='dwpi']").text
            except AttributeError:
                appln_s=None
            try:
                appln_l=appln.find("{*}applicationId/{*}number[@"+zz+"form='tsip']").text
            except AttributeError:
                appln_l=None
            try:
                appln_auth=appln.find("{*}applicationId/{*}countryCode").text
            except AttributeError:
                appln_auth=None
            try:
                appln_date=give_date(appln,publn_id)
            except AttributeError:
                appln_date=None
                
                
            data={
                "appln_s":appln_s,
                "appln_l":appln_l,
                "appln_auth":appln_auth,
                "appln_date":appln_date,
                "access_id":access_id,
                "publn_id":publn_id,
                "priority_code":pri_code
            }
            data_priorities.append(data)
        
            #try:
                #foo,status,comment,oknok=insert_to("priorities",data)
                #write_log(name,i,j,status,comment,oknok)
            #except mysql.connector.Error as err:
                #pass


# # INPUT TO TABLE 
# <b>INSERT_TO</b> writes the data in the respective table. The other functions can be used if, instead of generating dicts with the IDs, we want to auto_generate id's in MySQL. These functions search and extract the auto-generated ids for further use. They are not used in this code.

# In[51]:

def insert_to(table,data):
    #cnx=mysql.connector.connect(user=usr,password=pwd,database=db_name)
    #cursor=cnx.cursor()
    add_appln=INSERTS[table]
    try:
        cursor.executemany(add_appln,data)
        status="extracting "+table
        comment=""
        oknok="ok"
        get_id=cursor.lastrowid
    except mysql.connector.Error as err:
        status="extracting "+table
        comment=err.msg
        oknok="KO"
        get_id=None
        write_log(name,i,j,status,comment,oknok)
    #cnx.commit()
    #cursor.close()
    #cnx.close()
    #return(get_id,status,comment,oknok)

def find_appln_id(app_nr,access_nr):
    cnx=mysql.connector.connect(user=usr,password=pwd,database=db_name)
    cursor=cnx.cursor()
    data={}
    find=("SELECT APPLN_ID FROM MON_RAW_DERWENT_2017.DW101_APPLN WHERE (APPLN_NR_L=%(appln_nr_l)s AND ACCESS_NR=%(access_nr)s)")
    data={
        "appln_nr_l":app_nr,
        "access_nr":access_nr
    }
    try:
        cursor.execute(find,data)
        status="finding appln_id"
        comment=""
        oknok="ok"
        get_id=cursor.fetchone()[0]
    except mysql.connector.Error as err:
        status="finding appln_id"
        comment=err.msg
        oknok="KO"
        get_id=None
    cursor.close()
    cnx.close()
    return(get_id,status,comment,oknok)

def find_lost_appln_nr(app_nr,access_nr):
    cnx=mysql.connector.connect(user=usr,password=pwd,database=db_name)
    cursor=cnx.cursor()
    flag=False
 
    data={
        "appln_nr_l":app_nr,
        "access_nr":access_nr
    }
    
    find2=("SELECT APPLN_NR_S FROM MON_RAW_DERWENT_2017.DW101_APPLN WHERE (APPLN_NR_L=%(appln_nr_l)s AND ACCESS_NR=%(access_nr)s)")
 
    try:
        cursor.execute(find2,data)
        status="finding appln_nr_s"
        comment=""
        oknok="ok"
        get_nr=cursor.fetchone()[0]
        flag=False
    except TypeError as err:
        status="finding appln_nr_s"
        comment="deepshit"
        oknok="KO"
        get_nr=app_nr
        flag=True
        print("I am here with appln_nr_long:")
        print(app_nr)
    cursor.close()
    cnx.close()
    return(get_nr,flag)

def replace_appln_nr_s(app_nr,appln_id):
    cnx=mysql.connector.connect(user=usr,password=pwd,database=db_name)
    cursor=cnx.cursor()
    data={}

    data={
        "appln_nr_s":app_nr,
        "appln_id":access_nr
    }
    
    find3=("UPDATE DW101_APPLN SET APPLN_NR_S=%(appln_nr_s)s WHERE (APPLN_ID=%(appln_id)s)")
 
    try:
        cursor.execute(find3,data)
        status="replacing appln_nr_s"
        comment=""
        oknok="ok"
        print("replacing appln_nr_s for:")
        print(app_nr)
    except TypeError as err:
        status="replacing appln_nr_s"
        comment="deepshit2"
        oknok="KO"
        print("error")
    cursor.close()
    cnx.close()
    
def find_assig_id(assig_code,assig_type):
    cnx=mysql.connector.connect(user=usr,password=pwd,database=db_name)
    cursor=cnx.cursor()
    find=("SELECT ASSIG_ID FROM MON_RAW_DERWENT_2017.DW901_ASSIG_SUPPORT WHERE (ASSIG_CODE=%(assig_code)s AND ASSIG_TYPE=%(assig_type)s)")
    
    data={}
    data={
        "assig_code":assig_code,
        "assig_type":assig_type
    }
    
    try:
        cursor.execute(find,data)
        status="finding assig_id"
        comment=""
        oknok="ok"
        get_id=cursor.fetchone()[0]
    except mysql.connector.Error as err:
        status="finding assig_id"
        comment=err.msg
        oknok="KO"
        get_id=None
    cursor.close()
    cnx.close()
    return(get_id,status,comment,oknok)


# ## Extraction
# Finally, the extraction performs all the work in this algorithm. It reads through the compressed folders where data is and extracts one file at a time:
# - folder (years) -> multiple compressed files -> multiple xml files inside each.
# 
# After the extraction, parsing takes place. In the current configuration, data is stored in memory in the <b>global variables </b> named data_*something*. These are dumped into MySQL for every compressed file (storing several xml files at once). The log is written upon extraction, deletion and dumping of each. All along the code, there are inactive insert functons and write_log functions, which generate a connection after every element is parsed. This is useful for error tracking, since the log will identify exactly which document, on which folder and at which line the error ocurred. For efficiency issues, it's better to use the current configuration for large extractions.
# 
# The log is cleaned for all the 'ok' values, leaving only a track of 'KO' (errors in MySQL dumps) and extracted files (in order to restart from any given point) if necessary.
# 
# Global Dictionaries are used to uniquely define the IDs for all the necessary fields. They are loaded from pickle files upon call, or generated empty at the begining of the code if the entire extraction is desired.
# Finally, date-time placeholders are printed after the extraction of each year begins, in order to keep track of time elapsed.
# 
# ac_id, pu_id, as_id,ap_id need to be reinitialized at a different number if the extraction crashes and has to be relaunched. These are the ID's.
# 
# One very important yet trivial variable, named <b>zz</b> is the namespace in string form for all the fields. It is necessary when parsing in order to find tree Sub-elements and attributes.

# In[ ]:

del_ds(path) #remove intial DS_files

dict_publn=pickle.load(open(dict_dir+"/publn.p","r"))
dict_appln=pickle.load(open(dict_dir+"/appln.p","r"))
dict_assig=pickle.load(open(dict_dir+"/assig.p","r"))
dict_access=pickle.load(open(dict_dir+"/access.p","r"))
dict_fields=pickle.load(open(dict_dir+"/unexplored_fields.p","r"))
ac_id=1
pu_id=1
as_id=1
ap_id=1


years=os.listdir(path)
for i in years[0:]:
    path2=path+"/"+i
    del_ds(path2)
    print(i)
    d=datetime.now()
    print(d)
    zips=os.listdir(path2)
    
    for j in zips[0:]:
        path3=path2+"/"+j
        
        if tarfile.is_tarfile(path3):
            tar=tarfile.open(path3)
            del_ds(path3)
            names=tar.getnames()
            
            data_access=[]
            data_access_rel=[]
            data_publn=[]
            data_appln=[]
            data_publn_appln=[]
            data_assig_publn=[]
            data_assig=[]
            data_assig_access=[]
            data_assig_data=[]
            data_publn_des_countr=[]
            data_publn_rel=[]
            data_inventors=[]
            data_agents=[]
            data_priorities=[]
            data_publn_tit=[]
            data_tit_terms=[]
            data_claims=[]
            data_citations=[]
            data_citings=[]
            data_literature=[]
            data_Ipc=[]
            data_Cpc=[]
            data_ecla=[]
            data_dwpi=[]
            data_manual=[]
            data_uspc=[]
            data_jppc=[]
            data_jp_fclass=[]
            data_abstracts=[]
            data_abstract_use=[]
            data_abstract_novelty=[]
            data_abstract_description=[]
            data_abstract_advantage=[]
            data_abstract_drawings=[]
            data_abstract_tech_focus=[]
            data_abstract_extension=[]
            data_abstract_preferred=[]
            data_polymer_terms=[]
            data_keywords=[]
            data_chemical_codes=[]
            data_chemical_uncodes=[]
            data_polymer_code=[]
            data_polymer_serial=[]
            data_abstract_mech_action=[]
            data_abstract_activity=[]
        
            for name in names[0:]:
                tar.extract(name,path=outpath)
                write_log(name,i,j,"file extracted","","")
                foo,ns=parse_and_get_ns(name)
                zz=ns[""]
                parser(name)
                os.remove(name)
                write_log(name,i,j,"file deleted","","ok")
        
            tar.close()
            
            cnx=mysql.connector.connect(user=usr,password=pwd,database=db_name)
            cursor=cnx.cursor()
            insert_to("access",data_access)
            insert_to("access_rel",data_access_rel)
            insert_to("publn",data_publn)
            insert_to("appln",data_appln)
            insert_to("publn_appln",data_publn_appln)
            insert_to("assignees",data_assig)
            insert_to("assig_publn",data_assig_publn)
            insert_to("assig_access",data_assig_access)
            insert_to("assig_data",data_assig_data)
            insert_to("publn_des_countr",data_publn_des_countr)
            insert_to("publn_rel",data_publn_rel)
            insert_to("inventors",data_inventors)
            insert_to("agents",data_agents)
            insert_to("priorities",data_priorities)
            insert_to("publn_tit",data_publn_tit)
            insert_to("tit_terms",data_tit_terms)
            insert_to("claims",data_claims)
            insert_to("literature",data_literature)
            insert_to("citings",data_citings)
            insert_to("citations",data_citations)
            insert_to("Ipc",data_Ipc)
            insert_to("Cpc",data_Cpc)
            insert_to("ecla",data_ecla)
            insert_to("dwpi",data_dwpi)
            insert_to("manual",data_manual)
            insert_to("uspc",data_uspc)
            insert_to("jppc",data_jppc)
            insert_to("jp_fclass",data_jp_fclass)
            insert_to("abstracts",data_abstracts)
            insert_to("abstract_use",data_abstract_use)
            insert_to("abstract_novelty",data_abstract_novelty)
            insert_to("abstract_advantage",data_abstract_advantage)
            insert_to("abstract_drawings",data_abstract_drawings)
            insert_to("abstract_description",data_abstract_description)
            insert_to("abstract_tech_focus",data_abstract_tech_focus)
            insert_to("abstract_preferred",data_abstract_preferred)
            insert_to("abstract_extension",data_abstract_extension)
            insert_to("polymer_terms",data_polymer_terms)
            insert_to("keywords",data_keywords)
            insert_to("chemical_codes",data_chemical_codes)
            insert_to("chemical_uncodes",data_chemical_uncodes)
            insert_to("polymer_code",data_polymer_code)
            insert_to("polymer_serial",data_polymer_serial)
            insert_to("abstract_mech_action",data_abstract_mech_action)
            insert_to("abstract_activity", data_abstract_activity)
            cnx.commit()
            cursor.close()
            cnx.close()
            
            clean_log()
        else:
            pass
    pickle.dump(dict_access,open(dict_dir+"/access.p","w"))
    pickle.dump(dict_assig,open(dict_dir+"/assig.p","w"))
    pickle.dump(dict_publn,open(dict_dir+"/publn.p","w"))
    pickle.dump(dict_appln,open(dict_dir+"/appln.p","w"))
    pickle.dump(dict_fields,open(dict_dir+"/unexplored_fields.p","w"))
print("############    The process finished     ############")
print(datetime.now())
print(dict_fields)

