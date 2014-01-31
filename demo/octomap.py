
import numpy
import math

MIN_CELL_SIZE = 0.01

class OctNode:
	
	def __init__(self, position, size, data):
		
		self.position = position
		self.size = size
		
		self.isLeaf = True
		
		self.data = data
		
		self.branches = [None, None, None, None, None, None, None, None]
	

class OcTree:
		
	def __init__(self, mapSize):
		self.root = self.addNode((0.0,0.0,0.0), mapSize, [])
		self.mapSize = mapSize
		self.maxDepth = math.ceil(1 - math.log(MIN_CELL_SIZE/mapSize,2))
	
	def addNode(self, position, size, data):
		return OctNode(position, size, data)
	
	def insertData(self, position, data):
		insertData(self, self.root, position, data, depth=1)
	
	def insertData(self, root, position, data, depth):
		
		branch = pickBranch(position, root)
		
		#Check for empty child
		if root.branches(branch) = None:
			root.branches(branch) = addNode(childPosition(root, branch), root.size/2.0, [])
			
			
		#insert node at max depth.
		if depth = self.maxDepth:
			
			
		# if not at max depth, don't insert	
		else:
			insertData(self, root.branches(branch), position, data, depth+1 )
	
	
	def pickBranch(position, root):
		
		xThresh = root.position[1] + root.size/2
		yThresh = root.position[2] + root.size/2
		zThresh = root.position[3] + root.size/2
		
		if position[1] < xThresh:
			if position[2] < yThresh:
				if position[3] < zThresh:
					return 0
				else:
					return 4
			else:
				if position[3] < zThresh:
					return 2
				else:
					return 6
		else:
			if position[2] < yThresh:
				if position[3] < zThresh:
					return 1
				else:
					return 5
			else:
				if position[3] < zThresh:
					return 3
				else:
					return 7				
	
	def childPosition(parent, child):
		pos = parent.position
		
		adj = parent.size/2.0
		
		if child = 0:
			return parent.position
		elif child = 1:
			return (pos[1]+adj, pos[2], pos[3])
		elif child = 2:
			return (pos[1], pos[2]+adj, pos[3])
		elif child = 3:
			return (pos[1]+adj, pos[2]+adj, pos[3])
		elif child = 4:
			return (pos[1], pos[2], pos[3]+adj)
		elif child = 5:
			return (pos[1]+adj, pos[2], pos[3]+adj)
		elif child = 6:
			return (pos[1], pos[2]+adj, pos[3]+adj)
		else:
			return (pos[1]+adj, pos[2]+adj, pos[3]+adj)
	


															