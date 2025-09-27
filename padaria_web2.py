# padaria_erp_login_erp.py
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
        self.historico = []  # cada entrada: [produto, qtd, total, data_hora, funcionario, tipo]

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

# ================= Utilitários =================
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
                    margin-bottom: 12px;'>{'<h3 style="text-align:center; color:#4B2E2E; margin:6px 0;">'+icone+' '+texto+'</h3>'}
        </div>
    """, unsafe_allow_html=True)

# ================= Usuário =================
def cadastrar_usuario(username, senha, perfil):
    if not username or not senha or not perfil:
        st.error("Preencha todos os campos")
        return
    if any(u.username == username for u in st.session_state["usuarios"]):
        st.warning("Usuário já existe")
        return
    st.session_state["usuarios"].append(Usuario(username, senha, perfil))
    st.success(f"Usuário '{username}' cadastrado com perfil '{perfil}'")

def autenticar_usuario(username, senha):
    for u in st.session_state["usuarios"]:
        if u.username == username and u.senha == senha:
            st.session_state["usuario_logado"] = u
            return True
    return False

def logoff():
    st.session_state["usuario_logado"] = None
    st.experimental_rerun()

# ================= Funções de negócio =================
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
            st.success(f"Produto '{nome}' atualizado: +{qtd} unidades, preço R$ {preco:.2f}")
            return
    codigo = str(st.session_state["codigo_produto"]).zfill(3)
    st.session_state["produtos"].append(Produto(codigo, nome, qtd, preco))
    st.session_state["codigo_produto"] += 1
    st.success(f"Produto '{nome}' cadastrado com código {codigo}")

def cadastrar_funcionario(nome):
    if not nome or str(nome).strip() == "":
        st.error("Nome inválido")
        return
    nome = nome.title().strip()
    if nome in [f.nome for f in st.session_state["funcionarios"]]:
        st.warning("Funcionário já cadastrado")
        return
    st.session_state["funcionarios"].append(Funcionario(nome))
    st.success(f"Funcionário '{nome}' cadastrado")

def remover_funcionario(nome):
    st.session_state["funcionarios"] = [f for f in st.session_state["funcionarios"] if f.nome != nome]
    st.success(f"Funcionário '{nome}' removido")

def cadastrar_cliente(nome):
    if not nome or str(nome).strip() == "":
        st.error("Nome do cliente inválido")
        return None
    nome = nome.title().strip()
    for c in st.session_state["clientes"]:
        if c.nome.lower() == nome.lower():
            return c
    novo = Cliente(nome)
    st.session_state["clientes"].append(novo)
    st.success(f"Cliente '{nome}' cadastrado")
    return novo

def cadastrar_fornecedor(nome, contato="", produto="", preco=0.0, prazo=0):
    if not nome or str(nome).strip() == "":
        st.error("Nome do fornecedor inválido")
        return
    novo = Fornecedor(nome, contato, produto, float(preco), int(prazo))
    st.session_state["fornecedores"].append(novo)
    st.success(f"Fornecedor '{nome}' cadastrado")

def registrar_venda(produto, funcionario, cliente, quantidade, tipo="imediata"):
    quantidade = int(quantidade)
    if quantidade <= 0:
        st.error("Quantidade inválida")
        return
    if tipo == "imediata" and quantidade > produto.qtd:
        st.error("Quantidade insuficiente")
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

# ================= Telas =================
def tela_login_cadastro():
    mostrar_logo(250)
    tabs = st.tabs(["Login", "Cadastrar Usuário"])
    with tabs[0]:
        st.header("🔑 Login")
        username = st.text_input("Usuário", key="login_usuario")
        senha = st.text_input("Senha", type="password", key="login_senha")
        if st.button("Entrar", key="btn_login"):
            if autenticar_usuario(username, senha):
                st.success(f"Bem-vindo, {username}!")
                st.experimental_rerun()
            else:
                st.error("Usuário ou senha incorretos")
    with tabs[1]:
        st.header("➕ Cadastrar Usuário")
        username = st.text_input("Usuário", key="cad_usuario")
        senha = st.text_input("Senha", type="password", key="cad_senha")
        perfil = st.selectbox("Perfil", ["Gerente", "Caixa"], key="cad_perfil")
        if st.button("Cadastrar", key="btn_cad_usuario"):
            cadastrar_usuario(username, senha, perfil)

# ================= Dashboard =================
def dashboard():
    mostrar_logo(600)
    box_title("📊 Dashboard")
    total_caixa = sum(v[4] for v in st.session_state["vendas"] if v[5] == "imediata")
    display_valor = f"R$ {total_caixa:.2f}" if st.session_state["mostrar_caixa"] else "R$ ****"
    vendas_hoje = [v for v in st.session_state["vendas"] if v[5] == "imediata" and v[6].date() == datetime.now().date()]
    produtos_baixos = [p for p in st.session_state["produtos"] if p.qtd <= p.estoque_min]
    clientes_conta = [c for c in st.session_state["clientes"] if sum(x[2] for x in c.historico if x[5] == "reserva") > 0]
    total_contas = sum(sum(x[2] for x in c.historico if x[5] == "reserva") for c in clientes_conta)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"<div style='background-color:#4CAF50;padding:15px;border-radius:10px;color:white;text-align:center;'><h4>💰 Caixa</h4><h2>{display_valor}</h2></div>", unsafe_allow_html=True)
        if st.button("👁️", key="btn_caixa"):
            st.session_state["mostrar_caixa"] = not st.session_state["mostrar_caixa"]
    with col2:
        st.markdown(f"<div style='background-color:#2196F3;padding:15px;border-radius:10px;color:white;text-align:center;'><h4>🛒 Vendas Hoje</h4><h2>{len(vendas_hoje)}</h2></div>", unsafe_allow_html=True)
    with col3:
        lista = "<br>".join([f"{p.nome} ({p.qtd})" for p in produtos_baixos]) if produtos_baixos else "✅ OK"
        st.markdown(f"<div style='background-color:#FF9800;padding:15px;border-radius:10px;color:white;text-align:center;'><h4>📦 Produtos Baixos</h4><p>{lista}</p></div>", unsafe_allow_html=True)
    display_conta = f"R$ {total_contas:.2f}" if st.session_state["mostrar_contas"] else "R$ ****"
    with col4:
        st.markdown(f"<div style='background-color:#F44336;padding:15px;border-radius:10px;color:white;text-align:center;'><h4>👥 Contas em Aberto</h4><h2>{display_conta}</h2></div>", unsafe_allow_html=True)
        if st.button("👁️", key="btn_conta"):
            st.session_state["mostrar_contas"] = not st.session_state["mostrar_contas"]

# ================= Sidebar / Funcional =================
menu_principal = ["Dashboard", "Vendas", "Caixa"]
menu_expansivo = {
    "Estoque": ["Cadastrar Produto", "Produtos"],
    "Funcionários": ["Cadastrar Funcionário", "Funcionários", "Remover Funcionário"],
    "Clientes": ["Histórico", "Conta"],
    "Fornecedores": ["Cadastrar Fornecedor", "Fornecedores"],
    "Relatórios": ["Diário", "Semanal", "Mensal"]
}

def tela_funcional_completa():
    mostrar_logo(
