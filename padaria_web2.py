# padaria_erp_completo_login.py
import os
import streamlit as st
import pandas as pd
from datetime import datetime
from PIL import Image
import hashlib

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
        self.senha = hashlib.sha256(senha.encode()).hexdigest()
        self.perfil = perfil  # "Gerente" ou "Caixa"

# ================= Inicialização do session_state =================
if "usuarios" not in st.session_state:
    st.session_state["usuarios"] = []
if "usuario_logado" not in st.session_state:
    st.session_state["usuario_logado"] = None

if "produtos" not in st.session_state:
    st.session_state["produtos"] = []
if "funcionarios" not in st.session_state:
    st.session_state["funcionarios"] = []
if "clientes" not in st.session_state:
    st.session_state["clientes"] = []
if "fornecedores" not in st.session_state:
    st.session_state["fornecedores"] = []
if "vendas" not in st.session_state:
    st.session_state["vendas"] = []
if "codigo_produto" not in st.session_state:
    st.session_state["codigo_produto"] = 1

if "tela_selecionada" not in st.session_state:
    st.session_state["tela_selecionada"] = "Dashboard"
if "submenu_selecionado" not in st.session_state:
    st.session_state["submenu_selecionado"] = None
if "mostrar_caixa" not in st.session_state:
    st.session_state["mostrar_caixa"] = False
if "mostrar_contas" not in st.session_state:
    st.session_state["mostrar_contas"] = False

# ================= Utilitários =================
def mostrar_logo(size):
    logo_path = "logo.png"
    if os.path.exists(logo_path):
        try:
            img = Image.open(logo_path)
            st.image(img, width=size)
        except:
            st.markdown("<h1 style='text-align:center; color:#4B2E2E;'>🥖 Lucio Pães</h1>", unsafe_allow_html=True)
    else:
        st.markdown("<h1 style='text-align:center; color:#4B2E2E;'>🥖 Lucio Pães</h1>", unsafe_allow_html=True)

def box_title(texto, icone="📌"):
    st.markdown(f"""
        <div style='padding: 10px; background-color: #f9f9f9;
                    border-radius: 10px; box-shadow: 2px 2px 8px rgba(0,0,0,0.12);
                    margin-bottom: 12px;'>
            <h3 style='text-align:center; color:#4B2E2E; margin:6px 0;'>{icone} {texto}</h3>
        </div>
    """, unsafe_allow_html=True)

def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

# ================= Funções de login =================
def cadastrar_usuario(username, senha, perfil):
    username = username.strip()
    if any(u.username == username for u in st.session_state["usuarios"]):
        st.warning("Usuário já existe!")
        return
    st.session_state["usuarios"].append(Usuario(username, senha, perfil))
    st.success(f"Usuário '{username}' cadastrado com perfil '{perfil}'.")

def autenticar_usuario(username, senha):
    senha_hash = hash_senha(senha)
    for u in st.session_state["usuarios"]:
        if u.username == username and u.senha == senha_hash:
            st.session_state["usuario_logado"] = u
            return True
    return False

def logout():
    st.session_state["usuario_logado"] = None
    st.session_state["tela_selecionada"] = "Dashboard"

# ================= Funções de negócio (mantidas) =================
def cadastrar_produto(nome, qtd, preco):
    if not nome or str(nome).strip() == "":
        st.error("Nome do produto inválido.")
        return
    nome = nome.title().strip()
    qtd = int(qtd)
    preco = float(preco)
    for p in st.session_state["produtos"]:
        if p.nome == nome:
            p.qtd += qtd
            p.preco = preco
            st.success(f"Produto '{nome}' atualizado: +{qtd} unidades, preço atualizado R$ {preco:.2f}.")
            return
    codigo = str(st.session_state["codigo_produto"]).zfill(3)
    st.session_state["produtos"].append(Produto(codigo, nome, qtd, preco))
    st.session_state["codigo_produto"] += 1
    st.success(f"Produto '{nome}' cadastrado com código {codigo}.")

def cadastrar_funcionario(nome):
    if not nome or str(nome).strip() == "":
        st.error("Nome do funcionário inválido.")
        return
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
    if not nome or str(nome).strip() == "":
        st.error("Nome do cliente inválido.")
        return None
    nome = nome.title().strip()
    for c in st.session_state["clientes"]:
        if c.nome.lower() == nome.lower():
            return c
    novo = Cliente(nome)
    st.session_state["clientes"].append(novo)
    st.success(f"Cliente '{nome}' cadastrado.")
    return novo

def cadastrar_fornecedor(nome, contato="", produto="", preco=0.0, prazo=0):
    if not nome or str(nome).strip() == "":
        st.error("Nome do fornecedor inválido.")
        return
    st.session_state["fornecedores"].append(Fornecedor(nome, contato, produto, float(preco), int(prazo)))
    st.success(f"Fornecedor '{nome}' cadastrado.")

def registrar_venda(produto, funcionario, cliente, quantidade, tipo="imediata"):
    quantidade = int(quantidade)
    if quantidade <= 0:
        st.error("Quantidade inválida.")
        return
    if tipo == "imediata" and quantidade > produto.qtd:
        st.error("Quantidade insuficiente no estoque.")
        return
    if tipo == "imediata":
        produto.qtd -= quantidade
    total = quantidade * produto.preco
    data_hora = datetime.now()
    cliente_nome = cliente.nome if cliente else ""
    st.session_state["vendas"].append([produto.codigo, produto.nome, quantidade, produto.preco, total, tipo, data_hora, funcionario.nome, cliente_nome])
    if cliente:
        cliente.historico.append([produto.nome, quantidade, total, data_hora, funcionario.nome, tipo])
    st.success(f"Venda registrada: {quantidade} x {produto.nome} — {tipo} — atendido por {funcionario.nome}")
    if produto.qtd <= produto.estoque_min:
        st.warning(f"⚠ Estoque baixo: {produto.nome} — {produto.qtd} unidades restantes.")

# ================= Telas de login =================
def tela_login():
    st.title("🔑 Login")
    username = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        if autenticar_usuario(username, senha):
            st.success(f"Bem-vindo, {username}!")
            st.experimental_rerun()
        else:
            st.error("Usuário ou senha incorretos!")

def tela_cadastro_usuario():
    st.title("➕ Cadastrar Usuário")
    username = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")
    perfil = st.selectbox("Perfil", ["Gerente", "Caixa"])
    if st.button("Cadastrar"):
        if username and senha:
            cadastrar_usuario(username, senha, perfil)
        else:
            st.error("Preencha todos os campos!")

# ================= Menu principal =================
def menu_lateral():
    st.sidebar.header(f"👤 Usuário: {st.session_state['usuario_logado'].username} ({st.session_state['usuario_logado'].perfil})")
    st.sidebar.button("🔓 Logoff", on_click=logout)

    menu_principal = ["Dashboard", "Vendas", "Estoque", "Funcionários", "Clientes", "Fornecedores"]
    for item in menu_principal:
        if st.sidebar.button(item):
            st.session_state["tela_selecionada"] = item
            st.session_state["submenu_selecionado"] = None

# ================= Renderização principal =================
def render_principal():
    if st.session_state["usuario_logado"] is None:
        tab1, tab2 = st.tabs(["Login", "Cadastrar Usuário"])
        with tab1:
            tela_login()
        with tab2:
            tela_cadastro_usuario()
    else:
        menu_lateral()
        tela_funcional()

# ================= Run App =================
render_principal()
