# padaria_erp_completo_final.py
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

# ================= Inicialização =================
for key, default in [
    ("produtos", []), ("funcionarios", []), ("clientes", []),
    ("fornecedores", []), ("vendas", []), ("codigo_produto", 1)
]:
    if key not in st.session_state:
        st.session_state[key] = default

if "usuarios" not in st.session_state:
    st.session_state["usuarios"] = {
        "gerente": {"senha": "123", "perfil": "Gerente"},
        "caixa": {"senha": "123", "perfil": "Caixa"}
    }
if "usuario_logado" not in st.session_state:
    st.session_state["usuario_logado"] = None
if "perfil_logado" not in st.session_state:
    st.session_state["perfil_logado"] = None

for key, default in [("tela_selecionada", "Dashboard"),
                     ("submenu_selecionado", None),
                     ("mostrar_caixa", False),
                     ("mostrar_contas", False)]:
    if key not in st.session_state:
        st.session_state[key] = default

# ================= Utilitários =================
def mostrar_logo(size):
    logo_path = "logo.png"
    if os.path.exists(logo_path):
        try:
            img = Image.open(logo_path)
            st.image(img, width=size)
        except Exception:
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

# ================= Funções de negócio =================
def cadastrar_produto(nome, qtd, preco):
    if not nome.strip():
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
    if not nome.strip():
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
    if not nome.strip():
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
    if not nome.strip():
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

# ================= Login e Logoff =================
def tela_login():
    st.title("🔑 Login do Sistema")
    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        if usuario in st.session_state["usuarios"] and senha == st.session_state["usuarios"][usuario]["senha"]:
            st.session_state["usuario_logado"] = usuario
            st.session_state["perfil_logado"] = st.session_state["usuarios"][usuario]["perfil"]
            st.success(f"Bem-vindo(a) {st.session_state['perfil_logado']}!")
            st.experimental_rerun()
        else:
            st.error("Usuário ou senha incorretos.")

def logoff():
    st.session_state["usuario_logado"] = None
    st.session_state["perfil_logado"] = None
    st.session_state["tela_selecionada"] = "Dashboard"
    st.session_state["submenu_selecionado"] = None
    st.experimental_rerun()

# ================= Gerenciar Usuários =================
def gerenciar_usuarios():
    box_title("👤 Gerenciar Usuários")
    nome = st.text_input("Nome do Usuário", key="novo_user")
    senha = st.text_input("Senha", type="password", key="senha_user")
    perfil = st.selectbox("Perfil", ["Gerente", "Caixa"], key="perfil_user")
    if st.button("Criar Usuário", key="btn_criar_user"):
        if not nome or not senha:
            st.error("Preencha todos os campos!")
            return
        if nome in st.session_state["usuarios"]:
            st.warning("Usuário já existe!")
            return
        st.session_state["usuarios"][nome] = {"senha": senha, "perfil": perfil}
        st.success(f"Usuário '{nome}' criado com perfil '{perfil}'!")

