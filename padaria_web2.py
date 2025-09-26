# padaria_erp_integrado.py
import os
import streamlit as st
import pandas as pd
from datetime import datetime
from PIL import Image

# ================= Usuários / Login =================
class Usuario:
    def __init__(self, nome, senha, perfil):
        self.nome = nome.title().strip()
        self.senha = senha
        self.perfil = perfil

# Inicializar lista de usuários no session_state
if "usuarios" not in st.session_state:
    st.session_state["usuarios"] = []

def cadastrar_usuario(nome, senha, perfil):
    if not nome.strip() or not senha.strip():
        st.error("Digite usuário e senha")
        return
    # Verifica se já existe
    for u in st.session_state["usuarios"]:
        if u.nome.lower() == nome.lower():
            st.warning("Usuário já existe")
            return
    novo = Usuario(nome, senha, perfil)
    st.session_state["usuarios"].append(novo)
    st.success(f"Usuário {nome} ({perfil}) cadastrado com sucesso!")

def autenticar_usuario(nome, senha):
    for u in st.session_state["usuarios"]:
        if u.nome.lower() == nome.lower() and u.senha == senha:
            return u
    return None

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
    def __init__(self, nome, senha, perfil="Caixa"):
        self.nome = nome.strip()
        self.senha = senha
        self.perfil = perfil  # "Caixa" ou "Gerente"

