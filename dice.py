import random
import time

class Dice():
	def __init__(self):
		self.d1 = [[-1, 1],[-1, 1],[-1, 1]] # the opposing faces of the die and their parity
		self.d2 = [[-1, 1],[-1, 1],[-1, 1]]
		self.h1 = [] # history of die 1
		self.h2 = [] # history of die 2
		random.seed(time.time())
	def roll(self):
		index1 = (random.randint(0, 2), random.randint(0, 1))
		index2 = (random.randint(0, 2), random.randint(0, 1))
		result = (self.d1[index1[0]][index1[1]], self.d2[index2[0]][index2[1]]) # a face was rolled. This references the parity of that face.
		self.h1.append(result[0])
		self.h2.append(result[1])
		self.d1[index1[0]] = [result[0], result[0]] # set the pair of faces to whatever was rolled
		self.d2[index2[1]] = [result[1], result[1]]
		return result

def main():
	pass

if __name__ == '__main__':
	main()