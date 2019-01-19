"""
author : JAWAD FAYAZ (email: jfayaz@uci.edu)

------------------------------ Instructions ------------------------------------- 
This code downloads the Hazard Curves and Deaggregation information of a given the 
Site Location provided with other inputs.

You may run this code in python IDE: 'Spyder' or any other similar IDE

Make sure you have the following python libraries installed:
    pandas 
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
    imt (Intensity Measure Type):    'PGA', 'SA0P2', 'SA1P0' ; {PGA: Peak Ground Acceleration, SA0P2: Spectra Acceleration at 0.2 secs, SA1P0: Spectral Acceleration at 1 sec}
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
from urllib.request import urlopen
from string import ascii_uppercase
from openpyxl import load_workbook
import xlsxwriter
import requests
import json


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
    writer = pd.ExcelWriter('Output Data'+str(ii+1)+'.xlsx')
    DF_HAZARD_CURVES.to_excel(writer,'Hazard Curves',startrow=4)
   
 
    
    ### ---------- DEAGGREGATION ---------- ###
    
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
    
    # Seperating bfault_gr and bfault_ch
    list = (lx.loc[lx['source'].str.contains("bFault")]).index
     
    # Seperating both dataframes
    bFault_ch=lx[list[0]:list[1]]
    bFault_gr=lx[list[1]:]
    
    # Dropping nan values
    bFault_ch = bFault_ch.dropna()
    bFault_gr = bFault_gr.dropna()
     
    # Resetting indexes
    bFault_gr = bFault_gr.reset_index(drop=True)
    bFault_ch = bFault_ch.reset_index(drop=True)
    
    # Number of rows in each dataframe
    len_ch=len(bFault_ch.index)
    len_gr=len(bFault_gr.index)
  
    bFault_gr.to_excel(writer,sheet_name= 'Deaggregation',startrow=2)
    bFault_ch.to_excel(writer,sheet_name= 'Deaggregation',startrow=(len_gr+6))
    writer.save()
	
    import openpyxl
    xfile = openpyxl.load_workbook('Output Data'+str(ii+1)+'.xlsx')
    sheet = xfile.get_sheet_by_name('Deaggregation')
    sheet['A2'] = 'bFault_gr'
    sheet['A'+ str(len_gr + 6)] = 'bFault_ch'
    xfile.save('Output Data'+str(ii+1)+'.xlsx')
    
    sheet = xfile.get_sheet_by_name('Hazard Curves')
    sheet['A1'] = 'Latitude'
    sheet['B1'] =  lm['Latitude'][0]
    sheet['A2'] = 'Longitude'
    sheet['B2'] =  lm['Longitude'][0]
    sheet['A3'] = 'Vs30'
    sheet['B3'] =  lm['vs30'][0]
    
    xfile.save('Output Data'+str(ii+1)+'.xlsx')
    
    ### Clearing selected variables in Variable explorer
    del lm 
    del params
    del response1
    del response2
    del DF_HAZARD_CURVES
    del writer
    del data
    del lx
    del list
    del bFault_ch
    del bFault_gr