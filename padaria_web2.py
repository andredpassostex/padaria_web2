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
        self.historico = []

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
    ("fornecedores", []), ("vendas", []), ("codigo_produto", 1)
]:
    if key not in st.session_state:
        st.session_state[key] = default

for key in ["tela_selecionada","submenu_selecionado","mostrar_caixa","mostrar_contas"]:
    if key not in st.session_state:
        st.session_state[key] = None if "submenu" in key or "tela" in key else False

# ================= Funções Gerais =================
def mostrar_logo(size):
    logo_path = "logo.png"
    if os.path.exists(logo_path):
        img = Image.open(logo_path)
        st.image(img,width=size)
    else:
        st.markdown(f"<h1 style='text-align:center; color:#4B2E2E;'>🥖 Lucio Pães</h1>", unsafe_allow_html=True)

def box_title(texto,icone="📌"):
    st.markdown(f"""
        <div style='padding: 10px; background-color: #f9f9f9;
                    border-radius: 10px; box-shadow: 2px 2px 10px rgba(0,0,0,0.15);
                    margin-bottom: 12px;'>
            <h3 style='text-align: center; color: #4B2E2E; margin:6px 0;'>{icone} {texto}</h3>
        </div>""", unsafe_allow_html=True)

# ================= Cadastros =================
def cadastrar_produto(nome,qtd,preco):
    codigo = str(st.session_state["codigo_produto"]).zfill(3)
    st.session_state["produtos"].append(Produto(codigo,nome,int(qtd),float(preco)))
    st.session_state["codigo_produto"] +=1
    st.success(f"Produto {nome} cadastrado com código {codigo}.")

def cadastrar_funcionario(nome):
    if nome.strip()=="":
        st.error("Digite o nome")
        return
    if nome.title() in [f.nome for f in st.session_state["funcionarios"]]:
        st.warning("Funcionário já cadastrado")
    else:
        st.session_state["funcionarios"].append(Funcionario(nome))
        st.success(f"Funcionário {nome} cadastrado")

def remover_funcionario(nome):
    st.session_state["funcionarios"] = [f for f in st.session_state["funcionarios"] if f.nome!=nome]
    st.success(f"Funcionário {nome} removido.")

def cadastrar_cliente(nome):
    if nome.strip()=="":
        st.error("Digite o nome do cliente.")
        return None
    for c in st.session_state["clientes"]:
        if c.nome.lower()==nome.lower():
            return c
    novo = Cliente(nome)
    st.session_state["clientes"].append(novo)
    st.success(f"Cliente {nome} cadastrado")
    return novo

def cadastrar_fornecedor(nome,contato="",produto="",preco=0.0,prazo=0):
    if nome.strip()=="":
        st.error("Digite o nome do fornecedor")
        return
    novo = Fornecedor(nome,contato,produto,float(preco),int(prazo))
    st.session_state["fornecedores"].append(novo)
    st.success(f"Fornecedor {nome} cadastrado")

# ================= Vendas =================
def registrar_venda(produto_obj, funcionario_obj, cliente_obj, qtd, tipo):
    qtd = int(qtd)
    if qtd<=0:
        st.error("Quantidade inválida")
        return
    if tipo=="imediata" and qtd>produto_obj.qtd:
        st.error("Quantidade insuficiente")
        return
    if tipo=="imediata":
        produto_obj.qtd -= qtd
    total = qtd*produto_obj.preco
    data_hora = datetime.now()
    st.session_state["vendas"].append([produto_obj.codigo,produto_obj.nome,qtd,produto_obj.preco,total,tipo,data_hora,cliente_obj.nome,funcionario_obj.nome])
    cliente_obj.historico.append([produto_obj.nome,qtd,total,data_hora,funcionario_obj.nome,tipo])
    st.success(f"Venda registrada: {qtd}x {produto_obj.nome} para {cliente_obj.nome} ({tipo}).")
    if produto_obj.qtd<=produto_obj.estoque_min:
        st.warning(f"⚠ Estoque baixo de {produto_obj.nome}: {produto_obj.qtd} unidades restantes!")

def zerar_conta_cliente(cliente_obj):
    for compra in cliente_obj.historico:
        if compra[5]=="reserva":
            compra[5]="pago"
    st.success(f"Conta do cliente {cliente_obj.nome} zerada")

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

    col1,col2,col3,col4 = st.columns(4)
    col1.metric("Total Caixa", display_valor)
    if col1.button("👁️", key="btn_caixa"):
        st.session_state["mostrar_caixa"] = not st.session_state["mostrar_caixa"]
    col2.metric("Vendas Hoje", len(vendas_hoje))
    col3.metric("Produtos Baixos", len(produtos_baixos))
    display_conta = f"R$ {total_contas:.2f}" if st.session_state["mostrar_contas"] else "R$ ****"
    col4.metric("Clientes com Conta", display_conta)
    if col4.button("👁️", key="btn_conta"):
        st.session_state["mostrar_contas"] = not st.session_state["mostrar_contas"]

# ================= Telas Funcionais =================
def tela_funcional():
    mostrar_logo(200)
    tela = st.session_state["tela_selecionada"]
    submenu = st.session_state["submenu_selecionado"]

    # Aqui você implementa cadastro, listagem e operações conforme submenu selecionado
    # O padrão segue o que já discutimos (Produtos, Funcionários, Clientes, Fornecedores, Vendas e Relatórios)

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
    exp = st.sidebar.expander(item,expanded=False)
    with exp:
        for sub in submenus:
            if st.button(sub,key=f"{item}_{sub}"):
                st.session_state["tela_selecionada"]=item
                st.session_state["submenu_selecionado"]=sub

# ================= Render =================
if st.session_state["tela_selecionada"]=="Dashboard":
    dashboard()
else:
    tela_funcional()
