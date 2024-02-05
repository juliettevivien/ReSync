import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from os.path import join
import scipy

from interactive import select_sample
from utils import _update_and_save_params

def check_timeshift(
        session_ID: str, 
        LFP_synchronized, 
        sf_LFP, 
        external_synchronized, 
        sf_external, 
        saving_path: str
        ):

    """
    Check the timeshift between the intracranial and external recordings after
    synchronization. As the two recording systems are different, it may happen
    that the internal clocks are not completely identical. This function allows
    to check this and to warn in case of a large timeshift.
    To do so, the function plots the intracranial recording and the external one.
    On each plot, the user is asked to select the sample corresponding to the
    last artifact in the recording. The function then computes the time difference
    between the two times. If the difference is large, it may indicate a problem
    in the recording, such as a packet loss in the intracranial recording.

    Inputs:
        - session_ID: str, the subject ID
        - LFP_synchronized: pd.DataFrame, the intracranial recording containing all
        recorded channels
        - sf_LFP: sampling frequency of intracranial recording
        - external_synchronized: pd.DataFrame, the external recording containing all
        recorded channels
        - sf_external: sampling frequency of external recording
        - saving_path: str, path to the folder where the parameters.json file is
        saved

    """

    #import settings
    json_filename = (saving_path + '\\parameters_' + str(session_ID) + '.json')
    with open( json_filename, 'r') as f:
        loaded_dict =  json.load(f)
    
    LFP_channel_offset = LFP_synchronized[:,loaded_dict["CH_IDX_LFP"]]
    print(len(LFP_channel_offset))
    BIP_channel_offset = external_synchronized[:,loaded_dict["CH_IDX_EXTERNAL"]]
    print(len(BIP_channel_offset))

    # Generate new timescales:
    LFP_timescale_offset_s = np.arange(
        start = 0, 
        stop = len(LFP_channel_offset)/sf_LFP, 
        step = 1/sf_LFP
        )
    external_timescale_offset_s = np.arange(
        start = 0, 
        stop = len(external_synchronized)/sf_external, 
        step = 1/sf_external
        )

    # detrend external recording with high-pass filter before processing:
    b, a = scipy.signal.butter(1, 0.05, 'highpass')
    filtered_external_offset = scipy.signal.filtfilt(b, a, BIP_channel_offset)


    print ('Select the first sample of the last artifact in the intracranial recording')
    last_artifact_lfp_x = select_sample(
        signal = LFP_channel_offset, 
        sf = sf_LFP,
        color1 = 'peachpuff',
        color2 = 'darkorange'
        )
    print ('Select the first sample of the last artifact in the external recording')
    last_artifact_external_x = select_sample(
        signal = filtered_external_offset, 
        sf = sf_external,
        color1 = 'paleturquoise',
        color2 = 'darkcyan'
        ) 

    timeshift_ms = (last_artifact_external_x - last_artifact_lfp_x)*1000

    _update_and_save_params(
        key = "TIMESHIFT", 
        value = timeshift_ms, 
        session_ID = session_ID, 
        saving_path = saving_path
        )
    _update_and_save_params(
        key = "REC DURATION FOR TIMESHIFT", 
        value = last_artifact_external_x, 
        session_ID = session_ID, 
        saving_path = saving_path
        )

    if abs(timeshift_ms) > 100:
        print('WARNING: the timeshift is unusually high,' 
              'consider checking for packet loss in LFP data.')


    fig, (ax1, ax2) = plt.subplots(2, 1)
    fig.suptitle(str(session_ID))
    fig.set_figheight(12)
    fig.set_figwidth(6)
    ax1.axes.xaxis.set_ticklabels([])
    ax2.set_xlabel('Time (s)')
    ax1.set_ylabel('Intracranial LFP channel (µV)')
    ax2.set_ylabel('External bipolar channel (mV)')
    ax1.set_xlim(last_artifact_external_x - 0.1, last_artifact_external_x + 0.1) 
    ax2.set_xlim(last_artifact_external_x - 0.1, last_artifact_external_x + 0.1)
    ax1.plot(
        LFP_timescale_offset_s, 
        LFP_channel_offset, 
        color = 'peachpuff',
        zorder = 1
        )
    ax1.scatter(
        LFP_timescale_offset_s, 
        LFP_channel_offset, 
        color = 'darkorange', 
        s = 4, 
        zorder = 2
        ) 
    ax1.axvline(
        x = last_artifact_lfp_x, 
        ymin = min(LFP_channel_offset), 
        ymax = max(LFP_channel_offset), 
        color = 'black', 
        linestyle = 'dashed',
        alpha = .3
        )
    ax2.plot(
        external_timescale_offset_s, 
        filtered_external_offset, 
        color = 'paleturquoise', 
        zorder = 1
        ) 
    ax2.scatter(
        external_timescale_offset_s, 
        filtered_external_offset, 
        color = 'darkcyan', 
        s = 4, 
        zorder = 2
        ) 
    ax2.axvline(
        x = last_artifact_external_x, 
        color = 'black', 
        linestyle = 'dashed',
        alpha = .3
        )
    ax1.text(
        0.05, 
        0.85, 
        s = 'delay intra/exter: ' 
        + str(round(timeshift_ms, 2)) 
        + 'ms', 
        fontsize = 14, 
        transform = ax1.transAxes
        )
       
    plt.gcf()
    plt.show(block=True)
    fig.savefig(join(
        saving_path,
        'FigA-Timeshift - Intracranial and external recordings aligned - last artifact.png'), 
        bbox_inches = 'tight', 
        dpi = 1200
        )