# ================= Inicialização =================
for key, default in [
    ("produtos", []), ("funcionarios", []), ("clientes", []),
    ("fornecedores", []), ("vendas", []), ("codigo_produto", 1),
    ("usuarios", []), ("usuario_logado", None)
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
                    margin-bottom: 12px;'>{''}
            <h3 style='text-align: center; color: #4B2E2E; margin:6px 0;'>{icone} {texto}</h3>
        </div>""", unsafe_allow_html=True)

# ================= Funções de Cadastro =================
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

def cadastrar_usuario(nome,senha,perfil):
    if nome.strip()=="" or senha.strip()=="":
        st.error("Nome e senha são obrigatórios")
        return
    for u in st.session_state["usuarios"]:
        if u.nome.lower()==nome.lower():
            st.warning("Usuário já existe")
            return
    st.session_state["usuarios"].append(Usuario(nome,senha,perfil))
    st.success(f"Usuário {nome} criado com perfil {perfil}")

def autenticar_usuario(nome,senha):
    for u in st.session_state["usuarios"]:
        if u.nome.lower()==nome.lower() and u.senha==senha:
            return u
    return None

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

# ================= Vendas =================
def registrar_venda(produto, funcionario, cliente, quantidade, tipo="imediata"):
    if quantidade<=0 or quantidade>produto.qtd:
        st.error("Quantidade inválida ou maior que o estoque.")
        return
    produto.qtd -= quantidade
    total = quantidade*produto.preco
    data_hora = datetime.now()
    st.session_state["vendas"].append([produto.codigo, produto.nome, quantidade, produto.preco, total, tipo, data_hora, funcionario.nome, cliente.nome if cliente else ""])
    if cliente and tipo=="reserva":
        cliente.historico.append([produto.nome, quantidade, total, data_hora, funcionario.nome, tipo])
    st.success(f"Venda de {quantidade}x {produto.nome} registrada por {funcionario.nome}")
    if produto.qtd<=produto.estoque_min:
        st.warning(f"⚠ Estoque baixo: {produto.nome} apenas {produto.qtd} unidades restantes!")

# ================= Telas Funcionais =================
def tela_funcional():
    mostrar_logo(200)
    tela = st.session_state["tela_selecionada"]
    submenu = st.session_state["submenu_selecionado"]

    # Estoque
    if tela=="Estoque":
        if submenu=="Cadastrar Produto":
            box_title("Cadastrar Produto")
            nome = st.text_input("Nome do Produto")
            qtd = st.number_input("Quantidade", min_value=1,value=1)
            preco = st.number_input("Preço Unitário", min_value=0.01,value=1.0,format="%.2f")
            if st.button("Cadastrar Produto"):
                cadastrar_produto(nome,qtd,preco)
        elif submenu=="Produtos":
            box_title("Lista de Produtos")
            if st.session_state["produtos"]:
                df = pd.DataFrame([[p.codigo,p.nome,p.qtd,p.preco] for p in st.session_state["produtos"]],
                                  columns=["Código","Produto","Quantidade","Preço"])
                st.table(df)
            else:
                st.info("Nenhum produto cadastrado")

    # Funcionários
    elif tela=="Funcionários":
        if submenu=="Cadastrar Funcionário":
            box_title("Cadastrar Funcionário")
            nome = st.text_input("Nome do Funcionário")
            if st.button("Cadastrar Funcionário"):
                cadastrar_funcionario(nome)
        elif submenu=="Funcionários":
            box_title("Lista de Funcionários")
            if st.session_state["funcionarios"]:
                for f in st.session_state["funcionarios"]:
                    st.write(f.nome)
            else:
                st.info("Nenhum funcionário cadastrado")
        elif submenu=="Remover Funcionário":
            box_title("Remover Funcionário")
            if st.session_state["funcionarios"]:
                nomes = [f.nome for f in st.session_state["funcionarios"]]
                sel = st.selectbox("Escolha o funcionário para remover",nomes)
                if st.button("Remover Funcionário"):
                    remover_funcionario(sel)
            else:
                st.info("Nenhum funcionário cadastrado")

    # Clientes
    elif tela=="Clientes":
        if submenu=="Histórico":
            box_title("Clientes com pendências")
            if st.session_state["clientes"]:
                with st.expander("Clientes"):
                    for c in sorted(st.session_state["clientes"], key=lambda x:x.nome):
                        total_reserva = sum(x[2] for x in c.historico if x[5]=="reserva")
                        if total_reserva>0:
                            st.write(f"**{c.nome}**: {total_reserva:.2f} R$")
                            df = pd.DataFrame([x for x in c.historico if x[5]=="reserva"], columns=["Produto","Qtd","Total","Data/Hora","Funcionário","Tipo"])
                            st.table(df)
                        else:
                            st.write(f"**{c.nome}**: Sem pendências")
        elif submenu=="Conta":
            box_title("Gerenciar Conta do Cliente")
            if st.session_state["clientes"]:
                nomes = [c.nome for c in st.session_state["clientes"]]
                sel = st.selectbox("Escolha o cliente", nomes)
                cliente = next(c for c in st.session_state["clientes"] if c.nome==sel)
                total_reserva = sum(x[2] for x in cliente.historico if x[5]=="reserva")
                st.markdown(f"**Total em Reserva:** R$ {total_reserva:.2f}")
                historico_reserva = [x for x in cliente.historico if x[5]=="reserva"]
                if historico_reserva:
                    df = pd.DataFrame(historico_reserva, columns=["Produto", "Qtd", "Total", "Data/Hora", "Funcionário", "Tipo"])
                    st.table(df)
                else:
                    st.info("Sem compras em aberto.")
                if st.button("Zerar Conta"):
                    for x in cliente.historico:
                        if x[5]=="reserva":
                            x[5]="pago"
                    st.success(f"Conta de {cliente.nome} zerada.")
            else:
                st.info("Nenhum cliente cadastrado")

    # Fornecedores
    elif tela=="Fornecedores":
        if submenu=="Cadastrar Fornecedor":
            box_title("Cadastrar Fornecedor")
            nome = st.text_input("Nome do Fornecedor")
            contato = st.text_input("Contato")
            produto = st.text_input("Produto Fornecido")
            preco = st.number_input("Preço Unitário", min_value=0.01,value=1.0,format="%.2f")
            prazo = st.number_input("Prazo de Entrega (dias)",min_value=0,value=0)
            if st.button("Cadastrar Fornecedor"):
                cadastrar_fornecedor(nome,contato,produto,preco,prazo)
        elif submenu=="Fornecedores":
            box_title("Lista de Fornecedores")
            if st.session_state["fornecedores"]:
                df = pd.DataFrame([[f.nome,f.contato,f.produto,f.preco,f.prazo] for f in st.session_state["fornecedores"]],
                                  columns=["Fornecedor","Contato","Produto","Preço","Prazo"])
                st.table(df)
            else:
                st.info("Nenhum fornecedor cadastrado")

    # Vendas
    elif tela=="Vendas":
        box_title("Registrar Venda")
        if not st.session_state["produtos"] or not st.session_state["funcionarios"]:
            st.info("Cadastre produtos e funcionários antes de registrar vendas.")
        else:
            produtos_display = [f"{p.codigo} - {p.nome}" for p in st.session_state["produtos"]]
            prod_sel = st.selectbox("Produto",produtos_display)
            produto = next(p for p in st.session_state["produtos"] if p.codigo==prod_sel.split(" - ")[0])
            func_sel = st.selectbox("Funcionário",[f.nome for f in st.session_state["funcionarios"]])
            funcionario = next(f for f in st.session_state["funcionarios"] if f.nome==func_sel)
            cliente_nome = st.text_input("Nome do Cliente (opcional)")
            cliente = cadastrar_cliente(cliente_nome) if cliente_nome else None
            qtd = st.number_input("Quantidade", min_value=1,value=1)
            tipo = st.radio("Tipo de Venda",["imediata","reserva"])
            if st.button("Registrar Venda"):
                registrar_venda(produto,funcionario,cliente,qtd,tipo)
# ================= Login / Logout =================
def tela_login():
    st.title("🥖 Padaria Lucio Pães - Login")
    st.subheader("Faça login ou cadastre um novo usuário")
    
    tab1, tab2 = st.tabs(["Login", "Cadastro"])
    
    with tab1:
        nome = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")
        if st.button("Entrar"):
            usuario = autenticar_usuario(nome,senha)
            if usuario:
                st.session_state["usuario_logado"] = usuario
                st.success(f"Bem-vindo(a) {usuario.nome} ({usuario.perfil})")
                st.experimental_rerun()
            else:
                st.error("Usuário ou senha incorretos")

    with tab2:
        nome_c = st.text_input("Novo usuário", key="novo_usuario")
        senha_c = st.text_input("Senha", type="password", key="senha_nova")
        perfil = st.selectbox("Perfil",["Caixa","Gerente"])
        if st.button("Cadastrar"):
            cadastrar_usuario(nome_c,senha_c,perfil)

# ================= Sidebar =================
def sidebar_menu():
    usuario = st.session_state["usuario_logado"]
    st.sidebar.header(f"👋 {usuario.nome} ({usuario.perfil})")
    if st.sidebar.button("🔒 Logout"):
        st.session_state["usuario_logado"] = None
        st.experimental_rerun()

    menu_principal = ["Dashboard","Vendas","Caixa"]
    menu_expansivo = {
        "Estoque":["Cadastrar Produto","Produtos"],
        "Funcionários":["Cadastrar Funcionário","Funcionários","Remover Funcionário"],
        "Clientes":["Histórico","Conta"],
        "Fornecedores":["Cadastrar Fornecedor","Fornecedores"]
    }

    # Ajuste de permissões
    if usuario.perfil=="Caixa":
        menu_principal = ["Vendas","Caixa"]
        menu_expansivo = {"Clientes":["Conta"]}

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

# ================= Caixa / Relatórios =================
def tela_caixa(tipo_relatorio):
    box_title(f"📋 Caixa - {tipo_relatorio}")
    hoje = datetime.now()
    if tipo_relatorio=="Diário":
        vendas = [v for v in st.session_state["vendas"] if v[6].date()==hoje.date()]
    elif tipo_relatorio=="Semanal":
        semana = hoje.isocalendar()[1]
        vendas = [v for v in st.session_state["vendas"] if v[6].isocalendar()[1]==semana]
    elif tipo_relatorio=="Mensal":
        mes = hoje.month
        vendas = [v for v in st.session_state["vendas"] if v[6].month==mes]
    
    if vendas:
        df = pd.DataFrame(vendas, columns=["Código","Produto","Qtd","Preço Unit.","Total","Tipo","Data/Hora","Funcionário","Cliente"])
        st.table(df)
    else:
        st.info("Nenhuma venda registrada neste período.")

# ================= Render =================
if st.session_state["usuario_logado"] is None:
    tela_login()
else:
    sidebar_menu()
    tela = st.session_state["tela_selecionada"]
    if tela=="Dashboard":
        dashboard()
    elif tela=="Caixa":
        st.subheader("📊 Selecionar Relatório")
        tipo = st.radio("Escolha o período",["Diário","Semanal","Mensal"])
        tela_caixa(tipo)
    else:
        tela_funcional()