# ================= Tela Funcional =================
def tela_funcional():
    mostrar_logo(200)
    tela = st.session_state["tela_selecionada"]
    submenu = st.session_state["submenu_selecionado"]

    # ====== Estoque ======
    if tela=="Estoque":
        if submenu=="Cadastrar Produto":
            box_title("Cadastrar Produto")
            nome = st.text_input("Nome do Produto", key="cad_prod_nome")
            qtd = st.number_input("Quantidade", min_value=1, value=1, key="cad_prod_qtd")
            preco = st.number_input("Preço Unitário", min_value=0.01, value=1.0, format="%.2f", key="cad_prod_preco")
            if st.button("Cadastrar Produto", key="btn_cad_prod"):
                cadastrar_produto(nome, qtd, preco)
        elif submenu=="Produtos":
            box_title("Lista de Produtos")
            if st.session_state["produtos"]:
                df = pd.DataFrame([[p.codigo,p.nome,p.qtd,p.preco] for p in st.session_state["produtos"]],
                                  columns=["Código","Produto","Qtd","Preço"])
                st.dataframe(df, use_container_width=True)
            else:
                st.info("Nenhum produto cadastrado")

    # ====== Funcionários ======
    elif tela=="Funcionários":
        if submenu=="Cadastrar Funcionário":
            box_title("Cadastrar Funcionário")
            nome = st.text_input("Nome do Funcionário", key="cad_func_nome")
            if st.button("Cadastrar Funcionário", key="btn_cad_func"):
                cadastrar_funcionario(nome)
        elif submenu=="Funcionários":
            box_title("Lista de Funcionários")
            if st.session_state["funcionarios"]:
                df = pd.DataFrame([[f.nome] for f in st.session_state["funcionarios"]], columns=["Funcionário"])
                st.dataframe(df, use_container_width=True)
            else:
                st.info("Nenhum funcionário cadastrado")
        elif submenu=="Remover Funcionário":
            box_title("Remover Funcionário")
            if st.session_state["funcionarios"]:
                sel = st.selectbox("Escolha o funcionário", [f.nome for f in st.session_state["funcionarios"]], key="sel_rem_func")
                if st.button("Remover Funcionário", key="btn_rem_func"):
                    remover_funcionario(sel)
            else:
                st.info("Nenhum funcionário cadastrado")

    # ====== Clientes ======
    elif tela=="Clientes":
        if submenu=="Histórico":
            box_title("Histórico de Clientes")
            if not st.session_state["clientes"]:
                st.info("Nenhum cliente cadastrado")
            else:
                sel_cliente = st.selectbox("Selecione o cliente", [c.nome for c in st.session_state["clientes"]], key="hist_cli")
                cliente = next(c for c in st.session_state["clientes"] if c.nome==sel_cliente)
                if cliente.historico:
                    df = pd.DataFrame(cliente.historico, columns=["Produto","Qtd","Total","Data/Hora","Funcionário","Tipo"])
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("Sem histórico de compras")
        elif submenu=="Conta":
            box_title("Gerenciar Conta do Cliente")
            if st.session_state["clientes"]:
                sel_cliente = st.selectbox("Selecione o cliente", [c.nome for c in st.session_state["clientes"]], key="cont_cli")
                cliente = next(c for c in st.session_state["clientes"] if c.nome==sel_cliente)
                total_reserva = sum(x[2] for x in cliente.historico if x[5]=="reserva")
                st.markdown(f"**Total em Reserva:** R$ {total_reserva:.2f}")
                if st.button("Zerar Conta", key="btn_zerar"):
                    for x in cliente.historico:
                        if x[5]=="reserva":
                            x[5]="imediata"
                    st.success(f"Conta de {cliente.nome} zerada")
            else:
                st.info("Nenhum cliente cadastrado")

    # ====== Fornecedores ======
    elif tela=="Fornecedores":
        if submenu=="Cadastrar Fornecedor":
            box_title("Cadastrar Fornecedor")
            nome = st.text_input("Nome", key="forne_nome")
            contato = st.text_input("Contato", key="forne_contato")
            produto = st.text_input("Produto", key="forne_prod")
            preco = st.number_input("Preço", min_value=0.01, value=1.0, format="%.2f", key="forne_preco")
            prazo = st.number_input("Prazo (dias)", min_value=0, value=0, key="forne_prazo")
            if st.button("Cadastrar Fornecedor", key="btn_cad_for"):
                cadastrar_fornecedor(nome, contato, produto, preco, prazo)
        elif submenu=="Fornecedores":
            box_title("Lista de Fornecedores")
            if st.session_state["fornecedores"]:
                df = pd.DataFrame([[f.nome,f.contato,f.produto,f.preco,f.prazo] for f in st.session_state["fornecedores"]],
                                  columns=["Fornecedor","Contato","Produto","Preço","Prazo"])
                st.dataframe(df, use_container_width=True)
            else:
                st.info("Nenhum fornecedor cadastrado")

    # ====== Vendas ======
    elif tela=="Vendas":
        box_title("Registrar Venda")
        if not st.session_state["produtos"] or not st.session_state["funcionarios"]:
            st.info("Cadastre produtos e funcionários antes de registrar vendas")
        else:
            sel_prod = st.selectbox("Produto", [f"{p.codigo} - {p.nome}" for p in st.session_state["produtos"]], key="venda_prod")
            produto = next(p for p in st.session_state["produtos"] if p.codigo==sel_prod.split(" - ")[0])
            sel_func = st.selectbox("Funcionário", [f.nome for f in st.session_state["funcionarios"]], key="venda_func")
            funcionario = next(f for f in st.session_state["funcionarios"] if f.nome==sel_func)
            cliente_nome = st.text_input("Cliente (opcional)", key="venda_cli")
            cliente = cadastrar_cliente(cliente_nome) if cliente_nome else None
            qtd = st.number_input("Quantidade", min_value=1, value=1, key="venda_qtd")
            tipo = st.radio("Tipo", ["imediata","reserva"], key="venda_tipo")
            if st.button("Registrar Venda", key="btn_venda"):
                registrar_venda(produto, funcionario, cliente, qtd, tipo)

# ================= Sidebar =================
if st.session_state["usuario_logado"]:
    st.sidebar.header(f"👋 {st.session_state['usuario_logado']} ({st.session_state['perfil_logado']})")
    if st.sidebar.button("🔄 Logoff"):
        logoff()

    menu_principal = ["Dashboard", "Vendas", "Caixa"]
    menu_expansivo = {
        "Estoque": ["Cadastrar Produto", "Produtos"],
        "Funcionários": ["Cadastrar Funcionário", "Funcionários", "Remover Funcionário"],
        "Clientes": ["Histórico", "Conta"],
        "Fornecedores": ["Cadastrar Fornecedor", "Fornecedores"],
        "Relatórios": ["Diário", "Semanal", "Mensal"]
    }

    if st.session_state["perfil_logado"]=="Gerente":
        menu_expansivo["Usuários"] = ["Gerenciar Usuários"]

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
                    st.session_state["tela_selecionada"] = item
                    st.session_state["submenu_selecionado"] = sub

    # Render
    if st.session_state["tela_selecionada"]=="Dashboard":
        dashboard()
    elif st.session_state["tela_selecionada"]=="Usuários":
        gerenciar_usuarios()
    else:
        tela_funcional()
else:
    tela_login()
