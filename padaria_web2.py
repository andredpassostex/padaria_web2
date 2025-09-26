# padaria_web.py
import streamlit as st
import pandas as pd
from datetime import datetime
import io

# --- Dados ---
if 'produtos' not in st.session_state:
    st.session_state['produtos'] = []

if 'funcionarios' not in st.session_state:
    st.session_state['funcionarios'] = []

if 'vendas' not in st.session_state:
    st.session_state['vendas'] = []

if 'caixa_total' not in st.session_state:
    st.session_state['caixa_total'] = 0.0


# --- Funções ---
def cadastrar_produto(nome, qtd, preco):
    # Verifica se o produto já existe (case-insensitive)
    produto_existente = next((p for p in st.session_state['produtos']
                              if p[0].lower() == nome.lower()), None)
    if produto_existente:
        produto_existente[1] += qtd
        produto_existente[2] = preco
        st.success(f"Produto {nome} atualizado: estoque +{qtd} unidades.")
    else:
        st.session_state['produtos'].append([nome, qtd, preco])
        st.success(f"Produto {nome} cadastrado com sucesso!")


def cadastrar_funcionario(nome):
    if nome.lower() in [f.lower() for f in st.session_state['funcionarios']]:
        st.warning(f"Funcionário {nome} já cadastrado!")
    else:
        st.session_state['funcionarios'].append(nome)
        st.success(f"Funcionário {nome} cadastrado com sucesso!")


def registrar_venda(produto_nome, funcionario, venda_qtd):
    produto = next((p for p in st.session_state['produtos']
                    if p[0].lower() == produto_nome.lower()), None)
    if produto is None:
        st.error("Produto não encontrado!")
        return
    if venda_qtd > produto[1]:
        st.error("Quantidade insuficiente no estoque!")
        return

    produto[1] -= venda_qtd
    valor_venda = venda_qtd * produto[2]
    st.session_state['caixa_total'] += valor_venda
    data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    st.session_state['vendas'].append(
        [produto[0], venda_qtd, produto[2], funcionario, data_hora]
    )

    st.success(f"Venda de {venda_qtd}x {produto[0]} registrada por {funcionario}!")
    if produto[1] <= 5:
        st.warning(f"⚠ Restam apenas {produto[1]} itens de {produto[0]} em estoque!")


def gerar_relatorio(periodo="diario"):
    if not st.session_state['vendas']:
        st.warning("Nenhuma venda registrada ainda!")
        return

    df = pd.DataFrame(
        st.session_state['vendas'],
        columns=["Produto", "Quantidade", "Preço Unitário", "Funcionário", "Data/Hora"]
    )
    df["Data/Hora"] = pd.to_datetime(df["Data/Hora"])
    hoje = datetime.now()

    if periodo == "diario":
        df_periodo = df[df["Data/Hora"].dt.date == hoje.date()]
    elif periodo == "semanal":
        inicio_semana = hoje - pd.Timedelta(days=hoje.weekday())
        df_periodo = df[(df["Data/Hora"].dt.date >= inicio_semana.date()) &
                        (df["Data/Hora"].dt.date <= hoje.date())]
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


# --- Interface ---
st.title("Lucio Pães")

menu = st.sidebar.radio("Menu", ["Funcionários", "Estoque", "Venda", "Caixa"])

# Funcionários
if menu == "Funcionários":
    st.subheader("Cadastro de Funcionário")
    nome = st.text_input("Nome do funcionário")
    if st.button("Cadastrar Funcionário"):
        cadastrar_funcionario(nome)

    st.subheader("Funcionários Cadastrados")
    if st.session_state['funcionarios']:
        for f in st.session_state['funcionarios']:
            st.write(f)
    else:
        st.info("Nenhum funcionário cadastrado.")

# Estoque
elif menu == "Estoque":
    st.subheader("Cadastro de Produto")
    nome = st.text_input("Nome do produto")
    qtd = st.number_input("Quantidade inicial", min_value=1, step=1)
    preco = st.number_input("Preço unitário", min_value=0.01, step=0.01)
    if st.button("Cadastrar Produto"):
        cadastrar_produto(nome, qtd, preco)

    st.subheader("Produtos em Estoque")
    if st.session_state['produtos']:
        for p in st.session_state['produtos']:
            st.write(f"{p[0]} - Estoque: {p[1]} - R${p[2]:.2f}")
    else:
        st.info("Nenhum produto cadastrado.")

# Venda
elif menu == "Venda":
    st.subheader("Registrar Venda")
    if not st.session_state['produtos'] or not st.session_state['funcionarios']:
        st.info("Cadastre produtos e funcionários antes de registrar vendas.")
    else:
        # Campo de texto com sugestão dinâmica
        produto_digitado = st.text_input("Digite o nome do produto")

        sugestoes = [p[0] for p in st.session_state['produtos'] 
                     if produto_digitado.lower() in p[0].lower()] if produto_digitado else []

        if sugestoes:
            prod_nome = st.selectbox("Sugestões de produtos", sugestoes)
        else:
            prod_nome = None

        func_nome = st.selectbox("Funcionário", st.session_state['funcionarios'])
        qtd_venda = st.number_input("Quantidade", min_value=1, step=1)

        if st.button("Registrar Venda"):
            if prod_nome:
                registrar_venda(prod_nome, func_nome, qtd_venda)
            else:
                st.error("Digite e selecione um produto válido!")

# Caixa
elif menu == "Caixa":
    st.subheader("Caixa Total")
    st.write(f"R${st.session_state['caixa_total']:.2f}")

    st.subheader("Gerar Relatórios")
    if st.button("Relatório Diário"):
        gerar_relatorio("diario")
    if st.button("Relatório Semanal"):
        gerar_relatorio("semanal")

