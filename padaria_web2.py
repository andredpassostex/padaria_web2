# padaria_profissional_completo.py
import os
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from PIL import Image
import altair as alt

# ================= Classes =================
class Produto:
    def __init__(self, codigo, nome, qtd, preco, estoque_min=5, data_fabricacao=None, validade=None, lote=""):
        self.codigo = codigo
        self.nome = nome
        self.qtd = qtd
        self.preco = preco
        self.estoque_min = estoque_min
        self.data_fabricacao = data_fabricacao
        self.validade = validade
        self.lote = lote

class Funcionario:
    def __init__(self, nome):
        self.nome = nome.title().strip()

class Cliente:
    def __init__(self, nome):
        self.nome = nome.title().strip()
        self.historico_compras = []  # [produto, qtd, total, data_hora, funcionario, tipo] (tipo: "imediata" ou "reserva")

class Fornecedor:
    def __init__(self, nome, contato="", produto_fornecido="", preco=0.0, prazo_entrega=0):
        self.nome = nome
        self.contato = contato
        self.produto_fornecido = produto_fornecido
        self.preco = preco
        self.prazo_entrega = prazo_entrega

# ================= Inicialização =================
for key, default in [
    ("produtos", []), ("funcionarios", []), ("clientes", []),
    ("vendas", []), ("fornecedores", []), ("codigo_produto", 1)
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ================= Funções =================
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
    for path in ["logo.png", "./logo.png", "images/logo.png"]:
        if os.path.exists(path):
            try:
                return Image.open(path)
            except:
                continue
    return None

def card_metric(title, value, color="#4B2E2E"):
    st.markdown(
        f"""
        <div style='background-color:{color}; color:white; border-radius:10px;
                    padding:15px; text-align:center; margin:5px;'>
            <h4>{title}</h4>
            <h2>{value}</h2>
        </div>
        """, unsafe_allow_html=True
    )

# ================= Cabeçalho =================
logo = try_load_logo()
if logo:
    cols = st.columns([1,2,1])
    cols[1].image(logo, width=260)
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
menu = ["Dashboard","Funcionários","Clientes","Estoque","Venda","Caixa","Fornecedores","Relatórios"]
choice = st.sidebar.radio("Navegação", menu)

# ================= Dashboard =================
if choice == "Dashboard":
    box_title("📊 Dashboard")
    total_caixa = round(sum(v[4] for v in st.session_state["vendas"] if v[5]=="imediata"),2)
    vendas_hoje = [v for v in st.session_state["vendas"] if v[6].date() == datetime.now().date() and v[5]=="imediata"]
    produtos_baixos = [p for p in st.session_state["produtos"] if p.qtd <= p.estoque_min]
    clientes_conta = [c for c in st.session_state["clientes"] if sum(x[2] for x in c.historico_compras if x[5]=="reserva") > 0]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Caixa", f"R$ {total_caixa:.2f}")
    col2.metric("Vendas Hoje", len(vendas_hoje))
    col3.metric("Produtos Baixos", len(produtos_baixos))
    col4.metric("Clientes com conta", len(clientes_conta))

    if vendas_hoje:
        df_vendas = pd.DataFrame(vendas_hoje, columns=["Código","Item","Quantidade","Valor Unitário","Total","Tipo","Data/Hora","Cliente"])
        df_plot = df_vendas.groupby("Item")["Quantidade"].sum().reset_index()
        chart = alt.Chart(df_plot).mark_bar(color="#4B2E2E").encode(
            x='Item',
            y='Quantidade',
            tooltip=['Item','Quantidade']
        ).properties(title="Vendas por Produto Hoje")
        st.altair_chart(chart, use_container_width=True)

# ================= Funcionários =================
elif choice == "Funcionários":
    box_title("👨‍🍳 Funcionários")
    if st.session_state["funcionarios"]:
        for f in st.session_state["funcionarios"]:
            st.write(f.nome)
    else:
        st.info("Nenhum funcionário cadastrado.")

    box_title("➕ Cadastrar Funcionário")
    with st.form("form_funcionario"):
        nome_func = st.text_input("Nome do funcionário")
        submit_func = st.form_submit_button("Cadastrar")
        if submit_func:
            if nome_func.strip() == "":
                st.error("Digite o nome do funcionário.")
            elif nome_func.lower() in [f.nome.lower() for f in st.session_state["funcionarios"]]:
                st.warning(f"Funcionário {nome_func} já cadastrado!")
            else:
                st.session_state["funcionarios"].append(Funcionario(nome_func))
                st.success(f"Funcionário {nome_func} cadastrado!")

# ================= Clientes =================
elif choice == "Clientes":
    box_title("🧑‍🤝‍🧑 Clientes")
    if st.session_state["clientes"]:
        for c in st.session_state["clientes"]:
            st.markdown(f"### {c.nome}")
            total_cliente = sum(x[2] for x in c.historico_compras)
            st.write(f"Total acumulado: R$ {total_cliente:.2f}")
            if c.historico_compras:
                df_cliente = pd.DataFrame(c.historico_compras,
                                          columns=["Produto","Quantidade","Total","Data/Hora","Funcionário","Tipo"])
                st.dataframe(df_cliente.sort_values("Data/Hora", ascending=False))
                if st.button(f"Zerar conta de {c.nome}", key=f"zerar_{c.nome}"):
                    c.historico_compras = [x for x in c.historico_compras if x[5]=="imediata"]
                    st.success(f"Conta de {c.nome} zerada.")
    else:
        st.info("Nenhum cliente cadastrado.")

# ================= Estoque =================
elif choice == "Estoque":
    box_title("📦 Produtos")
    if st.session_state["produtos"]:
        df_estoque = pd.DataFrame([[p.codigo,p.nome,p.qtd,p.preco,p.estoque_min,p.lote,p.data_fabricacao,p.validade] for p in st.session_state["produtos"]],
                                   columns=["Código","Produto","Quantidade","Preço Unitário","Estoque Mínimo","Lote","Fabricação","Validade"])
        st.dataframe(df_estoque)
    else:
        st.info("Nenhum produto cadastrado.")

    box_title("➕ Cadastrar Produto")
    with st.form("form_produto"):
        nome_prod = st.text_input("Nome do produto")
        qtd_prod = st.number_input("Quantidade inicial", min_value=1, step=1)
        preco_prod = st.number_input("Preço unitário", min_value=0.01, step=0.01, format="%.2f")
        estoque_min = st.number_input("Estoque mínimo para alerta", min_value=1, step=1, value=5)
        lote = st.text_input("Lote (opcional)")
        data_fab = st.date_input("Data de fabricação")
        validade = st.date_input("Validade")
        submit_prod = st.form_submit_button("Cadastrar Produto")
        if submit_prod:
            if nome_prod.strip() == "":
                st.error("Digite o nome do produto.")
            else:
                codigo = str(st.session_state["codigo_produto"]).zfill(3)
                st.session_state["codigo_produto"] += 1
                st.session_state["produtos"].append(Produto(codigo, nome_prod, qtd_prod, preco_prod, estoque_min, data_fab, validade, lote))
                st.success(f"Produto {codigo} - {nome_prod} cadastrado!")

# ================= Venda =================
elif choice == "Venda":
    box_title("💰 Registrar Venda")
    if not st.session_state["produtos"] or not st.session_state["funcionarios"]:
        st.info("Cadastre produtos e funcionários antes de registrar vendas.")
    else:
        with st.form("form_venda"):
            produtos_display = [f"{p.codigo} - {p.nome}" for p in st.session_state["produtos"]]
            prod_sel = st.selectbox("Produto", produtos_display)
            produto_obj = next(p for p in st.session_state["produtos"] if p.codigo == prod_sel.split(" - ")[0])
            func_sel = st.selectbox("Funcionário", [f.nome for f in st.session_state["funcionarios"]])
            cliente_input = st.text_input("Cliente (opcional)")
            tipo_venda = st.radio("Tipo de venda", ["imediata", "reserva"])
            qtd_venda = st.number_input("Quantidade", min_value=1, step=1)
            submit_venda = st.form_submit_button("Registrar Venda")

        if submit_venda:
            cliente_nome = cliente_input.strip().title() if cliente_input.strip() else "Nenhum"
            if cliente_nome != "Nenhum" and cliente_nome.lower() not in [c.nome.lower() for c in st.session_state["clientes"]]:
                st.session_state["clientes"].append(Cliente(cliente_nome))
                st.success(f"Cliente {cliente_nome} cadastrado automaticamente!")

            if qtd_venda > produto_obj.qtd:
                st.error("Quantidade insuficiente no estoque!")
            else:
                produto_obj.qtd -= qtd_venda
                data_hora = datetime.now()
                total_venda = produto_obj.preco * qtd_venda

                venda_existente = None
                for v in st.session_state["vendas"]:
                    if v[0]==produto_obj.codigo and v[7]==cliente_nome and v[5]==tipo_venda:
                        venda_existente=v
                        break

                if venda_existente:
                    venda_existente[2] += qtd_venda
                    venda_existente[4] += total_venda
                    venda_existente[6] = data_hora
                    venda_existente[5] = tipo_venda
                    venda_existente[5] = func_sel
                else:
                    st.session_state["vendas"].append([
                        produto_obj.codigo, produto_obj.nome, qtd_venda,
                        produto_obj.preco, total_venda, tipo_venda, data_hora, cliente_nome
                    ])

                if cliente_nome!="Nenhum":
                    cliente_obj = next(c for c in st.session_state["clientes"] if c.nome==cliente_nome)
                    cliente_obj.historico_compras.append([produto_obj.nome, qtd_venda, total_venda, data_hora, func_sel, tipo_venda])

                st.success(f"Venda de {qtd_venda}x {produto_obj.nome} registrada para {cliente_nome} por {func_sel}!")
                if produto_obj.qtd <= produto_obj.estoque_min:
                    st.warning(f"⚠ Restam apenas {produto_obj.qtd} itens de {produto_obj.nome}!")

# ================= Caixa =================
elif choice == "Caixa":
    box_title("📊 Relatório de Vendas do Dia")
    if st.session_state["vendas"]:
        df_vendas = pd.DataFrame(st.session_state["vendas"],
                                 columns=["Código","Item","Quantidade","Valor Unitário","Total","Tipo","Data/Hora","Cliente"])
        df_vendas["Data/Hora"]=pd.to_datetime(df_vendas["Data/Hora"],errors="coerce")
        df_vendas["Total"]=pd.to_numeric(df_vendas["Total"],errors="coerce")
        hoje = datetime.now().date()
        df_vendas_dia = df_vendas[(df_vendas["Data/Hora"].dt.date==hoje) & (df_vendas["Tipo"]=="imediata")]

        if not df_vendas_dia.empty:
            st.dataframe(df_vendas_dia[["Código","Item","Quantidade","Valor Unitário","Total","Cliente","Data/Hora"]])
            total_dia = df_vendas_dia["Total"].sum()
            st.markdown(f"### TOTAL DO DIA: R$ {total_dia:.2f}")
        else:
            st.info("Nenhuma venda registrada hoje.")
    else:
        st.info("Nenhuma venda registrada.")

# ================= Fornecedores =================
elif choice == "Fornecedores":
    box_title("📋 Fornecedores")
    if st.session_state["fornecedores"]:
        df_fornecedores = pd.DataFrame([[f.nome,f.contato,f.produto_fornecido,f.preco,f.prazo_entrega] for f in st.session_state["fornecedores"]],
                                       columns=["Nome","Contato","Produto Fornecido","Preço","Prazo Entrega"])
        st.dataframe(df_fornecedores)
    with st.form("form_fornecedor"):
        nome_f = st.text_input("Nome do fornecedor")
        contato_f = st.text_input("Contato")
        produto_f = st.text_input("Produto fornecido")
        preco_f = st.number_input("Preço", min_value=0.0, step=0.01)
        prazo_f = st.number_input("Prazo entrega (dias)", min_value=0, step=1)
        submit_f = st.form_submit_button("Cadastrar Fornecedor")
        if submit_f:
            st.session_state["fornecedores"].append(Fornecedor(nome_f,contato_f,produto_f,preco_f,prazo_f))
            st.success(f"Fornecedor {nome_f} cadastrado!")

# ================= Relatórios =================
elif choice == "Relatórios":
    box_title("📈 Relatórios")
    st.info("Aqui você poderia gerar gráficos e exportar relatórios de vendas, produtos e clientes.")
