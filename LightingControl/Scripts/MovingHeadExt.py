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
		self.HomographyTop = None

		TDF.createProperty(self, 'targetListBtm', value=list(), dependable="deep", readOnly=False)
		TDF.createProperty(self, 'panTiltListBtm', value=list(), dependable="deep", readOnly=False)
		TDF.createProperty(self, 'panTiltOffsetListBtm', value=list(), dependable="deep", readOnly=False)
		TDF.createProperty(self, 'distanceListBtm', value=list(), dependable="deep", readOnly=False)
		TDF.createProperty(self, 'h_targetListBtm', value=list(), dependable="deep", readOnly=False)
		self.HomographyBtm = None

		self.HomographyLeft = None
		self.HomographyRight = None

		self.TempHomography = None

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
			datapoint_dict["HomogTarget"] = self.GetHomogTarget(i,'top')
			datapoints_top.append(datapoint_dict)
		json_config["DataPointsTop"] = datapoints_top

		datapoints_btm = []
		for i in range(len(self.targetListBtm)):
			datapoint_dict = dict()
			datapoint_dict["Target"] = self.GetTarget(i,'btm')
			datapoint_dict["PanTilt"] = self.GetPanTilt(i,'btm')
			datapoint_dict["PanTiltOffset"] = self.GetPanTiltOffset(i,'btm')
			datapoint_dict["Distance"] = self.GetDistance(i,'btm')
			datapoint_dict["HomogTarget"] = self.GetHomogTarget(i,'btm')
			datapoints_btm.append(datapoint_dict)
		json_config["DataPointsBtm"] = datapoints_btm

		json_config["HomographyTop"] = self.HomographyTop.tolist()
		json_config["HomographyBtm"] = self.HomographyBtm.tolist()
		json_config["HomographyLeft"] = self.HomographyLeft.tolist()
		json_config["HomographyRight"] = self.HomographyRight.tolist()
		
		json_config["DMXStartingAddress"] = self.DMXStartingAddress.val

		with open(file, 'w') as jsonFile:
			json.dump(json_config,jsonFile)

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
		self.HomographyLeft = np.array(parsed_json["HomographyLeft"])
		self.HomographyRight = np.array(parsed_json["HomographyRight"])

		self.DMXStartingAddress.val = parsed_json["DMXStartingAddress"]


	def math_range(value, in_range, out_range):
		return np.interp(value,in_range, out_range)
	
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
			x = math.tan(math.radians(pan))
			y = math.tan(math.radians(tilt)) / math.cos(math.radians(pan))
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
			x = math.tan(math.radians(pan))
			y = math.tan(math.radians(tilt)) / math.cos(math.radians(pan))
			temp_h_list.append([x,y])
		self.TempHomography, s = cv2.findHomography(targetList, np.array(temp_h_list))
	
	def CreateTempHomography(self, targetList, homogList):
		self.TempHomography, s = cv2.findHomography(targetList, homogList)
	
	def CalcHomogPosition(self, target, type):
		if type == 'top':
			homography = self.HomographyTop
		elif type == 'btm':
			homography = self.HomographyBtm
		else:
			homography = self.TempHomography
		point = [target[0], target[1], 1]
		dest_point_homog = np.dot(homography, point)
		dest_point_eucl = dest_point_homog / dest_point_homog[2]
		dest_point = dest_point_eucl[:2]
		return dest_point
	
	def CalcPanTilt(self, position):
		pan = math.degrees(math.atan(position[0]))
		tilt = math.degrees(math.atan(position[1] * math.cos(math.radians(pan)))) + self.PanTiltDirection.getRaw(1)
		pan = pan + self.PanTiltDirection.getRaw(0)
		if abs(pan) >= 90:
			debug(now)
			pan_tmp = pan - self.PanTiltDirection.getRaw(0)
			tilt_tmp = tilt - self.PanTiltDirection.getRaw(1)
			pan = pan_tmp * -1
			tilt = tilt_tmp * -1
		return [pan ,tilt]