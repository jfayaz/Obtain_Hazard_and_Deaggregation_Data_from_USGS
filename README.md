# Obtain Hazard and Deaggregation Data from USGS

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
The input data must be provided in form of Excel file as per the given 'Input Data.xlsx' file. The name of the excel file must be kept as 'Input Data.xlsx'. Row 1 of the file must contain the titles as follows:

        Edition	Region	Longitude	Latitude    Period	vs30	Return Period
   

The input data must be provided starting from row 2 of the sheet with the required values under each title. More than 1 rows can be provided as the data 

    E.g. the example file 'Input Data.xlsx' contains input for 2 sites 

Following are the options that can be provided under each title:   
    
    Edition (USGS edition)      :   '2008' , '2014'
    
    Region                      :   'COUS', 'WUS', 'CEUS'  ; {WUS: Western US, CEUS: Central Eastern US}
    
    Longitude                   :    Longitude of the Site
    
    Latitude                    :    Latitude of the Site
    
    Period                      :    First Mode Period of the Structure (sec) (Downloads PGA if Period = 0)
    Note: Closest results to the available USGS periods will be provided. USGS has results only for PGA, SA @ 0.2 sec, SA @ 1.0 sec, SA @ 2 sec     
    
    vs30 (Shear-Wave Velocity)  :    Shear wave velocity at 30 meters at the site (m/s)
    Note: Closest results to the available USGS vs30s will be provided. USGS has results only for '180', '259', '360', '537', '760', '1150' ; {in m/s , restricted to only these values}
    
    Return Period (Hazard)      :    Return Period Hazard (in years)
    Note: Closest results to the available USGS Hazard Levels will be provided. USGS has results only for '475', '975', '2475'


OUTPUT:
The output will be provided in a saperate Excel file 'Output Data.xlsx' for each input. The file will contain 2 sheets:

    1) 'Hazard Curves' sheet will contain information about the Hazard Curves at 0.2 sec, 1 sec and 2 secs. The output will have titles:
                Acceleration (g)	lambda PGA	 lambda Sa at 0.2 sec	 lambda Sa at 1 sec	  lambda Sa at 2 sec


    2) 'Deaggregation' sheet will contain information about the deaggregation of the site at given imt level. The output will have two saparate tables showing the deaggregation of faults from 'Gutenberg-Richter (gr)' and 'Characteristic (ch)' branches of the USGS logic tree. They both must be added weightedly to attain total deaggregation. Each table will have titles:
                source	r	m	ε	longitude	latitude	azimuth	  % contribution


Note: If a USGS branch other than 'afault' and 'bfault' is used in deaggregation, the results wont be provided for now! You are welcome to make the additions to the code to make it more exhaustive
