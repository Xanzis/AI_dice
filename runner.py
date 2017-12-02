from dice import Dice
import random

class Arena():
	def __init__(self, player1func, player2func, rounds_per_match, matches, choice_history=None, mode=''):
		self.player1func = player1func
		self.player2func = player2func
		self.choice_history = []
		if choice_history:
			self.choice_history = choice_history
		self.rounds_per_match = rounds_per_match
		self.matches = matches
		self.mode = mode
		self.dice = Dice()
		self.pot = 0
	def getchoices(self):
		choice1 = self.player1func(zip(self.dice.h1, self.dice.h2), self.choice_history) # pay attention to order, function makers
		choice2 = self.player2func(zip(self.dice.h1, self.dice.h2), self.choice_history)
		self.choice_history.append((choice1, choice2)) # gets choices from the functions being used. 
		return choice1, choice2
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
			choice_history = []
			pot = 0
			persistant = 0
			for __ in range(rounds_per_match):
				print "---"
				print "Round " + str(__ + 1)
				bet = input("Place your bet (-1 or 1)\n")
				ai_bet = ai_func(zip(dice.h1, dice.h2)[-5:], choice_history[-5:]) # passes most recent 5
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
				choice_history.append((bet, ai_bet))
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
		choice_history = []
		select_loc = random.randint(1, self.rounds_per_match)
		for _ in range(select_loc):
			p1_bet = self.player1func(zip(d.h1, d.h2)[-self.history_length:], choice_history[-self.history_length:])
			p2_bet = self.player2func(zip(d.h1, d.h2)[-self.history_length:], choice_history[-self.history_length:])
			roll = d.roll()
			choice_history.append((p1_bet, p2_bet))
		"""
		print len(choice_history)
		print select_loc
		print d.h1
		print d.h2
		print choice_history
		"""
		h1_final = d.h1.pop()
		h2_final = d.h2.pop()
		other_choice = choice_history.pop()[1]
		# following 'ideal choice' specification can be tweaked to reflect what we want the network to do
		if other_choice == h1_final or other_choice == h2_final:
			ideal_choice = other_choice
		else:
			ideal_choice = 0
		"""
		print ideal_choice
		print "The following is being sent off"
		print zip(d.h1, d.h2)[-self.history_length:]
		print choice_history[-self.history_length:]
		"""
		# returns a number from -1 to 1 (currently -1, 0, or 1). To rescale for use in training, add 1 and divide by 2
		# also returns last self.history_length dice histories and choice histories. Take care to buffer if no. iterations < 5
		return zip(d.h1, d.h2)[-self.history_length:], choice_history[-self.history_length:], ideal_choice



def sample_function(dice_hist, choice_hist):
	a = random.randint(0, 1)
	if a:
		return -1
	return 1

def main():
	Arena.run_manual(10, 2, sample_function)

if __name__ == '__main__':
	main()

