# OpenGL - CarGUI

### SparseDrive ( Detection, VectorMap, Motion planning )
![alt text](gif/car_gui_vec_traj_0907_.gif)

### Other models ( Detection, SegMap )
![alt text](gif/car_gui_seg_0907_.gif)

## Introduction
An on-board display system for autonomous driving, including surrounding traffic environment, front and back camera images, speedometer, turn singal and speed limit reminder.

We use those models to get environment infomation:

- SparseDrive (detection, vector map, motion planning)
- StreamPETR (detection)
- BEVFormer (dectction, segmentation map)




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

