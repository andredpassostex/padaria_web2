# padaria_erp_completo.py
import os
import streamlit as st
import pandas as pd
from datetime import datetime
from PIL import Image

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

# ================= Inicialização do session_state =================
for key, default in [
    ("produtos", []), ("funcionarios", []), ("clientes", []),
    ("fornecedores", []), ("vendas", []), ("codigo_produto", 1),
    ("usuarios", []), ("usuario_logado", None)
]:
    if key not in st.session_state:
        st.session_state[key] = default

# telas e visibilidades
if "tela_selecionada" not in st.session_state:
    st.session_state["tela_selecionada"] = "Dashboard"
if "submenu_selecionado" not in st.session_state:
    st.session_state["submenu_selecionado"] = None
if "mostrar_caixa" not in st.session_state:
    st.session_state["mostrar_caixa"] = False
if "mostrar_contas" not in st.session_state:
    st.session_state["mostrar_contas"] = False

# ================= Utilitários visuais =================
def mostrar_logo(size):
    logo_path = "logo.png"
    if os.path.exists(logo_path):
        try:
            img = Image.open(logo_path)
            st.image(img, width=size)
        except Exception:
            st.markdown(f"<h1 style='text-align:center; color:#4B2E2E;'>🥖 Lucio Pães</h1>", unsafe_allow_html=True)
    else:
        st.markdown(f"<h1 style='text-align:center; color:#4B2E2E;'>🥖 Lucio Pães</h1>", unsafe_allow_html=True)

def box_title(texto, icone="📌"):
    st.markdown(f"""
        <div style='padding: 10px; background-color: #f9f9f9;
                    border-radius: 10px; box-shadow: 2px 2px 8px rgba(0,0,0,0.12);
                    margin-bottom: 12px;'>{icone} {texto}</div>
    """, unsafe_allow_html=True)

# ================= Funções de Negócio =================
def cadastrar_usuario(username, senha, perfil):
    if not username or not senha or not perfil:
        st.error("Preencha todos os campos.")
        return
    if username in [u.username for u in st.session_state["usuarios"]]:
        st.warning("Usuário já existe.")
        return
    st.session_state["usuarios"].append(Usuario(username, senha, perfil))
    st.success(f"Usuário '{username}' criado como {perfil}.")

def login(username, senha):
    for u in st.session_state["usuarios"]:
        if u.username == username and u.senha == senha:
            st.session_state["usuario_logado"] = u
            st.success(f"Bem-vindo, {u.username} ({u.perfil})!")
            return True
    st.error("Usuário ou senha incorretos.")
    return False

def logout():
    st.session_state["usuario_logado"] = None
    st.experimental_rerun()

def cadastrar_produto(nome, qtd, preco):
    nome = nome.title().strip()
    qtd = int(qtd)
    preco = float(preco)
    for p in st.session_state["produtos"]:
        if p.nome == nome:
            p.qtd += qtd
            p.preco = preco
            st.success(f"Produto '{nome}' atualizado: +{qtd} unidades, preço R${preco:.2f}")
            return
    codigo = str(st.session_state["codigo_produto"]).zfill(3)
    st.session_state["produtos"].append(Produto(codigo, nome, qtd, preco))
    st.session_state["codigo_produto"] += 1
    st.success(f"Produto '{nome}' cadastrado com código {codigo}.")

def cadastrar_funcionario(nome):
    nome = nome.title().strip()
    if nome in [f.nome for f in st.session_state["funcionarios"]]:
        st.warning("Funcionário já cadastrado.")
        return
    st.session_state["funcionarios"].append(Funcionario(nome))
    st.success(f"Funcionário '{nome}' cadastrado.")

def remover_funcionario(nome):
    st.session_state["funcionarios"] = [f for f in st.session_state["funcionarios"] if f.nome != nome]
    st.success(f"Funcionário '{nome}' removido.")

def cadastrar_cliente(nome):
    nome = nome.title().strip()
    for c in st.session_state["clientes"]:
        if c.nome.lower() == nome.lower():
            return c
    novo = Cliente(nome)
    st.session_state["clientes"].append(novo)
    st.success(f"Cliente '{nome}' cadastrado.")
    return novo

def cadastrar_fornecedor(nome, contato="", produto="", preco=0.0, prazo=0):
    novo = Fornecedor(nome, contato, produto, float(preco), int(prazo))
    st.session_state["fornecedores"].append(novo)
    st.success(f"Fornecedor '{nome}' cadastrado.")

