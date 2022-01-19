#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 8 08:28:58 2022

@author: antonio
"""

import pandas as pd            #for creating the spreadsheet
import numpy as np             #for nan
import re as re                #for sub

import sys
sys.path.append("../..")

from Functions import cleandf, clean_treatments_names, check_spelling_manually_lol, id_order, find_int_in_string, order_treatments_on_2_columns

#####name of inputs
Name_File_Data = "COVID19 NMA Therapy Data (06-12-2021) - revised(1).xlsx"
nodes_name = "Table of nodes (27-11-2021).xlsx"
Dichotomous = "Dichotomous outcomes"
Continuous = "Continuous outcomes"

Dich_Dictionary = ["Mortality", "Mechanical ventilation", "Admission to hospital", "Adverse events", \
                   "Viral clearance", "Venous thromboembolism","Clinically important bleeding"]
Cont_Dictionary = ["Hospitalization LOS", "ICU LOS", "Ventilator-free days", \
                   "Duration of ventilation", "Symptom resolution", "Time to clearance"]

if nodes_name == 0:
    nodes_file = 0
    
else:
    nodes_file = pd.read_excel(nodes_name)

DichPrim = pd.read_excel(Name_File_Data, header = None, sheet_name = Dichotomous)
ContPrim = pd.read_excel(Name_File_Data, header = None, sheet_name = Continuous)

Dich =cleandf(DichPrim, total_nan = True)
Cont =cleandf(ContPrim, total_nan = True)

def data_prep_subdf(df, sheet):
    dfr = df.copy()
    if sheet == "Dichotomous outcomes":

        dfr.drop("Comments", axis = 1, level = 0, inplace = True)
        dfr.drop("Follow-up time (days)", axis = 1, level = 1, inplace = True)
        
    if sheet == "Continuous outcomes":    
        
        dfr.drop("Comments", axis = 1, level = 0, inplace = True)
        dfr.drop("Follow-up time (days)", axis = 1, level = 1, inplace = True)
        dfr.drop("Time to symptom resolution or time to clinical improvement criteria", axis = 1, level = 1, inplace = True)
        
    return dfr

Dich =data_prep_subdf(Dich, Dichotomous)
Cont =data_prep_subdf(Cont, Continuous)

Dich =id_order(Dich)
Cont =id_order(Cont)

Dich=clean_treatments_names(Dich, sheet = Dichotomous, directory_file = nodes_file, node_mask_inplace = False)
Cont =clean_treatments_names(Cont, sheet = Continuous, directory_file = nodes_file, node_mask_inplace = False)

Dich =find_int_in_string(Dich, start_column = 3, end_column = 5)
Cont =find_int_in_string(Cont, start_column = 3, end_column = 5)
Cont =find_int_in_string(Cont, start_column = 7, end_column = 7)

def find_float_in_string(df, start_column = 0, end_column = 1):
    
    dfr = df.copy()
    
    for i in range(0, len(df.index)):
        
        for j in range(start_column, end_column + 1):
            
            cell = dfr.iloc[i, j]
            
            if type(cell) == str:
                
                if any(c.isdigit() for c in cell):
                
                    aux_list = re.findall(r"[-+]?\d*\.\d+|\d+", df.iloc[i, j])
                    aux_list = [float(x) for x in aux_list]
                    
                    if len(tuple(aux_list)) > 1:
                        
                        dfr.iat[i, j] = tuple(aux_list)
                        
                    else:
                    
                        dfr.iloc[i,j] = aux_list[0]
                    
                else:
                    
                    dfr.iloc[i, j] = np.nan
                
    return dfr

Cont =find_float_in_string(Cont, start_column = 6, end_column = 6)
Cont =find_float_in_string(Cont, start_column = 8, end_column = 8)

Dich.columns = Dich.columns.get_level_values(1)
Cont.columns = Cont.columns.get_level_values(1)  

####Dich
Dich_Outcome_dict = ["Mortality", \
                     "Mechanical ventilation", \
                     "Admission to hospital", \
                     "Adverse effects leading to discontinuation", \
                     "Viral clearance", \
                     "Venous thromboembolism", \
                     "Clinically important bleeding"]

Dich["Number of events"] = pd.to_numeric(Dich["Number of events"])

Dichlong = Dich.groupby(["Ref ID", "1st Author", "Intervention 1 name node", "Outcome"], as_index = False)\
    [["N analyzed", "Number of events", "Intervention name"]].agg(lambda x: x.sum())
Dichlong = Dichlong.groupby(["Ref ID", "1st Author", "Outcome"]).filter(lambda d: len(d) > 1)

Dichlong.rename(columns = {"Ref ID" : "refid", \
                            "1st Author" : "stauthor", \
                            "Intervention 1 name node" : "interventionname", \
                            "Intervention name" : "treatment", \
                            "N analyzed" : "sampleSize", \
                            "Number of events" : "responder"}, inplace = True)

Dichlong = Dichlong[Dichlong.columns[[0,1,2,6,3,4,5]]]

Dichlong = Dichlong[Dichlong['sampleSize'].notna()]
Dichlong = Dichlong[Dichlong['responder'].notna()]

Dichlong = Dichlong.sort_values(by = ['stauthor', 'interventionname'])

#####
Dichwide = pd.merge(Dichlong, Dichlong, on = ["refid", "stauthor", "Outcome"])
Dichwide.drop(Dichwide[Dichwide['interventionname_x'] == Dichwide['interventionname_y']].index, inplace = True)
Dichwide = Dichwide.drop(["treatment_x", "treatment_y"], axis = 1)
Dichwide = order_treatments_on_2_columns(Dichwide, treatment1 = 'interventionname_x', treatment2 = 'interventionname_y', associated_vars1 = ["sampleSize_x", "responder_x"], associated_vars2 = ["sampleSize_y", "responder_y"], Total_N = False)
Dichwide.drop_duplicates(inplace=True, ignore_index=False)

Dichwide.rename(columns = {"stauthor" : "study", \
                           "interventionname_x" : "t1", \
                           "interventionname_y" : "t2", \
                           "sampleSize_x" : "e.total", \
                           "sampleSize_y" : "c.total", \
                           "responder_x" : "e.events", \
                           "responder_y" : "c.events"}, inplace = True)
    
Dichwide = Dichwide.drop(["refid"], axis = 1)
Dichwide = Dichwide[Dichwide.columns[[0,1,5,4,3,7,6,2]]]
  
def get_outcome(df, dichotomous_or_continuous, n_outcome):
    
    dfr = df.copy()
    
    dfr = dfr[dfr[dichotomous_or_continuous] == n_outcome]
    dfr = dfr.drop(["Outcome"], axis = 1)
    
    return dfr
    
for outcome in Dich_Outcome_dict:
    
    index = Dich_Outcome_dict.index(outcome) + 1
    
    outcome_long_df = get_outcome(Dichlong, "Outcome", index)
    outcome_long_df.to_csv(outcome + " - long data format.csv", index = False, )
    
    outcome_wide_df = get_outcome(Dichwide, "Outcome", index)
    outcome_wide_df.to_csv(outcome + " - wide data format.csv", index = False, )
    
"""
mortality_long = get_outcome(Dichlong, "Outcome", 1)

