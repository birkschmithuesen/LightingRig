from lampUser import LampUser

class Highlight(LampUser):

	cueTable = op.main.op('cue_table')
	dmxManager = op.DMX.ext.DMXManagerExt

	def __init__(self, trackId, cueId):
		super().__init__()
		self.trackId = trackId
		self.cueId = cueId
		self.initFromCueTable()
		self.intensity = 0
		self.intensityChannel = (cueId-1)*27+26
		self.zoomChannel = (cueId-1)*27+23
		self.tiltChannel = (cueId-1)*27+3
		self.redChannel = (cueId-1)*27+10
		self.greenChannel = (cueId-1)*27+12
		self.blueChannel = (cueId-1)*27+14
		self.whiteChannel = (cueId-1)*27+16
		# TODO init from DMX
		self.zoom = 0 # aka beamSize
		self.trackerPosition = (0,0,0)
		self.height = 0
		self.red = 0
		self.green = 0
		self.blue = 0
		self.white = 0
		Highlight.dmxManager.subscribeChannel(self.intensityChannel, self.setIntensityFromDmx)
		Highlight.dmxManager.subscribeChannel(self.zoomChannel, {'object':self,'name':'zoom'})
		Highlight.dmxManager.subscribeChannel(self.tiltChannel, {'object':self,'name':'height'})
		Highlight.dmxManager.subscribeChannel(self.redChannel, {'object':self,'name':'red'})
		Highlight.dmxManager.subscribeChannel(self.greenChannel, {'object':self,'name':'green'})
		Highlight.dmxManager.subscribeChannel(self.blueChannel, {'object':self,'name':'blue'})
		Highlight.dmxManager.subscribeChannel(self.whiteChannel, {'object':self,'name':'white'})

	def __repr__(self):
		#return f"highlight#{self.cntId} for {self.trackId} / cue {self.cueId} / col({self.red:.1f}, {self.green:.1f}, {self.blue:.1f}, {self.white:.1f}) with lamps {[lamp.lampId for lamp in self]} @ {float(self.intensity):.2f}/{float(self.zoom):.2f}"
		return f"highlight#{self.cntId} for {self.trackId} / cue {self.cueId} / with lamps {[lamp.lampId for lamp in self]} @ {float(self.intensity):.2f}/{float(self.zoom):.2f}"

	########## PROPERTIES

	@property
	def trackerPosition(self):
		return self._trackerPosition
	
	@trackerPosition.setter
	def trackerPosition(self, value):
		self._trackerPosition = value
		# promote to all lamps
		for lamp in self:
			lamp.trackerPosition = value

	@property
	def intensity(self):
		return self._intensity

	@intensity.setter
	def intensity(self, value):
		prev = self.intensity if hasattr(self, '_intensity') else 0
		self._intensity = value
		if value != prev:
			for lamp in self:
				lamp.intensity = value
			if value == 0:
				self.releaseAllLamps()
			if prev == 0:
				self.acquireLamps()

	# aka beamSize
	@property
	def zoom(self):
		return self._zoom

	@zoom.setter
	def zoom(self, value):
		if isinstance(value, int):
			value = value/255
		self._zoom = value
		for lamp in self:
			lamp.beamSize = value

	@property
	def red(self):
		return self._red

	@red.setter
	def red(self, value):
		if isinstance(value, int):
			value = value/255
		self._red = value
		for lamp in self:
			lamp.red = value

	@property
	def green(self):
		return self._green

	@green.setter
	def green(self, value):
		if isinstance(value, int):
			value = value/255
		self._green = value
		for lamp in self:
			lamp.green = value

	@property
	def blue(self):
		return self._blue

	@blue.setter
	def blue(self, value):
		if isinstance(value, int):
			value = value/255
		self._blue = value
		for lamp in self:
			lamp.blue = value

	@property
	def white(self):
		return self._white

	@white.setter
	def white(self, value):
		if isinstance(value, int):
			value = value/255
		self._white = value
		for lamp in self:
			lamp.white = value

	@property
	def height(self):
		return self._height

	@height.setter
	def height(self, value):
		if isinstance(value, int):
			value = value/255
		self._height = value
		for lamp in self:
			lamp.height = value


	########### "PUBLIC" METHODS

	def append(self, lamp):
		super().append(lamp)
		self.setLampAttributes(lamp)

	def delete(self):
		Highlight.dmxManager.unsubscribeChannel(self.intensityChannel, self.setIntensityFromDmx)
		super().delete()

	############# "PRIVATE" METHODS

	def initFromCueTable(self):
		self.activationId = int(Highlight.cueTable[str(self.cueId), 'Activation'].val)
		self.color = int(Highlight.cueTable[str(self.cueId), 'Color'].val)
		self.beam = int(Highlight.cueTable[str(self.cueId), 'Beam'].val)
		self.shutter = int(Highlight.cueTable[str(self.cueId), 'Shutter'].val)
		self.maxSize = int(Highlight.cueTable[str(self.cueId), 'Amount'].val)		
		self.priority = int(Highlight.cueTable[str(self.cueId), 'Priority'].val)		

	# gets called, whenever intensity changes from 0 to >0
	# TODO: gets called regularly or at least when lamps are released
	def acquireLamps(self):
		if self.intensity is not 0:
			lamps = self.lampManager.RequestLamps(self, self.maxSize)
		return

	def setLampAttributes(self, lamp):
		debug("setting")
		lamp.color = self.color
		lamp.beam = self.beam
		lamp.shutter = self.shutter
		lamp.activationId = self.activationId
		lamp.intensity = self.intensity
		lamp.trackerPosition = self.trackerPosition
		lamp.red = self.red
		lamp.green = self.green
		lamp.blue = self.blue
		lamp.white = self.white


	def setIntensityFromDmx(self, value):
		self.intensity = value/255


