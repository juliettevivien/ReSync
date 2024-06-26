import numpy as np
from scipy.signal import find_peaks
from itertools import compress


# Detection of artifacts in TMSi


def find_external_sync_artifact(data: np.ndarray, sf_external: int, start_index=0):
    """
    Function that finds artifacts caused by increasing/reducing
    stimulation from 0 to 1mA without ramp.
    For correct functioning, the external data recording should
    start in stim-off, and typically short pulses are given
    (without ramping). The first 2 seconds are used for threshold calculation
    and should therefore be free of any artifact.
    The signal are pre-processed previously with a high-pass
    Butterworth filter (1Hz) to ensure removal of slow drifts
    and offset around 0 (using _detrend_data function in utils.py).

    Inputs:
        - data: np.ndarray, single external channel (from bipolar electrode)
        - sf_external: int, sampling frequency of external recording
        - start_index: default is 0, which means that the function will start
            looking for artifacts from the beginning of the signal. If the
            function is called with a start_index different from 0, the function
            will start looking for artifacts from that index. This is useful when
            the recording was started in Stimulation ON or when there is another
            kind of artifact at the beginning of the recording
    Returns:
        - art_time_BIP: the timestamp where the artifact starts in external recording

    """

    """
    To be properly detected in external channel, artifacts have to look 
    like a downward deflection (they are more negative than positive). 
    If for some reason the data recorder picks up the artifact as an upward 
    deflection instead, then the signal has to be inverted before detecting 
    artifacts.
    """
    # check polarity of artifacts before detection:
    if abs(max(data[:-1000])) > abs(min(data[:-1000])):
        print("external signal is reversed")
        data = data * -1
        print("invertion undone")

    # define thresh_BIP as 1.5 times the difference between the max and min
    thresh_BIP = -1.5 * (np.ptp(data[: int(sf_external * 2)]))

    # find indexes of artifacts
    # the external sync artifact is a sharp downward deflexion repeated at a high
    # frequency (stimulation frequency). Therefore, the artifact is detected when
    # the signal is below the threshold, and when the signal is lower than the
    # previous and next sample (first peak of the artifact).

    for q in range(start_index, len(data) - 2):
        if (
            (data[q] <= thresh_BIP)
            and (data[q] < data[q + 1])
            and (data[q] < data[q - 1])
        ):
            art_time_BIP = q / sf_external
            break

    return art_time_BIP


