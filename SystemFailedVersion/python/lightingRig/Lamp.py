class Lamp:
	magicQ = op.magicQ
	maxSize = 400 	# how big can the spot be in cm max (for calculation of zoom dependent of distance and size)
	maxHeight = 6.0 

	def __init__(self, lampId, position):
		self.lampId = lampId
		self.activationId = None
		self.trackerId = 0
		self.intensity = 0
		self.beamSize = 0
		self.position = position
		self.trackerPosition = (0,0,0)
		self.height = -1
		self.zoom = 0
		self.owner = None
		self.dist = 0
		
	####### PROPERTIES

	@property
	def owner(self):
		return self._owner

	@owner.setter
	def owner(self, value):
		self._owner = value

	# should come in 0...1.0
	@property
	def height(self):
		if not hasattr(self, '_height'):
			self._height = 0
		return self._height	

	@height.setter
	def height(self, value):
		self._height = value * Lamp.maxHeight
		self.setMQTracker()

	@property
	def intensity(self):
		return self._intensity

	@intensity.setter
	def intensity(self, value):
		#debug(value)
		prev = -1 if not hasattr(self, '_intensity') else self._intensity
		if value == prev: return
		value = float(value)
		if value > 1.0:
			value = 1.0
		self._intensity = value
		if self.activationId == 66:
			Lamp.magicQ.SetActivationViaArtnet(self.activationId, self.intensity, self.lampId)
		elif self.activationId:
			Lamp.magicQ.SetActivation(self.activationId, self.intensity, self.lampId)
			Lamp.magicQ.SetColor(self.lampId, (self.red, self.green, self.blue, self.white))
			# to release the color fader
			if value == 0: Lamp.magicQ.SetColor(self.lampId, (0,0,0,0))


	@property
	def zoom(self):
		return self._zoom

	@zoom.setter
	def zoom(self, value):
		if isinstance(value, int):
			value = value/255
		if hasattr(self, '_zoom') and value == self.zoom: 
			return
		value = float(value)
		if value > 1.0:
			value = 1.0
		self._zoom = value
		if self.intensity > 0 or value == 0:
			Lamp.magicQ.SetZoom(self.lampId, value)

	@property
	def red(self):
		if not hasattr(self, '_red'):
			self._red = 0
		return self._red

	@red.setter
	def red(self, value):
		if isinstance(value, int):
			value = value/255
		value = min(float(value), 1.0)
		value = max(5/255, value)
		self._red = value
		#if self.intensity > 0 or value == 0:
		Lamp.magicQ.SetColor(self.lampId, (self.red, self.green, self.blue, self.white))

	@property
	def green(self):
		if not hasattr(self, '_green'):
			self._green = 0
		return self._green

	@green.setter
	def green(self, value):
		if isinstance(value, int):
			value = value/255
		value = min(float(value), 1.0)
		value = max(5/255, value)
		self._green = value
		#if self.intensity > 0 or value == 0:
		Lamp.magicQ.SetColor(self.lampId, (self.red, self.green, self.blue, self.white))

	@property
	def blue(self):
		if not hasattr(self, '_blue'):
			self._blue = 0
		return self._blue

	@blue.setter
	def blue(self, value):
		if isinstance(value, int):
			value = value/255
		value = min(float(value), 1.0)
		value = max(5/255, value)
		self._blue = value
		#if self.intensity > 0 or value == 0:
		Lamp.magicQ.SetColor(self.lampId, (self.red, self.green, self.blue, self.white))

	@property
	def white(self):
		if not hasattr(self, '_white'):
			self._white = 0
		return self._white

	@white.setter
	def white(self, value):
		if isinstance(value, int):
			value = value/255
		value = min(float(value), 1.0)
		value = max(5/255, value)
		self._white = value
		#if self.intensity > 0 or value == 0:
		Lamp.magicQ.SetColor(self.lampId, (self.red, self.green, self.blue, self.white))

	@property
	def activationId(self):
		return self._activationId

	@activationId.setter
	def activationId(self, value):
		if value:
			self._activationId = int(value)
		else:
			# TODO: what is this for?
			self._activationId = 0

	@property
	def trackerPosition(self):
		return self._trackerPosition
	
	@trackerPosition.setter
	def trackerPosition(self, value):
		self._trackerPosition = (value[0], value[1], self.height)

		#self._trackerPosition = value
		# if self.height:
		# 	self._trackerPosition = (value[0], value[1], value[2])
		# else:
		# 	self._trackerPosition = (value[0], value[1], self.height)
		if self.beamSize > 0:
			self.calculateZoomFromBeamSize()
		self.setMQTracker()

	@property
	def beamSize(self):
		return self._beamSize

	@beamSize.setter
	def beamSize(self, value):
		self._beamSize = value
		if self.beamSize > 0:
			self.calculateZoomFromBeamSize()

	@property
	def color(self):
		return self._colorId

	@color.setter
	def color(self, value):
		self._colorId = value
		# Lamp.magicQ.ChooseSoftPalette('color', int(value), self.lampId)

	@property
	def shutter(self):
		return self._shutterId

	@shutter.setter
	def shutter(self, value):
		self._shutterId = value
		Lamp.magicQ.ChooseSoftPalette('shutter', int(value), self.lampId)

	@property
	def beam(self):
		return self._beamId

	@beam.setter
	def beam(self, value):
		self._beamId = value
		Lamp.magicQ.ChooseSoftPalette('beam', int(value), self.lampId)


	############ "PRIVATE" METHODS


	def setMQTracker(self):
		Lamp.magicQ.SetTracker(self.lampId, self.trackerId, self.trackerPosition)

	def calculateZoomFromBeamSize(self):
		# calculate distance to tracker - all positions in m
		a = self.trackerPosition
		b = self.position
		dist = 100 * math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2 + (a[2]-b[2])**2)
		self.dist = dist
		if dist == 0 or self.beamSize == 0:
			return

		self.zoom = self.dmxValue(self.beamSize*Lamp.maxSize, dist)/255
		#debug(self.zoom)

	def dmxValue(self, size, distance):
		# size in cm
		# distance in cm
		size1cm = size/distance
		out = 216.73*size1cm**2 - 710.8*size1cm + 305.84
		if out <= 3: out = 3
		if out > 255: out = 255
		return out

	############ "PUBLIC" METHODS


	def __repr__(self):
		return f"lamp#{self.lampId} bz={self.beamSize:.1f} d={self.dist:.1f} z={self.zoom:.2f} h={self.height:.2f} col=({self.red:.1f}, {self.green:.1f}, {self.blue:.1f}, {self.white:.1f}) owned by {self.owner}"

	def release(self):
		self.owner = None
		self.intensity = 0
		self.zoom = 0

	def setControllableFromDmx(self, value):
		self.controllable = value

