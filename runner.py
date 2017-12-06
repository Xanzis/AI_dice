from dice import Dice
import random

class Arena():
	def __init__(self, player1func, player2func, rounds_per_match, matches, choice_history=None, mode=''):
		self.player1func = player1func
		self.player2func = player2func
		self.choice_history = [[], []]
		if choice_history:
			self.choice_history = choice_history
		self.rounds_per_match = rounds_per_match
		self.matches = matches
		self.mode = mode
		self.dice = Dice()
		self.pot = 0
		self.history_length = 5
	def getchoices(self):
		ch1 = self.choice_history[0][-self.history_length:]
		ch2 = self.choice_history[1][-self.history_length:]
		d1 = self.dice.h1[-self.history_length:]
		d2 = self.dice.h2[-self.history_length:]

		ch1 = (self.history_length - len(ch1)) * [0] + ch1
		ch2 = (self.history_length - len(ch2)) * [0] + ch2
		d1 = (self.history_length - len(d1)) * [0] + d1
		d2 = (self.history_length - len(d2)) * [0] + d2

		p1_bet = self.player1func(ch1, ch2, d1, d2)
		p2_bet = self.player2func(ch2, ch1, d2, d1)

		self.choice_history[0].append(p1_bet) # gets choices from the functions being used. 
		self.choice_history[1].append(p2_bet)
		return p1_bet, p2_bet
	def run(self):
		pot = 0 # this function implements a roll and scoring.
		for _ in range(self.matches):
			self.dice = Dice()
			for __ in range(self.rounds_per_match):
				choices = self.getchoices()
				roll = self.dice.roll()
				if choices[0] == choices[1]:
					if choices[0] == roll[0]:
						pot += 2
					if choices[1] == roll[1]:
						pot += 2
		return pot

	@classmethod # the following method is for manually playing with a function as the other player
	def run_manual(cls, rounds_per_match, matches, ai_func):
		for _ in range(matches):
			print "_______________"
			print "On match " + str(_ + 1) + " of " + str(matches)
			dice = Dice()
			choice_history = [[], []]
			pot = 0
			persistant = 0
			history_length = 5
			for __ in range(rounds_per_match):
				print "---"
				print "Round " + str(__ + 1)
				bet = input("Place your bet (-1 or 1)\n")

				ch1 = choice_history[0][-history_length:]
				ch2 = choice_history[1][-history_length:]
				d1 = dice.h1[-history_length:]
				d2 = dice.h2[-history_length:]

				ch1 = (history_length - len(ch1)) * [0] + ch1
				ch2 = (history_length - len(ch2)) * [0] + ch2
				d1 = (history_length - len(d1)) * [0] + d1
				d2 = (history_length - len(d2)) * [0] + d2

				ai_bet = ai_func(ch2, ch1, d2, d1) # from perspective of player 2
				# NOTE: if the history is less than five, it passes a shorter list. 
				print "AI bet: " + str(ai_bet)
				roll = dice.roll()
				print "Roll in format (your roll, ai roll)"
				print roll
				if bet == ai_bet:
					if bet == roll[0]:
						pot += 2
						print "You won 2"
					if bet == roll[1]:
						pot += 2
						print "The AI won 2"
				choice_history[0].append(bet)
				choice_history[1].append(ai_bet)
				print "Winnings: " + str(pot)
			print "Winnings at end of match: " + str(pot)
			persistant += pot
		print "Total winnings: " + str(persistant)

# Here's a runner class that will play nice with libgen to make training sets
class Generator():
	def __init__(self, player1func, player2func, rounds_per_match, history_length):
		self.player1func = player1func
		self.player2func = player2func
		self.rounds_per_match = rounds_per_match
		self.history_length = history_length
	def run(self):
		d = Dice()
		choice_history = [[], []]
		select_loc = random.randint(1, self.rounds_per_match)
		for _ in range(select_loc):
			ch1 = choice_history[0][-self.history_length:]
			ch2 = choice_history[1][-self.history_length:]
			d1 = d.h1[-self.history_length:]
			d2 = d.h2[-self.history_length:]
			#print ch1
			ch1 = (self.history_length - len(ch1)) * [0] + ch1
			ch2 = (self.history_length - len(ch2)) * [0] + ch2
			d1 = (self.history_length - len(d1)) * [0] + d1
			d2 = (self.history_length - len(d2)) * [0] + d2
			p1_bet = self.player1func(ch1, ch2, d1, d2)
			p2_bet = self.player2func(ch2, ch1, d2, d1)
			#print "Got through"
			roll = d.roll()
			choice_history[0].append(p1_bet)
			choice_history[1].append(p2_bet)
		"""
		print len(choice_history)
		print select_loc
		print d.h1
		print d.h2
		print choice_history
		"""
		h1_final = d.h1.pop()
		h2_final = d.h2.pop()
		other_choice = choice_history[1].pop()
		# following 'ideal choice' specification can be tweaked to reflect what we want the network to do
		if other_choice == h1_final or other_choice == h2_final:
			ideal_choice = other_choice
		else:
			ideal_choice = h1_final
		# Annoyingly, it looks like ideal will have to be a definite heads or tails for networks
		# to train properly using standard classification techniques. We'll see how this goes: I guess
		# it's a good start to focus on predicting the other player's guess, even if in the first round it
		# will be random.
		"""
		print ideal_choice
		print "The following is being sent off"
		print zip(d.h1, d.h2)[-self.history_length:]
		print choice_history[-self.history_length:]
		"""
		# returns a number from -1 to 1 (currently -1, 0, or 1). To rescale for use in training, add 1 and divide by 2
		# also returns last self.history_length dice histories and choice histories. Take care to buffer if no. iterations < 5
		return zip(d.h1, d.h2)[-self.history_length:], zip(choice_history[0], choice_history[1])[-self.history_length:], ideal_choice



def sample_function(*args):
	a = random.randint(0, 1)
	if a:
		return -1
	return 1

def main():
	Arena.run_manual(10, 2, sample_function)

if __name__ == '__main__':
	main()

