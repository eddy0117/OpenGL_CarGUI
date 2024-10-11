
from GetVanishingPoint import GetVanishingPoint
from TransformImage2Ground import TransformImage2Ground
from TransformGround2Image import TransformGround2Image
import cv2
import numpy as np
from math import sin, cos, pi
def TransformImage2GroundPoint(uvPoint, cameraInfo):
    u, v = uvPoint
    inPoint3 = np.array([u, v, 1], np.float32)

    c1 = cos(cameraInfo.pitch * pi / 180)
    s1 = sin(cameraInfo.pitch * pi / 180)
    c2 = cos(cameraInfo.yaw * pi / 180)
    s2 = sin(cameraInfo.yaw * pi / 180)

    matp = [
        [-cameraInfo.cameraHeight * c2 / cameraInfo.focalLengthX,
         cameraInfo.cameraHeight * s1 * s2 / cameraInfo.focalLengthY,
         (cameraInfo.cameraHeight * c2 * cameraInfo.opticalCenterX / cameraInfo.focalLengthX)
         - (cameraInfo.cameraHeight * s1 * s2 * cameraInfo.opticalCenterY / cameraInfo.focalLengthY)
         - cameraInfo.cameraHeight * c1 * s2],
        [cameraInfo.cameraHeight * s2 / cameraInfo.focalLengthX,
         cameraInfo.cameraHeight * s1 * c2 / cameraInfo.focalLengthY,
         (-cameraInfo.cameraHeight * s2 * cameraInfo.opticalCenterX / cameraInfo.focalLengthX)
         - (cameraInfo.cameraHeight * s1 * c2 * cameraInfo.opticalCenterY / cameraInfo.focalLengthY)
         - cameraInfo.cameraHeight * c1 * c2],
        [0, cameraInfo.cameraHeight * c1 / cameraInfo.focalLengthY,
         (-cameraInfo.cameraHeight * c1 * cameraInfo.opticalCenterY / cameraInfo.focalLengthY)
         + cameraInfo.cameraHeight * s1]
    ]

    inPoint3 = np.array(matp).dot(inPoint3)
    inPoint3 /= inPoint3[2]
    xyPoint = inPoint3[:2]

    return xyPoint


class Info(object):
    def __init__(self, dct):
        self.dct = dct

    def __getattr__(self, name):
        return self.dct[name]

# I = cv2.imread(r'data\nuscenes\samples\CAM_FRONT\n008-2018-08-27-11-48-51-0400__CAM_FRONT__1535385100862404.jpg')
I = cv2.imread(r'data\carla\img\100.jpg')
R = I[:, :, :]
height = int(I.shape[0]) # row y
width = int(I.shape[1]) # col x

cameraInfo = Info({
    "focalLengthX": 1266.4, # 1200.6831,         # focal length x
    "focalLengthY": 1266.4, # 1200.6831,         # focal length y
    # "opticalCenterX": 816, # 638.1608,        # optical center x
    # "opticalCenterY": 491, # 738.8648,       # optical center y
    "opticalCenterX": width // 2,
    "opticalCenterY": height // 2,
    "cameraHeight": 1500, # 1879.8,  # camera height in `mm`
    "pitch": 0,           # rotation degree around x
    "yaw": 0,              # rotation degree around y
    "roll": 0              # rotation degree around z
})
ipmInfo = Info({
    "inputWidth": width,
    "inputHeight": height,
    "left": 50,
    "right": width - 50,
    "top": 530,
    "bottom": height - 50
})
# IPM
vpp = GetVanishingPoint(cameraInfo)
vp_x = vpp[0][0]
vp_y = vpp[1][0]
ipmInfo.top = float(max(int(vp_y), ipmInfo.top))
uvLimitsp = np.array([[vp_x, ipmInfo.right, ipmInfo.left, vp_x],
            [ipmInfo.top, ipmInfo.top, ipmInfo.top, ipmInfo.bottom]], np.float32)

xyLimits = TransformImage2Ground(uvLimitsp, cameraInfo)
row1 = xyLimits[0, :]
row2 = xyLimits[1, :]
xfMin = min(row1)
xfMax = max(row1)
yfMin = min(row2)
yfMax = max(row2)
xyRatio = (xfMax - xfMin)/(yfMax - yfMin)
outImage = np.zeros((320,480,4), np.float32)
outImage[:,:,3] = 255
outRow = int(outImage.shape[0])
outCol = int(outImage.shape[1])
stepRow = (yfMax - yfMin)/outRow
stepCol = (xfMax - xfMin)/outCol
xyGrid = np.zeros((2, outRow*outCol), np.float32)
y = yfMax-0.5*stepRow

for i in range(0, outRow):
    x = xfMin+0.5*stepCol
    for j in range(0, outCol):
        xyGrid[0, (i-1)*outCol+j] = x
        xyGrid[1, (i-1)*outCol+j] = y
        x = x + stepCol
    y = y - stepRow

# TransformGround2Image
uvGrid = TransformGround2Image(xyGrid, cameraInfo)
# mean value of the image

# RR = R.astype(float)/255
RR = R / 255
for i in range(0, outRow):
    for j in range(0, outCol):
        ui = uvGrid[0, i*outCol+j]
        vi = uvGrid[1, i*outCol+j]
        #print(ui, vi)
        if ui < ipmInfo.left or ui > ipmInfo.right or vi < ipmInfo.top or vi > ipmInfo.bottom:
            outImage[i, j] = 0.0
        else:
           
            
            x1 = np.int32(ui)
            x2 = np.int32(ui+0.5)
            y1 = np.int32(vi)
            y2 = np.int32(vi+0.5)
            x = ui-float(x1)
            y = vi-float(y1)
   
            if x1 in range(50, 53) and y1 in range(600, 603):
                print(x1, x2, y1, y2, i, j)

            outImage[i, j, 0] = float(RR[y1, x1, 0])*(1-x)*(1-y)+float(RR[y1, x2, 0])*x*(1-y)+float(RR[y2, x1, 0])*(1-x)*y+float(RR[y2, x2, 0])*x*y
            outImage[i, j, 1] = float(RR[y1, x1, 1])*(1-x)*(1-y)+float(RR[y1, x2, 1])*x*(1-y)+float(RR[y2, x1, 1])*(1-x)*y+float(RR[y2, x2, 1])*x*y
            outImage[i, j, 2] = float(RR[y1, x1, 2])*(1-x)*(1-y)+float(RR[y1, x2, 2])*x*(1-y)+float(RR[y2, x1, 2])*(1-x)*y+float(RR[y2, x2, 2])*x*y
            
outImage[-1,:] = 0.0 
# show the result

outImage = outImage * 255
print("finished")
# save image
cv2.imwrite('pp.png',outImage)