import random,json,dtime

class Player:
	def __init__(self, user, playername, game):
		self.user = user
		self.display_name = playername	
		self.game = game
		self.status = "Active"

		self.hand = []
		self.bet = 0
		self.first_turn = True
		self.won = False

		# Getting money from json file
		with open('data.json', 'r') as js:
			self.data = json.load(js)
		if self.user.id in self.data:
			self.money = self.data[self.user.id]['money']
		else:
			self.money = 200
			self.data[self.user.id] = {
				"display_name":self.display_name,
				"money":200,
				"games":0,
				"won":0,
				"folds":0,
				"winrate":0,
				"lastbeg":[0,0,0,0]
			}
			with open('data.json', 'w') as outfile:  
				outfile.write(json.dumps(self.data, sort_keys=True,indent=4, separators=(',', ': ')))
		
	def fold(self):
		self.status = "Folded"

	def update(self):
		with open('data.json', 'r') as js:
			self.data = json.load(js)
		d = self.data[self.user.id]
		d['money'] = self.money
		d['games']+=1
		if(self.status == "Folded"):
			d['folds']+=1
		if(self.won):
			d['won']+=1
		d['winrate'] = int((d['won']/d['games'])*100)
		with open('data.json', 'w') as outfile:  
			outfile.write(json.dumps(self.data, sort_keys=True,indent=4, separators=(',', ': ')))

