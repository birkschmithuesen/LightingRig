"""
Extension classes enhance TouchDesigner components with python. An
extension is accessed via ext.ExtensionClassName from any operator
within the extended component. If the extension is promoted via its
Promote Extension parameter, all its attributes with capitalized names
can be accessed externally, e.g. op('yourComp').PromotedFunction().

Help: search "Extensions" in wiki
"""

from inspect import signature

class DMXManagerExt(list):
	"""
	DMXManagerExt description

	only here, the list is zero-based.
	outside of this file dmx-channels can be treated as one-based
	"""
	def __init__(self, ownerComp):
		# The component to which this extension is attached
		self.ownerComp = ownerComp
		self.initFromDmx()

	def initFromDmx(self):
		for i in range(512):
			value = op('dmxin1')[f'c{i+1}']
			#print(i, value)
			self.append({'value':value, 'callbacks':[]})

	def updateDmxChannel(self, channel, value):
		#debug(channel, value)
		index = channel - 1
		self[index]['value'] = value
		for callback in self[index]['callbacks']:
			self.executeCallback(index, callback)

	def subscribeChannel(self, channel, callback, sixteenBit=False):
		#debug(callback)
		index = channel - 1
		self[index]['callbacks'].append(callback)
		self.executeCallback(index, callback)

	def unsubscribeChannel(self, channel, callback):
		index = channel - 1
		if callback in self[index]['callbacks']:
			self[index]['callbacks'].remove(callback)
		#debug(self[channel])

	def executeCallback(self, index, callback):
		value = self[index]['value']
		if callable(callback):
			if len(signature(callback).parameters) == 1:
				callback(value)
			else:
				channel = index + 1
				callback(channel, value)
		else:
			setattr(callback['object'], callback['name'], int(value))

	def Reset(self):
		self.clear()
		self.initFromDmx()