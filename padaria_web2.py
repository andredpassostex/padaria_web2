# padaria_erp_pro.py
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
    ("produtos", []), ("funcionarios", []), ("clientes", []),
    ("vendas", []), ("fornecedores", []), ("codigo_produto", 1)
]:
    if key not in st.session_state:
        st.session_state[key] = default

if "tela_selecionada" not in st.session_state:
    st.session_state["tela_selecionada"] = "Dashboard"
if "submenu_selecionado" not in st.session_state:
    st.session_state["submenu_selecionado"] = None
if "mostrar_caixa" not in st.session_state:
    st.session_state["mostrar_caixa"] = False
if "mostrar_contas" not in st.session_state:
    st.session_state["mostrar_contas"] = False

# ================= Funções =================
def box_title(texto, icone="📌"):
    st.markdown(f"""
        <div style='padding: 10px; background-color: #f9f9f9;
                    border-radius: 10px; box-shadow: 2px 2px 10px rgba(0,0,0,0.15);
                    margin-bottom: 12px;'>
            <h3 style='text-align: center; color: #4B2E2E; margin:6px 0;'>{icone} {texto}</h3>
        </div>""", unsafe_allow_html=True)

def try_load_logo():
    for path in ["logo.png", "./logo.png", "images/logo.png"]:
        if os.path.exists(path):
            try:
                return Image.open(path)
            except:
                continue
    return None

# ================= Cadastro e Operações =================
def cadastrar_produto(nome,qtd,preco):
    codigo = str(st.session_state["codigo_produto"]).zfill(3)
    st.session_state["produtos"].append(Produto(codigo,nome,int(qtd),float(preco)))
    st.session_state["codigo_produto"] += 1
    st.success(f"Produto {nome} cadastrado com código {codigo}.")

def cadastrar_funcionario(nome):
    if nome.strip() == "":
        st.error("Digite o nome.")
        return
    if nome.title() in [f.nome for f in st.session_state["funcionarios"]]:
        st.warning("Funcionário já cadastrado.")
    else:
        st.session_state["funcionarios"].append(Funcionario(nome))
        st.success(f"Funcionário {nome} cadastrado.")

def remover_funcionario(nome):
    st.session_state["funcionarios"] = [f for f in st.session_state["funcionarios"] if f.nome != nome]
    st.success(f"Funcionário {nome} removido.")

def cadastrar_cliente(nome):
    if nome.strip() == "":
        st.error("Digite o nome do cliente.")
        return
    for c in st.session_state["clientes"]:
        if c.nome.lower() == nome.lower():
            return c
    novo = Cliente(nome)
    st.session_state["clientes"].append(novo)
    st.success(f"Cliente {nome} cadastrado.")
    return novo

def registrar_venda(produto_obj, funcionario_obj, cliente_obj, qtd, tipo):
    qtd = int(qtd)
    if qtd <= 0:
        st.error("Quantidade inválida.")
        return
    if tipo=="imediata" and qtd>produto_obj.qtd:
        st.error("Quantidade insuficiente no estoque!")
        return
    if tipo=="imediata":
        produto_obj.qtd -= qtd
    total = qtd*produto_obj.preco
    data_hora = datetime.now()
    st.session_state["vendas"].append([produto_obj.codigo,produto_obj.nome,qtd,produto_obj.preco,total,tipo,data_hora,cliente_obj.nome,funcionario_obj.nome])
    cliente_obj.historico.append([produto_obj.nome,qtd,total,data_hora,funcionario_obj.nome,tipo])
    st.success(f"Venda registrada: {qtd}x {produto_obj.nome} para {cliente_obj.nome} ({tipo}).")
    if produto_obj.qtd <= produto_obj.estoque_min:
        st.warning(f"⚠ Estoque baixo de {produto_obj.nome}: {produto_obj.qtd} unidades restantes!")

def zerar_conta_cliente(cliente_obj):
    for compra in cliente_obj.historico:
        if compra[5]=="reserva":
            compra[5]="pago"
    st.success(f"Conta do cliente {cliente_obj.nome} zerada (pagamentos realizados).")

# ================= Cabeçalho =================
logo = try_load_logo()
logo_banner_width = 600
logo_top_width = 200
def mostrar_logo(size):
    if logo:
        st.image(logo,width=size)
    else:
        st.markdown(f"<h1 style='text-align:center; color:#4B2E2E;'>🥖 Lucio Pães</h1>", unsafe_allow_html=True)

# ================= Dashboard =================
def dashboard():
    mostrar_logo(logo_banner_width)
    box_title("📊 Dashboard")
    total_caixa = sum(v[4] for v in st.session_state["vendas"] if v[5]=="imediata")
    vendas_hoje = [v for v in st.session_state["vendas"] if v[5]=="imediata" and v[6].date()==datetime.now().date()]
    produtos_baixos = [p for p in st.session_state["produtos"] if p.qtd<=p.estoque_min]
    clientes_conta = [c for c in st.session_state["clientes"] if sum(x[2] for x in c.historico if x[5]=="reserva")>0]

    col1,col2,col3,col4 = st.columns(4)
    display_valor = f"R$ {total_caixa:.2f}" if st.session_state["mostrar_caixa"] else "R$ ****"
    col1.metric("Total Caixa", display_valor)
    if col1.button("👁️", key="btn_caixa"):
        st.session_state["mostrar_caixa"] = not st.session_state["mostrar_caixa"]
    col2.metric("Vendas Hoje", len(vendas_hoje))
    col3.metric("Produtos Baixos", len(produtos_baixos))
    total_contas = sum(sum(x[2] for x in c.historico if x[5]=="reserva") for c in clientes_conta)
    display_conta = f"R$ {total_contas:.2f}" if st.session_state["mostrar_contas"] else "R$ ****"
    col4.metric("Clientes com Conta", display_conta)
    if col4.button("👁️", key="btn_conta"):
        st.session_state["mostrar_contas"] = not st.session_state["mostrar_contas"]

# ================= Tela Funcional =================
def tela_funcional():
    if st.session_state["tela_selecionada"]!="Dashboard":
        mostrar_logo(logo_top_width)
    tela = st.session_state["tela_selecionada"]
    submenu = st.session_state["submenu_selecionado"]

    # Aqui você pode implementar cada tela detalhada: Venda, Estoque, Clientes, Funcionários, Fornecedores e Relatórios
    # Para cada submenu, usando as funções acima (cadastro, venda, histórico, zerar conta, alertas, tabelas etc.)

# ================= Sidebar =================
menu_principal = ["Dashboard","Venda","Caixa"]
menu_expansivo = {
    "Estoque":["Cadastrar Produto","Produtos"],
    "Funcionários":["Cadastrar Funcionário","Funcionários","Remover Funcionário"],
    "Clientes":["Histórico","Conta"],
    "Fornecedores":["Cadastrar Fornecedor","Fornecedores"],
    "Relatórios":["Diário","Semanal","Mensal"]
}

st.sidebar.header("📌 Menu")
for item in menu_principal:
    if st.sidebar.button(item):
        st.session_state["tela_selecionada"]=item
        st.session_state["submenu_selecionado"]=None

for item, submenus in menu_expansivo.items():
    expand = st.sidebar.expander(item,expanded=False)
    with expand:
        for submenu in submenus:
            if st.button(submenu,key=f"{item}_{submenu}"):
                st.session_state["tela_selecionada"]=item
                st.session_state["submenu_selecionado"]=submenu

# ================= Render =================
if st.session_state["tela_selecionada"]=="Dashboard":
    dashboard()
else:
    tela_funcional()
