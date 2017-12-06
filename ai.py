# I stole most of this code from https://github.com/sdadas/Tensorflow-Tutorials/blob/master/3_net.py
# I'm not claiming any of the tf implementation here is my own work (for now), I was jsut using this 
# to get a baseline that I could work from (I didn't really understand any of the tensorflow tutorials).
# After training on the rand_v_rand.ts training data: accuracy is 0.5062 (which makes complete sense, 
# since at the moment the system is basically jsut rewarded for guessing what a random number thing does)

import libgen
import tensorflow as tf
import numpy as np
import runner

class Feeder():
	def __init__(self, loc):
		lI = libgen.LibI()
		self.epochs_trained = 0
		self.place = 0
		self.tr, self.va, self.te = lI.load_datasets(loc)
		for i in range(len(self.tr)):
			if int(self.tr[i][1]):
				self.tr[i] = (self.tr[i][0], np.array([0, 1]))
			else:
				self.tr[i] = (self.tr[i][0], np.array([1, 0]))
		for i in range(len(self.va)):
			if int(self.va[i][1]):
				self.va[i] = (self.va[i][0], np.array([0, 1]))
			else:
				self.va[i] = (self.va[i][0], np.array([1, 0]))
		for i in range(len(self.te)):
			if int(self.te[i][1]):
				self.te[i] = (self.te[i][0], np.array([0, 1]))
			else:
				self.te[i] = (self.te[i][0], np.array([1, 0]))
		print "Reformatted outputs to onehot arrays"
	def can_continue(self, num):
		if self.place + num <= len(self.tr) - 1:
			return True
		return False
	def next_batch(self, num):
		data = self.tr[self.place:self.place + num]
		self.place += num
		self.epochs_trained += 1
		return data

class AI1():
	def __init__(self, save_loc = None):
		self.save_loc = save_loc
		pass
	def train(self):
		x_input = tf.placeholder(tf.float32, [None, 20])
		y_input = tf.placeholder(tf.float32, [None, 2])

		feeder = Feeder('rvr_guessown.ts')

		def layer(input, shape, activation, name):
			with tf.name_scope(name):
				W = tf.Variable(tf.random_uniform(shape) * 0.1)
				b = tf.Variable(tf.random_uniform([shape[-1]]) * 0.01)
				res = activation(tf.matmul(input, W) + b)
			return res

		hidden = layer(x_input, [20, 10], tf.nn.sigmoid, 'hidden')
		y = layer(hidden, [10, 2], lambda _: _, 'output')

		cost = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(labels=y_input, logits=y))
		train = tf.train.GradientDescentOptimizer(0.5).minimize(cost)

		saver = tf.train.Saver()

		sess = tf.Session()
		sess.run(tf.global_variables_initializer())
		num_per_epoch = 100
		correct_prediction = tf.equal(tf.argmax(y_input, 1), tf.argmax(y, 1))
		accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))
		ticker = 5
		while feeder.epochs_trained < 200 and feeder.can_continue(num_per_epoch):
			print "Onto epoch number " + str(feeder.epochs_trained)
			x_batch, y_batch = zip(*feeder.next_batch(num_per_epoch))
			sess.run(train, feed_dict={x_input: x_batch, y_input: y_batch})
			ticker += -1
			if not ticker:
				te_x, te_y = zip(*feeder.te)
				print sess.run(accuracy, feed_dict={x_input: te_x, y_input: te_y})
				ticker = 5


		vld_x, vld_y = zip(*feeder.va)
		print sess.run(accuracy, feed_dict={x_input: vld_x, y_input: vld_y})

		if self.save_loc:
			saver.save(sess, self.save_loc)

		sess.close()

	def feedforward(self, x_ins):
		tf.reset_default_graph()

		x_input = tf.placeholder(tf.float32, [None, 20])
		y_input = tf.placeholder(tf.float32, [None, 2])

		def layer(input, shape, activation, name):
			with tf.name_scope(name):
				W = tf.Variable(tf.random_uniform(shape) * 0.01)
				b = tf.Variable(tf.random_uniform([shape[-1]]) * 0.01)
				res = activation(tf.matmul(input, W) + b)
			return res

		hidden = layer(x_input, [20, 10], tf.nn.sigmoid, 'hidden')
		y = layer(hidden, [10, 2], lambda _: _, 'output')

		cost = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(labels=y_input, logits=y))
		train = tf.train.GradientDescentOptimizer(0.5).minimize(cost)

		sess = tf.Session()
		saver = tf.train.Saver()
		saver.restore(sess, self.save_loc)

		print sess.run(y, feed_dict={x_input: x_ins})

class AIRunner():
	def __init__(self, loc):
		tf.reset_default_graph()
		# This is the same thing as AI1.feedforward, but it runs far faster because it only reloads the tf graph once.

		self.x_input = tf.placeholder(tf.float32, [None, 20])
		self.y_input = tf.placeholder(tf.float32, [None, 2])

		def layer(input, shape, activation, name):
			with tf.name_scope(name):
				W = tf.Variable(tf.random_uniform(shape) * 0.01)
				b = tf.Variable(tf.random_uniform([shape[-1]]) * 0.01)
				res = activation(tf.matmul(input, W) + b)
			return res

		self.hidden = layer(self.x_input, [20, 10], tf.nn.sigmoid, 'hidden')
		self.y = layer(self.hidden, [10, 2], lambda _: _, 'output')

		self.cost = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(labels=self.y_input, logits=self.y))
		self.train = tf.train.GradientDescentOptimizer(0.5).minimize(self.cost)

		self.sess = tf.Session()
		self.saver = tf.train.Saver()
		self.saver.restore(self.sess, loc)

	def run(self, x_ins):
		return self.sess.run(self.y, feed_dict={self.x_input: x_ins})

class AIToData():
	def __init__(self, loc):
		self.bot = AIRunner(loc)

		def ai_func(sc, oc, sd, od):
			# sc, oc, sd, od should each be length-five arrays of -1 and 1 values
			to_feed = np.array(sc + oc + sd + od)
			to_feed = (to_feed + 1) * 0.5
			ins = to_feed
			#print self.bot
			#print ins
			res = np.argmax(self.bot.run([ins]))
			return (res - 0.5) * 2

		self.ai_func = ai_func

		self.arena = runner.Arena(ai_func, ai_func, 10, 100)
		self.lg = libgen.LibGen()
	def generate(self, num, store_loc):
		self.lg.generate(num, self.ai_func, self.ai_func, 10, 5)
		self.lg.store(store_loc)

def main():
	#aid = AIToData('/Users/alehugh/Desktop/Programming/AI_dice/tf_saves/ai1_sd')
	#lg = libgne.LibGen()
	#lg.generate(40000, aid.ai_func, aid.ai_func, 10, 5)

	#aid.generate(80000, 'aisd_v_aisd_test.ts')
	ai = AI1('/Users/alehugh/Desktop/Programming/AI_dice/tf_saves/ai_guessown')
	ai.train()

if __name__ == '__main__':
	main()