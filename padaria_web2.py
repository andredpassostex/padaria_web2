# padaria_streamlit_cliente_conta.py
import os
import streamlit as st
import pandas as pd
from datetime import datetime
from PIL import Image

# ================= Classes =================
class Produto:
    def __init__(self, codigo, nome, qtd, preco, estoque_min=5):
        self.codigo = codigo
        self.nome = nome
        self.qtd = qtd
        self.preco = preco
        self.estoque_min = estoque_min

class Funcionario:
    def __init__(self, nome):
        self.nome = nome.title().strip()

class Cliente:
    def __init__(self, nome):
        self.nome = nome.title().strip()
        self.historico_compras = []  # cada item: [produto, qtd, total, data_hora, funcionario]

# ================= Inicialização =================
for key, default in [("produtos", []), ("funcionarios", []), ("vendas", []), ("clientes", []), ("codigo_produto", 1)]:
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
    st.markdown("<h1 style='text-align:center; color:#4B2E2E;'>🥖 Lucio Pães - Sistema de Padaria</h1>", unsafe_allow_html=True)
    uploaded = st.file_uploader("Upload da logo (PNG/JPG)", type=["png","jpg","jpeg"])
    if uploaded:
        logo = Image.open(uploaded)
        with open("logo.png","wb") as f:
            f.write(uploaded.getbuffer())
        st.success("Logo salva como 'logo.png'.")

# ================= Menu lateral =================
st.sidebar.header("📌 Menu")
menu = ["Dashboard", "Funcionários", "Clientes", "Estoque", "Venda", "Caixa"]
choice = st.sidebar.radio("Navegação", menu)

# ================= Dashboard =================
if choice == "Dashboard":
    box_title("📊 Dashboard")
    total_caixa = round(sum(v[4] for v in st.session_state["vendas"]),2)
    vendas_hoje = [v for v in st.session_state["vendas"] if v[6].date() == datetime.now().date()]
    produtos_baixos = [p for p in st.session_state["produtos"] if p.qtd <= p.estoque_min]
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

# ================= Clientes =================
elif choice == "Clientes":
    box_title("Clientes Cadastrados", "🧑‍🤝‍🧑")
    if st.session_state["clientes"]:
        for c in st.session_state["clientes"]:
            st.write(f"{c.nome} — Total acumulado: R$ {sum(x[2] for x in c.historico_compras):.2f}")
            if c.historico_compras:
                if st.button(f"Zerar conta de {c.nome}", key=f"zerar_{c.nome}"):
                    c.historico_compras.clear()
                    st.success(f"Conta de {c.nome} zerada.")
    else:
        st.info("Nenhum cliente cadastrado.")
    box_title("Cadastrar Cliente", "➕")
    with st.form("form_cliente"):
        nome_cliente = st.text_input("Nome do cliente")
        submit_cliente = st.form_submit_button("Cadastrar Cliente")
        if submit_cliente:
            if nome_cliente.strip() == "":
                st.error("Digite o nome do cliente.")
            elif nome_cliente.lower() in [c.nome.lower() for c in st.session_state["clientes"]]:
                st.warning(f"Cliente {nome_cliente} já cadastrado!")
            else:
                st.session_state["clientes"].append(Cliente(nome_cliente))
                st.success(f"Cliente {nome_cliente} cadastrado com sucesso!")

