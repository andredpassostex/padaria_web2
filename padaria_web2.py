# padaria_web_final.py
import os
import streamlit as st
import pandas as pd
from datetime import datetime
from PIL import Image

# ================= Classes =================
class Produto:
    def __init__(self, codigo, nome, qtd, preco):
        self.codigo = codigo
        self.nome = nome
        self.qtd = qtd
        self.preco = preco

class Funcionario:
    def __init__(self, nome):
        self.nome = nome.title().strip()

class Venda:
    def __init__(self, produto, funcionario, qtd):
        self.codigo = produto.codigo
        self.item = produto.nome
        self.quantidade = qtd
        self.valor_unitario = produto.preco
        self.total = produto.preco * qtd
        self.funcionario = funcionario.nome
        self.data_hora = datetime.now()

# ================= Inicialização do estado =================
if "produtos" not in st.session_state:
    st.session_state["produtos"] = []  # lista de Produto

if "funcionarios" not in st.session_state:
    st.session_state["funcionarios"] = []  # lista de Funcionario

if "vendas" not in st.session_state:
    st.session_state["vendas"] = []  # lista de Venda

if "caixa_total" not in st.session_state:
    st.session_state["caixa_total"] = 0.0

if "codigo_produto" not in st.session_state:
    st.session_state["codigo_produto"] = 1

# ================= Funções utilitárias =================
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

def try_load_logo():
    candidates = ["logo.png", "./logo.png", "images/logo.png"]
    for c in candidates:
        if os.path.exists(c):
            try:
                return Image.open(c)
            except:
                continue
    return None

# ================= Cabeçalho =================
logo = try_load_logo()
if logo:
    cols = st.columns([1,2,1])
    cols[1].image(logo, width=260)
    cols[1].markdown("<h2 style='text-align:center; color:#4B2E2E; margin-top:6px;'>Sistema de Padaria</h2>", unsafe_allow_html=True)
else:
    st.markdown("<h1 style='text-align:center; color:#4B2E2E;'>🥖 Lucio Pães</h1>", unsafe_allow_html=True)
    uploaded = st.file_uploader("Upload da logo (PNG/JPG)", type=["png","jpg","jpeg"])
    if uploaded:
        logo = Image.open(uploaded)
        with open("logo.png","wb") as f:
            f.write(uploaded.getbuffer())
        st.success("Logo salva como 'logo.png'.")

# ================= Menu lateral =================
st.sidebar.header("📌 Menu")
menu = ["Dashboard", "Funcionários", "Estoque", "Venda", "Caixa"]
choice = st.sidebar.radio("Navegação", menu)

# ================= Normaliza vendas antigas =================
vendas_corrigidas = []
for v in st.session_state["vendas"]:
    if isinstance(v, Venda):
        vendas_corrigidas.append(v)
    elif isinstance(v, list) and len(v) == 7:
        # [codigo, item, qtd, valor_unit, total, funcionario, data_hora]
        try:
            produto_temp = Produto(v[0], v[1], v[2], v[3])
            funcionario_temp = Funcionario(v[5])
            obj = Venda(produto_temp, funcionario_temp, v[2])
            obj.total = v[4]
            if isinstance(v[6], datetime):
                obj.data_hora = v[6]
            vendas_corrigidas.append(obj)
        except:
            continue
st.session_state["vendas"] = vendas_corrigidas

# ================= Dashboard =================
if choice == "Dashboard":
    box_title("📊 Dashboard")
    total_caixa = round(sum(v.total for v in st.session_state["vendas"] if isinstance(v, Venda)), 2)
    vendas_hoje = [v for v in st.session_state["vendas"] if isinstance(v, Venda) and v.data_hora.date() == datetime.now().date()]
    produtos_baixos = [p for p in st.session_state["produtos"] if p.qtd <=5]
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Caixa", f"R$ {total_caixa:.2f}")
    col2.metric("Vendas Hoje", len(vendas_hoje))
    col3.metric("Produtos Baixos", len(produtos_baixos))

    if produtos_baixos:
        st.warning("⚠ Produtos com estoque baixo: " + ", ".join(p.nome for p in produtos_baixos))

# ================= Funcionários =================
elif choice == "Funcionários":
    box_title("Funcionários Cadastrados", "👨‍🍳")
    if st.session_state["funcionarios"]:
        for f in st.session_state["funcionarios"]:
            st.write(f.nome)
    else:
        st.info("Nenhum funcionário cadastrado.")

    box_title("Cadastrar Funcionário", "➕")
    with st.form("form_funcionario"):
        nome_func = st.text_input("Nome do funcionário")
        submit_func = st.form_submit_button("Cadastrar Funcionário")
        if submit_func:
            if nome_func.strip() == "":
                st.error("Digite o nome do funcionário.")
            elif nome_func.lower() in [f.nome.lower() for f in st.session_state["funcionarios"]]:
                st.warning(f"Funcionário {nome_func} já cadastrado!")
            else:
                st.session_state["funcionarios"].append(Funcionario(nome_func))
                st.success(f"Funcionário {nome_func} cadastrado com sucesso!")

