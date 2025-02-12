import hashlib
import hmac
import time
import tkinter as tk
from tkinter import messagebox, ttk
import ttkbootstrap as tb
from ttkbootstrap.constants import *

# --- Определение классов для транзакций и блоков ---
class Transaction:
    def __init__(self, sender, receiver, amount, signature=None):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.timestamp = int(time.time())
        self.tx_hash = self.calculate_tx_hash()
        self.signature = signature

    def calculate_tx_hash(self):
        data = f"{self.sender}{self.receiver}{self.amount}{self.timestamp}"
        return hashlib.sha256(data.encode("utf-8")).hexdigest()

class Block:
    def __init__(self, transactions, previous_hash="0"):
        self.timestamp = time.ctime()
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.merkle_root = self.calculate_merkle_root()
        self.hash = self.calculate_hash()

    def calculate_merkle_root(self):
        tx_hashes = [tx.tx_hash for tx in self.transactions]
        return self.build_merkle_tree(tx_hashes)

    def build_merkle_tree(self, tx_hashes):
        while len(tx_hashes) > 1:
            if len(tx_hashes) % 2 != 0:
                tx_hashes.append(tx_hashes[-1])
            tx_hashes = [
                hashlib.sha256((tx_hashes[i] + tx_hashes[i + 1]).encode()).hexdigest()
                for i in range(0, len(tx_hashes), 2)
            ]
        return tx_hashes[0] if tx_hashes else "0"

    def calculate_hash(self):
        block_string = f"{self.timestamp}{self.merkle_root}{self.previous_hash}"
        return hashlib.sha256(block_string.encode("utf-8")).hexdigest()

# --- Блокчейн ---
class Blockchain:
    def __init__(self):
        self.chain = []
        self.utxo = {}
        self.private_keys = {}
        self.create_genesis_block()

    def create_genesis_block(self):
        self.utxo["System"] = 10000
        self.utxo["Мария"] = 1000
        self.utxo["Иван"] = 1000
        genesis_transactions = [
            Transaction("System", "Мария", 1000),
            Transaction("System", "Иван", 1000),
        ]
        genesis_block = Block(genesis_transactions)
        self.chain.append(genesis_block)
        self.update_utxo(genesis_transactions)

    def add_block(self, transactions):
        previous_block = self.chain[-1]
        new_block = Block(transactions, previous_block.hash)
        self.chain.append(new_block)
        self.update_utxo(transactions)

    def update_utxo(self, transactions):
        for tx in transactions:
            self.utxo[tx.receiver] = self.utxo.get(tx.receiver, 0) + tx.amount
            if tx.sender != "System":
                self.utxo[tx.sender] = self.utxo.get(tx.sender, 0) - tx.amount
                if self.utxo[tx.sender] < 0:
                    raise ValueError(f"Negative balance detected for {tx.sender}!")

blockchain = Blockchain()

# --- Генерация и проверка ключей ---
def generate_key():
    return hashlib.sha256(str(time.time()).encode()).hexdigest()

def sign_data(secret_key, data):
    return hmac.new(secret_key.encode(), data.encode(), hashlib.sha256).hexdigest()

# --- Функции GUI ---
def add_new_block_gui():
    sender = sender_entry.get()
    receiver = receiver_entry.get()
    amount = amount_entry.get()

    if not sender or not receiver or not amount.isdigit():
        messagebox.showwarning("Ошибка", "Заполните все поля корректно!")
        return

    amount = int(amount)
    if blockchain.utxo.get(sender, 0) < amount:
        messagebox.showwarning("Ошибка", "Недостаточно средств!")
        return

    secret_key = blockchain.private_keys.get(sender)
    if not secret_key:
        messagebox.showwarning("Ошибка", f"Нет ключа для {sender}!")
        return

    transaction_data = f"{sender}{receiver}{amount}"
    signature = sign_data(secret_key, transaction_data)
    transaction = Transaction(sender, receiver, amount, signature)
    blockchain.add_block([transaction])
    update_gui()

def generate_keys_gui():
    user = user_entry.get()
    if not user:
        messagebox.showwarning("Ошибка", "Введите имя пользователя!")
        return
    secret_key = generate_key()
    blockchain.private_keys[user] = secret_key
    messagebox.showinfo("Успех", f"Ключ для {user} создан!")

def update_gui():
    for widget in block_list_frame.winfo_children():
        widget.destroy()
    balances = "\n".join([f"{user}: {balance} монет" for user, balance in blockchain.utxo.items()])
    tk.Label(block_list_frame, text=f"Балансы:\n{balances}", bg="#333", fg="#fff", font=("Arial", 12)).pack(pady=5)
    for block in blockchain.chain:
        tk.Label(block_list_frame, text=f"{block}", bg="#333", fg="#fff", font=("Arial", 10)).pack(pady=5)

# --- Создание окна ---
root = tb.Window(themename="darkly")
root.title("Blockchain Explorer")
root.geometry("800x600")

# --- Интерфейс ---
input_frame = ttk.Frame(root)
input_frame.pack(pady=10)

ttks = ["Отправитель:", "Получатель:", "Сумма:", "Пользователь:"]
entries = []
for i, text in enumerate(ttks):
    ttk.Label(input_frame, text=text).grid(row=i, column=0, padx=5, pady=5)
    entry = ttk.Entry(input_frame, width=30)
    entry.grid(row=i, column=1, padx=5, pady=5)
    entries.append(entry)

sender_entry, receiver_entry, amount_entry, user_entry = entries

button_frame = ttk.Frame(root)
button_frame.pack(pady=10)

ttk.Button(button_frame, text="Добавить блок", command=add_new_block_gui, bootstyle=PRIMARY).grid(row=0, column=0, padx=5)
ttk.Button(button_frame, text="Сгенерировать ключ", command=generate_keys_gui, bootstyle=SUCCESS).grid(row=0, column=1, padx=5)

block_list_frame = ttk.Frame(root)
block_list_frame.pack(pady=20, fill=tk.BOTH, expand=True)

update_gui()
root.mainloop()