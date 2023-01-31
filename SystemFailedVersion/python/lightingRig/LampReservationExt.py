"""
Extension classes enhance TouchDesigner components with python. An
extension is accessed via ext.ExtensionClassName from any operator
within the extended component. If the extension is promoted via its
Promote Extension parameter, all its attributes with capitalized names
can be accessed externally, e.g. op('yourComp').PromotedFunction().

Help: search "Extensions" in wiki
"""

from lampUser import LampUser

class LampReservationExt(LampUser):
	"""
	LampReservationExt description
	"""
	dmxManager = op.DMX.ext.DMXManagerExt

	def __init__(self, ownerComp):
		# The component to which this extension is attached
		self.ownerComp = ownerComp
		super().__init__()
		self.priority = 99
		self.startChannel = 401
		for i in range(16):
			LampReservationExt.dmxManager.subscribeChannel(self.startChannel+i, self.setDmx)

	def setDmx(self, channel, value):
		#debug(channel, value)
		lampId = channel - self.startChannel
		if value == 0:
			op.lampManager.RequestLampById(self, lampId)
		else:
			self.releaseLamp(lampId)

	def __repr__(self):
		return "MagicQ"