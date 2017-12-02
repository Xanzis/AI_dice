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
Within the 5 values, the most recent iteration appears at the end.

Desired output requires another 2 bytes.
10 is heads, 00 is tails, 01 is each response is equally good/bad.
NOTE: For the network, it may be better to use two neurons as output
These 42 bits are stored in 6 bytes. (2 bits of desired output are directly after 40 in bits)
Last 6 bits of each 6 byte chunk are empty :(
"""

import dice
import runner
import struct
import numpy as np

class LibGen():
	def __init__(self):
		self.othr_ch = []
		self.self_ch = []
		self.othr_d = []
		self.self_d = []
		self.ideals = []
	def generate(self, num, p1func, p2func, rpm, hist_len):
		if not hist_len == 5:
			raise ValueError("Non-5 values for history length not currently supported")
		gen = runner.Generator(p1func, p2func, rpm, hist_len)
		for _ in range(num):
			dice_h, choice_h, ideal = gen.run()
			dice_h = (hist_len - len(dice_h)) * [(0, 0)] + dice_h
			choice_h = (hist_len - len(choice_h)) * [(0, 0)] + choice_h
			self_ch, othr_ch = zip(*choice_h)
			self_d, othr_d = zip(*dice_h)
			self_ch = [(c + 1) * 0.5 for c in self_ch]
			othr_ch = [(c + 1) * 0.5 for c in othr_ch]
			self_d = [(c + 1) * 0.5 for c in self_d]
			othr_d = [(c + 1) * 0.5 for c in othr_d]
			ideal = (ideal + 1) * 0.5
			self.othr_ch.append(othr_ch)
			self.self_ch.append(self_ch)
			self.othr_d.append(othr_d)
			self.self_d.append(self_d)
			self.ideals.append(ideal)
	def clear(self):
		self.othr_ch = []
		self.self_ch = []
		self.othr_d = []
		self.self_d = []
		self.ideals = []

	def store(self, loc):
		out = LibO()
		out.process(self.othr_ch, self.self_ch, self.othr_d, self.self_d, self.ideals)
		out.save(loc)

class LibI():
	def __init__(self):
		self.ocs = []
		self.scs = []
		self.ods = []
		self.sds = []
		self.idls = []
	def load(self, loc):
		with open(loc, 'rb') as f:
			byte_list = bytearray(f.read())
			#print byte_list
			num_list = []
			for i in range(len(byte_list)):
				num_list.append(byte_list[i])
			byte_list = [format(num, '08b') for num in num_list]
			samples = ["".join(byte_list[i:i+6]) for i in range(0, len(byte_list), 6)]
			#for s in samples:
			#	print s
			for _ in range(len(samples)):
				samples[_] = [int(samples[_][i:i+2], 2) for i in range(0, len(samples[_]), 2)]
			#print samples
			for s in samples:
				sc = [_ * 0.5 for _ in s[0:5]]
				oc = [_ * 0.5 for _ in s[5:10]]
				sd = [_ * 0.5 for _ in s[10:15]]
				od = [_ * 0.5 for _ in s[15:20]]
				idl = s[20] * 0.5
				self.scs.append(sc)
				self.ocs.append(oc)
				self.sds.append(sd)
				self.ods.append(od)
				self.idls.append(idl)
		print "Loaded"
		# This function works, and correctly recovers the exact data left by the LibGen.store() method. Do not change.
		#print self.scs
		#print self.ocs
		#print self.sds
		#print self.ods
		#print self.idls
	def compile_data(self, loc):
		self.load(loc)
		together = [self.scs[i] + self.ocs[i] + self.sds[i] + self.ods[i] for i in range(len(self.scs))]
		return together, self.idls

	def load_datasets(self, loc):
		TRAINING_SIZE = 50000
		VALIDATION_SIZE = 10000
		TEST_SIZE = 10000
		in_data, out_data = self.compile_data(loc)
		in_data = np.reshape(in_data, (len(in_data), len(in_data[0]), 1))
		# This next line assumes only one output neuron
		out_data = np.reshape(out_data, (len(out_data), 1, 1))
		data = zip(in_data, out_data)
		train_data = data[0:TRAINING_SIZE]
		valid_data = data[TRAINING_SIZE:TRAINING_SIZE+VALIDATION_SIZE]
		test__data = data[TRAINING_SIZE+VALIDATION_SIZE:TRAINING_SIZE+VALIDATION_SIZE+TEST_SIZE]
		print test__data[0:1]
		return train_data, valid_data, test__data
		



class LibO():
	def __init__(self):
		self.byte_list = None
	def process(self, ocs, scs, ods, sds, idls):
		bitstring = ""
		if not len(ocs[0]) == len(scs[0]) == len(ods[0]) == len(sds[0]) == 5:
			print scs
			print ocs
			print sds
			print ods
			print idls
			raise TypeError("rounds to save don't match up") # Right now this only really works for histlen of 5
		for _ in range(len(ocs)):
			oc = [format(int(i * 2), '02b') for i in ocs[_]]
			sc = [format(int(i * 2), '02b') for i in scs[_]]
			od = [format(int(i * 2), '02b') for i in ods[_]]
			sd = [format(int(i * 2), '02b') for i in sds[_]]
			idl = format(int(idls[_] * 2), '02b')
			to_add = "".join(sc) + "".join(oc) + "".join(sd) + "".join(od) + idl + "000000"
			if len(to_add) != 48:
				print "what in tarnation"
				print len(to_add)
				print to_add
				print oc, sc, od, sd, idl
			#print to_add
			bitstring += to_add
			# ending is padding. Eventually, for variable length, it may be best to dynamically mess with that.
		self.byte_list = [int(bitstring[i:i+8], 2) for i in range(0, len(bitstring), 8)]

	def save(self, loc):
		with open(loc, 'wb+') as f:
			f.write(bytearray(self.byte_list))
			print "Saved"



def main():
	#lg = LibGen()
	#lg.generate(80000, runner.sample_function, runner.sample_function, 10, 5)
	#lg.store('rand_v_rand.ts')
	lI = LibI()
	lI.load_datasets('rand_v_rand.ts')



if __name__ == '__main__':
	main()