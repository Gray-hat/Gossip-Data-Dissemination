#a file userd to create peers to be used
#to create a small network
import xmlrpclib
from SimpleXMLRPCServer import SimpleXMLRPCServer
from threading import Thread
import string 
import random
from Tkinter import *
import time

global root


class Graph():
	'''Graph data structure'''
	def __init__(self):

		self.__graph_dict = {} #store graph nodes

	def vertices(self):
		'''return all vertices'''

		return list(self.__graph_dict.keys())

	def edges(self):
		'''Return all existing edges'''
		return self.__get_edges()

	def add_vertix(self,vertix):
		'''Add a vertix into existing vertices'''
		if vertix not in self.__graph_dict:
			self.__graph_dict[vertix] = []

	def add_edge(self, edges):
		'''Add an edge between two vertices'''

		vertix1, vertix2 = tuple(edges)
		#check that the vertices exist. will ignore additio if they already exist
		self.add_vertix(vertix1)
		self.add_vertix(vertix2)

		self.__graph_dict[vertix1].append(vertix2)
		self.__graph_dict[vertix2].append(vertix1)

	def __get_edges(self):
		'''A method to get all edges in a graph'''

		edges = []

		for vertex in self.__graph_dict:
			for neigbour in self.__graph_dict[vertex]:
				if {vertex, neigbour} not in edges:
					edges.append({vertex, neigbour})
		return edges	

	def nodes_adjacent_vertices(self, peer):
		'''Return a nodes adjacent vertices'''

		if peer in self.__graph_dict:
			return self.__graph_dict[peer]

class ChatRoom(object):
	'''A simple chat room to display sending of messages to different
		peers via gossiping
	'''

	def __init__(self):

		self.chat_id = ""
		self.message = "Nothing to show"
		self.create_gui()

	def generate_rand_id(self):
		#generate a random string to serve as the chat_id 
		chars = string.ascii_uppercase + string.digits
		self.chat_id = ''.join(random.choice(chars) for i in range(5))

	def create_gui(self):
		'''Create a simple GUI for the chat'''
		title = "Simple Chat -- Node: "+str(self.serverport)
		root.title(title)
		self.window = Toplevel()
		self.window.geometry("320x220")
		self.msg = Message(self.window,text = self.message, width = 340)
		self.msg.config(font=('times', 12, 'italic'))
		self.msg.pack(fill=X, expand=YES, side = TOP)
		t = Thread(target = self.update_message_area)
		t.daemon = True
		t.start()
		

		

		self.ent = Entry(self.window)
		self.ent.insert(0, 'Type message here') 
		self.ent.pack(side=TOP, fill=X)
		self.ent.focus()
		self.btn = Button(self.window, text='Send', command=self.send_message)
		self.btn.pack(side=RIGHT)

	def send_message(self):
		message = [self.server_id, self.ent.get(), "me"]
		#generate a random message_id
		chars = string.ascii_uppercase + string.digits + string.ascii_lowercase
		message_id = ''.join(random.choice(chars) for i in range(7))
		message_id = message_id
		self.datastore[message_id] = message 
		self.routing({message_id:message})

	def update_message_area(self):
		data = ""
		for label in self.datastore:
			data = data + label + "." + self.datastore[label][0] + " >>> " + self.datastore[label][1] + "\n" + "received from: " + self.datastore[label][2] + "\n"
		self.message = data	

		self.msg["text"] = self.message
		self.msg.update_idletasks()
		time.sleep(1)
		self.update_message_area()


class Peer(ChatRoom):
	def __init__(self, serverport, datatype_used,serverhost = "localhost"):

		self.serverhost = serverhost
		self.serverport = serverport
		self.server_id = '%s:%s'%(serverhost, serverport)
		self.datastore = {} #keep record of what has been received
		self.probability = 0.5
		self.adt = datatype_used
		self.last_received_id = ""
		super(Peer,self).__init__()

	@property
	def adjacent_nodes(self):

		return self.adt.nodes_adjacent_vertices(self)

	def create_server(self):
		'''Server to listen ncoming connections'''
		self.server = SimpleXMLRPCServer((self.serverhost, self.serverport))
		self.server.register_function(self.update_message)
		print "Starting server on port", self.serverport
		#register functions
		self.server.serve_forever() 


	def connect_send_to_peer(self, address, data):
		'''Call methods in the server'''
		proxy = xmlrpclib.ServerProxy("http://"+address)
		infected = proxy.update_message(data, self.server_id)
		try:
			
			if infected:
				return True
			else:
				return False		

		except:
			print "An error occurred"
			return True #assume infected to prevent continuous loop
	def routing(self, data):
		'''Given the created graph. the routing function 
		sends the message to the other nodes connecting to
		the current node'''
		nodes = list(self.adjacent_nodes)
		while nodes:
			node = random.choice(nodes)
			nodes.remove(node)
			print "infecting",node.server_id
			infected = self.connect_send_to_peer(node.server_id,data)
			if not infected:
				print "infected" ,self.server_id,node.server_id

		print "%s is done infecting" %self.server_id

	def update_message(self,data, received_from):
		'''Update message in dict if not infected otherwise return True
		to denote infection'''
		for label in data:
			response = self.__is_infected(label)
			if not response:
				#update receivee
				data[label][2] = received_from
				self.datastore[label] = data[label]
				t = Thread(target = self.routing, args = (data,))
				t.daemon = True
				t.start()
				return False
			return True

	def __is_infected(self, label):
		'''Check if peer is already infected ''' 
		if self.datastore.get(label, None):
			return True
		else:
			return False	



root = Tk()
root.title("Simple Chat")
#using graph structure
graph = Graph()

peer1 = Peer(serverport = 8000, datatype_used =  graph)	
peer2 = Peer(serverport = 8001, datatype_used =  graph)
peer3 = Peer(serverport = 8002, datatype_used =  graph)	
peer4 = Peer(serverport = 8003, datatype_used =  graph)
peer5 = Peer(serverport = 8004, datatype_used =  graph)
peer6 = Peer(serverport = 8005, datatype_used =  graph)
peer7 = Peer(serverport = 8006, datatype_used =  graph)



graph.add_edge({peer1, peer2})
graph.add_edge({peer1, peer3})

graph.add_edge({peer2, peer4})
graph.add_edge({peer2, peer5})

graph.add_edge({peer3, peer6})
graph.add_edge({peer3, peer7})


t1 = Thread(target = peer1.create_server)
t1.daemon = True
t1.start()
t2 = Thread(target = peer2.create_server)
t2.daemon = True
t2.start()
t3 = Thread(target = peer3.create_server)
t3.daemon = True
t3.start()
t4 = Thread(target = peer4.create_server)
t4.daemon = True
t4.start()
t5 = Thread(target = peer5.create_server)
t5.daemon = True
t5.start()
t6 = Thread(target = peer6.create_server)
t6.daemon = True
t6.start()
t7 = Thread(target = peer7.create_server)
t7.daemon = True
t7.start()

root.mainloop()


