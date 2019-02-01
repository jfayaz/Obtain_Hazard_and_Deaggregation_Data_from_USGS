"""
author : JAWAD FAYAZ (email: jfayaz@uci.edu)
visit: (https://jfayaz.github.io)

------------------------------ Instructions ------------------------------------- 
This code downloads the Hazard Curves and Deaggregation information of a given the 
Site Location provided with other inputs.

You may run this code in python IDE: 'Spyder' or any other similar IDE

Make sure you have the following python libraries installed:
    pandas 
    numpy
    urllib.request 
    string 
    openpyxl 
    xlsxwriter
    requests
    json



INPUT:
The input data must be provided in form of Excel file as per the given 'Input Data.xlsx' file 
The name of the excel file must be kept as 'Input Data.xlsx'
Row 1 of the file must contain the titles as follows:
   Edition	Region	Longitude	Latitude	imt	vs30	Return Period

The input data must be provided starting from row 2 of the sheet with the required 
values under each title. More than 1 rows can be provided as the data 
E.g. the example file 'Input Data.xlsx' contains input for 3 sites 

Following are the options that can be provided under each title:   
    Edition (USGS edition)      :   'E2008' , 'E2014'
    Region                      :   'COUS', 'WUS', 'CEUS'  ; {WUS: Western US, CEUS: Central Eastern US}
    Longitude                   :    Longitude of the Site
    Latitude                    :    Latitude of the Site
    imt (Intensity Measure Type):    'PGA', 'SA0P2', 'SA1P0','SA2P0' ; {PGA: Peak Ground Acceleration, SA0P2: Spectral Acceleration at 0.2 secs, SA1P0: Spectral Acceleration at 1 sec, SA2P0: Spectral Acceleration at 2 sec}
    vs30 (Shear-Wave Velocity)  :    '180', '259', '360', '537', '760', '1150', '2000' ; {in m/s , restricted to only these values}



OUTPUT:
The output will be provided in a saperate Excel file 'Output Data.xlsx' for each input
The file will contain 2 sheets:
    1) 'Hazard Curves' sheet will contain information about the Hazard Curves at 0.2 sec, 1 sec and 2 secs
        The output will have titles:
            Acceleration (g)	lambda PGA	 lambda Sa at 0.2 sec	 lambda Sa at 1 sec	  lambda Sa at 2 sec
         
    2) 'Deaggregation' sheet will contain information about the deaggregation of the site at given imt level
        The output will have two saparate tables showing the deaggregation of faults from 'Gutenberg-Richter (gr)' and 'Characteristic (ch)' branches of the USGS logic tree. They both must be added weightedly to attain total deaggregation
        Each table will have titles:
            source	r	m	ε	longitude	latitude	azimuth	  % contribution
            
Note: If a USGS branch other than 'Gutenberg-Richter (gr)' and 'Characteristic (ch)' is used in deaggregation, the results wont be provided for now!
You are welcome to make the additions to the code to make it more exhaustive


%%%%% ========================================================================================================================================================================= %%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

"""

import pandas as pd
import numpy as np
from urllib.request import urlopen
from string import ascii_uppercase
from openpyxl import load_workbook
import xlsxwriter
import requests
import json
import openpyxl


# Reading given data
df = pd.read_excel('Input Data.xlsx', converters={'Edition':str,'Region':str,'imt':str})
sfmt = '{Edition}/{Region}/{Longitude}/{Latitude}/{imt}/{vs30}/{Return Period}'.format
imt_list = ['PGA', 'SA0P2', 'SA1P0','SA2P0']



