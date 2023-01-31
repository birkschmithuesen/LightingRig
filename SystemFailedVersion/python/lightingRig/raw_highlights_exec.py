# me - this DAT.
# 
# dat - the changed DAT
# rows - a list of row indices
# cols - a list of column indices
# cells - the list of cells that have changed content
# prev - the list of previous string contents of the changed cells
# 
# Make sure the corresponding toggle is enabled in the DAT Execute DAT.
# 
# If rows or columns are deleted, sizeChange will be called instead of row/col/cellChange.


# this shit is needed to get from the Table to python objects...

# whenever either a new ID appears or the cue for an existing ID changes, we have to compose a new Highlight
# composing an highlight consist of:
# - choose one or more Lamps to track the ID
# - send the respective trackers (continously)
# - (maybe trigger a new composition after a second or so)
# - trigger MQ-execs by osc
# -> op('lamps').NewHighlight(highlight):

# whenever an ID disappears from the list or the cue for an existing ID changes, we have to remove the former Highlight:
# - turn MQ-execs off by osc
# -> op('lamps').DeleteHighlight(highlight):

# whenever the position values for an ID change, we have to change the position for the respective trackers
# -> op('lamps').UpdatePosition(position):


def onTableChange(dat):
	# this will be called max once each frame and should send all the positions to the highlighterExt
	#debug('tableChange')
	for rowId in range(1,dat.numRows):
		trackId = int(dat[rowId,'Trackid'])
		position = (float(dat[rowId, 'Positionx']), float(dat[rowId, 'Positiony']), float(dat[rowId, 'Positionz']))
		#debug(trackId, position)
		op.highlighter.UpdatePosition(trackId, position)
	return

def onRowChange(dat, rows):
	#debug('rowChange')
	return

def onColChange(dat, cols):
	#debug(cols)
	return

def onCellChange(dat, cells, prev):
	reIndex = False
	for cell in cells:
		if cell.col in [0,16]:
			reIndex = True
			debug('onCellChange', cell)	
	if reIndex: op.highlighter.ReIndexHighlightsFromDat(dat)
	return

def onSizeChange(dat):
	debug('sizeChange')	
	op.highlighter.ReIndexHighlightsFromDat(dat)
	return


