import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
import mne
from os.path import join
import scipy

import matplotlib
matplotlib.use('Qt5Agg')

def plot_LFP_artifact_channel(
    session_ID: str,
    timescale: np.ndarray,
    data: np.ndarray, 
    color: str,
    saving_path: str,
    saving_folder = True
    ):

    """
    Plots the selected intracranial channel for 
    quick visualization (and saving).

    Input:
        - session_ID: str, the session ID
        - timescale: np.ndarray, the timescale of the signal to be plotted
        - data: np.ndarray, single channel containing datapoints
        - color: str, the color of the signal on the plot
        - saving_path: str, the folder where the plot has to be saved
        - saving_folder: Boolean, default = True, plots are automatically saved
    """

    figure(figsize=(12, 6), dpi=80)
    plt.plot(
        timescale, 
        data, 
        linewidth = 1, 
        color = color
    )
    plt.xlabel('Time (s)')
    plt.title(str(session_ID))
    plt.ylabel('Intracerebral LFP channel (µV)')

    if saving_folder:
        plt.savefig((join(
            saving_path, 
            'Fig4-Intracranial channel raw plot.png')),
            bbox_inches='tight'
            )




### Plot a single channel with its associated timescale ###

def plot_BIP_artifact_channel(
    session_ID: str,
    timescale: np.ndarray,
    data: np.ndarray, 
    color: str,
    saving_path: str,
    saving_folder = True
    ):

    """
    Plots the external bipolar channel for quick visualization (and saving).

    Input:
        - session_ID: str, the subject ID
        - timescale: np.ndarray, the timescale of the signal to be plotted
        - data: np.ndarray, single channel containing datapoints
        - color: str, the color of the signal on the plot
        - saving_path: str, the folder where the plot has to be saved
        - saving_folder: Boolean, default = True, plots automatically saved
    """

    figure(figsize=(12, 6), dpi=80)
    plt.plot(
        timescale, 
        data, 
        linewidth=1, 
        color=color
    )
    plt.xlabel('Time (s)')
    plt.title(str(session_ID))
    plt.ylabel('External bipolar channel - voltage (mV)')

    if saving_folder:
        plt.savefig((join(
            saving_path, 
            'Fig1-External bipolar channel raw plot.png')),
            bbox_inches='tight'
            )



### Plot both hemisphere LFP activity with stimulation amplitude ###

def plot_LFP_stim(
    session_ID: str,
    timescale: np.ndarray,
    LFP_rec: mne.io.array.array.RawArray,
    saving_path: str,
    saving_folder = True
    ):
    
    """
    Function that plots together the LFP and 
    the stimulation from the 2 hemispheres.

    Input:
        - session_ID: str, the subject ID
        - timescale: np.ndarray, the timescale of the signal to be plotted
        - LFP_rec: mne.io.array.array.RawArray (LFP recording as MNE object)
        - saving_path: str, the folder where the plot has to be saved
        - saving_folder: Boolean, default = True, plots automatically saved

    
    Returns:
        - the plotted signal with the stim
    """

    LFP_L_channel = LFP_rec.get_data()[0]
    LFP_R_channel = LFP_rec.get_data()[1]
    stim_L_channel = LFP_rec.get_data()[4]
    stim_R_channel = LFP_rec.get_data()[5]
    figure(figsize=(12, 6), dpi=80)
    fig, (ax1, ax2, ax3, ax4) = plt.subplots(4,1)
    ax1.set_title(str(session_ID))
    ax1.plot(
        timescale, 
        LFP_L_channel, 
        linewidth = 1, 
        color = 'darkorange'
        )
    ax2.plot(
        timescale, 
        stim_L_channel, 
        linewidth = 1, 
        color = 'darkorange', 
        Linestyle = 'dashed'
        )
    ax3.plot(
        timescale, 
        LFP_R_channel, 
        linewidth = 1, 
        color = 'purple'
        )
    ax4.plot(
        timescale, 
        stim_R_channel, 
        linewidth = 1, 
        color = 'purple',
        linestyle = 'dashed'
        )
    ax1.axes.xaxis.set_ticklabels([])
    ax2.axes.xaxis.set_ticklabels([])
    ax3.axes.xaxis.set_ticklabels([])
    ax1.set_ylabel('LFP \n left (µV)')
    ax2.set_ylabel('stim \n left (mA)')
    ax3.set_ylabel('LFP \n right (µV)')
    ax4.set_ylabel('stim \n right (mA)')
    ax1.set_ylim(min(LFP_L_channel) - 50, max(LFP_L_channel) + 50)
    ax2.set_ylim(0, max(stim_L_channel) + 0.5)
    ax3.set_ylim(min(LFP_R_channel) - 50, max(LFP_R_channel) + 50)
    ax4.set_ylim(0, max(stim_R_channel) + 0.5)
    plt.xlabel('Time (s)')
    fig.tight_layout()

    if saving_folder:
        plt.savefig((join(
            saving_path, 
            'LFP and stim bilateral - raw plot.png')),
            bbox_inches = 'tight'
            )
    return plt.gcf()