ventilation_long = get_outcome(Dichlong, "Outcome", 2)

hospital_admission_long = get_outcome(Dichlong, "Outcome", 3)

adverse_events_long = get_outcome(Dichlong, "Outcome", 4)

viral_clearance_long = get_outcome(Dichlong, "Outcome", 5)

venous_thromboembolism_long = get_outcome(Dichlong, "Outcome", 6)

bleeding_long = get_outcome(Dichlong, "Outcome", 7)

####
mortality_wide = get_outcome(Dichwide, "Outcome", 1)

ventilation_wide = get_outcome(Dichwide, "Outcome", 2)

hospital_admission_wide = get_outcome(Dichwide, "Outcome", 3)

adverse_events_wide = get_outcome(Dichwide, "Outcome", 4)

viral_clearance_wide = get_outcome(Dichwide, "Outcome", 5)

venous_thromboembolism_wide = get_outcome(Dichwide, "Outcome", 6)

bleeding_wide = get_outcome(Dichwide, "Outcome", 7)
"""
"""
1) Duration of hospitalization [days]
2) ICU length of stay [days]
3) Ventilator-free days [within 28 days; days]
4) Duration of ventilation [days]
5) Time to symptom resolution or time to clinical improvement [days]
6) Time to viral clearance [days]
"""
    

###Cont group
to_numeric_columns = ["Outcome", "Central tendency", "Measure of variability"]
for column in to_numeric_columns:
    
    Cont[column] = pd.to_numeric(Cont[column])

#Contgroup = Cont.groupby(["Ref ID", "1st Author", "Intervention 1 name node", "Outcome"], as_index = False)[["N analyzed", "Number of events", "Intervention name"]].agg(lambda x: x.sum())
#Contgroup = Contgroup.groupby(["Ref ID", "1st Author", "Outcome"]).filter(lambda d: len(d) > 1)

