class Dice():
    def __init__(self):
        self.curface = 0
        self.roll()
		
    def roll(self):
        import random
        self.curface =  random.randint(1,6)
        
    def face(self):
        return self.curface