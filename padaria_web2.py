# padaria_erp_completo_final.py
import os
import streamlit as st
import pandas as pd
from datetime import datetime
from PIL import Image

# ================= Classes =================
class Usuario:
    def __init__(self, nome, senha, perfil):
        self.nome = nome.title().strip()
        self.senha = senha
        self.perfil = perfil  # "Gerente" ou "Caixa"

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
        self.historico = []  # [produto, qtd, total, data_hora, funcionario, tipo]

class Fornecedor:
    def __init__(self, nome, contato="", produto="", preco=0.0, prazo=0):
        self.nome = nome.title().strip()
        self.contato = contato
        self.produto = produto
        self.preco = preco
        self.prazo = prazo

# ================= Inicialização =================
for key, default in [
    ("usuarios", []), ("produtos", []), ("funcionarios", []), ("clientes", []),
    ("fornecedores", []), ("vendas", []), ("codigo_produto", 1)
]:
    if key not in st.session_state:
        st.session_state[key] = default

if "usuario_logado" not in st.session_state:
    st.session_state["usuario_logado"] = None
if "perfil_logado" not in st.session_state:
    st.session_state["perfil_logado"] = None
if "tela_selecionada" not in st.session_state:
    st.session_state["tela_selecionada"] = "Dashboard"
if "submenu_selecionado" not in st.session_state:
    st.session_state["submenu_selecionado"] = None
if "mostrar_caixa" not in st.session_state:
    st.session_state["mostrar_caixa"] = False
if "mostrar_contas" not in st.session_state:
    st.session_state["mostrar_contas"] = False

# ================= Funções utilitárias =================
def mostrar_logo(size):
    logo_path = "logo.png"
    if os.path.exists(logo_path):
        try:
            img = Image.open(logo_path)
            st.image(img, width=size)
        except:
            st.markdown(f"<h1 style='text-align:center; color:#4B2E2E;'>🥖 Lucio Pães</h1>", unsafe_allow_html=True)
    else:
        st.markdown(f"<h1 style='text-align:center; color:#4B2E2E;'>🥖 Lucio Pães</h1>", unsafe_allow_html=True)

def box_title(texto, icone="📌"):
    st.markdown(f"""
        <div style='padding:10px; background-color:#f9f9f9; border-radius:10px;
                    box-shadow:2px 2px 8px rgba(0,0,0,0.12); margin-bottom:12px;'>
            <h3 style='text-align:center; color:#4B2E2E; margin:6px 0;'>{icone} {texto}</h3>
        </div>
    """, unsafe_allow_html=True)

# ================= Funções de negócio =================
def cadastrar_usuario(nome, senha, perfil):
    if not nome or not senha:
        st.error("Nome e senha são obrigatórios.")
        return
    for u in st.session_state["usuarios"]:
        if u.nome.lower() == nome.lower():
            st.warning("Usuário já existe.")
            return
    st.session_state["usuarios"].append(Usuario(nome, senha, perfil))
    st.success(f"Usuário {nome} criado com perfil {perfil}.")

def autenticar_usuario(nome, senha):
    for u in st.session_state["usuarios"]:
        if u.nome.lower() == nome.lower() and u.senha == senha:
            return u
    return None

def cadastrar_produto(nome, qtd, preco):
    if not nome.strip():
        st.error("Nome inválido")
        return
    qtd = int(qtd)
    preco = float(preco)
    for p in st.session_state["produtos"]:
        if p.nome.lower() == nome.lower():
            p.qtd += qtd
            p.preco = preco
            st.success(f"Produto {nome} atualizado: +{qtd}, preço R${preco:.2f}")
            return
    codigo = str(st.session_state["codigo_produto"]).zfill(3)
    st.session_state["produtos"].append(Produto(codigo, nome, qtd, preco))
    st.session_state["codigo_produto"] += 1
    st.success(f"Produto {nome} cadastrado com código {codigo}.")

def cadastrar_funcionario(nome):
    if not nome.strip():
        st.error("Nome inválido")
        return
    if nome.title() in [f.nome for f in st.session_state["funcionarios"]]:
        st.warning("Funcionário já cadastrado")
        return
    st.session_state["funcionarios"].append(Funcionario(nome))
    st.success(f"Funcionário {nome} cadastrado")

def remover_funcionario(nome):
    st.session_state["funcionarios"] = [f for f in st.session_state["funcionarios"] if f.nome != nome]
    st.success(f"Funcionário {nome} removido")

def cadastrar_cliente(nome):
    if not nome.strip():
        st.error("Nome inválido")
        return None
    for c in st.session_state["clientes"]:
        if c.nome.lower() == nome.lower():
            return c
    novo = Cliente(nome)
    st.session_state["clientes"].append(novo)
    st.success(f"Cliente {nome} cadastrado")
    return novo

def cadastrar_fornecedor(nome, contato="", produto="", preco=0.0, prazo=0):
    if not nome.strip():
        st.error("Nome inválido")
        return
    st.session_state["fornecedores"].append(Fornecedor(nome, contato, produto, preco, prazo))
    st.success(f"Fornecedor {nome} cadastrado")

