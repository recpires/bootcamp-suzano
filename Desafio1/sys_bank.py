from datetime import datetime
import sqlite3
import tkinter as tk
from tkinter import messagebox, simpledialog

# Conectar ao banco de dados SQLite
conn = sqlite3.connect('desafio1/extrato.db')
c = conn.cursor()

# Criar tabelas se não existirem
c.execute('''CREATE TABLE IF NOT EXISTS usuarios (
                cpf TEXT PRIMARY KEY,
                nome TEXT,
                data_nascimento TEXT,
                endereco TEXT
            )''')

c.execute('''CREATE TABLE IF NOT EXISTS contas (
                agencia TEXT,
                numero_conta INTEGER PRIMARY KEY,
                cpf TEXT,
                FOREIGN KEY (cpf) REFERENCES usuarios (cpf)
            )''')

c.execute('''CREATE TABLE IF NOT EXISTS transacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo TEXT,
                valor REAL,
                data TEXT,
                numero_conta INTEGER,
                FOREIGN KEY (numero_conta) REFERENCES contas (numero_conta)
            )''')

conn.commit()

def sacar(*, saldo, valor, limite, numero_saque, limite_saques, numero_conta):
    excedeu_saldo = valor > saldo
    excedeu_limite = valor > limite
    excedeu_saque = numero_saque >= limite_saques

    if excedeu_saldo:
        return f'\nSaldo insuficiente', numero_saque
    elif excedeu_saque:
        return 'Limite de saque diário atingido', numero_saque
    elif excedeu_limite:
        return 'Não é possível sacar esse valor, tente um valor abaixo de R$500.00', numero_saque
    elif valor > 0:
        saldo -= valor
        numero_saque += 1
        # Salvar transação no banco de dados
        c.execute("INSERT INTO transacoes (tipo, valor, data, numero_conta) VALUES (?, ?, ?, ?)",
                  ('Saque', valor, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), numero_conta))
        conn.commit()
        return f'Saque de R${valor:.2f} realizado com sucesso', numero_saque
    else:
        return 'Operação falhou! Valor inválido', numero_saque


def depositar(saldo, valor, numero_conta):
    saldo += valor
    # Salvar transação no banco de dados
    c.execute("INSERT INTO transacoes (tipo, valor, data, numero_conta) VALUES (?, ?, ?, ?)",
              ('Depósito', valor, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), numero_conta))
    conn.commit()
    return saldo


def exibir_extrato(saldo, numero_conta):
    extrato_str = 'Extrato\n'
    c.execute("SELECT tipo, valor, data FROM transacoes WHERE numero_conta = ?", (numero_conta,))
    transacoes = c.fetchall()
    for tipo, valor, data in transacoes:
        extrato_str += f'{data} - {tipo}: R${valor:.2f}\n'
    extrato_str += f'Saldo: R${saldo:.2f}'
    return extrato_str


def criar_user(usuarios):
    cpf = simpledialog.askstring("CPF", "Insira seu CPF (somente números):")
    usuario = filtrar_usuario(cpf, usuarios)

    if usuario:
        messagebox.showinfo("Erro", "Já existe usuário com esse CPF!")
        return

    nome = simpledialog.askstring("Nome", "Informe seu nome completo:")
    data_nascimento = simpledialog.askstring("Data de Nascimento", "Informe a data de nascimento (dd-mm-aaaa):")
    endereco = simpledialog.askstring("Endereço", "Insira seu endereço (logradouro, número, bairro, cidade/estado em sigla):")
    usuarios.append({'nome': nome, 'data_nascimento': data_nascimento, 'cpf': cpf, 'endereco': endereco})
    messagebox.showinfo("Sucesso", "Usuário cadastrado com sucesso")

    # Salvar no banco de dados
    c.execute("INSERT INTO usuarios (cpf, nome, data_nascimento, endereco) VALUES (?, ?, ?, ?)",
              (cpf, nome, data_nascimento, endereco))
    conn.commit()