### Plot a single channel with its associated timescale ###

def plot_channel(
    session_ID: str,
    timescale: np.ndarray,
    data: np.ndarray, 
    color: str,
    scatter = False
    ):

    """
    Plots the selected channel for quick visualization (and saving).

    Input:
        - session_ID: str, the subject ID
        - timescale: np.ndarray, the timescale of the signal to be plotted
        - data: np.ndarray, single channel containing datapoints
        - color: str, the color of the signal on the plot
        - scatter: Boolean, if the user wants to see the 
        samples instead of a continuous line
    
    Returns:
        - the plotted signal
    """

    figure(figsize=(12, 6), dpi=80)
    if scatter:
        plt.scatter(
            timescale, 
            data, 
            color = color
            )
    else:
        plt.plot(
            timescale, 
            data, 
            linewidth = 1, 
            color = color
            )
    plt.xlabel('Time (s)')
    plt.title(str(session_ID))

    return plt.gcf()




def plot_LFP_external(
        session_ID: str, 
        LFP_synchronized, 
        external_synchronized, 
        sf_LFP: int, 
        sf_external: int, 
        ch_idx_lfp: int, 
        ch_index_external: int, 
        saving_path: str
        ):
    
    """
    This function can be used to quickly plot the synchronized signals
    to check for artifacts and verify that they are aligned after
    synchronization.

    Inputs:
        - session_ID: str, the subject ID
        - LFP_synchronized: pd.DataFrame, the synchronized LFP signal
        - external_synchronized: pd.DataFrame, the synchronized external signal
        - sf_LFP: int, the sampling frequency of the LFP signal
        - sf_external: int, the sampling frequency of the external signal
        - ch_idx_lfp: int, the index of the LFP channel
        - ch_index_external: int, the index of the external channel
        - saving_path: str, the folder where the plot has to be saved

    Returns:
        - the plot of the synchronized signals
    """


    # Reselect artifact channels in the aligned (= cropped) files
    if type(ch_idx_lfp) == float: ch_idx_lfp = int(ch_idx_lfp)

    LFP_channel_offset = LFP_synchronized[:,ch_idx_lfp]
    BIP_channel_offset = external_synchronized[:,ch_index_external]

     # pre-processing of external bipolar channel :
    b, a = scipy.signal.butter(1, 0.05, 'highpass')
    filtered_external_offset = scipy.signal.filtfilt(b, a, BIP_channel_offset)

    # Generate new timescales:
    LFP_timescale_offset_s = np.arange(0,
                                       (len(LFP_channel_offset)/sf_LFP),
                                       1/sf_LFP
                                       )
    external_timescale_offset_s = np.arange(0,
                                            (len(BIP_channel_offset)/sf_external),
                                            1/sf_external
                                            )

    # PLOT 8: Both signals aligned with all their artifacts detected:
    fig, ax1 = plt.subplots()
    fig.suptitle(str(session_ID))
    fig.set_figheight(6)
    fig.set_figwidth(12)
    ax1.set_xlabel('Time (s)')
    ax1.set_ylabel('Intracerebral LFP channel (µV)')
    ax1.set_xlim(0,len(LFP_channel_offset)/sf_LFP) 
    ax1.plot(
        LFP_timescale_offset_s,
        LFP_channel_offset,
        color = 'darkorange',
        zorder = 1, 
        linewidth = 0.3
        )
    ax2 = ax1.twinx()
    ax2.plot(
        external_timescale_offset_s,
        filtered_external_offset,
        color = 'darkcyan',
        zorder = 1,
        linewidth = 0.1
        )
    ax2.set_ylabel('External bipolar channel (mV)')
    
        
    fig.savefig(join(
        saving_path,
        ('Fig8-Intracranial and external recordings aligned.png')),
        bbox_inches = 'tight'
        )
    plt.show(block=True)




