# -*- coding: utf-8 -*-
"""
Created on Tue Nov 16 09:17:58 2021

@author: Kevin D.
"""

import streamlit as st
import numpy as np
from matplotlib import pyplot as plt
#import pyautogui
import nmrglue as ng
from matplotlib.ticker import FormatStrFormatter
#from random import randint
#import SessionState

header = st.container()
info = st.container()
reset = st.container()
upload = st.container()
plot_setup = st.container()
plot = st.container()


#session_state = SessionState.get(state=0)


with header:
    st.title('Plot your CASPER data with this app!')
    
    
with info:
    st.subheader('Introduction')
    st.text('Upload your experimental and predicted NMR chemical shifts as .txt files.')
    st.text('The files should have the format: 13C space 1H, eg. 101.50 4.65.')
    st.text('Use a new line for each signal.')
    st.text('An example file can be downloaded by clicking the button below.')

    st.download_button(label='Download example file', file_name='shifts.txt')
    
#    if info.button('Clear the Files and reset the app.', help="Resets the app."):
        #session_state.state = str(randint(1000, 100000000))

    st.subheader('Upload your files below!')
    
with upload:
    left_col, right_col = st.columns(2)
    
    
    
        
    exp_data_upload = left_col.file_uploader('Upload experimental NMR Chemical Shifts', type=['txt'], accept_multiple_files=False, key='exp_data', help='Here you can upload '
                            'your experimental NMR chemical shifts')
    
    
    
    pred_data_upload = right_col.file_uploader('Upload predicted NMR Chemical Shifts', type=['txt'], accept_multiple_files=False, key='pred_data', help='Here you can upload '
                            'your predicted NMR chemical shifts')
    
    
    
    #st.write(type(exp_data))
    #st.write(type(pred_data_upload))

if exp_data_upload and pred_data_upload is not None:

    with plot_setup:
        st.subheader('Please specify the plotting option below.')
        location_legend = plot.selectbox('Where should the legend be displayed?', ('upper left', 'upper center', 'upper right', 'lower left', 'lower center', 'lower right'))
        x_values = st.slider('Select your ppm range in proton.', 0.0, 10.0, (6.0,3.0), step=0.05)
        y_values = st.slider('Select your ppm range in carbon.', 0, 120, (110,0), step=1)
        
        
        
    with plot:
        
        exp_data = np.recfromtxt(exp_data_upload)
        pred_data = np.recfromtxt(pred_data_upload)
        
        udic = {
        'ndim': 2,
        0: {'car': 1700.00,
            'complex': False,
            'encoding': 'states',
            'freq': True,
            'label': '13C',
            'obs': 150.0,
            'size': 512,
            'sw': 30000,
            'time': False},
        1: {'car': 5000.00,
            'complex': False,
            'encoding': 'direct',
            'freq': True,
            'label': '1H',
            'obs': 600.0,
            'size': 1024,
            'sw': 8000,
            'time': False}
        }
        
        #amps
        ampl = [100.0]
    
        fnames = [exp_data, pred_data]
        save_list = ['exp.ucsf', 'casper.ucsf']
        
        # loop over the files and colors
        for fname, save in zip(fnames, save_list):
        
            dic = ng.sparky.create_dic(udic)
            data = np.empty((512, 1024), dtype='float32')
        
            # read in the peak list
            peak_list = fname
            npeaks = len(peak_list)
        
            # convert the peak list from PPM to points
            uc_13C = ng.sparky.make_uc(dic, None, 0)
            uc_1H = ng.sparky.make_uc(dic, None, 1)
        
            lw_13C = 1.0    # 13C dimension linewidth in points
            lw_1H = 3.0    # 1H dimension linewidth in points
        
            params = []
            for ppm_13C, ppm_1H in peak_list:
                pts_13C = uc_13C.f(ppm_13C, 'ppm')
                pts_1H = uc_1H.f(ppm_1H, 'ppm')
                params.append([(pts_13C, lw_13C), (pts_1H, lw_1H)])
        
            # simulate the spectrum
            shape = (512, 1024)      # size should match the dictionary size
            lineshapes = ('g', 'g')  # gaussian in both dimensions
            amps = ampl * npeaks
            data = ng.linesh.sim_NDregion(shape, lineshapes, params, amps)
        
            # save the spectrum
            ng.sparky.write(save, dic, data.astype('float32'), overwrite=True)
        
        
        #plot spectra
            
        # contour levels
        contour_start = 5       # contour level start value
        contour_num = 20        # number of contour levels
        contour_factor = 1.30   # scaling factor between contour levels
        cl = contour_start * contour_factor ** np.arange(contour_num)
        
        # create the figure
        fig = plt.figure()
        ax = fig.add_subplot(111)
        
        dic, data = ng.sparky.read('exp.ucsf')
        dic_1, data_1 = ng.sparky.read('casper.ucsf')
        
        uc_x = ng.sparky.make_uc(dic, data, dim=1)
        x0, x1 = uc_x.ppm_limits()
        uc_y = ng.sparky.make_uc(dic, data, dim=0)
        y0, y1 = uc_y.ppm_limits()
        
        cntr1 = ax.contour(data, cl, colors='blue', extent=(x0, x1, y0, y1), linewidths=.2, alpha=.7)
        cntr2 = ax.contour(data_1, cl, colors='red', extent=(x0, x1, y0, y1), linewidths=.2, alpha=.7)
        h1,_ = cntr1.legend_elements()
        h2,_ = cntr2.legend_elements()
        leg = ax.legend([h1[0], h2[0]], ['Experimental', 'CASPER'], loc=location_legend, framealpha=.5, fancybox=True)
        
        
        # decorate the axes and set limits
        ax.set_ylabel(r"$^{13}$" + "C /ppm")
        ax.set_xlabel(r"$^1$" + "H /ppm")
        ax.set_xlim(x_values[1], x_values[0])
        ax.set_ylim(y_values[1], y_values[0])
        ax.xaxis.set_major_formatter(FormatStrFormatter('%.2f'))    
        
        for line in leg.get_lines():
            line.set_linewidth(3.0)
        
        
        st.write(fig)
        plt.savefig('plot.png', dpi=600)
        plt.savefig('plot.svg', dpi=600)
        
        
        with open('plot.png', 'rb') as file:
            btn = st.download_button(label='Download plot as png.',
                                     data=file,
                                     file_name='plot.png',
                                     mime='image/png')

        with open('plot.svg', 'rb') as file:
            btn = st.download_button(label='Download plot as svg.',
                                     data=file,
                                     file_name='plot.svg',
                                     mime='image/svg')        
      
else:
    st.subheader('No data uploaded. Please upload your data.')
    
    


    
    
    
    

