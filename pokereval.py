from deuces import *

translation = {
	":diamonds:" : "d",
	":clubs:" : "c",
	":hearts:" : "h",
	":spades:" : "s"
}

def translate(card):
	val = card.split(" ")[0];
	suit = card.split(" ")[1];

	if val == "10":
		val = "T"

	return (str(val)+translation[suit])

def winner(bboard, players):

	evaluator = Evaluator()

	board = []

	for card in bboard:
		board.append(Card.new(translate(card)))

	best = 100000;
	winner = players[0]
	besthand = ""

	for player in players:
		hand = [Card.new(translate(player.hand[0])),Card.new(translate(player.hand[1]))]
		score = evaluator.evaluate(board,hand)
		if(score < best):
			best = score
			winner = player;
			besthand = evaluator.class_to_string(evaluator.get_rank_class(score))

	return [winner,besthand]

def besthand(bboard,player):
	board = []
	evaluator = Evaluator()
	for card in bboard:
		board.append(Card.new(translate(card)))
	hand = [Card.new(translate(player.hand[0])),Card.new(translate(player.hand[1]))]
	score = evaluator.evaluate(board,hand)
	return evaluator.class_to_string(evaluator.get_rank_class(score))