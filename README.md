# OpenGL - CarGUI

### Vector Map version
![alt text](gif/car_gui_vec_0901.gif)

### Segmentation map version
![alt text](gif/car_gui_seg_0901.gif)

## Introduction
An on-board display system for autonomous driving, including surrounding traffic environment, front and back camera images, speedometer, turn singal and speed limit reminder.

We use those models to get environment infomation:

- StreamPETR (detection)
- BEVFormer (dectction, segmentation map)
- SparseDrive (detection, vector map)



### Available display objects in surronding environment :
- car
- truck
- pedestrian
- scooter
- cone
- signs
- ground traffic signs

## Installation
```
pip install -r requirements.txt
```

Ubuntu requires opencv-headless
```
pip install opencv-python-headless
```