# ================= Estoque =================
elif choice == "Estoque":
    box_title("Produtos Cadastrados", "📦")
    if st.session_state["produtos"]:
        df_estoque = pd.DataFrame([[p.codigo,p.nome,p.qtd,p.preco] for p in st.session_state["produtos"]],
                                   columns=["Código","Produto","Quantidade","Preço Unitário"])
        st.dataframe(df_estoque)
    else:
        st.info("Nenhum produto cadastrado.")

    box_title("Cadastrar Produto", "➕")
    with st.form("form_produto"):
        nome_prod = st.text_input("Nome do produto")
        qtd_prod = st.number_input("Quantidade inicial", min_value=1, step=1)
        preco_prod = st.number_input("Preço unitário", min_value=0.01, step=0.01, format="%.2f")
        submit_prod = st.form_submit_button("Cadastrar Produto")
        if submit_prod:
            if nome_prod.strip() == "":
                st.error("Digite o nome do produto.")
            else:
                codigo = str(st.session_state["codigo_produto"]).zfill(3)
                st.session_state["codigo_produto"] += 1
                st.session_state["produtos"].append(Produto(codigo, nome_prod, qtd_prod, preco_prod))
                st.success(f"Produto {codigo} - {nome_prod} cadastrado com sucesso!")

    box_title("Gerenciar Estoque", "⚙️")
    if st.session_state["produtos"]:
        codigos = [f"{p.codigo} - {p.nome}" for p in st.session_state["produtos"]]
        escolha = st.selectbox("Escolha um produto para remover", [""]+codigos)
        if st.button("Remover Produto"):
            if escolha:
                codigo_sel = escolha.split(" - ")[0]
                st.session_state["produtos"] = [p for p in st.session_state["produtos"] if p.codigo != codigo_sel]
                st.success("Produto removido com sucesso!")

        if st.button("Zerar Estoque"):
            for p in st.session_state["produtos"]:
                p.qtd = 0
            st.success("Estoque zerado com sucesso!")

# ================= Venda =================
elif choice == "Venda":
    box_title("Registrar Venda", "💰")
    if not st.session_state["produtos"] or not st.session_state["funcionarios"]:
        st.info("Cadastre produtos e funcionários antes de registrar vendas.")
    else:
        with st.form("form_venda"):
            produtos_display = [f"{p.codigo} - {p.nome}" for p in st.session_state["produtos"]]
            prod_sel = st.selectbox("Produto", produtos_display)
            produto_obj = next(p for p in st.session_state["produtos"] if p.codigo == prod_sel.split(" - ")[0])
            func_sel = st.selectbox("Funcionário", [f.nome for f in st.session_state["funcionarios"]])
            qtd_venda = st.number_input("Quantidade", min_value=1, step=1)
            submit_venda = st.form_submit_button("Registrar Venda")
            if submit_venda:
                if qtd_venda > produto_obj.qtd:
                    st.error("Quantidade insuficiente no estoque!")
                else:
                    produto_obj.qtd -= qtd_venda
                    func_obj = next(f for f in st.session_state["funcionarios"] if f.nome == func_sel)
                    venda = Venda(produto_obj, func_obj, qtd_venda)
                    st.session_state["vendas"].append(venda)
                    st.success(f"Venda de {qtd_venda}x {produto_obj.nome} registrada por {func_sel}!")
                    if produto_obj.qtd <=5:
                        st.warning(f"⚠ Restam apenas {produto_obj.qtd} itens de {produto_obj.nome} em estoque!")

# ================= Caixa =================
elif choice == "Caixa":
    box_title("Relatório de Vendas do Dia", "📊")

    # Filtra apenas vendas válidas (instâncias de Venda)
    vendas_validas = [v for v in st.session_state["vendas"] if isinstance(v, Venda)]

    if vendas_validas:
        # Cria DataFrame com todas vendas
        df_vendas = pd.DataFrame(
            [[v.codigo, v.item, v.quantidade, v.valor_unitario, v.total, v.funcionario, v.data_hora] 
             for v in vendas_validas],
            columns=["Código", "Item", "Quantidade", "Valor Unitário", "Total", "Funcionário", "Data/Hora"]
        )

        # Converte Data/Hora e Total para tipos corretos
        df_vendas["Data/Hora"] = pd.to_datetime(df_vendas["Data/Hora"], errors="coerce")
        df_vendas["Total"] = pd.to_numeric(df_vendas["Total"], errors="coerce")

        # Filtra apenas vendas do dia atual
        hoje = datetime.now().date()
        df_vendas_dia = df_vendas[df_vendas["Data/Hora"].dt.date == hoje]

        if not df_vendas_dia.empty:
            st.dataframe(df_vendas_dia[["Código", "Item", "Quantidade", "Valor Unitário", "Total", "Funcionário", "Data/Hora"]])
            
            # Calcula total do dia
            total_dia = df_vendas_dia["Total"].sum()
            st.markdown("### TOTAL DO DIA")
            st.table(pd.DataFrame([["", "", "", "", round(float(total_dia), 2), "", ""]],
                                  columns=["Código", "Item", "Quantidade", "Valor Unitário", "Total", "Funcionário", "Data/Hora"]))
        else:
            st.info("Nenhuma venda registrada hoje.")
    else:
        st.info("Nenhuma venda registrada ainda.")