for ii in range(0,len(df)):
    
    ### ---------- HAZARD CURVES ---------- ###
        
    def url_resp_values(row):
        # Contatenating the input params with the link
        url = "https://earthquake.usgs.gov/nshmp-haz-ws/hazard/" + row
        # Opening url
        data = requests.get(url).json()
        response1 = {'xvalues': data['response'][0]['metadata']['xvalues']}
        response2 = {'yvalues': data['response'][0]['data'][0]['yvalues']}
        return response1, response2
    
    lm=df[ii:ii+1].reset_index(drop=True)
    
    for j in range(0,len(imt_list)):
        lm['imt'] = imt_list[j] 
        params=lm.apply(lambda x: sfmt(**x), 1)
        response1, response2 = url_resp_values(params[0])
        
        if j == 0:
            DF_HAZARD_CURVES = pd.DataFrame.from_dict(response1)
            
        DF_HAZARD_CURVES = pd.concat([DF_HAZARD_CURVES, pd.DataFrame.from_dict(response2)], axis=1)  
        
    DF_HAZARD_CURVES.columns = ['Acceleration (g)','lambda PGA', 'lambda Sa at 0.2 sec', 'lambda Sa at 1 sec','lambda Sa at 2 sec']
    writer = pd.ExcelWriter('Output Data'+str(ii+1)+'.xlsx',engine='xlsxwriter')
    DF_HAZARD_CURVES.to_excel(writer,'Hazard Curves',startrow=4)
    worksheet = writer.sheets['Hazard Curves']
    worksheet.write('A1', 'Latitude')
    worksheet.write('B1', lm['Latitude'][0])
    worksheet.write('A2', 'Longitude')
    worksheet.write('B2', lm['Longitude'][0])
    worksheet.write('A3', 'Vs30 (m/s)')
    worksheet.write('B3', lm['vs30'][0])
    
    
    
    ### ---------- DEAGGREGATION ---------- ###
    
    lm=df[ii:ii+1].reset_index(drop=True)
    params=lm.apply(lambda x: sfmt(**x), 1)
    for i,row in enumerate(params.values):
        # Converting to utf encoding 8
        # Contatenating the input params with the link
        url = "https://earthquake.usgs.gov/nshmp-haz-ws/deagg/" + row
        # Opening url
        response =  urlopen(url)
        # Converting response to str format
        response_1 = response.read()
        # Terminating connection
        response.close()
              
    # Extracting sources from response
    data = json.loads(response_1)
       
    # json data starts with response->data->soruces
    lx = pd.DataFrame.from_dict(data['response'][0]['data'][0]['sources'])
    
    # Removing if contains pointsourcefinite
    lx=lx[~lx['name'].str.contains("PointSourceFinite")]
    epsilon = lx.columns[10]
    
    # Rearrange columns
    lx=lx[['name','source','r','m',epsilon,'longitude','latitude','azimuth','contribution']]
    
    # Deleting source column
    del lx['source']
    
    # Renaming column to source
    lx=lx.rename(columns={'name':'source'})
    
    #Getting indexes of faults
    Fault_Name_idx = np.asarray(np.where(lx['r'].isna()))
    Fault_Types = lx['source'][Fault_Name_idx[0]]
    Fault_Name_idx = np.append(Fault_Name_idx,[[len(lx)]],axis=1)
    position1 = 0
    position2 = 2
    
    #bFault type
    if(Fault_Types[Fault_Types.str.contains("bFault")].any()):
        bFault_idx =  Fault_Types[Fault_Types.str.contains("bFault")==True].to_frame().reset_index()
        # Finding how many types of bFaults are there
        if len(bFault_idx) > 0: 
            # Making a list containing dataframes for each type of bFault
            bFault_idx_true = np.where(np.in1d(Fault_Name_idx, bFault_idx['index'].values))[0]
            bFault_list = [[]]
            bFault_list[0] = lx[Fault_Name_idx[0][bFault_idx_true[0]]:Fault_Name_idx[0][bFault_idx_true[0]+1]].reset_index(drop=True)
            bFault_list[0][1:].to_excel(writer,sheet_name='Deaggregation',startrow=position1+1)
            worksheet = writer.sheets['Deaggregation']
            worksheet.write('A'+str(position1+1), bFault_list[0]['source'][0])
            position1 = len(bFault_list[0])
            # if more than 1 type of aFaults, appending them
            for i in range(1,len(bFault_idx_true)):
                bFault_list.append(lx[Fault_Name_idx[0][bFault_idx_true[i]]:Fault_Name_idx[0][bFault_idx_true[i]+1]].reset_index(drop=True))
                position1 = position1 + 3
                bFault_list[i][1:].to_excel(writer,sheet_name='Deaggregation',startrow=position1)
                worksheet = writer.sheets['Deaggregation']
                worksheet.write('A'+str(position1), bFault_list[i]['source'][0])
                position2 = position1 + len(bFault_list[i]) + 3
        del bFault_list
        del bFault_idx_true
                
                
    #aFault type
    if(Fault_Types[Fault_Types.str.contains("aFault")].any()):
        aFault_idx =  Fault_Types[Fault_Types.str.contains("aFault")==True].to_frame().reset_index()
        #Finding how many types of aFaults are there
        if len(aFault_idx) > 0: 
            # Making a list containing dataframes for each type of aFault
            aFault_idx_true = np.where(np.in1d(Fault_Name_idx, aFault_idx['index'].values))[0]
            aFault_list = [[]]
            aFault_list[0] = lx[Fault_Name_idx[0][aFault_idx_true[0]]:Fault_Name_idx[0][aFault_idx_true[0]+1]].reset_index(drop=True)
            position2 = position2
            aFault_list[0][1:].to_excel(writer,sheet_name='Deaggregation',startrow=position2-1) 
            worksheet = writer.sheets['Deaggregation']
            worksheet.write('A'+str(position2-1), aFault_list[0]['source'][0])
            # if more than 1 type of aFaults, appending them
            for i in range(1,len(aFault_idx_true)):
                aFault_list.append(lx[Fault_Name_idx[0][aFault_idx_true[i]]:Fault_Name_idx[0][aFault_idx_true[i]+1]].reset_index(drop=True))
                position2 = position2 + len(aFault_list[i-1]) + 2
                aFault_list[i][1:].to_excel(writer,sheet_name='Deaggregation',startrow=position2-1)
                worksheet = writer.sheets['Deaggregation']
                worksheet.write('A'+str(position2-1), aFault_list[i]['source'][0])
        del aFault_list
        del aFault_idx_true
        
    writer.save()
    
    del lm 
    del params
    del response1
    del response2
    del response_1
    del Fault_Name_idx
    del DF_HAZARD_CURVES
    del writer
    del data
    del lx
    del Fault_Types
    

