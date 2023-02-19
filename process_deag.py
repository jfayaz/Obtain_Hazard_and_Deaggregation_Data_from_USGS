# -*- coding: utf-8 -*-
"""
author : JAWAD FAYAZ (email: jfayaz@uci.edu)
visit: (https://jfayaz.github.io)
"""
from urllib.request import urlopen
import pandas as pd
import numpy as np
import json

def url_resp_values_deag(url_final):
    #deagg capture responses
    # Opening url
    #print(url_final)
    deag_response =  urlopen(url_final)
    # Converting response to str format
    response_1 = deag_response.read() 
    deag_response.close()
    return response_1

def url_deag_process(lm,sfmt,sfmt_2):
    ### ---------- HAZARD CURVES ---------- ###
    Deag_data_avaliable = 'No'
    lm['vs30']    = np.int(lm['vs30'])
    k,urls = checking_deag_urls(lm,sfmt,sfmt_2)
    print(urls)
    if k == 0:
        Deag_data_avaliable = 'No'
        print('\nNo Response from USGS for Deaggregation')
        print('\nUSGS Server Busy! No Response from USGS. Please try again after sometime.')
        return Deag_data_avaliable,0
    else:
        params_deag    = lm.apply(lambda x: sfmt(**x), 1)
        for i,row in enumerate(params_deag.values):
            url_deag = urls + row
        response_deag = url_resp_values_deag(url_deag)
        data = json.loads(response_deag)
        if data['status'] == 'success':
            Deag_data_avaliable = 'Yes'
            return Deag_data_avaliable,data
        else:
            print('\nNo Response from USGS for Deaggregation')
            print('\nUSGS Server Busy! No Response from USGS. Please try again after sometime.')
            return Deag_data_avaliable,0
            
            
def checking_deag_urls(lm,sfmt,sfmt_2):
    url_responses = {}
    data = pd.DataFrame()
    url_head = ["https://earthquake.usgs.gov/nshmp-haz-ws/deagg/"]
    url_tail_1 = list(lm.apply(lambda x: sfmt(**x), 1))
    url_tail_2 = list(lm.apply(lambda x: sfmt_2(**x), 1))
    urls = {1:url_head[0]+url_tail_1[0],2:url_head[0]+url_tail_2[0]}
    for i in range(1,3):
        data = pd.DataFrame()
        #print("\n\n Checking deaggregation URL:", i)
        #print(urls[i])
        df = url_resp_values_deag(urls[i])
        data = json.loads(df) 
        #print("\n Response from URL:", data['status'])
        url_responses.update({i:data['status']})
    for k, v in url_responses.items():
        if "success" == v and k in (1,3):
            return k,url_head[0]
        else:
            return 0,url_head[0]