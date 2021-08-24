#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 18 20:05:59 2021

@author: antonio
"""

import pandas as pd            #for creating the spreadsheet
import numpy as np             #for nan
#import re as re                #for sub

from Functions_2 import percentage_mechanical_ventilation_column

#functions for the condensed
#every function is a cell

def registered_cell(df):
    
    #dfr = df.copy()
    
    srs = df[("Trial registration", "Trial registration")]
    
    srs = srs.replace("NR", np.nan)
    
    size = srs.size
    
    total_nan = srs.isnull().sum()

    cell = f"{size - total_nan} ("  + "{:.1f}".format((size - total_nan)*100/size) + "%)"
    
    return pd.Series({"Registered" : cell})


def publication_cells(df):
    
    PSc = "Publication/Study characteristics"
    srs = df[(PSc, "Publication status")]
    
    preprint = 0
    published = 0
    unpublished = 0
    size = srs.size
    
    for i in range(0, len(srs.index)):
        
        aux_str = srs.loc[i]
        aux_str = str(aux_str).replace(",", "")
        aux_lst = [int(s) for s in aux_str.split() if s.isdigit()]
        aux_str = min(aux_lst)
        
        if aux_str == 2:
            
            preprint += 1
            
        elif aux_str == 1 or aux_str == 5:
            
            published += 1
            
        elif aux_str == 3 or aux_str == 4:
            
            unpublished += 1
            
        else:
            print(f"{aux_str}" + "wasnt counted. Contact maintainance")
            
    preprint = f"{preprint} ("  + "{:.1f}".format((preprint)*100/size) + "%)"
    published = f"{published} ("  + "{:.1f}".format((published)*100/size) + "%)"
    unpublished = f"{unpublished} ("  + "{:.1f}".format((unpublished)*100/size) + "%)"
            
    dat = {"Publication status" : "", "Preprint" : preprint, "Published" : published, "Unpublished" : unpublished}
            
    return pd.Series(dat)

def country_cells(df):
    
    Bpc = "Baseline patient characteristics"
    srs = df[(Bpc, "Country")]
    
    srs.replace("NR", np.nan, inplace = True)
    srs.fillna(value = "", inplace = True)
    
    size = srs.size
    
    list1 = []
    
    for i in range(0, len(srs.index)):
        
        aux_str = srs.loc[i]
        aux_lst = aux_str.split(",")
        
        for element in range(0, len(aux_lst)):
            
            aux_element = str(aux_lst[element]).lstrip().rstrip()
            
            if aux_element == "USA" or aux_element == "United states":
                
                aux_element = "United States"
            
            elif aux_element == "UK" or aux_element == "United kingdom":
                
                aux_element = "United Kingdom"

            aux_lst[element] = aux_element
            
        list1.extend(aux_lst)
        
    srs_from_list = pd.Series(list1)
    groupby_srs = srs_from_list.value_counts().head(5)
    
    for i in range(0, len(groupby_srs.index)):
        
        groupby_srs.iloc[i] = f"{groupby_srs.iloc[i]} ("  + "{:.1f}".format((groupby_srs.iloc[i])*100/size) + "%)"
        
    header_count = pd.Series({"Country" : ""})
    output = pd.concat([header_count, groupby_srs], axis = 0)
    
    return output

def intensity_of_care_cells(df):
    
    Bcc = "Baseline clinical characteristics"
    header_count = pd.Series({"Intensity of care" : ""})
    hospitalized =df[(Bcc, "Inpatient (%)")]
    intensive = df[(Bcc, "Intensive care (%)")]
    
    hospitalized.replace("NR", np.nan, inplace = True)
    intensive.replace("NR", np.nan, inplace = True)
    
    inpatient = hospitalized[hospitalized > 80]
    outpatient = hospitalized[hospitalized < 20]
    icu = intensive[intensive > 80]
    
    size = hospitalized.size
    
    outpatient = f"{outpatient.size} ("  + "{:.1f}".format(outpatient.size*100/size) + "%)"
    inpatient = f"{inpatient.size} ("  + "{:.1f}".format(inpatient.size*100/size) + "%)"
    icu = f"{icu.size} ("  + "{:.1f}".format(icu.size*100/size) + "%)"
    
    dat = {"Outpatient" : outpatient, "Inpatient" : inpatient, "ICU" : icu}
    res = pd.Series(dat)
    
    output = pd.concat([header_count, res], axis = 0)
    
    return output

def severity_cells(df):
    
    Bcc = "Baseline clinical characteristics"
    header_count = pd.Series({"Severity" : ""})
    
    mild = df[(Bcc, "Mild illness (%)")]
    moderate = df[(Bcc, "Moderate illness (%)")]
    severe = df[(Bcc, "Severe illness (%)")]
    critical = df[(Bcc, "Critical illness (%)")]
    
    size = mild.size
    
    mild.replace("NR", 0, inplace = True)
    moderate.replace("NR", 0, inplace = True)
    severe.replace("NR", 0, inplace = True)
    critical.replace("NR", 0, inplace = True)
    
    mild_moderate = mild + moderate
    severe_critical = severe + critical
    
    mild_moderate = mild_moderate[mild_moderate > 80]
    severe_critical = severe_critical[severe_critical > 80]
    
    mild_moderate = f"{mild_moderate.size} ("  + "{:.1f}".format(mild_moderate.size*100/size) + "%)"
    severe_critical = f"{severe_critical.size} ("  + "{:.1f}".format(severe_critical.size*100/size) + "%)"
    
    dat = {"Mild/moderate" : mild_moderate, "Severe/critical" : severe_critical}
    res = pd.Series(dat)
    
    output = pd.concat([header_count, res], axis = 0)
    
    return output

def ventilation_cell(df):
    
    dfr = df.copy()
    srs = percentage_mechanical_ventilation_column(dfr)[("% Mechanical \nventilation \n(at baseline)", "% Mechanical \nventilation \n(at baseline)")]
    srs.replace("NR", np.nan, inplace = True)
    
    median = srs.median()
    iqr = srs.quantile(0.75) - srs.quantile(0.25)

    output = pd.Series({"% ventilated" : "{:.1f}".format(median) + " [" + "{:.1f}".format(iqr) + "]"})
    
    return output

def number_patients_cell(df):
    
    N_rand = "N randomized"
    columns_patients = [("Intervention 1", N_rand), ("Intervention 2", N_rand), ("Intervention 3", N_rand), \
                        ("Intervention 4", N_rand), ("Intervention 5", N_rand)]
    
    dfr = df.copy()
    dfr = dfr[columns_patients]
    
    dfr.replace("NR", np.nan, inplace = True)
    
    total_patients = dfr.sum(axis = 1)
    
    median = total_patients.median()
    iqr = total_patients.quantile(0.75) - total_patients.quantile(0.25)
    
    output = pd.Series({"Number of patients" : "{:.1f}".format(median) + " [" + "{:.1f}".format(iqr) + "]"})
    
    return output
