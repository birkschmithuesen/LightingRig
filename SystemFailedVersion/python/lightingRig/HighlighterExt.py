"""
Extension classes enhance TouchDesigner components with python. An
extension is accessed via ext.ExtensionClassName from any operator
within the extended component. If the extension is promoted via its
Promote Extension parameter, all its attributes with capitalized names
can be accessed externally, e.g. op('yourComp').PromotedFunction().

Help: search "Extensions" in wiki
"""

from highlight import Highlight

class HighlighterExt(dict):
	"""
	HighlighterExt description
	"""
	def __init__(self, ownerComp):
		# The component to which this extension is attached
		self.ownerComp = ownerComp
		
		self.cueTable = op('../cue_table')
		self.cueAttributes = {}
		# init the cue intensities with the value from the cue_table 
		# these intensities will later be set by dmx
		for row in self.cueTable.rows():
			if row[0].val == "Cue": 
				continue
			self.cueAttributes[int(row[0].val)] = {'intensity': self.cueTable[row[0].val, 'Intensity'].val, 'zoom': 1.0}

	def Reset(self):
		debug('resetting Highlighter')
		for highlight in self:
			self[highlight].delete()
		self.clear()
		return

	# gets called onFrameStart from ExecuteDAT
	def Tick(self):
		debug("tick")
		self.reTriggerLampAcquisition()

	def printOutHighlights(self):
		out = ""
		for highlight in self.values():
			out += str(highlight) + "\n"
		return out

	def reTriggerLampAcquisition(self):
		for highlight in self.values():
			highlight.acquireLamps()


	def NewHighlight(self, highlight):
		if highlight.trackId in self:
			self.DeleteHighlight(highlight.trackId)
		self[highlight.trackId] = highlight
		return

	# whenever an ID disappears from the list or the highlightcue for an existing ID changes, we have to remove the former Highlight:
	# - turn MQ-execs off by osc
	def DeleteHighlight(self, highlightId):
		debug(f'Deleting Highlight {highlightId}')
		highlight = self.pop(highlightId)
		highlight.delete()
		return

	# whenever the position values for an ID change, we have to change the position for the respective trackers
	def UpdatePosition(self, trackId, position):
		if trackId not in self:
			return
		highlight = self[trackId]
		if not highlight:
			return
		for lamp in highlight:
			lamp.trackerPosition = position
		return


# this shit is needed to get from the Table to python objects...

	def ReIndexHighlightsFromDat(self, dat):
		debug ("start reIndex", self)
		# go thru the rows and find out if it is a new highlight or a known one and also look if old ones don't exist anymore
		tempHighlights = dict(self)
		newHighlights = []

		for rowId in range(1,dat.numRows):
			trackId = int(dat[rowId,'Trackid'].val)
			cueId = int(dat[rowId,'Highlightcue'].val)

			if cueId == 0:
				continue

			if trackId not in tempHighlights:
				# complete new Highlight!
				#debug(f"highlight for {trackId}/{cueId} is completely new!")
				highlight = Highlight(trackId, cueId)
				newHighlights.append(highlight)
			else:
				if tempHighlights[trackId].cueId != cueId:
					# this trackId has the cue changed - so it is considered new
					highlight = Highlight(trackId, cueId)
					#debug(f"{highlight} has a new cue-type!")
					newHighlights.append(highlight)
				else:
					# if this trackId had a highlight before AND had the same cue, it is considered already existent
					#debug(f"highlight for {trackId} already there")
					pass

				del tempHighlights[trackId]
			
		for oldHighlightId in tempHighlights:
			# debug(f"deleting {tempHighlights[oldHighlight]}")
			self.DeleteHighlight(oldHighlightId)

		for newHighlight in newHighlights:
			self.NewHighlight(newHighlight)

		#debug("stop reIndex", self)
		return