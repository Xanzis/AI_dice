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
				ai_bet = ai_func(zip(dice.h1, dice.h2), choice_history)
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



def sample_function(dice_hist, choice_hist):
	a = random.randint(0, 1)
	if a:
		return -1
	return 1

def main():
	Arena.run_manual(4, 2, sample_function)

if __name__ == '__main__':
	main()

