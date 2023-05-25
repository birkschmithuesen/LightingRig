"""
Extension classes enhance TouchDesigner components with python. An
extension is accessed via ext.ExtensionClassName from any operator
within the extended component. If the extension is promoted via its
Promote Extension parameter, all its attributes with capitalized names
can be accessed externally, e.g. op('yourComp').PromotedFunction().

Help: search "Extensions" in wiki
"""

from TDStoreTools import StorageManager
import TDFunctions as TDF

import cv2
import numpy as np

import json

class MovingHeadExt:
	"""
	MovingHeadExt description
	"""
	def __init__(self, ownerComp):
		# The component to which this extension is attached
		self.ownerComp = ownerComp

		TDF.createProperty(self, 'Position', value=list(parent.MovingHead.parGroup.Position.eval()), dependable="deep", readOnly=False)	
		TDF.createProperty(self, 'Rotation', value=list(parent.MovingHead.parGroup.Rotation.eval()), dependable="deep", readOnly=False)

		TDF.createProperty(self, 'PanTiltDirection', value=list(parent.MovingHead.parGroup.Pantiltdirection.eval()), dependable="deep", readOnly=False)

		TDF.createProperty(self, 'targetListTop', value=list(), dependable="deep", readOnly=False)
		TDF.createProperty(self, 'panTiltListTop', value=list(), dependable="deep", readOnly=False)
		TDF.createProperty(self, 'panTiltOffsetListTop', value=list(), dependable="deep", readOnly=False)
		TDF.createProperty(self, 'distanceListTop', value=list(), dependable="deep", readOnly=False)
		TDF.createProperty(self, 'h_targetListTop', value=list(), dependable="deep", readOnly=False)
		self.HomographyTop = np.array([[1.,.0,.0],[.0,1.,.0],[.0,.0,1.]])

		TDF.createProperty(self, 'targetListBtm', value=list(), dependable="deep", readOnly=False)
		TDF.createProperty(self, 'panTiltListBtm', value=list(), dependable="deep", readOnly=False)
		TDF.createProperty(self, 'panTiltOffsetListBtm', value=list(), dependable="deep", readOnly=False)
		TDF.createProperty(self, 'distanceListBtm', value=list(), dependable="deep", readOnly=False)
		TDF.createProperty(self, 'h_targetListBtm', value=list(), dependable="deep", readOnly=False)
		self.HomographyBtm = np.array([[1.,.0,.0],[.0,1.,.0],[.0,.0,1.]])

		self.HomographySide_1 = np.array([[1.,.0,.0],[.0,1.,.0],[.0,.0,1.]])
		self.HomographySide_2 = np.array([[1.,.0,.0],[.0,1.,.0],[.0,.0,1.]])

		self.TempHomography = np.array([[1.,.0,.0],[.0,1.,.0],[.0,.0,1.]])


		self.Dir = 'x'
		self.Axis = tdu.Dependency('x')

		self.DMXStartingAddress = tdu.Dependency(parent.MovingHead.par.Dmxstartingaddress.val)

	def CreateJSONConfig(self, file):
		json_config = {}
		json_config["Position"] = list(self.Position)
		json_config["Rotation"] = list(self.Rotation)

		json_config["PanTiltDirection"] = list(self.PanTiltDirection)

		datapoints_top = []
		for i in range(len(self.targetListTop)):
			datapoint_dict = dict()
			datapoint_dict["Target"] = self.GetTarget(i,'top')
			datapoint_dict["PanTilt"] = self.GetPanTilt(i,'top')
			datapoint_dict["PanTiltOffset"] = self.GetPanTiltOffset(i,'top')
			datapoint_dict["Distance"] = self.GetDistance(i,'top')
			try:
				datapoint_dict["HomogTarget"] = self.GetHomogTarget(i,'top')
			except:
				datapoint_dict["HomogTarget"] = [0,0]
			datapoints_top.append(datapoint_dict)
		json_config["DataPointsTop"] = datapoints_top

		datapoints_btm = []
		for i in range(len(self.targetListBtm)):
			datapoint_dict = dict()
			datapoint_dict["Target"] = self.GetTarget(i,'btm')
			datapoint_dict["PanTilt"] = self.GetPanTilt(i,'btm')
			datapoint_dict["PanTiltOffset"] = self.GetPanTiltOffset(i,'btm')
			datapoint_dict["Distance"] = self.GetDistance(i,'btm')
			try:
				datapoint_dict["HomogTarget"] = self.GetHomogTarget(i,'btm')
			except:
				datapoint_dict["HomogTarget"] = [0,0]
			datapoints_btm.append(datapoint_dict)
		json_config["DataPointsBtm"] = datapoints_btm

		json_config["HomographyTop"] = self.HomographyTop.tolist()
		json_config["HomographyBtm"] = self.HomographyBtm.tolist()
		json_config["HomographySide_1"] = self.HomographySide_1.tolist()
		json_config["HomographySide_2"] = self.HomographySide_2.tolist()

		json_config["Axis"] = self.Axis.val
		
		json_config["DMXStartingAddress"] = self.DMXStartingAddress.val

		with open(file, 'w') as jsonFile:
			json.dump(json_config,jsonFile,indent=4)

	def fillParFromJSON(self, prop, json, key):
		try:
			prop = json[key]
		except:
			debug("Couldnt find key.")

	def LoadJSONConfig(self, file):
		with open(file) as jsonfile:
			json_content = jsonfile.read()
		parsed_json = json.loads(json_content)

		self.Position = parsed_json["Position"]
		self.Rotation = parsed_json["Rotation"]

		try:
			self.PanTiltDirection = parsed_json["PanTiltDirection"]
		except:
			self.PanTiltDirection = list((0,90)) # setting standard
			debug("No PanTiltDirection par, old config")
		
		datapoints_top = parsed_json["DataPointsTop"]
		self.h_targetListTop = list()
		for datapoint in datapoints_top:
			target = datapoint.get("Target")
			pan_tilt = datapoint.get("PanTilt")
			pan_tilt_offset = datapoint.get("PanTiltOffset")
			distance = datapoint.get("Distane")
			homog_target = datapoint.get("HomogTarget")
			self.AddCapture(target, pan_tilt, pan_tilt_offset, distance, 'top')
			self.h_targetListTop.append(homog_target)

		datapoints_btm = parsed_json["DataPointsBtm"]
		self.h_targetListBtm = list()
		for datapoint in datapoints_btm:
			target = datapoint.get("Target")
			pan_tilt = datapoint.get("PanTilt")
			pan_tilt_offset = datapoint.get("PanTiltOffset")
			distance = datapoint.get("Distane")
			homog_target = datapoint.get("HomogTarget")
			self.AddCapture(target, pan_tilt, pan_tilt_offset, distance, 'btm')
			self.h_targetListBtm.append(homog_target)

		self.HomographyTop = np.array(parsed_json["HomographyTop"])
		self.HomographyBtm = np.array(parsed_json["HomographyBtm"])
		self.HomographySide_1 = np.array(parsed_json["HomographySide_1"])
		self.HomographySide_2 = np.array(parsed_json["HomographySide_2"])

		self.Axis.val = parsed_json["Axis"]

		self.DMXStartingAddress.val = parsed_json["DMXStartingAddress"]


	def math_range(self, value, in_range, out_range):
		return np.interp(value,in_range, out_range)

	def cycle_range(self, start, stop, value):
		range_size = stop - start
		return start + ((value - start) % range_size)
	
	def addTargetItem(self, target, type):
		if type == 'top':
			self.targetListTop.append(target)
		elif type == 'btm':
			self.targetListBtm.append(target)

	def addPanTiltItem(self, panTilt, type):
		if type == 'top':
			self.panTiltListTop.append(panTilt)
		elif type == 'btm':
			self.panTiltListBtm.append(panTilt)

	def addPanTiltOffsetItem(self, panTiltOffset, type):
		if type == 'top':
			self.panTiltOffsetListTop.append(panTiltOffset)
		elif type == 'btm':
			self.panTiltOffsetListBtm.append(panTiltOffset)
	
	def addDistanceItem(self, distance, type):
		if type == 'top':
			self.distanceListTop.append(distance)
		elif type == 'btm':
			self.distanceListBtm.append(distance)
	
	def AddCapture(self, target, panTilt, panTiltOffset, distance, type):
		self.addTargetItem(target, type)
		self.addPanTiltItem(panTilt, type)
		self.addPanTiltOffsetItem(panTiltOffset, type)
		self.addDistanceItem(distance, type)

	def ReCaptureAtIndex(self, target, panTilt, panTiltOffset, distance, index, type):
		if type == 'top':
			self.targetListTop.setItem(index,target)
			self.panTiltListTop.setItem(index,panTilt)
			self.panTiltOffsetListTop.setItem(index,panTiltOffset)
			self.distanceListTop.setItem(index,distance)
		elif type == 'btm':
			self.targetListBtm.setItem(index,target)
			self.panTiltListBtm.setItem(index,panTilt)
			self.panTiltOffsetListBtm.setItem(index,panTiltOffset)
			self.distanceListBtm.setItem(index,distance)

	def DeleteCapture(self, index, type):
		if type == 'top':
			self.targetListTop.pop(index)
			self.panTiltListTop.pop(index)
			self.panTiltOffsetListTop.pop(index)
			self.distanceListTop.pop(index)
		elif type == 'btm':
			self.targetListBtm.pop(index)
			self.panTiltListBtm.pop(index)
			self.panTiltOffsetListBtm.pop(index)
			self.distanceListBtm.pop(index)

	def DeleteLastCapture(self, type):
		if type == 'top':
			self.targetListTop.pop(len(self.targetListTop)-1)
			self.panTiltListTop.pop(len(self.panTiltListTop)-1)
			self.panTiltOffsetListTop.pop(len(self.panTiltOffsetListTop)-1)
			self.distanceListTop.pop(len(self.distanceListTop)-1)
		elif type == 'btm':
			self.targetListBtm.pop(len(self.targetListBtm)-1)
			self.panTiltListBtm.pop(len(self.panTiltListBtm)-1)
			self.panTiltOffsetListBtm.pop(len(self.panTiltOffsetListBtm)-1)
			self.distanceListBtm.pop(len(self.distanceListBtm)-1)

	def GetTargetList(self, type):
		if type == 'top':
			return self.targetListTop
		elif type == 'btm':
			return self.targetListBtm
	
	def GetPanTiltList(self, type):
		if type == 'top':
			return self.panTiltListTop
		elif type == 'btm':
			return self.panTiltListBtm
	
	def GetPanTiltOffsetList(self, type):
		if type == 'top':
			return self.panTiltOffsetListTop
		elif type == 'btm':
			return self.panTiltOffsetListBtm

	def GetDistanceList(self, type):
		if type == 'top':
			return self.distanceListTop
		elif type == 'btm':
			return self.distanceListBtm
	
	def GetTarget(self, index, type):
		if type == 'top':
			return self.targetListTop.getRaw(index)
		elif type == 'btm':
			return self.targetListBtm.getRaw(index)
	
	def GetPanTilt(self, index, type):
		if type == 'top':
			return self.panTiltListTop.getRaw(index)
		elif type == 'btm':
			return self.panTiltListBtm.getRaw(index)
	
	def GetPanTiltOffset(self, index, type):
		if type == 'top':
			return self.panTiltOffsetListTop.getRaw(index)
		elif type == 'btm':
			return self.panTiltOffsetListBtm.getRaw(index)
	
	def GetDistance(self, index, type):
		if type == 'top':
			return self.distanceListTop.getRaw(index)
		elif type == 'btm':
			return self.distanceListBtm.getRaw(index)
	
	def CalcHomography(self, type):
		targets_real_space = None
		targets_moving_head_space = None
		if type == 'top':
			targets_real_space = np.array(self.targetListTop).reshape(len(self.targetListTop),3)
			targets_moving_head_space = np.array(self.panTiltListTop).reshape(len(self.panTiltListTop),2)
		elif type == 'btm':
			targets_real_space = np.array(self.targetListBtm).reshape(len(self.targetListBtm),3)
			targets_moving_head_space = np.array(self.panTiltListBtm).reshape(len(self.panTiltListBtm),2)

		# delete y dimension of targets
		real_space_homography_points = np.delete(targets_real_space, 1, 1)

		# calculate x and z position from pan tilt for moving head space
		temp_h_list = list()
		for pan_tilt in targets_moving_head_space:
			pan = pan_tilt[0]
			tilt = pan_tilt[1]
			# layer way
			x = math.tan(math.radians(pan))
			y = math.tan(math.radians(tilt)) / math.cos(math.radians(pan))
			
			# spherical representation
			#x_vector = math.cos(math.radians(pan))
			#y_vector = math.sin(math.radians(tilt))
			#xy_vector = tdu.Vector(x_vector,y_vector,0)
			#length = math.tan(math.radians(tilt/2))
			#xy = xy_vector * length
			#x = xy.x
			#y = xy.y

			# fish eye representation
			#pan_x = np.interp(pan,(-180,180),(-60,60))
			#x = math.tan(math.radians(pan_x))
			#pan_cycle = self.cycle_range(-90,90,pan)
			#y = math.tan(math.radians(tilt) / math.cos(math.radians(pan_cycle)))

			temp_h_list.append([x,y])
		if type == 'top':
			self.h_targetListTop = temp_h_list
		elif type == 'btm':
			self.h_targetListBtm = temp_h_list
		
		# calculate homography
		if type == 'top':
			self.HomographyTop, s = cv2.findHomography(real_space_homography_points, np.array(temp_h_list))
		elif type == 'btm':
			self.HomographyBtm, s = cv2.findHomography(real_space_homography_points, np.array(temp_h_list))

	def CalcSideHomographies(self):
		targets_real_space_top = np.array(self.targetListTop).reshape(4,3)
		targets_moving_head_space_top = np.array(self.panTiltListTop).reshape(4,2)
		targets_real_space_btm = np.array(self.targetListBtm).reshape(4,3)
		targets_moving_head_space_btm = np.array(self.panTiltListBtm).reshape(4,2)

		# create sides
		targets_real_space_side_1_btm = targets_real_space_btm[:-2]
		targets_real_space_side_1_top = targets_real_space_top[:-2][::-1]
		targets_real_space_side_1 = np.concatenate((targets_real_space_side_1_btm,targets_real_space_side_1_top), axis=0)
		targets_real_space_side_2_btm = targets_real_space_btm[2:]
		targets_real_space_side_2_top = targets_real_space_top[2:][::-1]
		targets_real_space_side_2 = np.concatenate((targets_real_space_side_2_btm,targets_real_space_side_2_top), axis=0)

		# delete y dimension of targets
		# # # we need to check in which direction, x or z, the first points differ. or if one of them == 0
		x_delta = targets_real_space_btm[1][0] - targets_real_space_btm[0][0]
		z_delta = targets_real_space_btm[1][2] - targets_real_space_btm[0][2]

		if abs(x_delta) > abs(z_delta):
			self.Dir = 'x'
			real_space_homography_points_side_1 = np.delete(targets_real_space_side_1, 2, 1)
			real_space_homography_points_side_2 = np.delete(targets_real_space_side_2, 2, 1)
		else:
			self.Dir = 'z'
			real_space_homography_points_side_1 = np.delete(targets_real_space_side_1, 0, 1)
			real_space_homography_points_side_2 = np.delete(targets_real_space_side_2, 0, 1)

		targets_moving_head_space_side_1_btm = targets_moving_head_space_btm[:-2]
		targets_moving_head_space_side_1_top = targets_moving_head_space_top[:-2][::-1]
		targets_moving_head_space_side_1 = np.concatenate((targets_moving_head_space_side_1_btm,targets_moving_head_space_side_1_top), axis=0)
		targets_moving_head_space_side_2_btm = targets_moving_head_space_btm[2:]
		targets_moving_head_space_side_2_top = targets_moving_head_space_top[2:][::-1]
		targets_moving_head_space_side_2 = np.concatenate((targets_moving_head_space_side_2_btm,targets_moving_head_space_side_2_top), axis=0)

		# calculate x and z position from pan tilt for moving head space
		temp_h_list_side_1 = list()
		temp_h_list_side_2 = list()
		for i in range(4):
			pan_side_1 = targets_moving_head_space_side_1[i][0]
			tilt_side_1 = targets_moving_head_space_side_1[i][1]
			pan_side_2 = targets_moving_head_space_side_2[i][0]
			tilt_side_2 = targets_moving_head_space_side_2[i][1]

			# layer way
			x_side_1 = math.tan(math.radians(pan_side_1))
			y_side_1 = math.tan(math.radians(tilt_side_1)) / math.cos(math.radians(pan_side_1))
			x_side_2 = math.tan(math.radians(pan_side_2))
			y_side_2 = math.tan(math.radians(tilt_side_2)) / math.cos(math.radians(pan_side_2))
			
			# spherical representation
			#x_vector = math.cos(math.radians(pan))
			#y_vector = math.sin(math.radians(tilt))
			#xy_vector = tdu.Vector(x_vector,y_vector,0)
			#length = math.tan(math.radians(tilt/2))
			#xy = xy_vector * length
			#x = xy.x
			#y = xy.y

			# fish eye representation
			#pan_x = np.interp(pan,(-180,180),(-60,60))
			#x = math.tan(math.radians(pan_x))
			#pan_cycle = self.cycle_range(-90,90,pan)
			#y = math.tan(math.radians(tilt) / math.cos(math.radians(pan_cycle)))

			temp_h_list_side_1.append([x_side_1,y_side_1])
			temp_h_list_side_2.append([x_side_2,y_side_2])

		self.HomographySide_1, s_1 = cv2.findHomography(real_space_homography_points_side_1, np.array(temp_h_list_side_1))
		self.HomographySide_2, s_2 = cv2.findHomography(real_space_homography_points_side_2, np.array(temp_h_list_side_2))
		debug(self.HomographySide_1,self.HomographySide_2)
	
	def GetHomogTargetList(self, type):
		if type == 'top':
			return self.h_targetListTop
		elif type == 'btm':
			return self.h_targetListBtm
	
	def GetHomogTarget(self, index, type):
		if type == 'top':
			return self.h_targetListTop.getRaw(index)
		elif type == 'btm':
			return self.h_targetListBtm.getRaw(index)
		
	def CreateTempHomographyFromPanTilt(self, targetList, panTiltList):
		temp_h_list = list()
		for pan_tilt in panTiltList:
			pan = pan_tilt[0]
			tilt = pan_tilt[1]
			# laser way
			x = math.tan(math.radians(pan))
			y = math.tan(math.radians(tilt)) / math.cos(math.radians(pan))

			# spherical representation
			#x_vector = math.cos(math.radians(pan))
			#y_vector = math.sin(math.radians(tilt))
			#xy_vector = tdu.Vector(x_vector,y_vector,0)
			#length = math.tan(math.radians(tilt/2))
			#xy = xy_vector * length
			#x = xy.x
			#y = xy.y

			# fish eye representation
			#pan_x = np.interp(pan,(-180,180),(-60,60))
			#x = math.tan(math.radians(pan_x))
			#pan_cycle = self.cycle_range(-90,90,pan)
			#y = math.tan(math.radians(tilt) / math.cos(math.radians(pan_cycle)))

			temp_h_list.append([x,y])
		h, s = cv2.findHomography(targetList, np.array(temp_h_list))
		if h.any():
			self.TempHomography = h
		else:
			self.TempHomography = np.array([[1.,.0,.0],[.0,1.,.0],[.0,.0,1.]])
	
	def CreateTempHomography(self, targetList, homogList):
		h, s = cv2.findHomography(targetList, homogList)
		if h.any():
			self.TempHomography = h
		else:
			self.TempHomography = np.array([[1.,.0,.0],[.0,1.,.0],[.0,.0,1.]])
	
	def CalcHomogPosition(self, target, type):
		if type == 'top':
			homography = self.HomographyTop
		elif type == 'btm':
			homography = self.HomographyBtm
		elif type == 'side_1':
			homography = self.HomographySide_1
		elif type == 'side_2':
			homography = self.HomographySide_2
		else:
			homography = self.TempHomography
		point = [target[0], target[1], 1]
		dest_point_homog = np.dot(homography, point)
		dest_point_eucl = dest_point_homog / dest_point_homog[2]
		dest_point = dest_point_eucl[:2]
		return dest_point
	
	def CalcPanTilt(self, position):
		# laser way
		pan = math.degrees(math.atan(position[0]))
		tilt = math.degrees(math.atan(position[1] * math.cos(math.radians(pan)))) + self.PanTiltDirection.getRaw(1)
		pan = pan + self.PanTiltDirection.getRaw(0)
		#if abs(pan) >= 90:
		#	debug(now)
		#	pan_tmp = pan - self.PanTiltDirection.getRaw(0)
		#	tilt_tmp = tilt - self.PanTiltDirection.getRaw(1)
		#	pan = pan_tmp * -1
		#	tilt = tilt_tmp * -1
		
		# spherical representation
		#vec = tdu.Vector(position[0],position[1],0)
		#debug("vec", vec)
		#length = vec.length()
		#debug("length", length)
		#vec.normalize()
		#debug("vec_n", vec)
		#tilt = math.degrees(math.atan(length)) * 2 
		#pan = math.degrees(math.acos(vec.x))

		# fish eye
		#pan_x = math.degrees(math.atan(position[0]))
		#debug("pan_x",pan_x)
		#pan = np.interp(pan_x,(-60,60),(-180,180))
		#debug("pan",pan)
		#pan_cycle = self.cycle_range(-90,90,pan)
		#debug("pan_cycle",pan_cycle)
		#tilt = math.degrees(math.atan(position[1] * math.cos(math.radians(pan_cycle)))) + self.PanTiltDirection.getRaw(1)
		#pan = pan + self.PanTiltDirection.getRaw(0)
		return [pan ,tilt]