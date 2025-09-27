import streamlit as st
import pandas as pd
from datetime import datetime

# ================= CLASSES =================
class Produto:
    def __init__(self, nome, preco, quantidade):
        self.nome = nome
        self.preco = preco
        self.quantidade = quantidade

class Funcionario:
    def __init__(self, nome):
        self.nome = nome

class Cliente:
    def __init__(self, nome):
        self.nome = nome
        self.historico = []

class Usuario:
    def __init__(self, nome, senha, perfil):
        self.nome = nome
        self.senha = senha
        self.perfil = perfil  # "gerente" ou "caixa"

# ================= INICIALIZAÇÃO =================
if "produtos" not in st.session_state:
    st.session_state["produtos"] = []
if "funcionarios" not in st.session_state:
    st.session_state["funcionarios"] = []
if "clientes" not in st.session_state:
    st.session_state["clientes"] = []
if "vendas" not in st.session_state:
    st.session_state["vendas"] = []
if "usuarios" not in st.session_state:
    st.session_state["usuarios"] = [Usuario("admin","admin","gerente")]
if "usuario_logado" not in st.session_state:
    st.session_state["usuario_logado"] = None
if "tela" not in st.session_state:
    st.session_state["tela"] = "login"

# ================= FUNÇÕES USUÁRIOS =================
def cadastrar_usuario(nome, senha, perfil):
    for u in st.session_state["usuarios"]:
        if u.nome.lower() == nome.lower():
            st.warning("Usuário já existe.")
            return
    st.session_state["usuarios"].append(Usuario(nome, senha, perfil))
    st.success("Usuário cadastrado com sucesso!")

def autenticar_usuario(nome, senha):
    for u in st.session_state["usuarios"]:
        if u.nome.lower() == nome.lower() and u.senha == senha:
            return u
    return None

# ================= FUNÇÕES NEGÓCIO =================
def registrar_venda(produto, quantidade, funcionario, cliente=None, tipo="pago"):
    if quantidade > produto.quantidade:
        st.error("Estoque insuficiente!")
        return

    total = produto.preco * quantidade
    produto.quantidade -= quantidade

    venda = {
        "Produto": produto.nome,
        "Qtd": quantidade,
        "Total": total,
        "Data/Hora": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "Funcionário": funcionario,
        "Tipo": tipo
    }
    st.session_state["vendas"].append(venda)

    if cliente:
        cliente.historico.append([
            produto.nome, quantidade, total,
            datetime.now().strftime("%d/%m/%Y %H:%M"),
            funcionario, tipo
        ])

    st.success("Venda registrada com sucesso!")

    if produto.quantidade < 5:
        st.warning(f"⚠️ Estoque baixo para {produto.nome}: {produto.quantidade} unidades restantes!")

# ================= TELAS =================
def tela_login():
    st.title("🔐 Login do Sistema")
    nome = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        user = autenticar_usuario(nome, senha)
        if user:
            st.session_state["usuario_logado"] = user
            st.session_state["tela"] = "sistema"
            st.experimental_rerun()
        else:
            st.error("Usuário ou senha incorretos")

    st.markdown("---")
    if st.button("Cadastrar Novo Usuário"):
        st.session_state["tela"] = "cadastro"
        st.experimental_rerun()

def tela_cadastro():
    st.title("📝 Cadastro de Usuários")
    nome_c = st.text_input("Novo Usuário")
    senha_c = st.text_input("Senha", type="password")
    perfil = st.selectbox("Perfil", ["gerente","caixa"])

    if st.button("Cadastrar Usuário"):
        cadastrar_usuario(nome_c, senha_c, perfil)

    if st.button("Voltar para Login"):
        st.session_state["tela"] = "login"
        st.experimental_rerun()

