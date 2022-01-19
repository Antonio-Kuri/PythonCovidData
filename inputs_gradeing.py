#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 15 18:21:17 2021

@author: antonio
"""

# Definicion de variables globales
old_Name_File_Data = "COVID19 NMA Therapy Data (22-11-2021) - revised.xlsx"
Name_File_Data = "COVID19 NMA Therapy Data (06-12-2021) - revised(1).xlsx" #nombre de archivo

Trial_Data = "Trial characteristics" #nombre de una hoja
Trial_Data2 = "Risk of bias"

Dichotomous = "Dichotomous outcomes"
Continuous = "Continuous outcomes"

severity = 2

#Nodes 
#Replace with ( nodes_name = 0 ) if the coded grouping is desired to be used, instead of the file
#nodes_name = 0
nodes_name = "Table of nodes (27-11-2021).xlsx"

#trial characteristics table
#filter by treatment pair
filter_treat = []#["molnupiravir", "fluvoxamine"]