import hashlib
import time








class Kok():
	"""docstring for ClassName"""
	def __init__(self, index, prevHash, timestamp, data, hash):
		self.index = index
		self.prevHash = prevHash
		self.timestamp = timestamp
		self.data = data
		self.hash = calcHash(index, prevHash, data)


	def vis(self):
		return f'kok {self.index} : {self.data}'

	
	def calcHash(self, index, prevHash, data):
		return hashlib.sha256(f"{index}{prevHash}{data}".encode("utf-8").hexdigest())
	 


class GensKok(Kok):
	def __init__(self,):
		self.gensKok = Kok(
				0,
				"0",
				int(time.time()),
				"GensKok !",
				self.calcHash(0, "0", "GensKok !")
			)

class SubGensKok(GensKok):
	def __init__(self,):
		pass

class Sls():
	       def __init__(self,):
	       	self.sls = []
        	def create_gensKok(self):
		        self.gensKok = GensKok()
		        self.sls.append(gensKok)
		create_gensKok()
		def addKok(self, data):
	                self.data = data
	                prevKok = self.sls[-1]
	                index =prevKok.index + 1
	                timestamp = int(time.time())
	                hashValue = Kok.calcHash(index, prevKok.hash, data)
	                new = Kok(index, prevKok.hash, timestamp, data, hashValue)
	                self.sls.append(new)

	       def displaySls(self):
                        
                        for kok in self.sls:
	                        print(f"Index : {kok.index}")
	                        print(f"Timestamp : {kok.timestamp}")
	                        print(f"Data : {kok.data}")
	                        print(f"Hash : {kok.hash}")
	                        print(f"PrevKok : {kok.prevKok}")
	                        print("_"*50)


	       def sim(self, kok_Index, new_data):
	                if 0 <= kok_Index < len(self.sls):
	                        self.sls[kok_Index].data = new_data
	                        self.sls[kok_Index].hash = self.calcHash(
	                                self.sls[kok_Index].index,
	                                self.sls[kok_Index].prevKok,
	                                new_data,
	                                )




class SubSls(Sls):
	def __init__(self,):
		pass


if "__name__" == "__name__":
	slsKok = Sls()
	slsKok.addKok("kok 0 Data !")
	slsKok.addKok("kok 1 Data !")
	slsKok.addKok("kok 2 Data !")
	slsKok.addKok("kok 3 Data !")
	slsKok.addKok("kok 4 Data !")
	slsKok.addKok("kok 5 Data !")
	slsKok.addKok("kok 6 Data !")


	print("Original sls :")
	slsKok.displaySls()