def tela_funcional():
    user = st.session_state["usuario_logado"]

    st.sidebar.title(f"👤 {user.nome} ({user.perfil})")
    if st.sidebar.button("🔒 Logoff"):
        st.session_state["usuario_logado"] = None
        st.session_state["tela"] = "login"
        st.experimental_rerun()

    # Menus diferentes para gerente e caixa
    if user.perfil == "gerente":
        tela = st.sidebar.selectbox("Menu",["Dashboard","Funcionários","Caixa","Relatórios"])
    else:  # caixa
        tela = st.sidebar.selectbox("Menu",["Vendas","Estoque","Clientes"])

    # ========== Dashboard (apenas gerente) ==========
    if tela=="Dashboard" and user.perfil=="gerente":
        st.header("📊 Dashboard")
        if st.session_state["vendas"]:
            df = pd.DataFrame(st.session_state["vendas"])
            st.dataframe(df)
        else:
            st.info("Nenhuma venda registrada.")

    # ========== Funcionários ==========
    elif tela=="Funcionários" and user.perfil=="gerente":
        st.header("👨‍🍳 Funcionários")
        nome = st.text_input("Nome do Funcionário")
        if st.button("Cadastrar Funcionário"):
            st.session_state["funcionarios"].append(Funcionario(nome))
            st.success("Funcionário cadastrado.")
        if st.session_state["funcionarios"]:
            st.dataframe(pd.DataFrame([{"Nome":f.nome} for f in st.session_state["funcionarios"]]))

    # ========== Caixa ==========
    elif tela=="Caixa" and user.perfil=="gerente":
        st.header("💰 Caixa")
        if st.session_state["vendas"]:
            df = pd.DataFrame(st.session_state["vendas"])
            st.dataframe(df)
        else:
            st.info("Nenhuma venda registrada.")

    # ========== Relatórios ==========
    elif tela=="Relatórios" and user.perfil=="gerente":
        st.header("📈 Relatórios")
        if st.session_state["vendas"]:
            df = pd.DataFrame(st.session_state["vendas"])
            st.dataframe(df)
        else:
            st.info("Nenhuma venda registrada.")

    # ========== Vendas ==========
    elif tela=="Vendas" and user.perfil=="caixa":
        st.header("🛒 Registrar Venda")
        if not st.session_state["produtos"]:
            st.warning("Nenhum produto cadastrado.")
            return
        if not st.session_state["funcionarios"]:
            st.warning("Nenhum funcionário cadastrado.")
            return

        prod = st.selectbox("Produto", [p.nome for p in st.session_state["produtos"]])
        produto = next(p for p in st.session_state["produtos"] if p.nome==prod)
        qtd = st.number_input("Quantidade", min_value=1, step=1)
        func = st.selectbox("Funcionário", [f.nome for f in st.session_state["funcionarios"]])
        nome_cliente = st.text_input("Nome do Cliente (opcional)")
        tipo = st.radio("Tipo de venda",["pago","reserva"])

        if st.button("Registrar Venda"):
            cliente = None
            if nome_cliente:
                cliente = next((c for c in st.session_state["clientes"] if c.nome.lower()==nome_cliente.lower()), None)
                if not cliente:
                    cliente = Cliente(nome_cliente)
                    st.session_state["clientes"].append(cliente)
            registrar_venda(produto,qtd,func,cliente,tipo)

    # ========== Estoque ==========
    elif tela=="Estoque" and user.perfil=="caixa":
        st.header("📦 Controle de Estoque")
        nome = st.text_input("Nome do Produto")
        preco = st.number_input("Preço", min_value=0.0, step=0.01)
        qtd = st.number_input("Quantidade", min_value=0, step=1)
        if st.button("Cadastrar Produto"):
            existente = next((p for p in st.session_state["produtos"] if p.nome.lower()==nome.lower()), None)
            if existente:
                existente.quantidade += qtd
                existente.preco = preco
                st.success("Produto atualizado no estoque.")
            else:
                st.session_state["produtos"].append(Produto(nome,preco,qtd))
                st.success("Produto adicionado ao estoque.")

        if st.session_state["produtos"]:
            dados = [{"Produto":p.nome,"Preço":p.preco,"Qtd":p.quantidade} for p in st.session_state["produtos"]]
            st.dataframe(pd.DataFrame(dados))

    # ========== Clientes ==========
    elif tela=="Clientes" and user.perfil=="caixa":
        st.header("📖 Histórico de Clientes")
        if st.session_state["clientes"]:
            cliente_sel = st.selectbox("Selecione o Cliente", [c.nome for c in st.session_state["clientes"]])
            cliente = next(c for c in st.session_state["clientes"] if c.nome==cliente_sel)
            if cliente.historico:
                df = pd.DataFrame(cliente.historico,columns=["Produto","Qtd","Total","Data/Hora","Funcionário","Tipo"])
                st.dataframe(df)
            else:
                st.info("Sem histórico.")
        else:
            st.info("Nenhum cliente cadastrado.")

# ================= MAIN =================
def main():
    if st.session_state["tela"] == "login":
        tela_login()
    elif st.session_state["tela"] == "cadastro":
        tela_cadastro()
    elif st.session_state["tela"] == "sistema":
        tela_funcional()

if __name__ == "__main__":
    main()
