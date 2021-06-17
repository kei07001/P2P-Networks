from socket import *
from threading import *

class p2p_server:
	network_nodes = []
	node_server_str = '\nS'
	
	def __init__(self):
		self.s_sock = socket(AF_INET, SOCK_STREAM)
		self.ip = ''
		self.port = 4094
		self.s_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
		self.s_sock.bind((self.ip, self.port))
		print("Waiting for Network Nodes")
		self.s_sock.listen(100)
		self.accept_Network_Node()

	def accept_Network_Node(self):
		while True:
			network_node = n_socket, (ip,port) = self.s_sock.accept()
			if network_node not in self.network_nodes:
				self.network_nodes.append(network_node)
			print(ip, ':', str(port), 'is connected')
			self.refresh_network_nodes()
			self.send_node_server_info()
			t_server = Thread(target=self.receive_node_server_info, args=(n_socket,))
			t_server.start()
				

	def receive_node_server_info(self, n_socket):
		while True:
			try:
				server_info = n_socket.recv(1024)
				if not server_info:
					break
			except:
				continue
			else:	
				self.node_server_str = self.node_server_str + '/' + server_info.decode('utf-8')
				print(self.node_server_str)
				self.send_node_server_info()
		n_socket.close()

	def send_node_server_info(self):
		for network_node in self.network_nodes:
			n_socket, (ip, port) = network_node
			n_socket.sendall(self.node_server_str.encode('utf-8'))

	def refresh_network_nodes(self):
		network_nodes_str = '\nC'
		for network_node in self.network_nodes:
			n_socket, (ip, port) = network_node
			network_nodes_str = network_nodes_str + '/' + ip + ':' + str(port)
		for network_node in self.network_nodes:
			n_socket, (ip, port) = network_node
			n_socket.sendall(network_nodes_str.encode('utf-8'))
		print(network_nodes_str)
					


if __name__ == "__main__":
	p2p_server()
