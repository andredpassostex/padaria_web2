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

# ================= Inicialização do session_state =================
for key, default in [
    ("produtos", []), ("funcionarios", []), ("clientes", []),
    ("fornecedores", []), ("vendas", []), ("codigo_produto", 1)
]:
    if key not in st.session_state:
        st.session_state[key] = default

# Login
if "usuario_logado" not in st.session_state:
    st.session_state["usuario_logado"] = None
if "perfil_logado" not in st.session_state:
    st.session_state["perfil_logado"] = None

# Telas e visibilidades
if "tela_selecionada" not in st.session_state:
    st.session_state["tela_selecionada"] = "Dashboard"
if "submenu_selecionado" not in st.session_state:
    st.session_state["submenu_selecionado"] = None
if "mostrar_caixa" not in st.session_state:
    st.session_state["mostrar_caixa"] = False
if "mostrar_contas" not in st.session_state:
    st.session_state["mostrar_contas"] = False

# ================= Funções Login =================
def tela_login():
    st.title("🔑 Login do Sistema")
    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        usuarios = {
            "gerente": {"senha": "123", "perfil": "Gerente"},
            "caixa": {"senha": "123", "perfil": "Caixa"}
        }
        if usuario in usuarios and senha == usuarios[usuario]["senha"]:
            st.session_state["usuario_logado"] = usuario
            st.session_state["perfil_logado"] = usuarios[usuario]["perfil"]
            st.success(f"Bem-vindo(a) {usuarios[usuario]['perfil']}!")
            st.experimental_rerun()
        else:
            st.error("Usuário ou senha incorretos")

def logoff():
    st.session_state["usuario_logado"] = None
    st.session_state["perfil_logado"] = None
    st.success("Desconectado com sucesso!")
    st.experimental_rerun()

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
                    margin-bottom: 12px;'>
            <h3 style='text-align:center; color:#4B2E2E; margin:6px 0;'>{icone} {texto}</h3>
        </div>
    """, unsafe_allow_html=True)

# ================= Funções de Negócio =================
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
            st.success(f"Produto '{nome}' atualizado: +{qtd} unidades, preço atualizado para R$ {preco:.2f}.")
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
    novo = Fornecedor(nome, contato, produto, float(preco), int(prazo))
    st.session_state["fornecedores"].append(novo)
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
    st.session_state["vendas"].append([
        produto.codigo, produto.nome, quantidade, produto.preco, total, tipo, data_hora, funcionario.nome, cliente_nome
    ])
    if cliente:
        cliente.historico.append([produto.nome, quantidade, total, data_hora, funcionario.nome, tipo])
    st.success(f"Venda registrada: {quantidade} x {produto.nome} — {tipo} — atendido por {funcionario.nome}")
    if produto.qtd <= produto.estoque_min:
        st.warning(f"⚠ Estoque baixo: {produto.nome} — {produto.qtd} unidades restantes.")

# ================= Funções de Tela =================
# Aqui você mantém dashboard() e tela_funcional() como no seu código original
# ================= Menu e Permissões =================

def menu_sidebar():
    st.sidebar.header("📌 Menu")
    perfil = st.session_state["perfil_logado"]

    # Todos podem acessar Dashboard
    if st.sidebar.button("Dashboard"):
        st.session_state["tela_selecionada"] = "Dashboard"
        st.session_state["submenu_selecionado"] = None

    # Gerente tem acesso completo
    if perfil == "Gerente":
        expansivos = {
            "Estoque": ["Cadastrar Produto", "Produtos"],
            "Funcionários": ["Cadastrar Funcionário", "Funcionários", "Remover Funcionário"],
            "Clientes": ["Histórico", "Conta"],
            "Fornecedores": ["Cadastrar Fornecedor", "Fornecedores"],
            "Relatórios": ["Diário", "Semanal", "Mensal"],
            "Vendas": []
        }
    else:  # Caixa
        expansivos = {
            "Vendas": [],
            "Estoque": ["Produtos"],
            "Clientes": ["Conta"]
        }

    for item, submenus in expansivos.items():
        exp = st.sidebar.expander(item, expanded=False)
        with exp:
            for sub in submenus:
                if st.button(sub, key=f"{item}_{sub}"):
                    st.session_state["tela_selecionada"] = item
                    st.session_state["submenu_selecionado"] = sub

# ================= Render Principal =================
if not st.session_state["usuario_logado"]:
    tela_login()
else:
    st.sidebar.markdown(f"**Usuário:** {st.session_state['usuario_logado']} | Perfil: {st.session_state['perfil_logado']}")
    if st.sidebar.button("🔓 Logoff"):
        logoff()
    else:
        menu_sidebar()
        if st.session_state["tela_selecionada"] == "Dashboard":
            dashboard()
        else:
            tela_funcional()
