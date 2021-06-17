from socket import *
from threading import *
from tkinter import *
from tkinter.scrolledtext import ScrolledText
from blockchain import Blockchain
import uuid
import json

difficulty = 4

class p2p_network_node:
	network_node_socket = None
	s_sock = None
	network_nodes = []
	cnt = 0
	my_ip = ""
	my_port = 0
	server_socket_port = 0
	input_list = []
	node_server_sockets = []
	connected_server_sockets = []
	final_received_message = ""
	p2p_clnt_socket_list = []
	user_id = ''
	BC = Blockchain()

	def __init__(self, ip, port):
		self.user_id = str(uuid.uuid4())
		self.initialize_socket(ip, port)
		self.listen_thread_server_message()
		self.initialize_gui()
		

	def initialize_gui(self):
		self.root = Tk()
		self.root.title(str(len(self.network_nodes)))
		self.root.geometry('1800x950')
		self.root.resizable(0,0)
		self.backFrame = Frame(master=self.root,
                    			width=1800,
                    			height=950,
                   		 	bg='lavender')

		self.id_label = Label(self.root, text = 'Your ID is [ {} ] , and Your URL is [ {}:{} ]' .format(self.user_id, self.my_ip, self.server_socket_port), 
				bg='lavender', fg='black', font=('Times', 20))
		self.id_label.place(x=30, y=30)

		self.chain_area = ScrolledText(height=65, width=40)
		self.chain_area.place(x=40, y=90)

		self.chain_label= Label(self.root, text='Chain', bg='lavender', fg='slate gray', font=('Times', 20))
		self.chain_label.place(x=144, y=820)

		self.chain_label= Label(self.root, text='Chain', bg='lavender', fg='slate gray', font=('Times', 20))
		self.chain_label.place(x=144, y=820)

		self.chain_refresh_button = Button(self.root, text='Refresh', font=('Times', 12), command=self.refresh_chain)
		self.chain_refresh_button.place(x=138, y=870)

		self.pending_transactions_area = ScrolledText(height=65, width=40)
		self.pending_transactions_area.place(x=400, y=90)
		self.pending_transactions_area.configure(state='disabled')

		self.pending_transactions_label= Label(self.root, text='Pending Transactions', bg='lavender', fg='slate gray', font=('Times', 20))
		self.pending_transactions_label.place(x=410, y=820)

		self.pending_transactions_refresh_button = Button(self.root, text='Refresh', font=('Times', 12), command=self.refresh_pending_transaction)
		self.pending_transactions_refresh_button.place(x=500, y=870)

		self.mining_log_area = ScrolledText(height=65, width=40)
		self.mining_log_area.place(x=760, y=90)
		self.pending_transactions_area.configure(state='disabled')

		self.mining_log_label= Label(self.root, text='Mining Log', bg='lavender', fg='slate gray', font=('Times', 20))
		self.mining_log_label.place(x=850, y=820)

		self.mining_button = Button(self.root, text='Mine', font=('Times', 12), command=self.mine)
		self.mining_button.place(x=880, y=870)

		self.network_nodes_area = ScrolledText(height=65, width=40)
		self.network_nodes_area.place(x=1120, y=90)

		self.network_nodes_label= Label(self.root, text='Network Nodes', bg='lavender', fg='slate gray', font=('Times', 20))
		self.network_nodes_label.place(x=1175, y=820)

		self.network_nodes_refresh_button = Button(self.root, text='Refresh', font=('Times', 12), command=self.refresh_nodes)
		self.network_nodes_refresh_button.place(x=1225, y=870)

		self.amount_label = Label(self.root, text='Amount', bg='lavender', fg='black')
		self.amount_label.place(x=1480, y=90)
		self.get_amount = Entry(self.root)
		self.get_amount.place(x=1530, y = 90)

		self.recipient_label = Label(self.root, text='Recipient', bg='lavender', fg='black')
		self.recipient_label.place(x=1459, y=130)
		self.get_recipient = Entry(self.root)
		self.get_recipient.place(x=1530, y = 130)

		self.add_to_pending_transaction_button = Button(self.root, text='Send', font=('Times', 12), command=self.send_transaction)
		self.add_to_pending_transaction_button.place(x=1700, y=105)

		self.backFrame.pack()
		self.backFrame.propagate(0)

	def initialize_socket(self, ip, port):
		self.network_node_socket = socket(AF_INET, SOCK_STREAM)
		remote_ip = ip
		remote_port = port
		self.network_node_socket.connect((remote_ip, remote_port))	

	def listen_thread_server_message(self):
		t1 = Thread(target=self.recv_from_server, args=(self.network_node_socket,))
		t2 = Thread(target=self.accept_network_node, args=())
		t1.start()	
		t2.start()
	
	def refresh_chain(self):
		self.chain_area.configure(state='normal')
		self.chain_area.delete("1.0", "end")
		json_chain = json.dumps(self.BC.chain, indent=1)
		self.chain_area.insert(INSERT, json_chain)
		self.chain_area.configure(state='disabled')

	def refresh_nodes(self):
		nodes_str = ''
		cnt = 1
		self.network_nodes_area.configure(state='normal')
		self.network_nodes_area.delete("1.0", "end")
		for s in self.node_server_sockets:
			nodes_str = nodes_str + '{} {}:{}\n' .format(cnt, s[0], s[1])
			cnt += 1
		self.network_nodes_area.insert(INSERT, nodes_str)
		self.network_nodes_area.configure(state='disabled')

	def refresh_pending_transaction(self):
		self.pending_transactions_area.configure(state='normal')
		self.pending_transactions_area.delete("1.0", "end")
		json_pending_transactions = json.dumps(self.BC.pending_transactions, indent=1)
		self.pending_transactions_area.insert(INSERT, json_pending_transactions)
		self.pending_transactions_area.configure(state='disabled')

	def send_transaction(self):
		if (not (self.get_amount == '')) and (not(self.get_recipient == '')):
			try :
				amount = float(self.get_amount.get())
				recipient = self.get_recipient.get()
				new_transaction = self.BC.create_new_transaction(amount, self.user_id, recipient)
				adding_block_num = self.BC.add_transaction_to_pending_transactions(new_transaction)
			except:
				pass
		self.refresh_pending_transaction()
		self.broadcast_pending_transactions()

	def proof_of_work(self, previous_block_hash, current_block_data):
		self.mining_log_area.configure(state='normal')
		self.mining_log_area.delete("1.0", "end")
		nonce = 0
		hash_data = self.BC.hash_block(previous_block_hash, current_block_data, nonce)
		while(hash_data[0:difficulty] != '0'*difficulty):	
			nonce += 1
			self.mining_log_area.insert(INSERT, '[Mining] [Difficutly = {}] : {}\n' .format(difficulty, nonce))	
			self.mining_log_area.yview(END)
			hash_data = self.BC.hash_block(previous_block_hash, current_block_data, nonce)
		self.mining_log_area.configure(state='disabled')
		return nonce

	def mine(self):
		last_block = self.BC.get_last_block()
		previous_block_hash = last_block['previous_block_hash']
		current_block_data = self.BC.pending_transactions
		nonce = self.proof_of_work(previous_block_hash, current_block_data)
		hash_data = self.BC.hash_block(previous_block_hash, current_block_data, nonce)
		new_block = self.BC.create_new_block(nonce, previous_block_hash, hash_data)
		self.refresh_chain()
		self.broadcast_chain()
		self.refresh_chain()
	
	def broadcast_chain(self):
		data = json.dumps(self.BC.chain).encode('utf-8')
		for c_sock in self.p2p_clnt_socket_list :
			c_sock.send(data)

	def broadcast_pending_transactions(self):
		data = json.dumps(self.BC.pending_transactions).encode('utf-8')
		for c_sock in self.p2p_clnt_socket_list :
			c_sock.send(data)

	def recv_from_server(self, so, ):
		while True : 
			self.input_list.clear()
			buf = so.recv(1024)
			if not buf : 
				break
			self.input_list = buf.decode('utf-8').split('\n')
			for i in self.input_list:
				if not (i == '') :
					if i[0] == 'C':
						self.refresh_network_nodes(i)
					elif i[0] == 'S':
						self.recv_nodes_server_info(i)
						self.connect_to_p2p_servers()						
		so.close()

	def refresh_network_nodes(self, msg):
		msg = msg[1:]
		self.network_nodes.clear()
		self.cnt += 1
		rnn_split1 = msg.split('/')	
		for rs in rnn_split1:
			if not (rs == '') :
				rnn_split2 = rs.split(':')
				self.network_nodes.append((rnn_split2[0], int(rnn_split2[1])))
		if self.cnt == 1 :
			self.my_ip = self.network_nodes[len(self.network_nodes)-1][0]
			self.my_port = self.network_nodes[len(self.network_nodes)-1][1]
		if self.s_sock == None:
			self.make_server_socket()

	def recv_nodes_server_info(self, msg):
		msg = msg[1:]
		self.node_server_sockets.clear()
		nss_split1 = msg.split('/')
		for ns in nss_split1:
			if not(ns == ''):
				nss_split2 = ns.split(':')
				self.node_server_sockets.append((nss_split2[0], int(nss_split2[1])))
		
	def make_server_socket(self):
		self.s_sock = socket(AF_INET, SOCK_STREAM)
		self.s_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
		nss_port = []
		for nss in self.node_server_sockets:
			nss_port.append(nss[1])
		for p in range(3000, 9000) :
			if p not in nss_port:
				try: 
					self.s_sock.bind((self.my_ip, p))	
				except:
					pass
				else:
					self.server_socket_port = p
					break
		self.s_sock.listen(100)
		server_info = '{0}:{1}' .format(self.my_ip, self.server_socket_port)
		self.network_node_socket.send(server_info.encode('utf-8'))

	
	def connect_to_p2p_servers(self):
		for nss in self.node_server_sockets:
			if (nss not in self.connected_server_sockets) and (not nss[1] == self.server_socket_port):
				print('connecting to node server {0}:{1}' .format(nss[0], nss[1]))
				temp_socket = None
				temp_socket = socket(AF_INET, SOCK_STREAM)
				remote_ip = nss[0]
				remote_port = nss[1]
				temp_socket.connect((remote_ip, remote_port))	
				self.p2p_clnt_socket_list.append(temp_socket)
				self.connected_server_sockets.append(nss)

	def receive_message_from_node(self, n_socket):
		while True:
			try:
				incoming_message = n_socket.recv(1024)
				if not incoming_message:
					break
			except:
				continue
			else:	
				self.final_received_message = incoming_message.decode('utf-8')
				dict_data = json.loads(self.final_received_message)
				if 'amount' in dict_data[0].keys() :
					self.BC.pending_transactions = dict_data
					
				elif 'index' in dict_data[0].keys():
					self.BC.chain = dict_data
					self.BC.pending_transactions.clear()
					
		n_socket.close()	


	def accept_network_node(self):
		while True:
			if len(self.node_server_sockets) > 1 :
				network_node = n_socket, (ip,port) = self.s_sock.accept()
				print('[p2p network]', ip, ':', str(port), 'is connected')				
			else :
				continue
			t_receive = Thread(target=self.receive_message_from_node, args=(n_socket,))
			t_receive.start()
	

if __name__ == "__main__":
	ip = input("server IP addr: ")
	if ip == '':
		ip = '127.0.0.1'
	port = 4094
	pnn = p2p_network_node(ip, port)

	mainloop()
	

