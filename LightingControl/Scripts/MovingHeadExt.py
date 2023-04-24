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
		
		TDF.createProperty(self, 'targetList', value=list(), dependable="deep", readOnly=False)
		TDF.createProperty(self, 'panTiltList', value=list(), dependable="deep", readOnly=False)
		TDF.createProperty(self, 'panTiltOffsetList', value=list(), dependable="deep", readOnly=False)
		TDF.createProperty(self, 'distanceList', value=list(), dependable="deep", readOnly=False)

		self.DMXStartingAddress = tdu.Dependency(parent.MovingHead.par.Dmxstartingaddress.val)

		self.Homography = None
		TDF.createProperty(self, 'h_targetList', value=list(), dependable="deep", readOnly=False)

	def CreateJSONConfig(self, file):
		json_config = {}
		json_config["Position"] = list(self.Position)
		json_config["Rotation"] = list(self.Rotation)
		json_config["DMXStartingAddress"] = self.DMXStartingAddress.val
		datapoints = []
		for i in range(len(self.targetList)):
			datapoint_dict = dict()
			datapoint_dict["Target"] = self.GetTarget(i)
			datapoint_dict["PanTilt"] = self.GetPanTilt(i)
			datapoint_dict["PanTiltOffset"] = self.GetPanTiltOffset(i)
			datapoint_dict["Distance"] = self.GetDistance(i)
			datapoint_dict["HomogTarget"] = self.GetHomogTarget(i)
			datapoints.append(datapoint_dict)
		json_config["DataPoints"] = datapoints

		json_config["Homography"] = self.Homography.tolist()

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
		self.DMXStartingAddress.val = parsed_json["DMXStartingAddress"]
		#self.fillParFromJSON(self.Rotation,parsed_json,"Rotation")
		#self.fillParFromJSON(self.DMXStartingAddress,parsed_json,"DMXStartingAddress")
		
		data_points = parsed_json["DataPoints"]
		self.h_targetList = list()
		for data_point in data_points:
			target = data_point.get("Target")
			pan_tilt = data_point.get("PanTilt")
			pan_tilt_offset = data_point.get("PanTiltOffset")
			distance = data_point.get("Distane")
			homog_target = data_point.get("HomogTarget")
			self.AddCapture(target, pan_tilt, pan_tilt_offset, distance)
			self.h_targetList.append(homog_target)

		self.Homography = np.array(parsed_json["Homography"])

	def math_range(value, in_range, out_range):
		return np.interp(value,in_range, out_range)
	
	def addTargetItem(self, target):
		self.targetList.append(target)

	def addPanTiltItem(self, panTilt):
		self.panTiltList.append(panTilt)

	def addPanTiltOffsetItem(self, panTiltOffset):
		self.panTiltOffsetList.append(panTiltOffset)
	
	def addDistanceItem(self, distance):
		self.distanceList.append(distance)
	
	def AddCapture(self, target, panTilt, panTiltOffset, distance):
		self.addTargetItem(target)
		self.addPanTiltItem(panTilt)
		self.addPanTiltOffsetItem(panTiltOffset)
		self.addDistanceItem(distance)

	def ReCaptureAtIndex(self, target, panTilt, panTiltOffset, distance, index):
		self.targetList.setItem(index,target)
		self.panTiltList.setItem(index,panTilt)
		self.panTiltOffsetList.setItem(index,panTiltOffset)
		self.distanceList.setItem(index,distance)

	def DeleteCapture(self, index):
		self.targetList.pop(index)
		self.panTiltList.pop(index)
		self.panTiltOffsetList.pop(index)
		self.distanceList.pop(index)

	def DeleteLastCapture(self):
		self.targetList.pop(len(self.targetList)-1)
		self.panTiltList.pop(len(self.panTiltList)-1)
		self.panTiltOffsetList.pop(len(self.panTiltOffsetList)-1)
		self.distanceList.pop(len(self.distanceList)-1)

	def GetTargetList(self):
		return self.targetList
	
	def GetPanTiltList(self):
		return self.panTiltList
	
	def GetPanTiltOffsetList(self):
		return self.panTiltOffsetList

	def GetDistanceList(self):
		return self.distanceList
	
	def GetTarget(self, index):
		return self.targetList.getRaw(index)
	
	def GetPanTilt(self, index):
		return self.panTiltList.getRaw(index)
	
	def GetPanTiltOffset(self, index):
		return self.panTiltOffsetList.getRaw(index)
	
	def GetDistance(self, index):
		return self.distanceList.getRaw(index)
	
	def CalcHomography(self):
		targets_real_space = np.array(self.targetList).reshape(len(self.targetList),3)
		targets_moving_head_space = np.array(self.panTiltList).reshape(len(self.panTiltList),2)

		# delete y dimension of targets
		real_space_homography_points = np.delete(targets_real_space, 1, 1)

		# calculate x and z position from pan tilt for moving head space
		self.h_targetList = list()
		mhs_homography_points = list()
		for pan_tilt in targets_moving_head_space:
			pan = pan_tilt[0]
			tilt = pan_tilt[1]

			#sollinger
			#x = math.tan(math.radians(pan)) / math.cos(math.radians(tilt))
			#y = math.tan(math.radians(tilt))

			# azimuth elevation, normally on xyz
			#x = math.cos(pan) * math.cos(tilt)
			#y = math.sin(pan) * math.cos(tilt)

			# uv from az and el
			#x = math.cos(math.radians(tilt)) * math.sin(math.radians(pan))
			#y = math.cos(math.radians(tilt)) * math.cos(math.radians(pan))

			# sollinger resorted
			x = math.tan(math.radians(pan))
			y = math.tan(math.radians(tilt)) / math.cos(math.radians(pan))

			self.h_targetList.append([x,y])
			mhs_homography_points.append([x,y])

		mhs_homography_points = np.array(mhs_homography_points)

		# calculate homography
		self.Homography, s = cv2.findHomography(real_space_homography_points,mhs_homography_points)
		debug(self.Homography)

	def GetHomogTargetList(self):
		return self.h_targetList
	
	def GetHomogTarget(self, index):
		return self.h_targetList.getRaw(index)
	
	def CalcHomogPosition(self, target):
		point = [target[0], target[1], 1]
		dest_point_homog = np.dot(self.Homography, point)
		dest_point_eucl = dest_point_homog / dest_point_homog[2]
		dest_point = dest_point_eucl[:2]
		return dest_point
	
	def CalcPanTilt(self, position):
		# sollinger
		tilt = math.degrees(math.atan(position[1]))
		pan = math.degrees(math.atan(position[0]*math.cos(math.radians(tilt))))
		# xyz to azimuth and elevation
		distance = math.sqrt(position[0]**2 + position[1]**2 + 1**2)
		tilt = math.degrees(math.acos(1/distance))
		pan = math.degrees(math.atan2(position[0],position[1]))
		# sollinger resorted
		pan = math.degrees(math.atan(position[0]))
		tilt = math.degrees(math.atan(position[1] * math.cos(math.radians(pan))))
		return [pan,tilt]