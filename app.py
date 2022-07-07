import json
from flask import Flask
import cv2
import numpy as np
from scipy.signal import butter, convolve, find_peaks, filtfilt


app = Flask(__name__)


class NumpyEncoder(json.JSONEncoder):
    """ Special json encoder for numpy types """

    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)


def butter_highpass(cutoff, fs, order=5):
    nyq = 0.5*fs
    normal_cutoff = cutoff/nyq
    b, a = butter(order, normal_cutoff, btype='high',analog=False, output='ba')
    return b, a


def butter_lowpass(cutoff, fs, order=5):
    nyq = 0.5*fs
    normal_cutoff = cutoff/nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False, output='ba')
    return b, a


def filter_all(data, fs, order=5, cutoff_high=8, cutoff_low=25):
    b, a = butter_highpass(cutoff_high, fs, order=order)
    highpassed_signal = filtfilt(b, a, data)
    d, c = butter_lowpass(cutoff_low, fs, order=order)
    bandpassed_signal = filtfilt(d, c, highpassed_signal)
    return bandpassed_signal


def process_signal(y, order_of_bandpass, high, low, sampling_rate, average_filter_sample_length):
    filtered_signal = filter_all(
        y, sampling_rate, order_of_bandpass, high, low)
    squared_signal = filtered_signal**2
    b = (np.ones(average_filter_sample_length))/average_filter_sample_length
    a = np.ones(1)
    averaged_signal = convolve(squared_signal, b)
    averaged_signal = filtfilt(b, a, squared_signal)
    return averaged_signal


def give_bpm(r_averaged,time_bw_fram):
    r_min_peak = min(r_averaged)+(max(r_averaged)-min(r_averaged))/16
    r_peaks = find_peaks(r_averaged, height=r_min_peak)

    diff_sum = 0
    total_peaks = len(r_peaks[0])
    i = 0

    while i < total_peaks-1:
        diff_sum = diff_sum+r_peaks[0][i+1]-r_peaks[0][i]
        i = i+1

    avg_diff = diff_sum/(total_peaks-1)
    avg_time_bw_peaks = avg_diff*time_bw_fram
    bpm = 60/avg_time_bw_peaks
    print("Calculated heart rate "+str(bpm))
    return bpm


@app.route('/api', methods=['GET'])
def get_beats_per_min():
#declaring array for storing R,G,B values 
    R = np.array([])
    G = np.array([])
    B = np.array([])
    
    # Create a video capture object and read
    video_data = cv2.VideoCapture('sample/ppgdata.mp4')
    fps = video_data.get(cv2.CAP_PROP_FPS)
    frame_count = int(video_data.get(cv2.CAP_PROP_FRAME_COUNT))
    vid_length = frame_count/fps
    time_bw_fram = 1/fps

    while True:
        ret,frame=video_data.read()

        if ret==False:
            break
        
        no_of_pixels = 0
        sumr = 0
        sumg =0
        sumb =0

        #loop for pixels row, only pixels in mid are selected
        for i in frame[int((len(frame)-100)/2) : int((len(frame)+100)/2)]:
            #loop for pixel col, only pixels in mid are selected
            for j in i[int((len(frame[0])-100)/2) : int((len(frame[0])+100)/2)]:
                sumr = sumr+j[2]
                sumg = sumg+j[1]
                sumb = sumb+j[0]
                no_of_pixels = no_of_pixels + 1
        R = np.append(R,sumr/no_of_pixels)
        G = np.append(G,sumg/no_of_pixels)
        B = np.append(B,sumb/no_of_pixels)


    # discarding first few frames and last few 

    R = R[100:-100]
    G = G[100:-100]
    B = B[100:-100]

    # R value is choosen for further filtering,bandpassed,squared
    # declaring filter variables

    r_cutoff_high = 10
    r_cutoff_low = 100
    r_order_of_bandpass = 5
    r_sampling_rate = 8*int(fps+1)
    r_average_filter_sample_length = 7


    r_averaged = process_signal(R,r_order_of_bandpass,r_cutoff_high,r_cutoff_low,r_sampling_rate,r_average_filter_sample_length)
    g_averaged = process_signal(G,r_order_of_bandpass,r_cutoff_high,r_cutoff_low,r_sampling_rate,r_average_filter_sample_length)
    b_averaged = process_signal(B,r_order_of_bandpass,r_cutoff_high,r_cutoff_low,r_sampling_rate,r_average_filter_sample_length)

    bpms = []
    bpms.append(give_bpm(r_averaged,time_bw_fram))
    bpms.append(give_bpm(g_averaged,time_bw_fram))
    bpms.append(give_bpm(b_averaged,time_bw_fram))

    bpm = (bpms[0]+bpms[1]+bpms[2])/3

    result = {
        "r_avg" : r_averaged,
        "g_avg" : g_averaged,
        "b_avg" : b_averaged,
        "r_bpm" : bpms[0],
        "g_bpm" : bpms[1],
        "b_bpm" : bpms[2],
        "avg_bpm" : bpm
    }

    json_dump = json.dumps(result,cls=NumpyEncoder)
    return json_dump

if __name__ == "__main__":
    app.run()
