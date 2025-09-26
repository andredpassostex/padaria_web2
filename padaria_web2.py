# padaria_web.py
import streamlit as st
import pandas as pd
from datetime import datetime
import io

# --- Inicialização dos dados ---
if 'produtos' not in st.session_state:
    st.session_state['produtos'] = []  # [codigo, nome, qtd, preco]

if 'funcionarios' not in st.session_state:
    st.session_state['funcionarios'] = []

if 'vendas' not in st.session_state:
    st.session_state['vendas'] = []

if 'caixa_total' not in st.session_state:
    st.session_state['caixa_total'] = 0.0

if 'contador_produtos' not in st.session_state:
    st.session_state['contador_produtos'] = 0

# --- Funções ---
def cadastrar_produto(nome, qtd, preco):
    # Normaliza nome
    nome = nome.strip().title()

    # Verifica se já existe
    produto_existente = next(
        (p for p in st.session_state['produtos'] if p[1].lower() == nome.lower()),
        None
    )
    if produto_existente:
        produto_existente[2] += qtd
        produto_existente[3] = preco
        st.success(f"Produto {nome} atualizado: estoque +{qtd}.")
    else:
        st.session_state['contador_produtos'] += 1
        codigo = str(st.session_state['contador_produtos']).zfill(3)
        st.session_state['produtos'].append([codigo, nome, qtd, preco])
        st.success(f"Produto {nome} cadastrado com sucesso!")

def cadastrar_funcionario(nome):
    if nome.lower() in [f.lower() for f in st.session_state['funcionarios']]:
        st.warning(f"Funcionário {nome} já cadastrado!")
    else:
        st.session_state['funcionarios'].append(nome)
        st.success(f"Funcionário {nome} cadastrado com sucesso!")

def registrar_venda(produto_nome, funcionario, venda_qtd):
    produto = next((p for p in st.session_state['produtos'] if p[1].lower() == produto_nome.lower()), None)
    if produto is None:
        st.error("Produto não encontrado!")
        return
    if venda_qtd > produto[2]:
        st.error("Quantidade insuficiente no estoque!")
        return

    produto[2] -= venda_qtd
    valor_venda = venda_qtd * produto[3]
    st.session_state['caixa_total'] += valor_venda
    data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state['vendas'].append([produto[1], venda_qtd, produto[3], funcionario, data_hora])

    st.success(f"Venda de {venda_qtd}x {produto[1]} registrada por {funcionario}!")

    if produto[2] <= 5:
        st.warning(f"⚠ Restam apenas {produto[2]} itens de {produto[1]} em estoque!")

