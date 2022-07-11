# Heart Rate API

Heart-Rate-Api helps to estimate heart rate using PPG data from mobile camera.

## Use 

- Record a 15 second video by keeping finger over the camera with flash on.
- Send url link of video to the api to perform PPG and estimate heart rate.

## Approach

- Place finger over the camera and 15 second video was recorded with flash on in each case.
- This video is imported to our python based api using ```open cv2``` and video object was created, FPS, frame count were determined.
- The first few frames and last few frames were dropped as a data pre processing measure as they contain most of the error.
```eg. placing finger and removing finger, stablizing time etc.```
- For each image of the video, pixels in the middle were selected and average of RGB colors were calculated.
- Array of each RGB color was maintained to storage average values.
- Array with red pixels was selected for further processing and determination of results as red color gives best result `
(Assumption)`
- Following arrays were treated as signal objects.
- `Lowpass filter` and `highpass filter` is use to remove unwanted frequencies from signals.
- Further, signal was squared to elongate it, so that it was easy to determine peaks `(Assumption)`
- Peaks were detected using peak detection algorithm from `SCIPY.SIGNAL` library and average time between peaks were calculated.
- Thus, calculating **Heart rate**.

## Deployed API link
```
https://heart-rate-07.herokuapp.com/api?query=video_url_link
 ```
> The query must contain url link of ppg data captured using mobile camera with flash on.

## Example of API call

```
https://heart-rate-07.herokuapp.com/api?query=https://firebasestorage.googleapis.com/v0/b/heart-rate-monitor-cee6e.appspot.com/o/files%2Ftest.mp4?alt=media&token=61d6c17c-4f85-4c32-b9a7-7ea0fd19400c
```

## Example of API response

```
API response example

{
   "r_avg":[
      0.00018912736029968232,
      0.002454027341541433,
      0.0046238379461607014,
      0.0059273051392782815,
      .....
   ],
   "g_avg":[
      5.739757749447178e-05,
      0.002728729471758443,
      0.005252370906011639,
      0.006246822018310483,
      .....
   ],
   "b_avg":[
      0.00012713453865537887,
      0.0009398674441625056,
      0.001593039182660829,
      0.0019041612619612055,
      .....
   ],
   "r_bpm":131.9763664543775,
   "g_bpm":112.5044435348792,
   "b_bpm":104.61541243334804,
   "avg_bpm":116.3654074742016
}
```
## References

- [**Scipy Signal**](https://docs.scipy.org/doc/scipy/reference/signal.html)
- [**Research Gate**](https://www.researchgate.net/publication/329896875_Image_Analysis_on_Fingertip_Video_To_Obtain_PPG)
- [**Open CV**](https://docs.opencv.org/3.4/d8/dfe/classcv_1_1VideoCapture.html)
- [**heart rate ppg camera**](https://www.researchgate.net/publication/329896875_Image_Analysis_on_Fingertip_Video_To_Obtain_PPG)