# ================= Estoque =================
elif choice == "Estoque":
    box_title("Produtos Cadastrados", "📦")
    if st.session_state["produtos"]:
        df_estoque = pd.DataFrame([[p.codigo,p.nome,p.qtd,p.preco,p.estoque_min] for p in st.session_state["produtos"]],
                                   columns=["Código","Produto","Quantidade","Preço Unitário","Estoque Mínimo"])
        st.dataframe(df_estoque)
    else:
        st.info("Nenhum produto cadastrado.")

    box_title("Cadastrar Produto", "➕")
    with st.form("form_produto"):
        nome_prod = st.text_input("Nome do produto")
        qtd_prod = st.number_input("Quantidade inicial", min_value=1, step=1)
        preco_prod = st.number_input("Preço unitário", min_value=0.01, step=0.01, format="%.2f")
        estoque_min = st.number_input("Estoque mínimo para alerta", min_value=1, step=1, value=5)
        submit_prod = st.form_submit_button("Cadastrar Produto")
        if submit_prod:
            if nome_prod.strip() == "":
                st.error("Digite o nome do produto.")
            else:
                codigo = str(st.session_state["codigo_produto"]).zfill(3)
                st.session_state["codigo_produto"] += 1
                st.session_state["produtos"].append(Produto(codigo, nome_prod, qtd_prod, preco_prod, estoque_min))
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
            if st.session_state["clientes"]:
                cliente_sel = st.selectbox("Cliente (opcional)", ["Nenhum"] + [c.nome for c in st.session_state["clientes"]])
            else:
                cliente_sel = "Nenhum"

            qtd_venda = st.number_input("Quantidade", min_value=1, step=1)
            submit_venda = st.form_submit_button("Registrar Venda")
        
        if submit_venda:
            if qtd_venda > produto_obj.qtd:
                st.error("Quantidade insuficiente no estoque!")
            else:
                produto_obj.qtd -= qtd_venda
                data_hora = datetime.now()
                total_venda = produto_obj.preco * qtd_venda
                
                # Atualiza linha de venda existente para mesmo produto e cliente
                venda_existente = None
                if cliente_sel != "Nenhum":
                    for v in st.session_state["vendas"]:
                        if v[0] == produto_obj.codigo and v[7] == cliente_sel:
                            venda_existente = v
                            break
                else:
                    for v in st.session_state["vendas"]:
                        if v[0] == produto_obj.codigo and v[7] == "Nenhum":
                            venda_existente = v
                            break
                
                if venda_existente:
                    venda_existente[2] += qtd_venda
                    venda_existente[4] += total_venda
                    venda_existente[6] = data_hora
                    venda_existente[5] = func_sel
                else:
                    st.session_state["vendas"].append([
                        produto_obj.codigo,
                        produto_obj.nome,
                        qtd_venda,
                        produto_obj.preco,
                        total_venda,
                        func_sel,
                        data_hora,
                        cliente_sel
                    ])
                
                # Atualiza histórico do cliente
                if cliente_sel != "Nenhum":
                    cliente_obj = next(c for c in st.session_state["clientes"] if c.nome == cliente_sel)
                    cliente_obj.historico_compras.append([produto_obj.nome, qtd_venda, total_venda, data_hora, func_sel])
                
                st.success(f"Venda de {qtd_venda}x {produto_obj.nome} registrada por {func_sel} para {cliente_sel}!")

                # Alerta de estoque baixo
                key_popup = f"popup_{produto_obj.codigo}"
                if produto_obj.qtd <= produto_obj.estoque_min:
                    if key_popup not in st.session_state:
                        st.session_state[key_popup] = True
                    if st.session_state[key_popup]:
                        st.warning(f"⚠ Restam apenas {produto_obj.qtd} itens de {produto_obj.nome} em estoque!")
                        if st.button("OK", key=f"ok_{produto_obj.codigo}"):
                            st.session_state[key_popup] = False

# ================= Caixa =================
elif choice == "Caixa":
    box_title("Relatório de Vendas do Dia", "📊")
    if st.session_state["vendas"]:
        df_vendas = pd.DataFrame(st.session_state["vendas"],
                                 columns=["Código","Item","Quantidade","Valor Unitário","Total","Funcionário","Data/Hora","Cliente"])
        df_vendas["Data/Hora"] = pd.to_datetime(df_vendas["Data/Hora"], errors="coerce")
        df_vendas["Total"] = pd.to_numeric(df_vendas["Total"], errors="coerce")
        hoje = datetime.now().date()
        df_vendas_dia = df_vendas[df_vendas["Data/Hora"].dt.date == hoje]

        if not df_vendas_dia.empty:
            st.dataframe(df_vendas_dia[["Código","Item","Quantidade","Valor Unitário","Total","Funcionário","Cliente","Data/Hora"]])
            total_dia = df_vendas_dia["Total"].sum()
            st.markdown("### TOTAL DO DIA")
            st.table(pd.DataFrame([["","","","","{:.2f}".format(total_dia),"","",""]],
                                  columns=["Código","Item","Quantidade","Valor Unitário","Total","Funcionário","Cliente","Data/Hora"]))
        else:
            st.info("Nenhuma venda registrada hoje.")
    else:
        st.info("Nenhuma venda registrada ainda.")
