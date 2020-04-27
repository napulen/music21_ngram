import music21
import numpy as np
import os

'''
Receives a Music21 score and outputs a list of simultaneous onsets in the outer voices.
The "resolution" is set for 8th notes by default (0.5 of a quarter). Rests are ignored.
'''
def getOnsets(score, resolution=0.5):
	b = music21.note.Rest
	s = music21.note.Rest
	onsets = [[-1.0, b, s]]

	# Soprano is usually the first spine (right to left)
	soprano = score.parts[0]
	soprano = soprano.flat.notesAndRests.stream()

	# Bass is the last spine (right to left)
	bass = score.parts[-1]
	bass = bass.flat.notesAndRests.stream()
	
	# Get the offset from the last note of the score
	ns = score.flat.notesAndRests.stream()
	lastOffset = ns[-1].offset
	
	for offset in np.arange(0.0, lastOffset+resolution, resolution):
		bs = bass.getElementsByOffset(offset)
		ss = soprano.getElementsByOffset(offset)
		bs = [n for n in bs if not type(n) == music21.chord.Chord]
		ss = [n for n in ss if not type(n) == music21.chord.Chord]
		notesOnBass = (len(bs) == 1)
		notesOnSoprano = (len(ss) == 1)
		if notesOnBass or notesOnSoprano:
			if notesOnBass:
				b = bs[0]
			if notesOnSoprano:
				s = ss[0]
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
		# Harmonic 1
		if bass1.isRest or soprano1.isRest:
			H1 = music21.interval.Interval()
			H1.name = "-"
		else:
			H1 = music21.interval.Interval(bass1, soprano1)

		# Melodic in the bass
		if bass1.isRest and not bass2.isRest:
			Mbass = music21.interval.Interval()
			Mbass.directedName = "X"
		elif bass2.isRest:
			Mbass = music21.interval.Interval()
			Mbass.directedName = "-"
		else:
			Mbass = music21.interval.Interval(bass1, bass2)

		# Melodic in the soprano
		if soprano1.isRest and not soprano2.isRest:
			Msoprano = music21.interval.Interval()
			Msoprano.directedName = "X"
		elif soprano2.isRest:
			Msoprano = music21.interval.Interval()
			Msoprano.directedName = "-"
		else:
			Msoprano = music21.interval.Interval(soprano1, soprano2)

		# Harmonic 2
		if bass2.isRest or soprano2.isRest:
			H2 = music21.interval.Interval()
			H2.name = "-"
		else:
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
			print('\t{}, {}-{}'.format(file, start, end))

'''
Prints unique bigram interval strings
'''
def printUnique(bigramDict):
	for interval,locations in bigramDict.items():
		if len(locations) == 1:
			print(interval)
			for l in locations:
				file, start, end = l
				print('\t{}, {}-{}'.format(file, start, end))

# Print iterations progress
def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█'):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = '\r')
    # Print New Line on Complete
    if iteration == total: 
        print()

if __name__ == '__main__':
	allIntervalBigrams = {}
	srcdir = "/home/napulen/dev/haydn_op20_harm/all"
	filenames = os.listdir(srcdir)
	for idx,filename in enumerate(filenames):
		printProgressBar(idx, len(filenames), "Progress", filename)
		if filename.endswith(".krn"):						
			s = music21.converter.parse(os.path.join(srcdir, filename))
			onsets = getOnsets(s)
			bigrams = getBigrams(onsets)
			intervalBigrams = getIntervals(bigrams)
			for startOffset, endOffset, interval in intervalBigrams:
				if interval not in allIntervalBigrams:
					allIntervalBigrams[interval] = [(filename, startOffset, endOffset)]
				else:
					allIntervalBigrams[interval].append((filename, startOffset, endOffset))
	printAll(allIntervalBigrams)




