"""
program for generating libraries to train a network on (with a class for writing and interpreting them in compact form)
The following format will be used for storage:
42 bits can store the input to a network and the desired output. For now:
4 sets of 5 layers of history to store. They are:

Own choice history
Others' choice history
Own die history
Others' die history

For now, this will be stored as the most recent 5 iterations of the game.
For each of these four, the information will be stored in 10 bits (2 per iteration)
where: 10 is heads, 00 is tails, 01 is NA (history doesn't go back that far)
These 40 bits will be arranged end to end in 5 bytes. Look at IO classes for protocol.

Desired output requires another 2 bytes.
10 is heads, 00 is tails, 01 is each response is equally good/bad.
NOTE: For the network, it may be better to use two neurons as output
These 42 bits are stored in 6 bytes. (2 bits of desired output are directly after 40 in bits)
Last 6 bits of each 6 byte chunk are empty :(
"""

import dice

class LibGen():
	def __init__(self):
		pass

class LibI():
	def __init__(self):
		pass

class LibO():
	def __init__(self):
		pass