def registrar_venda(produto, funcionario, cliente, qtd, tipo="imediata"):
    qtd = int(qtd)
    if qtd <= 0:
        st.error("Quantidade inválida")
        return
    if tipo=="imediata" and qtd>produto.qtd:
        st.error("Estoque insuficiente")
        return
    if tipo=="imediata":
        produto.qtd -= qtd
    total = qtd*produto.preco
    data_hora = datetime.now()
    nome_cliente = cliente.nome if cliente else ""
    st.session_state["vendas"].append([produto.codigo, produto.nome, qtd, produto.preco, total, tipo, data_hora, funcionario.nome, nome_cliente])
    if cliente:
        cliente.historico.append([produto.nome, qtd, total, data_hora, funcionario.nome, tipo])
    st.success(f"Venda registrada: {qtd}x {produto.nome} — {tipo} — por {funcionario.nome}")
    if produto.qtd <= produto.estoque_min:
        st.warning(f"⚠ Estoque baixo: {produto.nome} — {produto.qtd} unidades restantes")

# ================= Tela Inicial (Cadastro/Login) =================
def tela_login():
    mostrar_logo(200)
    st.subheader("🔐 Login")
    nome = st.text_input("Usuário", key="login_nome")
    senha = st.text_input("Senha", type="password", key="login_senha")
    if st.button("Login"):
        usuario = autenticar_usuario(nome, senha)
        if usuario:
            st.session_state["usuario_logado"] = usuario.nome
            st.session_state["perfil_logado"] = usuario.perfil
            st.success(f"Bem-vindo, {usuario.nome} ({usuario.perfil})")
            st.experimental_rerun()
        else:
            st.error("Usuário ou senha incorretos")

def tela_cadastro_usuario():
    mostrar_logo(200)
    st.subheader("📝 Criar Primeiro Usuário")
    nome = st.text_input("Nome", key="cad_nome")
    senha = st.text_input("Senha", type="password", key="cad_senha")
    perfil = st.selectbox("Perfil", ["Gerente", "Caixa"], key="cad_perfil")
    if st.button("Cadastrar Usuário"):
        cadastrar_usuario(nome, senha, perfil)
        st.experimental_rerun()

# ================= Dashboard =================
def dashboard():
    mostrar_logo(600)
    box_title("📊 Dashboard")
    total_caixa = sum(v[4] for v in st.session_state["vendas"] if v[5]=="imediata")
    display_valor = f"R$ {total_caixa:.2f}" if st.session_state["mostrar_caixa"] else "R$ ****"
    vendas_hoje = [v for v in st.session_state["vendas"] if v[5]=="imediata" and v[6].date()==datetime.now().date()]
    produtos_baixos = [p for p in st.session_state["produtos"] if p.qtd<=p.estoque_min]
    clientes_conta = [c for c in st.session_state["clientes"] if sum(x[2] for x in c.historico if x[5]=="reserva")>0]
    total_contas = sum(sum(x[2] for x in c.historico if x[5]=="reserva") for c in clientes_conta)
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

# ================= Funções de tela funcional =================
def tela_funcional():
    mostrar_logo(200)
    tela = st.session_state["tela_selecionada"]
    submenu = st.session_state["submenu_selecionado"]

    # Aqui você pode adicionar todas as funcionalidades já existentes do ERP
    # Estoque, Funcionários, Clientes, Fornecedores, Vendas
    st.info(f"Tela funcional: {tela} - submenu: {submenu}")

# ================= Sidebar =================
def sidebar_menu():
    st.sidebar.header(f"👤 {st.session_state['usuario_logado']} ({st.session_state['perfil_logado']})")
    if st.sidebar.button("🔒 Logoff"):
        st.session_state["usuario_logado"] = None
        st.session_state["perfil_logado"] = None
        st.experimental_rerun()

    menu_principal = ["Dashboard", "Vendas", "Caixa"]
    menu_expansivo = {
        "Estoque": ["Cadastrar Produto", "Produtos"],
        "Funcionários": ["Cadastrar Funcionário", "Funcionários", "Remover Funcionário"],
        "Clientes": ["Histórico", "Conta"],
        "Fornecedores": ["Cadastrar Fornecedor", "Fornecedores"],
        "Relatórios": ["Diário", "Semanal", "Mensal"]
    }

    for item in menu_principal:
        if st.sidebar.button(item):
            st.session_state["tela_selecionada"] = item
            st.session_state["submenu_selecionado"] = None

    for item, submenus in menu_expansivo.items():
        exp = st.sidebar.expander(item, expanded=False)
        with exp:
            for sub in submenus:
                if st.button(sub, key=f"{item}_{sub}"):
                    st.session_state["tela_selecionada"] = item
                    st.session_state["submenu_selecionado"] = sub

# ================= Render principal =================
if not st.session_state["usuarios"]:
    tela_cadastro_usuario()
elif not st.session_state["usuario_logado"]:
    tela_login()
else:
    sidebar_menu()
    if st.session_state["tela_selecionada"] == "Dashboard":
        dashboard()
    else:
        tela_funcional()
