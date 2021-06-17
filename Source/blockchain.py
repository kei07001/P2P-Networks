import time
import hashlib
import uuid

class Blockchain:

	def __init__(self):
		self.chain = []
		self.pending_transactions = []
		self.create_new_block(100, '0','0') #genesis block

	def create_new_block(self, nonce, previous_block_hash, hash_data) :
		if len(self.chain) == 0 :
			timestamp = 0
		else:
			timestamp = time.time()
		new_block = {
			"index" : len(self.chain) + 1,
			"timestamp" : timestamp,
			"transactions" : self.pending_transactions,
			"nonce" : nonce,
			"hash_data" : hash_data,
			"previous_block_hash" : previous_block_hash
		}
		self.pending_transactions = []
		self.chain.append(new_block);
		return new_block

	def get_last_block(self):
		return self.chain[len(self.chain) - 1]

	def create_new_transaction(self, amount, sender, recipient):
		new_transaction = {
			"amount" : amount,
			"sender" : sender,
			"recipient" : recipient,
			"transaction_id" : str(uuid.uuid4())
		}
		return new_transaction
	
	def add_transaction_to_pending_transactions(self, transaction_obj):
		self.pending_transactions.append(transaction_obj)
		return self.get_last_block()['index'] + 1

	def hash_block(self, previous_block_hash, current_block_data, nonce) :
		data_string = previous_block_hash + str(nonce) + str(current_block_data)
		hash_data = hashlib.sha256(data_string.encode()).hexdigest()
		return hash_data