import json

def ecg(
        session_ID: str, 
        LFP_synchronized: pd.DataFrame, 
        sf_LFP: int,
        external_synchronized: pd.DataFrame,
        sf_external: int,
        saving_path: str,
        xmin: float,
        xmax: float
):
    """
    This function can be used to quickly plot the beginning of the signal
    to check for cardiac artifacts and verify that they are aligned after 
    synchronization.

    Inputs:
        - session_ID: str, the subject ID
        - LFP_synchronized: pd.DataFrame, the synchronized LFP signal
        - sf_LFP: int, the sampling frequency of the LFP signal
        - external_synchronized: pd.DataFrame, the synchronized external signal
        - sf_external: int, the sampling frequency of the external signal
        - saving_path: str, the folder where the plot has to be saved
        - xmin: float, the timestamp to start the plot
        - xmax: float, the timestamp to end the plot

    Returns:
        - the plot of the synchronized signals (zoom on the beginning)
    """

    #import settings
    json_filename = (join(saving_path, 'parameters_' + str(session_ID) + '.json'))
    with open( json_filename, 'r') as f:
        loaded_dict =  json.load(f)

    # Reselect artifact channels in the aligned (= cropped) files
    LFP_channel_offset = LFP_synchronized[:, loaded_dict['CH_IDX_LFP']] 
    BIP_channel_offset = external_synchronized[:, loaded_dict['CH_IDX_EXTERNAL']]


    # Generate new timescales:
    LFP_timescale_offset_s = np.arange(0, 
                                       (len(LFP_channel_offset)/sf_LFP), 
                                       1/sf_LFP
                                       )
    external_timescale_offset_s = np.arange(0, 
                                            (len(BIP_channel_offset)/sf_external), 
                                            1/sf_external
                                            )

    #make plot on beginning of recordings:
    fig, (ax1, ax2) = plt.subplots(2,1)
    fig.suptitle(str(loaded_dict['SUBJECT_ID']))
    fig.set_figheight(6)
    fig.set_figwidth(18)
    ax1.axes.xaxis.set_ticklabels([])
    ax2.set_xlabel('Time (s)')
    ax1.set_ylabel('Intracerebral LFP channel (µV)')
    ax2.set_ylabel('External bipolar channel (mV)')
    ax1.set_xlim(xmin, xmax) 
    ax2.set_xlim(xmin, xmax)
    ax1.set_ylim(-50, 50)
    ax1.plot(
        LFP_timescale_offset_s, 
        LFP_channel_offset, 
        color = 'darkorange', 
        zorder = 1, 
        linewidth = 1
        )
    ax2.plot(
        external_timescale_offset_s,
        BIP_channel_offset, 
        color = 'darkcyan', 
        zorder = 1, 
        linewidth = 1
        ) 
    fig.savefig((join(saving_path, 'Fig_ECG.png')), bbox_inches='tight')