def registrar_venda(produto, funcionario, cliente, quantidade, tipo="imediata"):
    quantidade = int(quantidade)
    if tipo=="imediata" and quantidade > produto.qtd:
        st.error("Estoque insuficiente")
        return
    if tipo=="imediata":
        produto.qtd -= quantidade
    total = quantidade * produto.preco
    data_hora = datetime.now()
    cliente_nome = cliente.nome if cliente else ""
    st.session_state["vendas"].append([produto.codigo, produto.nome, quantidade, produto.preco, total, tipo, data_hora, funcionario.nome, cliente_nome])
    if cliente:
        cliente.historico.append([produto.nome, quantidade, total, data_hora, funcionario.nome, tipo])
    st.success(f"Venda registrada: {quantidade}x {produto.nome} ({tipo}) por {funcionario.nome}")
    if produto.qtd <= produto.estoque_min:
        st.warning(f"⚠ Estoque baixo: {produto.nome} - {produto.qtd} restantes")

# ================= TELA INICIAL =================
def tela_cadastro_usuario():
    st.title("Cadastro de Usuário")
    st.info("Crie o primeiro usuário para acessar o ERP")
    username = st.text_input("Usuário", key="cad_username")
    senha = st.text_input("Senha", type="password", key="cad_senha")
    perfil = st.selectbox("Perfil", ["Gerente", "Caixa"], key="cad_perfil")
    if st.button("Cadastrar Usuário"):
        cadastrar_usuario(username, senha, perfil)

def tela_login():
    st.title("Login")
    username = st.text_input("Usuário", key="login_username")
    senha = st.text_input("Senha", type="password", key="login_senha")
    if st.button("Entrar"):
        if login(username, senha):
            st.experimental_rerun()

# ================= DASHBOARD =================
def dashboard():
    st.title("Dashboard")
    total_caixa = sum(v[4] for v in st.session_state["vendas"] if v[5]=="imediata")
    st.write(f"💰 Caixa: R$ {total_caixa:.2f}")
    st.write(f"🛒 Vendas hoje: {len([v for v in st.session_state['vendas'] if v[5]=='imediata' and v[6].date()==datetime.now().date()])}")
    st.write(f"📦 Produtos baixos: {[p.nome+'('+str(p.qtd)+')' for p in st.session_state['produtos'] if p.qtd<=p.estoque_min]}")

# ================= MAIN =================
def main():
    if not st.session_state["usuarios"]:
        tela_cadastro_usuario()
        return

    if not st.session_state["usuario_logado"]:
        tela_login()
        return

    u = st.session_state["usuario_logado"]
    st.sidebar.write(f"👤 {u.username} ({u.perfil})")
    if st.sidebar.button("Logoff"):
        logout()

    # Menu lateral
    if u.perfil=="Gerente":
        menu = ["Dashboard", "Estoque", "Funcionários", "Clientes", "Fornecedores", "Vendas", "Relatórios", "Cadastrar Usuário"]
    else:
        menu = ["Dashboard", "Vendas"]

    escolha = st.sidebar.radio("Menu", menu)

    if escolha=="Dashboard":
        dashboard()
    elif escolha=="Cadastrar Usuário":
        tela_cadastro_usuario()
    elif escolha=="Estoque":
        st.subheader("Estoque")
        st.write([p.nome for p in st.session_state["produtos"]])
    elif escolha=="Vendas":
        st.subheader("Registrar Vendas")
        if not st.session_state["produtos"] or not st.session_state["funcionarios"]:
            st.info("Cadastre produtos e funcionários antes de vender.")
        else:
            produtos_display = [f"{p.codigo} - {p.nome}" for p in st.session_state["produtos"]]
            prod_sel = st.selectbox("Produto", produtos_display, key="venda_prod_sel")
            prod_codigo = prod_sel.split(" - ")[0]
            produto = next(p for p in st.session_state["produtos"] if p.codigo == prod_codigo)
            func_sel = st.selectbox("Funcionário", [f.nome for f in st.session_state["funcionarios"]], key="venda_func_sel")
            funcionario = next(f for f in st.session_state["funcionarios"] if f.nome == func_sel)
            cliente_nome = st.text_input("Nome do Cliente (opcional)", key="venda_cliente_nome")
            cliente = cadastrar_cliente(cliente_nome) if cliente_nome else None
            qtd = st.number_input("Quantidade", min_value=1, value=1, key="venda_qtd")
            tipo = st.radio("Tipo de Venda", ["imediata", "reserva"], key="venda_tipo")
            if st.button("Registrar Venda", key="btn_registrar_venda"):
                registrar_venda(produto, funcionario, cliente, qtd, tipo)

if __name__ == "__main__":
    main()
