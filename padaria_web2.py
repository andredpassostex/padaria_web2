# padaria_web.py
import os
import streamlit as st
import pandas as pd
from datetime import datetime
from PIL import Image
import io

# --- Inicialização do estado ---
if "produtos" not in st.session_state:
    st.session_state["produtos"] = []  # [codigo, nome, qtd, preco]

if "funcionarios" not in st.session_state:
    st.session_state["funcionarios"] = []

if "vendas" not in st.session_state:
    st.session_state["vendas"] = []  # [codigo, nome, qtd, preco_unit, total, funcionario, data_hora]

if "caixa_total" not in st.session_state:
    st.session_state["caixa_total"] = 0.0

if "codigo_produto" not in st.session_state:
    st.session_state["codigo_produto"] = 1


# --- Funções utilitárias ---
def box_title(texto, icone="📌"):
    st.markdown(
        f"""
        <div style='padding: 10px; background-color: #f9f9f9;
                    border-radius: 10px; box-shadow: 2px 2px 10px rgba(0,0,0,0.15);
                    margin-bottom: 12px;'>
            <h3 style='text-align: center; color: #4B2E2E; margin:6px 0;'>{icone} {texto}</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )


def cadastrar_produto(nome, qtd, preco):
    nome = nome.strip().title()
    if not nome:
        st.error("Digite o nome do produto.")
        return
    produto_existente = next((p for p in st.session_state["produtos"] if p[1].lower() == nome.lower()), None)
    if produto_existente:
        produto_existente[2] += int(qtd)
        produto_existente[3] = float(preco)
        st.success(f"Produto {nome} atualizado: estoque +{qtd} unidades.")
    else:
        codigo = str(st.session_state["codigo_produto"]).zfill(3)
        st.session_state["produtos"].append([codigo, nome, int(qtd), float(preco)])
        st.session_state["codigo_produto"] += 1
        st.success(f"Produto {codigo} - {nome} cadastrado com sucesso!")


def cadastrar_funcionario(nome):
    nome = nome.strip().title()
    if not nome:
        st.error("Digite o nome do funcionário.")
        return
    if nome.lower() in [f.lower() for f in st.session_state["funcionarios"]]:
        st.warning(f"Funcionário {nome} já cadastrado!")
    else:
        st.session_state["funcionarios"].append(nome)
        st.success(f"Funcionário {nome} cadastrado com sucesso!")


def registrar_venda(produto_nome, funcionario, venda_qtd):
    produto = next((p for p in st.session_state["produtos"] if p[1].lower() == produto_nome.lower()), None)
    if produto is None:
        st.error("Produto não encontrado!")
        return
    venda_qtd = int(venda_qtd)
    if venda_qtd <= 0:
        st.error("Quantidade inválida.")
        return
    if venda_qtd > produto[2]:
        st.error("Quantidade insuficiente no estoque!")
        return

    produto[2] -= venda_qtd
    valor_venda = venda_qtd * produto[3]
    st.session_state["caixa_total"] += valor_venda
    data_hora = datetime.now()  # armazenamos como datetime
    st.session_state["vendas"].append([produto[0], produto[1], venda_qtd, produto[3], valor_venda, funcionario, data_hora])
    st.success(f"Venda de {venda_qtd}x {produto[1]} registrada por {funcionario}!")
    if produto[2] <= 5:
        st.warning(f"⚠ Restam apenas {produto[2]} itens de {produto[1]} em estoque!")


def zerar_estoque():
    for p in st.session_state["produtos"]:
        p[2] = 0
    st.success("✅ Estoque zerado com sucesso!")


def remover_produto(codigo):
    antes = len(st.session_state["produtos"])
    st.session_state["produtos"] = [p for p in st.session_state["produtos"] if p[0] != codigo]
    depois = len(st.session_state["produtos"])
    if depois < antes:
        st.success("🗑 Produto removido com sucesso!")
    else:
        st.warning("Código não encontrado.")


# --- Carregar / Upload da logo com fallback ---
def try_load_logo():
    # caminhos candidatos (tente 'logo.png' na pasta do app)
    candidates = ["logo.png", "./logo.png", "images/logo.png"]
    for c in candidates:
        if os.path.exists(c):
            try:
                return Image.open(c)
            except Exception:
                continue
    return None


logo = try_load_logo()

# Cabeçalho / banner centralizado
if logo is None:
    st.warning("Logo não encontrada (arquivo 'logo.png'). Você pode fazer upload da logo abaixo ou colocar 'logo.png' na pasta do app.")
    uploaded = st.file_uploader("Upload da logo (PNG/JPG) — será salva como logo.png", type=["png", "jpg", "jpeg"])
    if uploaded is not None:
        try:
            logo = Image.open(uploaded)
            # salvar cópia local
            with open("logo.png", "wb") as f:
                f.write(uploaded.getbuffer())
            st.success("Logo salva como 'logo.png'.")
        except Exception as e:
            st.error(f"Erro ao abrir/salvar imagem: {e}")

# exibir (centralizado)
if logo is not None:
    cols = st.columns([1, 2, 1])
    cols[1].image(logo, width=260)
    cols[1].markdown("<h2 style='text-align:center; color:#4B2E2E; margin-top:6px;'>Sistema de Padaria</h2>", unsafe_allow_html=True)
else:
    # fallback textual centralizado
    st.markdown("<h1 style='text-align:center; color:#4B2E2E;'>🥖 Lucio Pães - Sistema de Padaria</h1>", unsafe_allow_html=True)


# --- Menu lateral ---
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
    nome_func = st.text_input("Nome do funcionário", key="input_nome_funcionario")
    if st.button("Cadastrar Funcionário"):
        cadastrar_funcionario(nome_func)


# --- Estoque ---
elif choice == "Estoque":
    box_title("Produtos Cadastrados", "📦")

    # normaliza produtos antigos que pudessem não ter código (compatibilidade)
    normalized = []
    for p in st.session_state["produtos"]:
        if len(p) == 3:  # [nome, qtd, preco]
            codigo = str(st.session_state["codigo_produto"]).zfill(3)
            st.session_state["codigo_produto"] += 1
            normalized.append([codigo, p[0], int(p[1]), float(p[2])])
        else:
            normalized.append([p[0], p[1], int(p[2]), float(p[3])])
    st.session_state["produtos"] = normalized

    if st.session_state["produtos"]:
        df_estoque = pd.DataFrame(st.session_state["produtos"], columns=["Código", "Produto", "Quantidade", "Preço Unitário"])
        st.table(df_estoque)
    else:
        st.info("Nenhum produto cadastrado.")

    box_title("Cadastrar Produto", "➕")
    nome_prod = st.text_input("Nome do produto", key="input_nome_produto")
    qtd_prod = st.number_input("Quantidade inicial", min_value=1, step=1, key="input_qtd_prod")
    preco_prod = st.number_input("Preço unitário", min_value=0.01, step=0.01, format="%.2f", key="input_preco_prod")
    if st.button("Cadastrar Produto"):
        cadastrar_produto(nome_prod, qtd_prod, preco_prod)

    box_title("Gerenciar Estoque", "⚙️")
    if st.button("Zerar Estoque"):
        zerar_estoque()

    if st.session_state["produtos"]:
        codigos = [f"{p[0]} - {p[1]}" for p in st.session_state["produtos"]]
        escolha = st.selectbox("Escolha um produto para remover", [""] + codigos, key="select_remover")
        if st.button("Remover Produto"):
            if escolha:
                codigo_sel = escolha.split(" - ")[0]
                remover_produto(codigo_sel)


# --- Venda ---
elif choice == "Venda":
    box_title("Registrar Venda", "💰")

    if not st.session_state["produtos"] or not st.session_state["funcionarios"]:
        st.info("Cadastre produtos e funcionários antes de registrar vendas.")
    else:
        # listagem clara: mostrar "Código - Nome" na seleção
        produtos_display = [f"{p[0]} - {p[1]}" for p in st.session_state["produtos"]]
        prod_sel = st.selectbox("Produto", produtos_display, key="select_prod_venda")
        # extrai nome por código
        prod_codigo = prod_sel.split(" - ")[0]
        produto_obj = next((p for p in st.session_state["produtos"] if p[0] == prod_codigo), None)
        func_sel = st.selectbox("Funcionário", st.session_state["funcionarios"], key="select_func_venda")
        qtd_venda = st.number_input("Quantidade", min_value=1, step=1, key="input_qtd_venda")
        if st.button("Registrar Venda"):
            if produto_obj and func_sel:
                registrar_venda(produto_obj[1], func_sel, qtd_venda)


# --- Caixa ---
elif choice == "Caixa":
    box_title("Relatório de Vendas do Dia", "📊")

    if st.session_state["vendas"]:
        df_vendas = pd.DataFrame(st.session_state["vendas"], columns=["Código", "Item", "Quantidade", "Valor Unitário", "Total", "Funcionário", "Data/Hora"])
        # garante datetime
        df_vendas["Data/Hora"] = pd.to_datetime(df_vendas["Data/Hora"], errors="coerce")
        df_vendas["Total"] = pd.to_numeric(df_vendas["Total"], errors="coerce")

        hoje = datetime.now().date()
        df_vendas_dia = df_vendas[df_vendas["Data/Hora"].dt.date == hoje]

        if not df_vendas_dia.empty:
            st.table(df_vendas_dia[["Item", "Quantidade", "Valor Unitário", "Total"]])
            total_dia = df_vendas_dia["Total"].sum()
            st.markdown("### TOTAL DO DIA")
            st.table(pd.DataFrame([["", "", "", round(float(total_dia), 2)]], columns=["Item", "Quantidade", "Valor Unitário", "Total"]))
        else:
            st.info("Nenhuma venda registrada hoje.")
    else:
        st.info("Nenhuma venda registrada ainda.")
