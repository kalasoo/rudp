MAX_CONN  = 1000

#-------------------#
# DataStructure     #
#-------------------#
class ListDict():
	def __init__(self):
	#addr => a ref to an element in the list 
		self.dict = dict()
	#pos  => [addr, value]
		self.list = list()
	#length of dict & list
		self.len  = 0

	def __getitem__(self, addr):
		ref = self.dict[addr]
		self.list.remove(ref)
		self.list.append(ref)
		return ref[1]

	def resetItem(self, addr,value):
		ref = self.dict[addr]
		self.list.remove(ref)
		self.list.append(ref)
		ref[1] = value

	def newItem(self, addr, value):
		if self.len == MAX_CONN:
		#remove the first one in the ListDict
			del self.dict[self.list[0][0]]
			self.list.pop(0)
		else:
			self.len += 1
	#add new item
		ref = [addr, value]
		self.list.append(ref)
		self.dict[addr] = ref

	def __delitem__(self, addr):
		self.list.remove( self.dict[addr] )
		del self.dict[addr]
		self.len -= 1
