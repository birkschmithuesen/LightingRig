"""
Extension classes enhance TouchDesigner components with python. An
extension is accessed via ext.ExtensionClassName from any operator
within the extended component. If the extension is promoted via its
Promote Extension parameter, all its attributes with capitalized names
can be accessed externally, e.g. op('yourComp').PromotedFunction().

Help: search "Extensions" in wiki
"""

class MQInterfaceExt:
	"""
	MQInterfaceEXt description
	"""
	def __init__(self, ownerComp):
		# The component to which this extension is attached
		self.ownerComp = ownerComp
		self.oscSender = op('oscout_mq')
		self.mqSender = op('tracker_sender')
		self.dmxOut = op('dmxout_chans')
		self.oscThrottelCounter = 0
		self.executeDict = {
			'activation': {'page': 13},
			'color': {'page': 14},
			'beam': {'page': 12},
			'shutter': {'page': 12},
			'zoom': {'page': 15}
		}
		self.verbose = 1 # 0:quiet, 1: oscMessages, 2: +incoming values, 3: +tracker-messages
		self.tracker = {gid: {'tid': 0, 'position': (0,0,0)} for gid in range(16)}

	def SetActivation(self, activationId, intensity, lampId):
		if self.verbose > 1: debug(activationId, intensity, lampId)
		oscMessage = f"/exec/{self.executeDict['activation']['page']}/{activationId + lampId}"
		if self.verbose > 0: debug(oscMessage, intensity)
		self.oscSender.sendOSC(oscMessage, [intensity], useNonStandardTypes=True)

	def SetActivationViaArtnet(self, activationId, intensity, lampId):
		if self.verbose > 1: debug(activationId, intensity, lampId)
		if activationId == 1:
			index = activationId + lampId
			value = 255 * intensity
		self.dmxOut.par[f'value{index}'] = value

	def ChooseSoftPalette(self, attributeName, attributeId, lampId):
		if self.verbose > 1: debug(attributeName, attributeId, lampId)
		oscMessage = f"/exec/{self.executeDict[attributeName]['page']}/{attributeId + lampId}"
		if self.verbose > 0: debug(oscMessage)
		self.oscSender.sendOSC(oscMessage, [int(100)], useNonStandardTypes=True)

	def SetZoom(self, lampId, value):
		if self.verbose > 1: debug(lampId, value)
		# TODO move this to artnet and use the measured zoom-values
		#if we send 1.0 the value in MQ is going to 0
		index = lampId
		dmx = 255 * value
		self.dmxOut.par[f'value{index}'] = dmx

	def SetColor(self, lampId, color):
		if self.verbose > 0: debug(lampId, color)
		index = lampId
		dmxRed = 255 * color[0]
		dmxGreen = 255 * color[1]
		dmxBlue = 255 * color[2]
		dmxWhite = 255 * color[3]
		self.dmxOut.par[f'value{16+index}'] = dmxRed
		self.dmxOut.par[f'value{32+index}'] = dmxGreen
		self.dmxOut.par[f'value{48+index}'] = dmxBlue
		self.dmxOut.par[f'value{64+index}'] = dmxWhite

	def SetZoomViaOSC(self, lampId, value):
		if self.verbose > 1: debug(lampId, value)
		# TODO move this to artnet and use the measured zoom-values
		oscMessage = f"/exec/{self.executeDict['zoom']['page']}/{lampId+1}"
		if self.verbose > 0: debug(oscMessage, value*0.999999)
		#if we send 1.0 the value in MQ is going to 0
		self.oscThrottelCounter += 1
		if self.oscThrottelCounter%2 == 0:			
			self.oscSender.sendOSC(oscMessage, [value*0.999999], useNonStandardTypes=True)

	def SetTracker(self, gid, tid, position):
		if self.verbose > 1: debug(gid, tid, position)
		if gid not in self.tracker:
			debug("cannot set tracker for gid ", gid)
			return
		self.tracker[gid]['tid'] = tid
		self.tracker[gid]['position'] = position

	# called by execute-DAT
	def SendTracker(self):
		for gid in self.tracker:
			x = self.tracker[gid]['position'][0]
			y = self.tracker[gid]['position'][2]
			z = -1*self.tracker[gid]['position'][1]
			tid = self.tracker[gid]['tid']
			msg = f'{x:.2f},{y:.2f},{z:.2f},{gid},Tracker:{tid}'
			if self.verbose > 2: debug(msg)
			self.mqSender.send(msg)


