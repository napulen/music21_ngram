import music21
import numpy as np
import os

'''
Receives a Music21 score and outputs a list of simultaneous onsets in the outer voices.
The "resolution" is set for 8th notes by default (0.5 of a quarter). Rests are ignored.
'''
def getOnsets(score, resolution=0.5):
	onsets = []

	# Soprano is usually the first spine (right to left)
	soprano = score[0]
	soprano = soprano.flat.getElementsByClass(music21.note.Note)

	# Bass is the last spine (right to left)
	bass = score[-1]
	bass = bass.flat.getElementsByClass(music21.note.Note)
	
	# Get the offset from the last note of the score
	ns = score.flat.getElementsByClass(music21.note.Note)
	lastOffset = ns[-1].offset

	b = music21.note.Rest(quarterLength=bass[0].offset)
	s = music21.note.Rest(quarterLength=soprano[0].offset)
	
	for offset in np.arange(0, lastOffset+resolution, resolution):
		bs = bass.getElementsByOffset(offset)
		ss = soprano.getElementsByOffset(offset)
		if len(bs) == 1 or len(ss) == 1:
			if len(bs) == 1:
				b = bs[0]
			if len(ss) == 1: 
				s = ss[0]
			if not b.isRest and not s.isRest:			
				onsets.append([offset, b, s])
	return onsets

'''
Receives a list of onsets and outputs a list of bigram tuples from it
'''
def getBigrams(onsets):
	return list(zip(onsets, onsets[1:]))
	
'''
Receives a list of bigram tuples and outputs a string with the intervals for each bigram
'''
def getIntervals(bigrams):
	intervalBigrams = []
	for bigram in bigrams:
		# Unpack the bigrams
		offset1, bass1, soprano1 = bigram[0]
		offset2, bass2, soprano2 = bigram[1]
		# Compute intervals
		H1 = music21.interval.Interval(bass1, soprano1)
		Mbass = music21.interval.Interval(bass1, bass2)
		Msoprano = music21.interval.Interval(soprano1, soprano2)
		H2 = music21.interval.Interval(bass2, soprano2)
		intervalBigrams.append((offset1, offset2, '({} [{} {}] {})'.format(H1.name, Mbass.directedName, Msoprano.directedName, H2.name)))
	return intervalBigrams

'''
Prints all bigram interval strings
'''
def printAll(bigramDict):
	for interval,locations in bigramDict.items():
		print(interval)
		for l in locations:
			file, start, end = l
			print('\t{}, {}-{}'.format(file, start/2.0, end/2.0))


'''
Prints unique bigram interval strings
'''
def printUnique(bigramDict):
	for interval,locations in bigramDict.items():
		if len(locations) == 1:
			print(interval)
			for l in locations:
				file, start, end = l
				print('\t{}, {}-{}'.format(file, start/2.0, end/2.0))


if __name__ == '__main__':
	allIntervalBigrams = {}
	for filename in os.listdir("."):
		if filename.endswith(".krn"):
			s = music21.converter.parse(filename)
			onsets = getOnsets(s)
			bigrams = getBigrams(onsets)
			intervalBigrams = getIntervals(bigrams)
			for startOffset, endOffset, interval in intervalBigrams:
				if interval not in allIntervalBigrams:
					allIntervalBigrams[interval] = [(filename, startOffset, endOffset)]
				else:
					allIntervalBigrams[interval].append((filename, startOffset, endOffset))
	printUnique(allIntervalBigrams)




