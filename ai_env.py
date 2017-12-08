import ai
import dice
import os
import random

class Env():
	def __init__(self, path):
		self.d = dice.Dice()
		self.air = ai.AIRunner(path)
		self.c1 = [0, 0, 0, 0, 0]
		self.c2 = [0, 0, 0, 0, 0]
		self.d1 = [0, 0, 0, 0, 0]
		self.d2 = [0, 0, 0, 0, 0] # c1 c2 d1 d2 is correct order for AIR
		self.qubit = [0, 0, 0, 0, 0] # this is dumb

		self.observation_state.shape = (25)
		self.action_space.n = 2 # maybe incorrect

	def step(self, action):
		done = False
		own_choice = action # should be -1 or 1
		to_feed = (np.array(self.c1 + self.c2 + self.d1 + self.d2) + 1) * 0.5
		other_choice = (np.argmax(self.air.run([to_feed])) - 0.5) * 2

		droll_1, droll_2 = self.d.roll()

		reward = Env.reward(droll_1, droll_2, other_choice, own_choice)

		self.c1 = self.c1[1:] + [own_choice] # this might be slow
		self.c2 = self.c2[1:] + [other_choice]
		self.d1 = self.d1[1:] + [droll_1]
		self.d2 = self.d2[1:] + [droll_2]
		# ignoring qubit for now

		new_state = np.array([self.c1 + self.c2 + self.d1 + self.d2 + self.qubit])

		endprob = 0.1
		if random.random() < endprob:
			done = True

		return new_state, reward, done



	def reset(self):
		self.d = dice.Dice()
		self.c1 = [0, 0, 0, 0, 0]
		self.c2 = [0, 0, 0, 0, 0]
		self.d1 = [0, 0, 0, 0, 0]
		self.d2 = [0, 0, 0, 0, 0] # c1 c2 d1 d2 is correct order for AIR
		self.qubit = [0, 0, 0, 0, 0]

	@classmethod
	def reward(cls, d1, d2, c2, own_bet):
		reward = 0.5 * (own_bet == d1) + 0.5 * (own_bet == d2) + 0.1 * (own_bet == c1) # slight bias towards matching other, major bias towards matching dice
		return reward
