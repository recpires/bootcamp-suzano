import sqlite3
import tkinter as tk
from tkinter import messagebox

# Database setup
conn = sqlite3.connect('Desafio1/bank.db')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS transactions
                  (id INTEGER PRIMARY KEY, type TEXT, amount REAL)''')
conn.commit()

# Tkinter setup
root = tk.Tk()
root.title("Banking System")

saldo = 0
limite = 500
numero_saques = 0
LIMITE_SAQUES = 3

def depositar():
    global saldo
    valor = float(entry_valor.get())
    if valor > 0:
        saldo += valor
        cursor.execute("INSERT INTO transactions (type, amount) VALUES (?, ?)", ('Depósito', valor))
        conn.commit()
        messagebox.showinfo("Sucesso", f"Depósito de R$ {valor:.2f} realizado com sucesso!")
    else:
        messagebox.showerror("Erro", "Operação falhou! O valor informado é inválido.")

def sacar():
    global saldo, numero_saques
    valor = float(entry_valor.get())
    excedeu_saldo = valor > saldo
    excedeu_limite = valor > limite
    excedeu_saques = numero_saques >= LIMITE_SAQUES

    if excedeu_saldo:
        messagebox.showerror("Erro", "Operação falhou! Você não tem saldo suficiente.")
    elif excedeu_limite:
        messagebox.showerror("Erro", "Operação falhou! O valor do saque excede o limite.")
    elif excedeu_saques:
        messagebox.showerror("Erro", "Operação falhou! Número máximo de saques excedido.")
    elif valor > 0:
        saldo -= valor
        numero_saques += 1
        cursor.execute("INSERT INTO transactions (type, amount) VALUES (?, ?)", ('Saque', valor))
        conn.commit()
        messagebox.showinfo("Sucesso", f"Saque de R$ {valor:.2f} realizado com sucesso!")
    else:
        messagebox.showerror("Erro", "Operação falhou! O valor informado é inválido.")

def exibir_extrato():
    cursor.execute("SELECT * FROM transactions")
    rows = cursor.fetchall()
    extrato = "\n".join([f"{row[1]}: R$ {row[2]:.2f}" for row in rows])
    extrato = "Não foram realizadas movimentações." if not extrato else extrato
    messagebox.showinfo("Extrato", f"================ EXTRATO ================\n{extrato}\n\nSaldo: R$ {saldo:.2f}\n==========================================")

def sair():
    conn.close()
    root.destroy()

# Tkinter widgets
label_valor = tk.Label(root, text="Valor:")
label_valor.pack()

entry_valor = tk.Entry(root)
entry_valor.pack()

button_depositar = tk.Button(root, text="Depositar", command=depositar)
button_depositar.pack()

button_sacar = tk.Button(root, text="Sacar", command=sacar)
button_sacar.pack()

button_extrato = tk.Button(root, text="Extrato", command=exibir_extrato)
button_extrato.pack()

button_sair = tk.Button(root, text="Sair", command=sair)
button_sair.pack()

root.mainloop()