import cv2
import numpy as np

# real world target position
target_list = np.array([	[0., 0.],
       				[1., 0.],
       				[1., 1.],
       				[0., 1.]])
print("Target List", target_list)

# pan tilt in degrees to hit real world targets
pan_tilt_list = np.array([	[3.97973514, 45.3091774 ],
       				[31.8413868, 46.40531921],
       				[47.31228638, 31.03630066],
       				[-4.61433363, 27.64239883]])
print("Pan Tilt", pan_tilt_list)

# calculating x and y coordinates from the pan and tilt rotations
pan_tilt_to_xy_list = list()
for pan_tilt in pan_tilt_list:
    pan = pan_tilt[0]
    tilt = pan_tilt[1]
    x = math.tan(math.radians(pan)) / math.cos(math.radians(tilt))
    y = math.tan(math.radians(tilt))
    pan_tilt_to_xy_list.append([x,y])
pan_tilt_to_xy_list = np.array(pan_tilt_to_xy_list)
print("Pan X Tilt Y", pan_tilt_to_xy_list)

# calculate homography from the point pairs
homography, status = cv2.findHomography(target_list, pan_tilt_to_xy_list)
print("Homography", homography)

target_to_find = [0.5, 0.5]

# calculate x and y coordinates for the moving head
h_target_to_find = [target_to_find[0], target_to_find[1], 1] # converting to homogenous space
h_target_in_moving_head = np.dot(homography, h_target_to_find) # applying homography transformation to the point
target_in_moving_head = h_target_in_moving_head / h_target_in_moving_head[2] # converting the point back from homogenous to euclidean space
target_xy = target_in_moving_head[:2] # deleting z axis
print("Target XY", target_xy)

# calculate pan and tilt from x and y
tilt = math.degrees(math.atan(target_xy[1]))
pan = math.degrees(math.atan(target_xy[0] * math.cos(math.radians(tilt))))
print("Pan Tilt", pan, tilt)

# correct values
c_pan = 19.936401
c_tilt = 36.96672