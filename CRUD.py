import tkinter as tk
from tkinter import messagebox
import sqlite3

# Configuração do banco de dados
conn = sqlite3.connect('database.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users
             (id INTEGER PRIMARY KEY, name TEXT, age INTEGER)''')
conn.commit()

# Funções CRUD
def create_user():
    name = entry_name.get()
    age = entry_age.get()
    if name and age:
        c.execute("INSERT INTO users (name, age) VALUES (?, ?)", (name, age))
        conn.commit()
        messagebox.showinfo("Sucesso", "Usuário criado com sucesso!")
        entry_name.delete(0, tk.END)
        entry_age.delete(0, tk.END)
        read_users()
    else:
        messagebox.showwarning("Atenção", "Preencha todos os campos!")

def read_users():
    listbox_users.delete(0, tk.END)
    for row in c.execute("SELECT * FROM users"):
        listbox_users.insert(tk.END, row)

def update_user():
    try:
        selected_item = listbox_users.curselection()[0]
        user_id = listbox_users.get(selected_item)[0]
        new_name = entry_name.get()
        new_age = entry_age.get()
        if new_name and new_age:
            c.execute("UPDATE users SET name = ?, age = ? WHERE id = ?", (new_name, new_age, user_id))
            conn.commit()
            messagebox.showinfo("Sucesso", "Usuário atualizado com sucesso!")
            entry_name.delete(0, tk.END)
            entry_age.delete(0, tk.END)
            read_users()
        else:
            messagebox.showwarning("Atenção", "Preencha todos os campos!")
    except IndexError:
        messagebox.showwarning("Atenção", "Selecione um usuário para atualizar!")

def delete_user():
    try:
        selected_item = listbox_users.curselection()[0]
        user_id = listbox_users.get(selected_item)[0]
        c.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        messagebox.showinfo("Sucesso", "Usuário deletado com sucesso!")
        read_users()
    except IndexError:
        messagebox.showwarning("Atenção", "Selecione um usuário para deletar!")

# Interface gráfica
root = tk.Tk()
root.title("CRUD com Tkinter")

tk.Label(root, text="Nome:").grid(row=0, column=0)
entry_name = tk.Entry(root)
entry_name.grid(row=0, column=1)

tk.Label(root, text="Idade:").grid(row=1, column=0)
entry_age = tk.Entry(root)
entry_age.grid(row=1, column=1)

tk.Button(root, text="Criar", command=create_user).grid(row=2, column=0)
tk.Button(root, text="Atualizar", command=update_user).grid(row=2, column=1)
tk.Button(root, text="Deletar", command=delete_user).grid(row=2, column=2)

listbox_users = tk.Listbox(root)
listbox_users.grid(row=3, column=0, columnspan=3)
read_users()

root.mainloop()

# Fechar conexão com o banco de dados ao sair
conn.close()