def filtrar_usuario(cpf, usuarios):
    c.execute("SELECT * FROM usuarios WHERE cpf = ?", (cpf,))
    usuario = c.fetchone()
    return usuario


def criar_conta_corrente(agencia, numero_conta, usuarios):
    cpf = simpledialog.askstring("CPF", "Insira seu CPF (somente números):")
    usuario = filtrar_usuario(cpf, usuarios)

    if usuario:
        messagebox.showinfo("Sucesso", "Conta criada com sucesso")
        c.execute("INSERT INTO contas (agencia, numero_conta, cpf) VALUES (?, ?, ?)",
                  (agencia, numero_conta, cpf))
        conn.commit()
        return {'agencia': agencia, 'numero_conta': numero_conta, 'usuario': usuario}
    messagebox.showinfo("Erro", "Usuário não encontrado")


def listar_contas(contas):
    c.execute("SELECT * FROM contas")
    contas = c.fetchall()
    contas_str = ""
    for conta in contas:
        contas_str += f"""\ 
            Agência: {conta[0]}
            C/C: {conta[1]}
            Titular: {conta[2]}
        """
    messagebox.showinfo("Contas", contas_str)


def main():
    saldo = 0
    limite = 500
    extrato = []
    numero_saques = 0
    limite_saque = 3
    usuarios = []
    contas = []
    numero_conta = 1
    agencia = '0001'

    def exibir_saldo():
        messagebox.showinfo("Saldo", f'Seu saldo atual é: R${saldo:.2f}')

    def realizar_deposito():
        nonlocal saldo
        valor = simpledialog.askfloat("Depósito", "Valor que você gostaria de depositar: R$")
        if valor > 0:
            saldo = depositar(saldo, valor, numero_conta)
            extrato.append(('Depósito', valor))
            messagebox.showinfo("Sucesso", f'Depósito de R${valor:.2f} realizado com sucesso')
        else:
            messagebox.showinfo("Erro", "Valor inválido para depósito.")

    def realizar_saque():
        nonlocal saldo, numero_saques
        valor = simpledialog.askfloat("Saque", "Valor que você gostaria de sacar: R$")
        mensagem, numero_saques = sacar(
            saldo=saldo,
            valor=valor,
            limite=limite,
            numero_saque=numero_saques,
            limite_saques=limite_saque,
            numero_conta=numero_conta
        )
        messagebox.showinfo("Saque", mensagem)
        if 'realizado' in mensagem:  # Só adiciona o saque ao extrato se foi realizado com sucesso
            extrato.append(('Saque', valor))

    def exibir_extrato_func():
        extrato_str = exibir_extrato(saldo, numero_conta)
        messagebox.showinfo("Extrato", extrato_str)

    def criar_usuario():
        criar_user(usuarios)

    def criar_conta():
        nonlocal numero_conta
        numero_conta = len(contas) + 1
        conta = criar_conta_corrente(agencia, numero_conta, usuarios)
        if conta:
            contas.append(conta)

    def listar_todas_contas():
        listar_contas(contas)

    root = tk.Tk()
    root.title("Sistema Bancário")

    tk.Button(root, text="Exibir Saldo", command=exibir_saldo).pack(pady=5)
    tk.Button(root, text="Depósito", command=realizar_deposito).pack(pady=5)
    tk.Button(root, text="Saque", command=realizar_saque).pack(pady=5)
    tk.Button(root, text="Exibir Extrato", command=exibir_extrato_func).pack(pady=5)
    tk.Button(root, text="Criar Novo Usuário", command=criar_usuario).pack(pady=5)
    tk.Button(root, text="Nova Conta", command=criar_conta).pack(pady=5)
    tk.Button(root, text="Listar Contas", command=listar_todas_contas).pack(pady=5)
    tk.Button(root, text="Sair", command=root.quit).pack(pady=5)

    root.mainloop()

if __name__ == "__main__":
    main()