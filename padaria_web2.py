# Salve como padaria_web.py e rode com: streamlit run padaria_web.py
import streamlit as st
import pandas as pd
from datetime import datetime

# --- Dados ---
if 'produtos' not in st.session_state:
    st.session_state.produtos = []

if 'funcionarios' not in st.session_state:
    st.session_state.funcionarios = []

if 'vendas' not in st.session_state:
    st.session_state.vendas = []

if 'caixa_total' not in st.session_state:
    st.session_state.caixa_total = 0.0

# --- Funções ---
def cadastrar_produto(nome, qtd, preco):
    st.session_state.produtos.append([nome, qtd, preco])
    st.success(f"Produto {nome} cadastrado com sucesso!")

def cadastrar_funcionario(nome):
    st.session_state.funcionarios.append(nome)
    st.success(f"Funcionário {nome} cadastrado com sucesso!")

def registrar_venda(produto_nome, funcionario, venda_qtd):
    produto = next((p for p in st.session_state.produtos if p[0]==produto_nome), None)
    if produto is None:
        st.error("Produto não encontrado!")
        return
    if venda_qtd > produto[1]:
        st.error("Quantidade insuficiente no estoque!")
        return
    produto[1] -= venda_qtd
    valor_venda = venda_qtd * produto[2]
    st.session_state.caixa_total += valor_venda
    data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.vendas.append([produto[0], venda_qtd, produto[2], funcionario, data_hora])
    st.success(f"Venda de {venda_qtd}x {produto[0]} registrada por {funcionario}!")
    if produto[1] <= 5:
        st.warning(f"⚠ Restam apenas {produto[1]} itens de {produto[0]} em estoque!")

def gerar_relatorio(periodo="diario"):
    if not st.session_state.vendas:
        st.warning("Nenhuma venda registrada ainda!")
        return
    df = pd.DataFrame(st.session_state.vendas, columns=["Produto", "Quantidade", "Preço Unitário", "Funcionário", "Data/Hora"])
    df["Data/Hora"] = pd.to_datetime(df["Data/Hora"])
    hoje = datetime.now()
    if periodo=="diario":
        df_periodo = df[df["Data/Hora"].dt.date==hoje.date()]
        nome_arquivo = f"relatorio_diario_{hoje.strftime('%Y%m%d')}.xlsx"
    elif periodo=="semanal":
        inicio_semana = hoje - pd.Timedelta(days=hoje.weekday())
        df_periodo = df[(df["Data/Hora"].dt.date>=inicio_semana.date()) & (df["Data/Hora"].dt.date<=hoje.date())]
        nome_arquivo = f"relatorio_semanal_{hoje.strftime('%Y%m%d')}.xlsx"
    else:
        st.error("Período inválido!")
        return
    if df_periodo.empty:
        st.info(f"Nenhuma venda registrada no período {periodo}.")
        return
    df_periodo.to_excel(nome_arquivo, index=False)
    st.success(f"Relatório {periodo} gerado: {nome_arquivo}")

# --- Interface ---
st.title("Sistema Padaria - Web Clean UX")

menu = ["Cadastro Produto", "Cadastro Funcionário", "Registrar Venda", "Relatórios", "Estoque e Caixa"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Cadastro Produto":
    st.subheader("Cadastrar Produto")
    nome = st.text_input("Nome do produto")
    qtd = st.number_input("Quantidade inicial", min_value=1, step=1)
    preco = st.number_input("Preço unitário", min_value=0.01, step=0.01)
    if st.button("Cadastrar Produto"):
        cadastrar_produto(nome, qtd, preco)

elif choice == "Cadastro Funcionário":
    st.subheader("Cadastrar Funcionário")
    nome = st.text_input("Nome do funcionário")
    if st.button("Cadastrar Funcionário"):
        cadastrar_funcionario(nome)

elif choice == "Registrar Venda":
    st.subheader("Registrar Venda")
    if not st.session_state.produtos or not st.session_state.funcionarios:
        st.info("Cadastre produtos e funcionários antes de registrar vendas.")
    else:
        prod_nome = st.selectbox("Produto", [p[0] for p in st.session_state.produtos])
        func_nome = st.selectbox("Funcionário", st.session_state.funcionarios)
        qtd_venda = st.number_input("Quantidade", min_value=1, step=1)
        if st.button("Registrar Venda"):
            registrar_venda(prod_nome, func_nome, qtd_venda)

elif choice == "Relatórios":
    st.subheader("Gerar Relatórios")
    if st.button("Relatório Diário"):
        gerar_relatorio("diario")
    if st.button("Relatório Semanal"):
        gerar_relatorio("semanal")

elif choice == "Estoque e Caixa":
    st.subheader("Estoque Atual")
    for nome, qtd, preco in st.session_state.produtos:
        st.write(f"{nome} - Estoque: {qtd} - R${preco:.2f}")
    st.subheader("Caixa Total")
    st.write(f"R${st.session_state.caixa_total:.2f}")
