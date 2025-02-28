import hashlib
import time
import random

class Block:
    def __init__(self, index, previous_hash, transactions, validator):
        self.index = index
        self.previous_hash = previous_hash
        self.transactions = transactions
        self.validator = validator
        self.timestamp = time.time()
        self.hash = self.compute_hash()

    def compute_hash(self):
        block_content = f"{self.index}{self.previous_hash}{self.transactions}{self.validator}{self.timestamp}"
        return hashlib.sha256(block_content.encode()).hexdigest()


class Blockchain:
    def __init__(self):
        self.chain = []
        self.stake_dict = {}  # Renamed to avoid conflict
        self.delegations = {}
        self.pending_transactions = []
        self.rewards = {}
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis_block = Block(0, "0", [], "Genesis")
        self.chain.append(genesis_block)

    def add_transaction(self, transaction):
        self.pending_transactions.append(transaction)

    def add_stake(self, node, amount):  # Renamed method
        self.stake_dict[node] = self.stake_dict.get(node, 0) + amount

    def delegate(self, delegator, validator, amount):
        if delegator not in self.delegations:
            self.delegations[delegator] = {}
        self.delegations[delegator][validator] = self.delegations[delegator].get(validator, 0) + amount
        self.add_stake(validator, amount)

    def select_validator(self):
        total_stake = sum(self.stake_dict.values())
        if total_stake == 0:
            return None
        pick = random.uniform(0, total_stake)
        current = 0
        for node, stake in self.stake_dict.items():
            current += stake
            if current >= pick:
                return node

    def validate_transactions(self, transactions):
        # Placeholder validation logic
        return True

    def add_block(self):
        validator = self.select_validator()
        if not validator:
            return "No validator available"
        if not self.validate_transactions(self.pending_transactions):
            return "Invalid transactions"

        new_block = Block(len(self.chain), self.chain[-1].hash, self.pending_transactions, validator)
        self.chain.append(new_block)
        self.rewards[validator] = self.rewards.get(validator, 0) + 10
        self.pending_transactions = []
        return new_block.hash
blockchain = Blockchain()
blockchain.add_stake("Validator1", 100)  # Use the new method name
blockchain.add_stake("Validator2", 50)
blockchain.delegate("User1", "Validator1", 20)
blockchain.add_transaction("Alice pays Bob 10 coins")

print("Validator selected:", blockchain.select_validator())
print("New block added:", blockchain.add_block())
print("Blockchain state:", [block.hash for block in blockchain.chain])
print("Validators' Rewards:", blockchain.rewards)