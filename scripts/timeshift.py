import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from utils import _filtering
from interactive import select_sample
from utils import _update_and_save_params

def check_timeshift(
        session_ID: str, 
        LFP_df_offset: pd.DataFrame, 
        sf_LFP, 
        external_df_offset: pd.DataFrame, 
        sf_external, 
        saving_path: str, 
        SHOW_FIGURES: bool = True
        ):

    """
    Check the timeshift between the intracerebral and external recordings after
    synchronization. As the two recording systems are different, it may happen
    that the internal clocks are not completely identical. This function allows
    to check this and to warn in case of a large timeshift.
    To do so, the function plots the intracerebral recording and the external one.
    On each plot, the user is asked to select the sample corresponding to the
    last artifact in the recording. The function then computes the time difference
    between the two times. If the difference is large, it may indicate a problem
    in the recording, such as a packet loss in the intracerebral recording.

    Inputs:
        - session_ID: str, the subject ID
        - LFP_df_offset: pd.DataFrame, the intracerebral recording containing all
        recorded channels
        - sf_LFP: sampling frequency of intracranial recording
        - external_df_offset: pd.DataFrame, the external recording containing all
        recorded channels
        - sf_external: sampling frequency of external recording
        - saving_path: str, path to the folder where the parameters.json file is
        saved
        - SHOW_FIGURES: bool = True

    """

    #import settings
    json_filename = (saving_path + '\\parameters_' + str(session_ID) + '.json')
    with open( json_filename, 'r') as f:
        loaded_dict =  json.load(f)

    # Reselect artifact channels in the aligned (= cropped) files:
    LFP_channel_offset = LFP_df_offset.iloc[:, 
                                            loaded_dict["CH_IDX_LFP"]].to_numpy()  
    BIP_channel_offset = external_df_offset.iloc[:, 
                                                 loaded_dict["CH_IDX_EXTERNAL"]].to_numpy() 

    # Generate new timescales:
    LFP_timescale_offset_s = np.arange(
        start=0, 
        stop=len(LFP_channel_offset)/sf_LFP, 
        step=1/sf_LFP
    )
    external_timescale_offset_s = np.arange(
        start=0, 
        stop=len(external_df_offset)/sf_external, 
        step=1/sf_external
    )

    # detrend external recording with high-pass filter before processing:
    filtered_external_offset = _filtering(BIP_channel_offset)

    print ('Select the sample corresponding to the last artifact in the intracranial recording')
    last_artifact_lfp_x = select_sample(LFP_channel_offset, sf_LFP)
    print ('Select the sample corresponding to the last artifact in the external recording')
    last_artifact_external_x = select_sample(filtered_external_offset, sf_external) 

    timeshift_ms = (last_artifact_external_x - last_artifact_lfp_x)*1000

    _update_and_save_params("TIMESHIFT", timeshift_ms, session_ID, saving_path)
    _update_and_save_params("REC DURATION FOR TIMESHIFT", 
                            last_artifact_external_x, session_ID, saving_path)

    if abs(timeshift_ms) > 100:
        print('WARNING: the timeshift is unusually high,' 
              'consider checking for packet loss in LFP data.')


    fig, (ax1, ax2) = plt.subplots(2, 1)
    fig.suptitle(str(session_ID))
    fig.set_figheight(12)
    fig.set_figwidth(6)
    ax1.axes.xaxis.set_ticklabels([])
    ax2.set_xlabel('Time (s)')
    ax1.set_ylabel('Intracerebral LFP channel (µV)')
    ax2.set_ylabel('External bipolar channel (mV)')
    ax1.set_xlim(last_artifact_external_x - 0.1, last_artifact_external_x + 0.1) 
    ax2.set_xlim(last_artifact_external_x - 0.1, last_artifact_external_x + 0.1)
    ax1.plot(LFP_timescale_offset_s, LFP_channel_offset, color='peachpuff', 
             zorder=1)
    ax1.scatter(LFP_timescale_offset_s, LFP_channel_offset, color='darkorange', 
                s=4, zorder=2) 
    ax1.axvline(x=last_artifact_lfp_x, ymin=min(LFP_channel_offset), 
                ymax=max(LFP_channel_offset), color='black', linestyle='dashed', 
                alpha=.3)
    ax2.plot(external_timescale_offset_s, filtered_external_offset, 
             color='paleturquoise', zorder=1) 
    ax2.scatter(external_timescale_offset_s, filtered_external_offset, 
                color='darkcyan', s=4, zorder=2) 
    ax2.axvline(x=last_artifact_external_x, color='black', linestyle='dashed', 
                alpha=.3)
    ax1.text(0.05, 0.85, s='delay intra/exter: ' + str(round(timeshift_ms, 2)) 
             + 'ms', fontsize=14, transform=ax1.transAxes)
       
    plt.gcf()
    fig.savefig(saving_path 
                + '\\FigA-Timeshift_Intracerebral and external recordings aligned_last artifact.png', 
                bbox_inches='tight', dpi=1200)

    if SHOW_FIGURES: 
        plt.show(block=False)
    else: 
        plt.close()