def gerar_relatorio(periodo="diario"):
    if not st.session_state['vendas']:
        st.warning("Nenhuma venda registrada ainda!")
        return

    df = pd.DataFrame(st.session_state['vendas'], columns=["Produto", "Quantidade", "Preço Unitário", "Funcionário", "Data/Hora"])
    df["Data/Hora"] = pd.to_datetime(df["Data/Hora"])
    hoje = datetime.now()

    if periodo == "diario":
        df_periodo = df[df["Data/Hora"].dt.date == hoje.date()]
    elif periodo == "semanal":
        inicio_semana = hoje - pd.Timedelta(days=hoje.weekday())
        df_periodo = df[(df["Data/Hora"].dt.date >= inicio_semana.date()) & (df["Data/Hora"].dt.date <= hoje.date())]
    else:
        st.error("Período inválido!")
        return

    if df_periodo.empty:
        st.info(f"Nenhuma venda registrada no período {periodo}.")
        return

    output = io.BytesIO()
    df_periodo.to_excel(output, index=False)
    output.seek(0)

    st.download_button(
        label=f"Baixar relatório {periodo}",
        data=output,
        file_name=f"relatorio_{periodo}_{hoje.strftime('%Y%m%d')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

def zerar_estoque():
    for p in st.session_state['produtos']:
        p[2] = 0
    st.success("✅ Estoque zerado com sucesso!")

def remover_produto(codigo):
    st.session_state['produtos'] = [p for p in st.session_state['produtos'] if p[0] != codigo]
    st.success("🗑 Produto removido com sucesso!")

# --- Interface ---
st.title("Lucio Pães")

menu = st.sidebar.radio("Menu", ["Funcionários", "Estoque", "Venda", "Caixa"])

# Funcionários
if menu == "Funcionários":
    st.subheader("Cadastro de Funcionários")
    nome = st.text_input("Nome do funcionário")
    if st.button("Cadastrar Funcionário"):
        cadastrar_funcionario(nome)

    st.subheader("Lista de Funcionários")
    for f in st.session_state['funcionarios']:
        st.write(f)

# Estoque
elif menu == "Estoque":
    st.subheader("Produtos Cadastrados")

    if st.session_state['produtos']:
        df_estoque = pd.DataFrame(
            st.session_state['produtos'],
            columns=["Código", "Produto", "Quantidade", "Preço Unitário"],
        )
        st.table(df_estoque)
    else:
        st.info("Nenhum produto cadastrado.")

    st.subheader("Cadastrar Produto")
    nome = st.text_input("Nome do produto")
    qtd = st.number_input("Quantidade inicial", min_value=1, step=1)
    preco = st.number_input("Preço unitário", min_value=0.01, step=0.01)
    if st.button("Cadastrar Produto"):
        cadastrar_produto(nome, qtd, preco)

    st.subheader("Gerenciar Estoque")
    if st.button("Zerar Estoque"):
        zerar_estoque()

    if st.session_state['produtos']:
        codigos = [p[0] + " - " + p[1] for p in st.session_state['produtos']]
        escolha = st.selectbox("Escolha um produto para remover", codigos)
        if st.button("Remover Produto"):
            remover_produto(escolha.split(" - ")[0])

# Venda
elif menu == "Venda":
    st.subheader("Registrar Venda")
    if not st.session_state['produtos'] or not st.session_state['funcionarios']:
        st.info("Cadastre produtos e funcionários antes de registrar vendas.")
    else:
        produto_digitado = st.text_input("Digite o nome do produto")
        sugestoes = [p[1] for p in st.session_state['produtos'] if produto_digitado.lower() in p[1].lower()] if produto_digitado else []
        prod_nome = st.selectbox("Sugestões de produtos", sugestoes) if sugestoes else None

        func_nome = st.selectbox("Funcionário", st.session_state['funcionarios'])
        qtd_venda = st.number_input("Quantidade", min_value=1, step=1)

        if st.button("Registrar Venda"):
            if prod_nome:
                registrar_venda(prod_nome, func_nome, qtd_venda)
            else:
                st.error("Digite e selecione um produto válido!")

# Caixa
elif menu == "Caixa":
    st.subheader("Relatório de Vendas do Dia")

    if st.session_state['vendas']:
      df_vendas = pd.DataFrame(
    st.session_state['vendas'],
    columns=["Produto", "Quantidade", "Preço Unitário", "Funcionário", "Data/Hora"],
)

# Converte "Data/Hora" de string para datetime
df_vendas["Data/Hora"] = pd.to_datetime(df_vendas["Data/Hora"], errors="coerce")

# Calcula o total por venda
df_vendas["Total"] = df_vendas["Quantidade"] * df_vendas["Preço Unitário"]

hoje = datetime.now().date()
df_vendas_dia = df_vendas[df_vendas["Data/Hora"].dt.date == hoje]


        if not df_vendas_dia.empty:
            st.table(df_vendas_dia[["Produto", "Quantidade", "Preço Unitário", "Total"]])

            total_dia = df_vendas_dia["Total"].sum()
            st.markdown("### TOTAL DO DIA")
            st.table(pd.DataFrame([["", "", "", total_dia]], columns=["Produto", "Quantidade", "Preço Unitário", "Total"]))
        else:
            st.info("Nenhuma venda registrada hoje.")
    else:
        st.info("Nenhuma venda registrada.")

    st.subheader("Gerar Relatórios")
    if st.button("Relatório Diário"):
        gerar_relatorio("diario")
    if st.button("Relatório Semanal"):
        gerar_relatorio("semanal")

