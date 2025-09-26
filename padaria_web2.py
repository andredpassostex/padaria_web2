# padaria_erp_completo_v2.py
import os
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
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

# ================= Inicialização do session_state =================
for key, default in [
    ("produtos", []), ("funcionarios", []), ("clientes", []),
    ("fornecedores", []), ("vendas", []), ("codigo_produto", 1)
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
                    margin-bottom: 12px;'>{''}
            <h3 style='text-align:center; color:#4B2E2E; margin:6px 0;'>{icone} {texto}</h3>
        </div>
    """, unsafe_allow_html=True)

def estilizar_historico(df):
    # Coluna "Tipo" com cores
    def color_tipo(val):
        color = 'orange' if val.lower() == "reserva" else 'green'
        return f'color: {color}; font-weight: bold'
    return df.style.applymap(color_tipo, subset=["Tipo"])

# ================= Funções de negócio =================
def cadastrar_produto(nome, qtd, preco):
    if not nome or str(nome).strip() == "":
        st.error("Nome do produto inválido.")
        return
    codigo = str(st.session_state["codigo_produto"]).zfill(3)
    st.session_state["produtos"].append(Produto(codigo, nome, int(qtd), float(preco)))
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
        # Registra todas as vendas no histórico do cliente
        cliente.historico.append([produto.nome, quantidade, total, data_hora, funcionario.nome, tipo])
    st.success(f"Venda registrada: {quantidade} x {produto.nome} — {tipo} — atendido por {funcionario.nome}")
    if produto.qtd <= produto.estoque_min:
        st.warning(f"⚠ Estoque baixo: {produto.nome} — {produto.qtd} unidades restantes.")

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
    with col4:
        display_conta = f"R$ {total_contas:.2f}" if st.session_state["mostrar_contas"] else "R$ ****"
        st.markdown(f"<div style='background-color:#F44336;padding:15px;border-radius:10px;color:white;text-align:center;'><h4>👥 Contas em Aberto</h4><h2>{display_conta}</h2></div>", unsafe_allow_html=True)
        if st.button("👁️", key="btn_conta"):
            st.session_state["mostrar_contas"] = not st.session_state["mostrar_contas"]

# ================= Tela Funcional =================
def tela_funcional():
    mostrar_logo(200)
    tela = st.session_state["tela_selecionada"]
    submenu = st.session_state["submenu_selecionado"]

    # ----------------- Clientes -----------------
    if tela == "Clientes" and submenu == "Histórico":
        box_title("Histórico de Clientes")
        if not st.session_state["clientes"]:
            st.info("Nenhum cliente cadastrado")
        else:
            with st.expander("Clientes", expanded=True):
                nomes_clientes = sorted([c.nome for c in st.session_state["clientes"]])
                sel_cliente = st.selectbox("Selecione o cliente", nomes_clientes, key="hist_sel_cliente")
                cliente = next(c for c in st.session_state["clientes"] if c.nome == sel_cliente)
                if cliente.historico:
                    df = pd.DataFrame(cliente.historico, columns=["Produto", "Qtd", "Total", "Data/Hora", "Funcionário", "Tipo"])
                    st.dataframe(estilizar_historico(df), height=400)
                else:
                    st.info("Sem histórico de compras.")

    # ----------------- Caixa / Vendas -----------------
    elif tela == "Caixa" and submenu in ["Diário", "Semanal", "Mensal"]:
        box_title(f"Vendas - {submenu}")
        if not st.session_state["vendas"]:
            st.info("Nenhuma venda registrada.")
        else:
            now = datetime.now()
            if submenu == "Diário":
                vendas_filtradas = [v for v in st.session_state["vendas"] if v[6].date() == now.date()]
            elif submenu == "Semanal":
                today = now.date()
                start_week = today - timedelta(days=today.weekday())
                end_week = start_week + timedelta(days=6)
                vendas_filtradas = [v for v in st.session_state["vendas"] if start_week <= v[6].date() <= end_week]
            elif submenu == "Mensal":
                vendas_filtradas = [v for v in st.session_state["vendas"] if v[6].year == now.year and v[6].month == now.month]

            if vendas_filtradas:
                df = pd.DataFrame([[v[1], v[2], v[6].strftime("%d/%m/%Y %H:%M"), v[7], v[5]] for v in vendas_filtradas], columns=["Produto", "Qtd", "Hora", "Funcionário", "Tipo"])
                st.dataframe(estilizar_historico(df), height=400)
                total_vendas = sum(v[4] for v in vendas_filtradas)
                st.markdown(f"**Total Vendas ({submenu}): R$ {total_vendas:.2f}**")
            else:
                st.info(f"Nenhuma venda registrada no período {submenu.lower()}.")

# ================= Sidebar (menu) =================
menu_principal = ["Dashboard", "Vendas", "Caixa"]
menu_expansivo = {
    "Estoque": ["Cadastrar Produto", "Produtos"],
    "Funcionários": ["Cadastrar Funcionário", "Funcionários", "Remover Funcionário"],
    "Clientes": ["Histórico", "Conta"],
    "Fornecedores": ["Cadastrar Fornecedor", "Fornecedores"],
    "Relatórios": ["Diário", "Semanal", "Mensal"]
}

st.sidebar.header("📌 Menu")
for item in menu_principal:
    if st.sidebar.button(item):
        st.session_state["tela_selecionada"] = item
        st.session_state["submenu_selecionado"] = None
for item, submenus in menu_expansivo.items():
    exp = st.sidebar.expander(item, expanded=False)
    with exp:
        for sub in submenus:
            if st.button(sub, key=f"{item}_{sub}"):
                if item == "Relatórios":
                    st.session_state["tela_selecionada"] = "Caixa"
                    st.session_state["submenu_selecionado"] = sub
                else:
                    st.session_state["tela_selecionada"] = item
                    st.session_state["submenu_selecionado"] = sub

# ================= Render principal =================
if st.session_state["tela_selecionada"] == "Dashboard":
    dashboard()
else:
    tela_funcional()
