# padaria_web.py
import streamlit as st
import pandas as pd
from datetime import datetime
from PIL import Image

# --- Inicialização ---
if "produtos" not in st.session_state:
    st.session_state["produtos"] = []

if "funcionarios" not in st.session_state:
    st.session_state["funcionarios"] = []

if "vendas" not in st.session_state:
    st.session_state["vendas"] = []

if "caixa_total" not in st.session_state:
    st.session_state["caixa_total"] = 0.0

if "codigo_produto" not in st.session_state:
    st.session_state["codigo_produto"] = 1


# --- Funções ---
def box_title(texto, icone="📌"):
    st.markdown(
        f"""
        <div style='padding: 10px; background-color: #f9f9f9; 
                    border-radius: 10px; box-shadow: 2px 2px 10px rgba(0,0,0,0.2); 
                    margin-bottom: 15px;'>
            <h3 style='text-align: center; color: #333;'>{icone} {texto}</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )


def cadastrar_produto(nome, qtd, preco):
    produto_existente = next(
        (p for p in st.session_state["produtos"] if p[1].lower() == nome.lower()), None
    )
    if produto_existente:
        produto_existente[2] += qtd
        produto_existente[3] = preco
        st.success(f"Produto {nome} atualizado: estoque +{qtd} unidades.")
    else:
        codigo = str(st.session_state["codigo_produto"]).zfill(3)
        st.session_state["produtos"].append([codigo, nome, qtd, preco])
        st.session_state["codigo_produto"] += 1
        st.success(f"Produto {nome} cadastrado com sucesso!")


def cadastrar_funcionario(nome):
    if nome.lower() in [f.lower() for f in st.session_state["funcionarios"]]:
        st.warning(f"Funcionário {nome} já cadastrado!")
    else:
        st.session_state["funcionarios"].append(nome)
        st.success(f"Funcionário {nome} cadastrado com sucesso!")


def registrar_venda(produto_nome, funcionario, venda_qtd):
    produto = next(
        (p for p in st.session_state["produtos"] if p[1].lower() == produto_nome.lower()),
        None,
    )
    if produto is None:
        st.error("Produto não encontrado!")
        return
    if venda_qtd > produto[2]:
        st.error("Quantidade insuficiente no estoque!")
        return

    produto[2] -= venda_qtd
    valor_venda = venda_qtd * produto[3]
    st.session_state["caixa_total"] += valor_venda
    data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    st.session_state["vendas"].append(
        [produto[0], produto[1], venda_qtd, produto[3], valor_venda, funcionario, data_hora]
    )

    st.success(f"Venda de {venda_qtd}x {produto[1]} registrada por {funcionario}!")

    if produto[2] <= 5:
        st.warning(f"⚠ Restam apenas {produto[2]} itens de {produto[1]} em estoque!")


# --- Interface ---
# Banner com logo
logo = Image.open("logo.png")
st.image(logo, use_column_width=False, width=250)

st.markdown(
    """
    <h2 style='text-align: center; color: #4B2E2E;'>
        Sistema de Padaria
    </h2>
    """,
    unsafe_allow_html=True
)

st.sidebar.header("📌 Menu")
menu = ["Funcionários", "Estoque", "Venda", "Caixa"]
choice = st.sidebar.radio("Navegação", menu)

# --- Funcionários ---
if choice == "Funcionários":
    box_title("Funcionários Cadastrados", "👨‍🍳")

    if st.session_state["funcionarios"]:
        for f in st.session_state["funcionarios"]:
            st.write(f)
    else:
        st.info("Nenhum funcionário cadastrado.")

    box_title("Cadastrar Funcionário", "➕")
    nome = st.text_input("Nome do funcionário")
    if st.button("Cadastrar Funcionário"):
        cadastrar_funcionario(nome)

# --- Estoque ---
elif choice == "Estoque":
    box_title("Produtos Cadastrados", "📦")

    if st.session_state["produtos"]:
        df_estoque = pd.DataFrame(
            st.session_state["produtos"],
            columns=["Código", "Produto", "Quantidade", "Preço Unitário"],
        )
        st.table(df_estoque)
    else:
        st.info("Nenhum produto cadastrado.")

    box_title("Cadastrar Produto", "➕")
    nome = st.text_input("Nome do produto")
    qtd = st.number_input("Quantidade inicial", min_value=1, step=1)
    preco = st.number_input("Preço unitário", min_value=0.01, step=0.01)
    if st.button("Cadastrar Produto"):
        cadastrar_produto(nome, qtd, preco)

    box_title("Gerenciar Estoque", "⚙️")
    if st.button("Zerar Estoque"):
        for p in st.session_state["produtos"]:
            p[2] = 0
        st.success("Estoque zerado com sucesso!")

    produto_remover = st.selectbox(
        "Selecione um produto para remover", [""] + [p[1] for p in st.session_state["produtos"]]
    )
    if st.button("Remover Produto"):
        if produto_remover:
            st.session_state["produtos"] = [
                p for p in st.session_state["produtos"] if p[1] != produto_remover
            ]
            st.success(f"Produto {produto_remover} removido do estoque.")

# --- Venda ---
elif choice == "Venda":
    box_title("Registrar Venda", "💰")

    if not st.session_state["produtos"] or not st.session_state["funcionarios"]:
        st.info("Cadastre produtos e funcionários antes de registrar vendas.")
    else:
        prod_nome = st.selectbox(
            "Produto",
            [p[1] for p in st.session_state["produtos"]],
            index=None,
            placeholder="Digite para buscar...",
        )
        func_nome = st.selectbox("Funcionário", st.session_state["funcionarios"])
        qtd_venda = st.number_input("Quantidade", min_value=1, step=1)
        if st.button("Registrar Venda"):
            if prod_nome and func_nome:
                registrar_venda(prod_nome, func_nome, qtd_venda)

# --- Caixa ---
elif choice == "Caixa":
    box_title("Relatório de Vendas do Dia", "📊")

    if st.session_state["vendas"]:
        df_vendas = pd.DataFrame(
            st.session_state["vendas"],
            columns=["Código", "Item", "Quantidade", "Valor Unitário", "Total", "Funcionário", "Data/Hora"],
        )

        df_vendas["Data/Hora"] = pd.to_datetime(df_vendas["Data/Hora"])
        hoje = datetime.now().date()
        df_vendas_dia = df_vendas[df_vendas["Data/Hora"].dt.date == hoje]

        if not df_vendas_dia.empty:
            st.table(df_vendas_dia[["Item", "Quantidade", "Valor Unitário", "Total"]])

            total_dia = df_vendas_dia[["Quantidade", "Valor Unitário", "Total"]].sum(numeric_only=True)
            total_df = pd.DataFrame(
                [["TOTAL DO DIA", total_dia["Quantidade"], total_dia["Valor Unitário"], total_dia["Total"]]],
                columns=["Item", "Quantidade", "Valor Unitário", "Total"],
            )
            st.table(total_df)
        else:
            st.info("Nenhuma venda registrada hoje.")
    else:
        st.info("Nenhuma venda registrada ainda.")
