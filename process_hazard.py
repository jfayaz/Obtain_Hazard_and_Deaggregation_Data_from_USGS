# -*- coding: utf-8 -*-
"""
author : JAWAD FAYAZ (email: jfayaz@uci.edu)
visit: (https://jfayaz.github.io)
"""
from requests import get
import pandas as pd


def url_resp_values_haz(url_final):
    #hazard  capture response 
    #print(url_final)
    # Opening url
    r = get(url_final)
    data = r.json()
    return data
    
                    
def url_haz_process(df,lm,imt_list,sfmt,sfmt_2,DF_Cols):
    ### ---------- HAZARD CURVES ---------- ###
    global Plot_Hazard_Curves
    k,urls = checking_hazard_urls(lm,sfmt,sfmt_2)
    if k == 0:
        Plot_Hazard_Curves = 'No'
        print('\nUSGS Server Busy! No Response from USGS. Please try again after sometime.')
        return Plot_Hazard_Curves,0
    else:
        Plot_Hazard_Curves = 'Yes'
        for j in range(0,len(imt_list)):
            lm['imt'] = imt_list[j]
            lm['vs30'] = lm['vs30'].astype(int)
            params = ""
            params     = lm.apply(lambda x: sfmt(**x), 1)
            url_hazard = urls+params[0]
            data = url_resp_values_haz(url_hazard)
            if data['status'] == 'success':
                response1 = {'xvalues': data['response'][0]['metadata']['xvalues']}
                response2 = {'yvalues': data['response'][0]['data'][0]['yvalues']}
                if j == 0:
                    DF_HAZARD_CURVES = pd.DataFrame.from_dict(response1)
                    DF_HAZARD_CURVES = DF_HAZARD_CURVES.rename(columns={"xvalues": "Acceleration (g)"})
                DF_HAZARD_CURVES = pd.concat([DF_HAZARD_CURVES, pd.DataFrame.from_dict(response2)], axis=1)
                DF_HAZARD_CURVES = DF_HAZARD_CURVES.rename(columns={"yvalues": DF_Cols[j]})
        return Plot_Hazard_Curves,DF_HAZARD_CURVES

def checking_hazard_urls(lm,sfmt,sfmt_2):
    url_responses = {}
    data = pd.DataFrame()
    url_head = ["https://earthquake.usgs.gov/nshmp-haz-ws/hazard/","https://prod01-earthquake.cr.usgs.gov/nshmp-haz-ws/hazard/"]
    url_tail_1 = list(lm.apply(lambda x: sfmt(**x), 1))
    url_tail_2 = list(lm.apply(lambda x: sfmt_2(**x), 1))
    urls = {1:url_head[0]+url_tail_1[0],2:url_head[0]+url_tail_2[0],3:url_head[1]+url_tail_1[0],4:url_head[1]+url_tail_2[0]}
    for i in range(1,5):
        data = pd.DataFrame()
        #print("\n\n Checking Hazard URL:", i)
        data = url_resp_values_haz(urls[i])
        #print("\n Response from URL:", data['status'])
        url_responses.update({i:data['status']})
    for k, v in url_responses.items():
        if "success" == v and k in (1,3):
            return k,url_head[0]
        elif "success" == v and k in (2,4):
            return k,url_head[1]
        else:
            return 0,url_head[0]
        
    