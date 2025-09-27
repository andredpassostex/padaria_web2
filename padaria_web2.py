# padaria_erp_completo.py
import streamlit as st
import pandas as pd
from datetime import datetime

# ================= Classes =================
class Produto:
    def __init__(self, codigo, nome, qtd, preco, estoque_min=5):
        self.codigo = codigo
        self.nome = nome.title()
        self.qtd = qtd
        self.preco = preco
        self.estoque_min = estoque_min

class Funcionario:
    def __init__(self, nome):
        self.nome = nome.title().strip()

class Cliente:
    def __init__(self, nome):
        self.nome = nome.title().strip()
        self.historico = []

class Fornecedor:
    def __init__(self, nome, contato="", produto="", preco=0.0, prazo=0):
        self.nome = nome.title().strip()
        self.contato = contato
        self.produto = produto
        self.preco = preco
        self.prazo = prazo

class Usuario:
    def __init__(self, username, senha, perfil):
        self.username = username
        self.senha = senha
        self.perfil = perfil  # "Gerente" ou "Caixa"

# ================= Inicialização =================
for key, default in [
    "usuarios", "usuario_logado",
    "produtos", "funcionarios", "clientes", "fornecedores", "vendas", "codigo_produto"
]:
    if key not in st.session_state:
        st.session_state[key] = [] if key!="usuario_logado" else None
if "codigo_produto" not in st.session_state:
    st.session_state["codigo_produto"] = 1

# ================= Funções Usuário =================
def cadastrar_usuario(username, senha, perfil):
    if not username or not senha or not perfil:
        st.error("Preencha todos os campos!")
        return
    if username in [u.username for u in st.session_state["usuarios"]]:
        st.warning("Usuário já existe!")
        return
    st.session_state["usuarios"].append(Usuario(username, senha, perfil))
    st.success(f"Usuário '{username}' cadastrado como {perfil}.")

def login(username, senha):
    for u in st.session_state["usuarios"]:
        if u.username == username and u.senha == senha:
            st.session_state["usuario_logado"] = u
            st.success(f"Bem-vindo(a) {u.username} ({u.perfil})")
            return True
    st.error("Usuário ou senha incorretos!")
    return False

def logout():
    st.session_state["usuario_logado"] = None
    st.experimental_rerun()

# ================= Funções ERP =================
def cadastrar_produto(nome, qtd, preco):
    qtd = int(qtd)
    preco = float(preco)
    for p in st.session_state["produtos"]:
        if p.nome.lower() == nome.lower():
            p.qtd += qtd
            p.preco = preco
            st.success(f"Produto '{nome}' atualizado (+{qtd}) preço R${preco:.2f}")
            return
    codigo = str(st.session_state["codigo_produto"]).zfill(3)
    st.session_state["produtos"].append(Produto(codigo, nome, qtd, preco))
    st.session_state["codigo_produto"] += 1
    st.success(f"Produto '{nome}' cadastrado com código {codigo}.")

def cadastrar_funcionario(nome):
    nome = nome.title()
    if nome in [f.nome for f in st.session_state["funcionarios"]]:
        st.warning("Funcionário já cadastrado!")
        return
    st.session_state["funcionarios"].append(Funcionario(nome))
    st.success(f"Funcionário '{nome}' cadastrado.")

def remover_funcionario(nome):
    st.session_state["funcionarios"] = [f for f in st.session_state["funcionarios"] if f.nome != nome]
    st.success(f"Funcionário '{nome}' removido.")

def cadastrar_cliente(nome):
    nome = nome.title()
    for c in st.session_state["clientes"]:
        if c.nome.lower() == nome.lower():
            return c
    novo = Cliente(nome)
    st.session_state["clientes"].append(novo)
    st.success(f"Cliente '{nome}' cadastrado.")
    return novo

def registrar_venda(produto, funcionario, cliente, quantidade, tipo="imediata"):
    quantidade = int(quantidade)
    if tipo=="imediata" and quantidade > produto.qtd:
        st.error("Estoque insuficiente!")
        return
    if tipo=="imediata":
        produto.qtd -= quantidade
    total = quantidade*produto.preco
    data_hora = datetime.now()
    cliente_nome = cliente.nome if cliente else ""
    st.session_state["vendas"].append([produto.codigo, produto.nome, quantidade, produto.preco, total, tipo, data_hora, funcionario.nome, cliente_nome])
    if cliente:
        cliente.historico.append([produto.nome, quantidade, total, data_hora, funcionario.nome, tipo])
    st.success(f"Venda registrada: {quantidade}x {produto.nome} ({tipo})")