# Detection of artifacts in LFP
def find_LFP_sync_artifact(data: np.ndarray, sf_LFP: int, use_method: str):
    """
    Function that finds artifacts caused by
    augmenting-reducing stimulation from 0 to 1mA without ramp.
    For correct functioning, the LFP data should
    start in stim-off, and typically short pulses
    are given (without ramping).
    The function can use two different methods:
    'thresh': a threshold computed on the baseline is used to detect the stim-artifact.
    '1' & '2' are 2 versions of a method using kernels. A kernel mimics the 
    stimulation artifact shape. This kernel is multiplied with time-series
    snippets of the same length. If the time-serie is
    similar to the kernel, the dot-product is high, and this
    indicates a stim-artifact.

    Input:
        - data: np.ndarray, single data channel of intracranial recording, containing
            the stimulation artifact
        - sf_LFP: int, sampling frequency of intracranial recording
        - use_method: str, '1' or '2' or 'thresh'. The kernel/method
            used to detect the stim-artifact.
                '1' is a simple kernel that only detects the steep decrease
            of the stim-artifact.
                '2' is a more complex kernel that takes into account the
            steep decrease and slow recover of the stim-artifact.
                'thresh' is a method that uses a threshold to detect
            the stim-artifact.

    Returns:
        - art_time_LFP: the timestamp where the artifact starts in the
        intracranial recording.
    """

    # checks correct input for use_kernel variable
    assert use_method in ["1", "2", "thresh"], "use_method incorrect. Should be '1', '2' or 'thresh'"

    if use_method == "thresh":
        thres_window = sf_LFP * 2
        thres = np.ptp(data[:thres_window])
        # Compute absolute value to be invariant to the polarity of the signal
        abs_data = np.abs(data)
        # Check where the data exceeds the threshold
        over_thres = np.where(abs_data > thres)[0][0]
        # Take last sample that lies within the value distribution of the thres_window before the threshold passing
        # The percentile is something that can be varied
        stim_idx = np.where(
            abs_data[:over_thres] <= np.percentile(abs_data[:over_thres], 95)
        )[0][-1]



    else:
        signal_inverted = False  # defaults false

        kernels = {
            "1": np.array([1, -1]),
            "2": np.array([1, 0, -1] + list(np.linspace(-1, 0, 20))),
        }
        ker = kernels[use_method]

        
        # get dot-products between kernel and time-serie snippets
        res = []  # store results of dot-products
        for i in np.arange(0, len(data) - len(ker)):
            res.append(ker @ data[i : i + len(ker)])
            # calculate dot-product of vectors
            # the dot-product result is high when the timeseries snippet
            # is very similar to the kernel
        res = np.array(res)  # convert list to array

        # normalise dot product results
        res = res / max(res)

        # calculate a ratio between std dev and maximum during
        # the first seconds to check whether an stim-artifact was present
        ratio_max_sd = np.max(res[: sf_LFP * 30] / np.std(res[: sf_LFP * 5]))

        # find peak of kernel dot products
        # pos_idx contains all the positive peaks, neg_idx all the negative peaks
        pos_idx = find_peaks(x=res, height=0.3 * max(res), distance=sf_LFP)[0]
        neg_idx = find_peaks(x=-res, height=-0.3 * min(res), distance=sf_LFP)[0]

        # check warn if NO STIM artifacts are suspected
        if (len(neg_idx) > 20 and ratio_max_sd < 8) or (len(pos_idx) > 20 and ratio_max_sd < 8):
            print(
                "WARNING: probably the LFP signal did NOT"
                " contain any artifacts. Many incorrect timings"
                " could be returned"
            )

        # check whether signal is inverted
        if neg_idx[0] < pos_idx[0]:
            # the first peak should be POSITIVE (this is for the dot-product results)
            # actual signal is first peak negative
            # if NEG peak before POS then signal is inverted
            print("intracranial signal is inverted")
            signal_inverted = True
            # re-check inverted for difficult cases with small pos-lfp peak
            # before negative stim-artifact
            if (
                pos_idx[0] - neg_idx[0]
            ) < 50:  # if first positive and negative are very close
                width_pos = 0
                r_i = pos_idx[0]
                while res[r_i] > (max(res) * 0.3):
                    r_i += 1
                    width_pos += 1
                width_neg = 0
                r_i = neg_idx[0]
                while res[r_i] < (min(res) * 0.3):
                    r_i += 1
                    width_neg += 1
                # undo invertion if negative dot-product (pos lfp peak) is very narrow
                if width_pos > (2 * width_neg):
                    signal_inverted = False
                    print("invertion undone")

        # return either POS or NEG peak-indices based on normal or inverted signal
        if not signal_inverted:
            stim_idx = pos_idx  # this is for 'normal' signal

        elif signal_inverted:
            stim_idx = neg_idx

        # filter out inconsistencies in peak heights (assuming sync-stim-artifacts are stable)
        abs_heights = [max(abs(data[i - 5 : i + 5])) for i in stim_idx]

        # check polarity of peak
        if not signal_inverted:
            sel_idx = np.array([min(data[i - 5 : i + 5]) for i in stim_idx]) < (
                np.median(abs_heights) * -0.5
            )
        elif signal_inverted:
            sel_idx = np.array([max(data[i - 5 : i + 5]) for i in stim_idx]) > (
                np.median(abs_heights) * 0.5
            )
        stim_idx_all = list(compress(stim_idx, sel_idx))
        stim_idx = stim_idx_all[0]

    art_time_LFP = stim_idx / sf_LFP

    return art_time_LFP
