import streamlit as st
import pandas as pd
from datetime import datetime

# ==================== MODELOS ====================
class Usuario:
    def __init__(self, nome, senha, perfil):
        self.nome = nome
        self.senha = senha
        self.perfil = perfil  # "Gerente" ou "Caixa"

class Produto:
    def __init__(self, nome, quantidade):
        self.nome = nome
        self.quantidade = quantidade

class Venda:
    def __init__(self, produto, quantidade, funcionario, tipo):
        self.produto = produto
        self.quantidade = quantidade
        self.hora = datetime.now().strftime("%H:%M:%S")
        self.data = datetime.now().date()
        self.funcionario = funcionario
        self.tipo = tipo  # "Pago" ou "Reserva"

# ==================== DADOS GLOBAIS ====================
if "usuarios" not in st.session_state:
    st.session_state["usuarios"] = [Usuario("admin", "admin", "Gerente")]

if "usuario_logado" not in st.session_state:
    st.session_state["usuario_logado"] = None

if "produtos" not in st.session_state:
    st.session_state["produtos"] = []

if "vendas" not in st.session_state:
    st.session_state["vendas"] = []

# ==================== FUNÇÕES USUÁRIOS ====================
def cadastrar_usuario(nome, senha, perfil):
    for u in st.session_state["usuarios"]:
        if u.nome.lower() == nome.lower():
            return False
    st.session_state["usuarios"].append(Usuario(nome, senha, perfil))
    return True

def autenticar_usuario(nome, senha):
    for u in st.session_state["usuarios"]:
        if u.nome.lower() == nome.lower() and u.senha == senha:
            return u
    return None

# ==================== TELAS ====================
def tela_login():
    st.title("🔑 Login do Sistema")

    nome = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        user = autenticar_usuario(nome, senha)
        if user:
            st.session_state["usuario_logado"] = user
            st.rerun()
        else:
            st.error("Usuário ou senha incorretos")

    st.markdown("---")
    st.subheader("Cadastrar Novo Usuário")
    nome_c = st.text_input("Novo Usuário", key="nome_cadastro")
    senha_c = st.text_input("Nova Senha", type="password", key="senha_cadastro")
    perfil = st.selectbox("Perfil", ["Gerente", "Caixa"], key="perfil_cadastro")
    if st.button("Cadastrar"):
        if nome_c and senha_c:
            if cadastrar_usuario(nome_c, senha_c, perfil):
                st.success("Usuário cadastrado com sucesso!")
            else:
                st.error("Usuário já existe!")
        else:
            st.warning("Preencha todos os campos.")

def tela_dashboard():
    st.title("📊 Dashboard - Visão do Gerente")
    total_produtos = sum([p.quantidade for p in st.session_state["produtos"]])
    total_vendas = len(st.session_state["vendas"])
    st.metric("Produtos em Estoque", total_produtos)
    st.metric("Total de Vendas", total_vendas)

    st.subheader("Produtos com Estoque Baixo (≤5)")
    baixos = [p for p in st.session_state["produtos"] if p.quantidade <= 5]
    if baixos:
        df = pd.DataFrame([(p.nome, p.quantidade) for p in baixos], columns=["Produto", "Quantidade"])
        st.table(df)
    else:
        st.success("Nenhum produto com estoque crítico.")

def tela_estoque():
    st.title("📦 Controle de Estoque")
    nome = st.text_input("Produto")
    qtd = st.number_input("Quantidade", min_value=1, step=1)
    if st.button("Cadastrar Produto"):
        if nome and qtd:
            for p in st.session_state["produtos"]:
                if p.nome.lower() == nome.lower():
                    p.quantidade += qtd
                    st.success(f"Quantidade atualizada! Estoque de {p.nome}: {p.quantidade}")
                    st.rerun()
            st.session_state["produtos"].append(Produto(nome, qtd))
            st.success(f"Produto {nome} cadastrado com {qtd} unidades.")

    st.subheader("📋 Produtos em Estoque")
    if st.session_state["produtos"]:
        df = pd.DataFrame([(p.nome, p.quantidade) for p in st.session_state["produtos"]],
                          columns=["Produto", "Quantidade"])
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Nenhum produto cadastrado.")

def tela_vendas():
    st.title("🛒 Registrar Venda")
    if not st.session_state["produtos"]:
        st.warning("Cadastre produtos antes de vender.")
        return

    produtos = [p.nome for p in st.session_state["produtos"]]
    produto = st.selectbox("Produto", produtos)
    qtd = st.number_input("Quantidade", min_value=1, step=1)
    tipo = st.radio("Tipo", ["Pago", "Reserva"])

    if st.button("Registrar Venda"):
        prod = next((p for p in st.session_state["produtos"] if p.nome == produto), None)
        if prod:
            if qtd > prod.quantidade:
                st.error("Quantidade insuficiente em estoque!")
            else:
                prod.quantidade -= qtd
                v = Venda(produto, qtd, st.session_state["usuario_logado"].nome, tipo)
                st.session_state["vendas"].append(v)
                st.success(f"Venda registrada: {qtd}x {produto} ({tipo})")

    st.subheader("📑 Histórico de Vendas")
    if st.session_state["vendas"]:
        df = pd.DataFrame(
            [(v.produto, v.quantidade, v.hora, v.funcionario, v.tipo) for v in st.session_state["vendas"]],
            columns=["Produto", "Qtd", "Hora", "Funcionário", "Tipo"]
        )
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Nenhuma venda registrada.")

# ==================== MAIN ====================
def main():
    if not st.session_state["usuario_logado"]:
        tela_login()
        return

    user = st.session_state["usuario_logado"]

    st.sidebar.title(f"Bem-vindo, {user.nome} 👋")
    if st.sidebar.button("🚪 Logoff"):
        st.session_state["usuario_logado"] = None
        st.rerun()

    if user.perfil == "Gerente":
        menu = st.sidebar.radio("Menu", ["Dashboard", "Estoque", "Vendas"])
        if menu == "Dashboard":
            tela_dashboard()
        elif menu == "Estoque":
            tela_estoque()
        elif menu == "Vendas":
            tela_vendas()

    elif user.perfil == "Caixa":
        menu = st.sidebar.radio("Menu", ["Vendas", "Estoque"])
        if menu == "Vendas":
            tela_vendas()
        elif menu == "Estoque":
            tela_estoque()

if __name__ == "__main__":
    main()