# ================= Telas =================
def tela_cadastro_usuario():
    st.title("📋 Cadastro de Usuário")
    username = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")
    perfil = st.selectbox("Perfil", ["Gerente", "Caixa"])
    if st.button("Cadastrar Usuário"):
        cadastrar_usuario(username, senha, perfil)

def tela_login():
    st.title("🔐 Login")
    username = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        if login(username, senha):
            st.experimental_rerun()

def tela_dashboard():
    st.title("📊 Dashboard")
    st.write(f"💰 Caixa total: R$ {sum(v[4] for v in st.session_state['vendas'] if v[5]=='imediata'):.2f}")
    st.write(f"🛒 Vendas hoje: {len([v for v in st.session_state['vendas'] if v[5]=='imediata' and v[6].date()==datetime.now().date()])}")
    st.write(f"📦 Produtos baixos: {[p.nome+'('+str(p.qtd)+')' for p in st.session_state['produtos'] if p.qtd<=p.estoque_min]}")

def main_erp():
    u = st.session_state["usuario_logado"]
    st.sidebar.write(f"👤 {u.username} ({u.perfil})")
    if st.sidebar.button("Logoff"):
        logout()
    
    if u.perfil=="Gerente":
        menu = ["Dashboard","Cadastrar Produto","Cadastrar Funcionário","Vendas","Cadastrar Usuário"]
    else:
        menu = ["Dashboard","Vendas"]

    escolha = st.sidebar.radio("Menu", menu)

    if escolha=="Dashboard":
        tela_dashboard()
    elif escolha=="Cadastrar Usuário":
        tela_cadastro_usuario()
    elif escolha=="Cadastrar Produto":
        st.subheader("Cadastrar Produto")
        nome = st.text_input("Nome do Produto", key="prod_nome")
        qtd = st.number_input("Quantidade", min_value=1, value=1, key="prod_qtd")
        preco = st.number_input("Preço", min_value=0.01, value=1.0, key="prod_preco")
        if st.button("Cadastrar Produto", key="btn_prod"):
            cadastrar_produto(nome, qtd, preco)
    elif escolha=="Cadastrar Funcionário":
        st.subheader("Cadastrar Funcionário")
        nome = st.text_input("Nome do Funcionário", key="func_nome")
        if st.button("Cadastrar Funcionário", key="btn_func"):
            cadastrar_funcionario(nome)
    elif escolha=="Vendas":
        st.subheader("Registrar Venda")
        if not st.session_state["produtos"] or not st.session_state["funcionarios"]:
            st.info("Cadastre produtos e funcionários antes de vender.")
        else:
            produtos_display = [f"{p.codigo} - {p.nome}" for p in st.session_state["produtos"]]
            prod_sel = st.selectbox("Produto", produtos_display, key="venda_prod")
            prod_codigo = prod_sel.split(" - ")[0]
            produto = next(p for p in st.session_state["produtos"] if p.codigo==prod_codigo)
            func_sel = st.selectbox("Funcionário", [f.nome for f in st.session_state["funcionarios"]], key="venda_func")
            funcionario = next(f for f in st.session_state["funcionarios"] if f.nome==func_sel)
            cliente_nome = st.text_input("Nome do Cliente (opcional)")
            cliente = cadastrar_cliente(cliente_nome) if cliente_nome else None
            qtd = st.number_input("Quantidade", min_value=1, value=1)
            tipo = st.radio("Tipo de Venda", ["imediata","reserva"])
            if st.button("Registrar Venda"):
                registrar_venda(produto, funcionario, cliente, qtd, tipo)

# ================= Main =================
def main():
    if not st.session_state["usuarios"]:
        tela_cadastro_usuario()
        return
    if not st.session_state["usuario_logado"]:
        tela_login()
        return
    main_erp()

if __name__=="__main__":
    main()
