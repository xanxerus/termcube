#!/usr/bin/env pypy
#~ All credit to Chen Shuang (cs0x7f) for this random state scrambler.
#~ His source can be found at <https://gist.github.com/cs0x7f/2566010>
#~ I did not see a license. If this is not okay, please contact me.

from random import randrange
from . import SkewbTurn
from .. import TurnSequence

class SkewbSearch():
	def __init__(self):
		self.center = [0]*360
		self.corner = [0]*8748
		self.centermv = [[0 for col in range(4)] for row in range(360)]
		self.cornermv = [[0 for col in range(4)] for row in range(8748)]
		self.calcperm()
		
	@staticmethod
	def cycle3(arr, i1, i2, i3):
		arr[i1], arr[i2], arr[i3] =\
		arr[i2], arr[i3], arr[i1]

	@staticmethod
	def getctmv(p, m):
		ps = [0, 0, 0, 0, 0, 1]
		s = 0
		for i in range(3, -1, -1):
			p, ps[i] = divmod(p, 6-i)
			s = s + ps[i]
			for j in range(i+1, 6):
				if (ps[j] >= ps[i]):
					ps[j] += 1
		if (s % 2 == 1):
			temp = ps[5]
			ps[5] = ps[4]
			ps[4] = temp
		if (m==0):#L
			SkewbSearch.cycle3(ps, 0, 5, 1)
		elif (m==1):#R
			SkewbSearch.cycle3(ps, 0, 2, 4)
		elif (m==2):#D
			SkewbSearch.cycle3(ps, 1, 3, 2)
		elif (m==3):#B
			SkewbSearch.cycle3(ps, 3, 5, 4)
		idx = 0
		for i in range(0, 4):
			idx *= (6-i)
			for j in range(i+1, 6):
				if (ps[i] > ps[j]):
					idx += 1
		return idx    

	@staticmethod
	def getcnmv(p, m):
		ps = [0] * 8
		for i in range(0, 7):
			p, ps[i] = divmod(p, 3)
		ps[7] = (30 - ps[4] - ps[5] - ps[6]) % 3
		fcmv = [[1, 2, 0, 3], [2, 1, 3, 0], [3, 0, 2, 1], [0, 3, 1, 2]]
		p = fcmv[m][p]
		ps[m] = (ps[m] + 1) % 3
		if (m==0):
			ps[5], ps[6], ps[4] = ps[4]+2, ps[5]+2, ps[6]+2
		elif (m==1):
			ps[6], ps[7], ps[4] = ps[4]+2, ps[6]+2, ps[7]+2
		elif (m==2):
			ps[7], ps[4], ps[5] = ps[4]+2, ps[5]+2, ps[7]+2
		elif (m==3):
			ps[7], ps[5], ps[6] = ps[5]+2, ps[6]+2, ps[7]+2
		for i in range(6, -1, -1):
			p = p * 3 + (ps[i] % 3)
		return p

	def calcperm(self):
		for p in range(0, 360):
			self.center[p]=-1
			for m in range(0, 4):
				self.centermv[p][m] = SkewbSearch.getctmv(p,m)
		for p in range(0, 8748):
			self.corner[p]=-1
			for m in range(0, 4):
				self.cornermv[p][m] = SkewbSearch.getcnmv(p,m)

		self.center[0]=0
		for l in range(0, 5):
			n=0
			for p in range(0, 360):
				if(self.center[p]==l):
					for m in range(0, 4):
						q=p
						for c in range(0, 2):
							q = self.centermv[q][m]
							if (self.center[q]==-1):
								self.center[q]=l+1
								n+=1 
		self.corner[0]=0
		for l in range(0, 7):
			n=0
			for p in range(0, 8748):
				if (self.corner[p]==l):
					for m in range(0, 4):
						q=p
						for c in range(0, 2):
							q = self.cornermv[q][m]
							if (self.corner[q]==-1):
								self.corner[q]=l+1
								n+=1

	def search(self, sol, ct, cn, l, lm = -1):
		if (l==0):
			if (ct==0 and cn==0):
				return True
		else:
			if (self.center[ct]>l or self.corner[cn]>l):
				return False
			for m in range(0, 4):
				if(m!=lm):
					p=ct
					s=cn
					for a in range(0, 2):
						p = self.centermv[p][m]
						s = self.cornermv[s][m]
						sol.append('LRDB'[m]+" '"[a])
						if (self.search(sol, p, s, l-1, m)):
							return 1
						sol.pop()
		return 0
		
	def solutionToString(self):
		sol = []
		cn=randrange(8747)
		ct=randrange(359)
		for l in range(0, 100):
			if(self.search(sol, ct, cn, l)):
				break
		return ' '.join(sol)

def scramble():
    return TurnSequence(SkewbSearch().solutionToString(), SkewbTurn)
