#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 10 14:36:20 2021

@author: antonio
"""

import pandas as pd            #for creating the spreadsheet
import numpy as np             #for nan
import glob
import itertools
#import re as re                


####Functions
def create_columns(dfPrim):
    dfsP = np.split(dfPrim, [3,6,9,12], axis = 1)

    drop_list = []
    index = -1
    for df in dfsP:
        index += 1
        df.dropna(how = "all", inplace = True)
    
        if df.iloc[1,0] != "None":
        
            df["Effect"] = df.iloc[0,0]
            df.drop([0], inplace = True)
            mapping = {df.columns[0]:'Treatment', df.columns[1]: 'Values', df.columns[2]:'Certainty'}
            df.rename(columns=mapping, inplace = True)
        
        else:
            drop_list.append(index)
        
    for index in sorted(drop_list, reverse=True):
        del dfsP[index]
    
    df = pd.concat(dfsP)
    return df

def bg_color(subrow):
    blank = '' 

    subrow_out =  pd.Series(blank, index=subrow.index)
    
    if (subrow[1] =="HIGH" or subrow[1] =="MODERATE") and subrow[2] == "Best":
        subrow_out[0] = 'background-color: #465c1e'
        return subrow_out
    
    if (subrow[1] =="HIGH" or subrow[1] =="MODERATE") and subrow[2] == "Better than SC":
        subrow_out[0] = 'background-color: #6aa84f'
        return subrow_out
    
    if (subrow[1] =="HIGH" or subrow[1] =="MODERATE") and subrow[2] == "Not different than SC":
        subrow_out[0] = 'background-color: #ffd966'
        return subrow_out
    
    if (subrow[1] =="HIGH" or subrow[1] =="MODERATE") and subrow[2] == "Harmful":
        subrow_out[0] = 'background-color: #e69138'
        return subrow_out
    
    if (subrow[1] =="HIGH" or subrow[1] =="MODERATE") and subrow[2] == "Worst":
        subrow_out[0] = 'background-color: #cc0000'
        return subrow_out
    
    if subrow[1] =="LOW" and subrow[2] == "Best":
        subrow_out[0] = 'background-color: #d7e8b1'
        return subrow_out
    
    if subrow[1] =="LOW" and subrow[2] == "Better than SC":
        subrow_out[0] = 'background-color: #d9ead3'
        return subrow_out
    
    if subrow[1] =="LOW" and subrow[2] == "Not different than SC":
        subrow_out[0] = 'background-color: #fff2cc'
        return subrow_out
    
    if subrow[1] =="LOW" and subrow[2] == "Harmful":
        subrow_out[0] = 'background-color: #f9cb9c'
        return subrow_out
    
    if subrow[1] =="LOW" and subrow[2] == "Worst":
        subrow_out[0] = 'background-color: #f4cccc'
        return subrow_out
    
    if subrow[1] =="VERY LOW":
        subrow_out[0] = 'background-color: #efefef'
        return subrow_out
     
    else:
         return subrow_out

def round_value(df, name):
    
    dfr = df.copy()
    
    for i in range(0, len(df.index)):
        
        aux_str = df.loc[i, (name, "Values")]
        aux_list = aux_str.split(' (')
        value = aux_list[0]
        interval = " (" + aux_list[1]
        value = str(round(float(value)))
        dfr.loc[i, (name, "Values")] = value + interval
        
    return dfr

#####import whole directory xlsx files
list_files = glob.glob('./*.xlsx')
sheet = "Automatic classification"
list_name =[]
list_df = []
name_excel = "Figure 2.xlsx"

try:
    list_files.remove("./" + name_excel)
except ValueError:
    5

for file in list_files:
    name1 = file.split(' - ')[0]
    name = name1.split("./")[1]
    list_name.append(name)
    
    Name_File_Data = file

    dfPrim = pd.read_excel(Name_File_Data, header = None, sheet_name = sheet)

    df = create_columns(dfPrim)
    
    df.columns = pd.MultiIndex.from_product([[name], df.columns])
    df.reset_index(inplace = True, drop = True)
    
    df = round_value(df, name)
    
    list_df.append(df)
    
list_df= sorted(list_df, key=lambda x:len(x), reverse = True)

### join all the dataframes by treatment
merge_df = pd.concat([df.set_index(df.columns[0]) for df in list_df], axis=1).reset_index().sort_values('index')
#merge_df = merge_df.rename(columns={'': 'Values'})

out_df = merge_df.copy()
out_df.set_index(("index",""), drop = True, inplace = True)

#### cartesian products for correct ordering

values = ["Values"]
outcomes = out_df.iloc[:, out_df.columns.get_level_values(1)=='Values'].columns.get_level_values(0).tolist()
cols_out = list(itertools.product(outcomes, values))

elses = ["Certainty","Effect"]
cols_else = list(itertools.product(outcomes, elses))
cols_order = cols_out + cols_else

out_df = out_df[cols_order]

writer = pd.ExcelWriter(name_excel, engine='xlsxwriter')

styled_df = out_df.copy().style

for output in list(set(styled_df.columns.get_level_values(0))):

    styled_df = styled_df.apply(bg_color, subset = output, axis = 1)

styled_df.to_excel(writer, sheet_name = 'Summary', columns = cols_out, header = True)

workbook = writer.book
worksheet = writer.sheets['Summary']  # pull worksheet 

worksheet.set_zoom(80)

format_left = workbook.add_format({'align': 'left', 'valign': 'top', 'bold' : False})
format_center = workbook.add_format({'align': 'center', 'valign': 'top'})

worksheet.set_column(0, 0, 35, format_left)
worksheet.set_column(1, len(list_df), 25, format_center)

writer.save()