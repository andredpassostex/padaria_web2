# padaria_erp_completo.py
import os
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from PIL import Image
from io import BytesIO

# ================= Classes =================
class Produto:
    def __init__(self, codigo, nome, qtd, preco, estoque_min=5):
        self.codigo = codigo
        self.nome = nome.title().strip()
        self.qtd = int(qtd)
        self.preco = float(preco)
        self.estoque_min = int(estoque_min)

class Funcionario:
    def __init__(self, nome):
        self.nome = nome.title().strip()

class Cliente:
    def __init__(self, nome):
        self.nome = nome.title().strip()
        # cada entrada: [produto, qtd, total, data_hora, funcionario, tipo]
        self.historico = []

class Fornecedor:
    def __init__(self, nome, contato="", produto="", preco=0.0, prazo=0):
        self.nome = nome.title().strip()
        self.contato = contato
        self.produto = produto
        self.preco = float(preco)
        self.prazo = int(prazo)

# ================= Inicialização do session_state =================
defaults = {
    "produtos": [],
    "funcionarios": [],
    "clientes": [],
    "fornecedores": [],
    "vendas": [],
    "codigo_produto": 1,
    "tela_selecionada": "Dashboard",
    "submenu_selecionado": None,
    "mostrar_caixa": False,
    "mostrar_contas": False
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ================= Utilitários visuais =================
def mostrar_logo(size):
    logo_path = "logo.png"
    if os.path.exists(logo_path):
        try:
            img = Image.open(logo_path)
            st.image(img, width=size)
        except Exception:
            st.markdown("<h1 style='text-align:center; color:#4B2E2E;'>🥖 Lucio Pães</h1>", unsafe_allow_html=True)
    else:
        st.markdown("<h1 style='text-align:center; color:#4B2E2E;'>🥖 Lucio Pães</h1>", unsafe_allow_html=True)

def box_title(texto, icone="📌"):
    st.markdown(f"""
        <div style='padding: 10px; background-color: #f9f9f9;
                    border-radius: 10px; box-shadow: 2px 2px 8px rgba(0,0,0,0.12);
                    margin-bottom: 12px;'>
            <h3 style='text-align:center; color:#4B2E2E; margin:6px 0;'>{icone} {texto}</h3>
        </div>
    """, unsafe_allow_html=True)

# ================= Funções de negócio =================
def cadastrar_produto(nome, qtd, preco):
    if not nome or str(nome).strip() == "":
        st.error("Nome do produto inválido.")
        return
    nome = str(nome).title().strip()
    qtd = int(qtd)
    preco = float(preco)
    # busca por nome (case-insensitive)
    for p in st.session_state["produtos"]:
        if p.nome.lower() == nome.lower():
            p.qtd += qtd
            p.preco = preco
            st.success(f"Produto '{nome}' atualizado: +{qtd} unidades (novo estoque {p.qtd}), preço atualizado para R$ {preco:.2f}.")
            return
    codigo = str(st.session_state["codigo_produto"]).zfill(3)
    novo = Produto(codigo, nome, qtd, preco)
    st.session_state["produtos"].append(novo)
    st.session_state["codigo_produto"] += 1
    st.success(f"Produto '{nome}' cadastrado com código {codigo}.")

def cadastrar_funcionario(nome):
    if not nome or str(nome).strip() == "":
        st.error("Nome do funcionário inválido.")
        return
    nome = str(nome).title().strip()
    if nome in [f.nome for f in st.session_state["funcionarios"]]:
        st.warning("Funcionário já cadastrado.")
        return
    st.session_state["funcionarios"].append(Funcionario(nome))
    st.success(f"Funcionário '{nome}' cadastrado.")

def remover_funcionario(nome):
    st.session_state["funcionarios"] = [f for f in st.session_state["funcionarios"] if f.nome != nome]
    st.success(f"Funcionário '{nome}' removido.")

def cadastrar_cliente(nome):
    if not nome or str(nome).strip() == "":
        return None
    nome = str(nome).title().strip()
    for c in st.session_state["clientes"]:
        if c.nome.lower() == nome.lower():
            return c
    novo = Cliente(nome)
    st.session_state["clientes"].append(novo)
    st.success(f"Cliente '{nome}' cadastrado.")
    return novo

def cadastrar_fornecedor(nome, contato="", produto="", preco=0.0, prazo=0):
    if not nome or str(nome).strip() == "":
        st.error("Nome do fornecedor inválido.")
        return
    novo = Fornecedor(nome, contato, produto, float(preco), int(prazo))
    st.session_state["fornecedores"].append(novo)
    st.success(f"Fornecedor '{nome}' cadastrado.")

def registrar_venda(produto_obj, funcionario_obj, cliente_obj, quantidade, tipo="imediata"):
    # produto_obj: Produto instance, funcionario_obj: Funcionario instance, cliente_obj: Cliente or None
    quantidade = int(quantidade)
    if quantidade <= 0:
        st.error("Quantidade inválida.")
        return
    # validar estoque apenas para vendas que baixam estoque (imediata)
    if tipo == "imediata":
        if quantidade > produto_obj.qtd:
            st.error(f"Estoque insuficiente para {produto_obj.nome}. Disponível: {produto_obj.qtd}")
            return
        produto_obj.qtd -= quantidade
    total = quantidade * produto_obj.preco
    data_hora = datetime.now()
    cliente_nome = cliente_obj.nome if cliente_obj else ""
    st.session_state["vendas"].append([
        produto_obj.codigo, produto_obj.nome, quantidade, produto_obj.preco,
        total, tipo, data_hora, funcionario_obj.nome, cliente_nome
    ])
    if cliente_obj:
        # registra no histórico do cliente (todas as vendas)
        cliente_obj.historico.append([produto_obj.nome, quantidade, total, data_hora, funcionario_obj.nome, tipo])
    st.success(f"Venda registrada: {quantidade} x {produto_obj.nome} — {tipo} — atendido por {funcionario_obj.nome}")
    # alerta estoque baixo
    if produto_obj.qtd <= produto_obj.estoque_min:
        st.warning(f"⚠ Estoque baixo: {produto_obj.nome} — {produto_obj.qtd} unidades restantes.")

# ================= Helpers para DataFrames / Relatórios =================
def vendas_to_df(vendas_list):
    # vendas_list items: [codigo, produto, qtd, valor_unit, total, tipo, data_hora, funcionario, cliente]
    if not vendas_list:
        return pd.DataFrame(columns=["Código","Produto","Quantidade","Valor Unitário","Total","Tipo","TipoVisual","Data/Hora","Funcionário","Cliente"])
    rows = []
    for v in vendas_list:
        tipo = v[5]
        tipo_visual = "🟠 Reserva" if tipo == "reserva" else "🟢 Pago"
        rows.append({
            "Código": v[0],
            "Produto": v[1],
            "Quantidade": v[2],
            "Valor Unitário": float(v[3]),
            "Total": float(v[4]),
            "Tipo": tipo,
            "TipoVisual": tipo_visual,
            "Data/Hora": v[6],
            "Funcionário": v[7],
            "Cliente": v[8] if len(v) > 8 else ""
        })
    df = pd.DataFrame(rows)
    # permitir ordenar com st.dataframe: convert Data/Hora to datetime if not already
    if df.shape[0] > 0:
        df["Data/Hora"] = pd.to_datetime(df["Data/Hora"])
    return df

def cliente_historico_to_df(cliente):
    # cliente.historico entries: [produto, qtd, total, data_hora, funcionario, tipo]
    if not cliente.historico:
        return pd.DataFrame(columns=["Produto","Quantidade","Total","Data/Hora","Funcionário","Tipo","TipoVisual"])
    rows = []
    for h in cliente.historico:
        tipo = h[5]
        tipo_visual = "🟠 Reserva" if tipo == "reserva" else "🟢 Pago"
        rows.append({
            "Produto": h[0],
            "Quantidade": h[1],
            "Total": float(h[2]),
            "Data/Hora": h[3],
            "Funcionário": h[4],
            "Tipo": tipo,
            "TipoVisual": tipo_visual
        })
    df = pd.DataFrame(rows)
    df["Data/Hora"] = pd.to_datetime(df["Data/Hora"])
    return df

def produtos_to_df(produtos_list):
    if not produtos_list:
        return pd.DataFrame(columns=["Código","Produto","Quantidade","Preço","Estoque Mínimo"])
    rows = []
    for p in produtos_list:
        rows.append({
            "Código": p.codigo,
            "Produto": p.nome,
            "Quantidade": p.qtd,
            "Preço": float(p.preco),
            "Estoque Mínimo": p.estoque_min
        })
    return pd.DataFrame(rows)

def df_to_csv_bytes(df):
    towrite = BytesIO()
    df.to_csv(towrite, index=False)
    towrite.seek(0)
    return towrite

# ================= Dashboard =================
def dashboard():
    mostrar_logo(480)
    box_title("📊 Dashboard")
    df_vendas = vendas_to_df(st.session_state["vendas"])
    total_caixa = df_vendas[df_vendas["Tipo"]!="reserva"]["Total"].sum() if not df_vendas.empty else 0.0
    display_valor = f"R$ {total_caixa:.2f}" if st.session_state["mostrar_caixa"] else "R$ ****"

    # vendas hoje
    hoje = datetime.now().date()
    vendas_hoje = df_vendas[df_vendas["Data/Hora"].dt.date == hoje] if not df_vendas.empty else pd.DataFrame()
    produtos_baixos = [p for p in st.session_state["produtos"] if p.qtd <= p.estoque_min]
    clientes_conta = [c for c in st.session_state["clientes"] if any(h[5] == "reserva" for h in c.historico)]
    total_contas = sum(sum(h[2] for h in c.historico if h[5] == "reserva") for c in clientes_conta)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
            <div style='background-color:#4CAF50;padding:12px;border-radius:10px;color:white;text-align:center;'>
                <h4 style='margin:6px 0;'>💰 Caixa</h4>
                <h2 style='margin:6px 0;'>{display_valor}</h2>
            </div>
        """, unsafe_allow_html=True)
        if st.button("👁️ Mostrar / Ocultar Caixa", key="btn_caixa"):
            st.session_state["mostrar_caixa"] = not st.session_state["mostrar_caixa"]

    with col2:
        st.markdown(f"""
            <div style='background-color:#2196F3;padding:12px;border-radius:10px;color:white;text-align:center;'>
                <h4 style='margin:6px 0;'>🛒 Vendas Hoje</h4>
                <h2 style='margin:6px 0;'>{len(vendas_hoje)}</h2>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        lista = "<br>".join([f"{p.nome} ({p.qtd})" for p in produtos_baixos]) if produtos_baixos else "✅ OK"
        st.markdown(f"""
            <div style='background-color:#FF9800;padding:12px;border-radius:10px;color:white;text-align:center;'>
                <h4 style='margin:6px 0;'>📦 Produtos Baixos</h4>
                <p style='margin:6px 0;'>{lista}</p>
            </div>
        """, unsafe_allow_html=True)

    with col4:
        display_conta = f"R$ {total_contas:.2f}" if st.session_state["mostrar_contas"] else "R$ ****"
        st.markdown(f"""
            <div style='background-color:#F44336;padding:12px;border-radius:10px;color:white;text-align:center;'>
                <h4 style='margin:6px 0;'>👥 Contas em Aberto</h4>
                <h2 style='margin:6px 0;'>{display_conta}</h2>
            </div>
        """, unsafe_allow_html=True)
        if st.button("👁️ Mostrar / Ocultar Contas", key="btn_conta"):
            st.session_state["mostrar_contas"] = not st.session_state["mostrar_contas"]

    st.markdown("---")
    # Quick mini-relatório: top 5 produtos vendidos (quantidade)
    if not df_vendas.empty:
        top_prod = df_vendas.groupby("Produto")["Quantidade"].sum().sort_values(ascending=False).head(5)
        st.subheader("Top produtos vendidos (quant.)")
        st.table(top_prod.reset_index().rename(columns={"Quantidade":"Total Vendido"}))
    else:
        st.info("Sem vendas registradas ainda.")

# ================= Telas funcionais (com relatórios) =================
def tela_funcional():
    mostrar_logo(220)
    tela = st.session_state["tela_selecionada"]
    submenu = st.session_state["submenu_selecionado"]

    # ---------- Estoque ----------
    if tela == "Estoque":
        if submenu == "Cadastrar Produto":
            box_title("Cadastrar Produto")
            nome = st.text_input("Nome do Produto", key="cad_prod_nome")
            qtd = st.number_input("Quantidade", min_value=1, value=1, step=1, key="cad_prod_qtd")
            preco = st.number_input("Preço Unitário", min_value=0.01, value=1.0, format="%.2f", key="cad_prod_preco")
            if st.button("Cadastrar / Atualizar Produto", key="btn_cad_prod"):
                cadastrar_produto(nome, qtd, preco)
        elif submenu == "Produtos":
            box_title("Lista de Produtos")
            df = produtos_to_df(st.session_state["produtos"])
            if not df.empty:
                st.dataframe(df.sort_values(by="Produto"), height=300, use_container_width=True)
                csv = df_to_csv_bytes(df)
                st.download_button("Baixar CSV - Produtos", csv, file_name="produtos.csv")
            else:
                st.info("Nenhum produto cadastrado.")

    # ---------- Funcionários ----------
    elif tela == "Funcionários":
        if submenu == "Cadastrar Funcionário":
            box_title("Cadastrar Funcionário")
            nome = st.text_input("Nome do Funcionário", key="cad_func_nome")
            if st.button("Cadastrar Funcionário", key="btn_cad_func"):
                cadastrar_funcionario(nome)
        elif submenu == "Funcionários":
            box_title("Lista de Funcionários")
            if st.session_state["funcionarios"]:
                df = pd.DataFrame([{"Funcionário": f.nome} for f in st.session_state["funcionarios"]])
                st.dataframe(df.sort_values("Funcionário"), height=300, use_container_width=True)
            else:
                st.info("Nenhum funcionário cadastrado.")
        elif submenu == "Remover Funcionário":
            box_title("Remover Funcionário")
            if st.session_state["funcionarios"]:
                nomes = [f.nome for f in st.session_state["funcionarios"]]
                sel = st.selectbox("Escolha o funcionário para remover", nomes, key="sel_remover_func")
                if st.button("Remover Funcionário", key="btn_remover_func"):
                    remover_funcionario(sel)
            else:
                st.info("Nenhum funcionário cadastrado.")

    # ---------- Clientes ----------
    elif tela == "Clientes":
        if submenu == "Histórico":
            box_title("Histórico de Clientes")
            if st.session_state["clientes"]:
                nomes_clientes = sorted([c.nome for c in st.session_state["clientes"]])
                sel_cliente = st.selectbox("Selecione o cliente", nomes_clientes, key="hist_sel_cliente")
                cliente = next(c for c in st.session_state["clientes"] if c.nome == sel_cliente)
                df = cliente_historico_to_df(cliente)
                if not df.empty:
                    # mostramos coluna TipoVisual (com emoji) para clareza e manter ordenação
                    st.dataframe(df.sort_values("Data/Hora", ascending=False), height=350, use_container_width=True)
                    csv = df_to_csv_bytes(df)
                    st.download_button("Baixar CSV - Histórico do cliente", csv, file_name=f"historico_{cliente.nome}.csv")
                else:
                    st.info("Sem histórico de compras para este cliente.")
            else:
                st.info("Nenhum cliente cadastrado.")

        elif submenu == "Conta":
            box_title("Gerenciar Conta do Cliente")
            if st.session_state["clientes"]:
                sel = st.selectbox("Escolha o cliente", [c.nome for c in st.session_state["clientes"]], key="conta_sel")
                cliente = next(c for c in st.session_state["clientes"] if c.nome == sel)
                historico_reserva = [h for h in cliente.historico if h[5] == "reserva"]
                total_reserva = sum(h[2] for h in historico_reserva)
                st.markdown(f"**Total em Reserva:** R$ {total_reserva:.2f}")
                df = cliente_historico_to_df(cliente)
                df_reserva = df[df["Tipo"] == "reserva"]
                if not df_reserva.empty:
                    st.dataframe(df_reserva.sort_values("Data/Hora", ascending=False), height=300, use_container_width=True)
                else:
                    st.info("Sem compras em aberto (reservas).")
                if st.button("Zerar Conta (marcar reservas como pagas)", key="btn_zerar_conta"):
                    for h in cliente.historico:
                        if h[5] == "reserva":
                            h[5] = "imediata"  # marcamos como pagas
                    st.success(f"Conta de {cliente.nome} zerada.")
            else:
                st.info("Nenhum cliente cadastrado.")

    # ---------- Fornecedores ----------
    elif tela == "Fornecedores":
        if submenu == "Cadastrar Fornecedor":
            box_title("Cadastrar Fornecedor")
            nome = st.text_input("Nome do Fornecedor", key="cad_forne_nome")
            contato = st.text_input("Contato", key="cad_forne_contato")
            produto = st.text_input("Produto Fornecido", key="cad_forne_prod")
            preco = st.number_input("Preço Unitário", min_value=0.01, value=1.0, format="%.2f", key="cad_forne_preco")
            prazo = st.number_input("Prazo de Entrega (dias)", min_value=0, value=0, key="cad_forne_prazo")
            if st.button("Cadastrar Fornecedor", key="btn_cad_forne"):
                cadastrar_fornecedor(nome, contato, produto, preco, prazo)
        elif submenu == "Fornecedores":
            box_title("Lista de Fornecedores")
            if st.session_state["fornecedores"]:
                df = pd.DataFrame([{"Fornecedor": f.nome, "Contato": f.contato, "Produto": f.produto, "Preço": f.preco, "Prazo": f.prazo} for f in st.session_state["fornecedores"]])
                st.dataframe(df.sort_values("Fornecedor"), height=300, use_container_width=True)
            else:
                st.info("Nenhum fornecedor cadastrado.")

    # ---------- Vendas ----------
    elif tela == "Vendas":
        box_title("Registrar Venda")
        if not st.session_state["produtos"] or not st.session_state["funcionarios"]:
            st.info("Cadastre produtos e funcionários antes de registrar vendas.")
        else:
            produtos_display = [f"{p.codigo} - {p.nome} (Estoque: {p.qtd})" for p in st.session_state["produtos"]]
            prod_sel = st.selectbox("Produto", produtos_display, key="venda_prod_sel")
            prod_codigo = prod_sel.split(" - ")[0]
            produto = next(p for p in st.session_state["produtos"] if p.codigo == prod_codigo)
            func_sel = st.selectbox("Funcionário", [f.nome for f in st.session_state["funcionarios"]], key="venda_func_sel")
            funcionario = next(f for f in st.session_state["funcionarios"] if f.nome == func_sel)
            # cliente: escolha existente ou novo
            nomes_clientes = ["-- Nenhum --", "Novo Cliente"] + [c.nome for c in st.session_state["clientes"]]
            sel_cliente = st.selectbox("Cliente (opcional)", nomes_clientes, key="venda_cliente_sel")
            cliente_obj = None
            if sel_cliente == "Novo Cliente":
                nome_novo = st.text_input("Nome do novo cliente", key="venda_cliente_novo")
            elif sel_cliente != "-- Nenhum --":
                cliente_obj = next(c for c in st.session_state["clientes"] if c.nome == sel_cliente)
            qtd = st.number_input("Quantidade", min_value=1, value=1, key="venda_qtd")
            tipo = st.radio("Tipo de Venda", ["imediata", "reserva"], key="venda_tipo")
            if st.button("Registrar Venda", key="btn_registrar_venda"):
                if sel_cliente == "Novo Cliente":
                    if not nome_novo or str(nome_novo).strip() == "":
                        st.error("Digite o nome do cliente para cadastrá-lo.")
                    else:
                        cliente_obj = cadastrar_cliente(nome_novo)
                        registrar_venda(produto, funcionario, cliente_obj, qtd, tipo)
                else:
                    registrar_venda(produto, funcionario, cliente_obj, qtd, tipo)

    # ---------- Caixa / Relatórios ----------
    elif tela == "Caixa":
        if submenu in ["Diário", "Semanal", "Mensal"]:
            box_title(f"Relatório de Vendas — {submenu}")
            df_vendas = vendas_to_df(st.session_state["vendas"])
            if df_vendas.empty:
                st.info("Nenhuma venda registrada.")
            else:
                now = datetime.now()
                if submenu == "Diário":
                    df_period = df_vendas[df_vendas["Data/Hora"].dt.date == now.date()]
                elif submenu == "Semanal":
                    today = now.date()
                    start_week = today - timedelta(days=today.weekday())
                    end_week = start_week + timedelta(days=6)
                    df_period = df_vendas[(df_vendas["Data/Hora"].dt.date >= start_week) & (df_vendas["Data/Hora"].dt.date <= end_week)]
                else:  # Mensal
                    df_period = df_vendas[(df_vendas["Data/Hora"].dt.year == now.year) & (df_vendas["Data/Hora"].dt.month == now.month)]

                if df_period.empty:
                    st.info("Nenhuma venda no período selecionado.")
                else:
                    # mostrar tabela ordenável
                    st.dataframe(df_period.sort_values("Data/Hora", ascending=False), height=400, use_container_width=True)
                    total_period = df_period["Total"].sum()
                    st.markdown(f"**Total Vendas ({submenu}): R$ {total_period:.2f}**")
                    csv = df_to_csv_bytes(df_period)
                    st.download_button("Baixar CSV - Vendas (período)", csv, file_name=f"vendas_{submenu.lower()}.csv")
        else:
            box_title("Caixa")
            df_vendas = vendas_to_df(st.session_state["vendas"])
            total_caixa = df_vendas[df_vendas["Tipo"] != "reserva"]["Total"].sum() if not df_vendas.empty else 0.0
            st.markdown(f"**Total em Caixa (vendas pagas): R$ {total_caixa:.2f}**")
            if not df_vendas.empty:
                st.dataframe(df_vendas.sort_values("Data/Hora", ascending=False), height=350, use_container_width=True)
                csv = df_to_csv_bytes(df_vendas)
                st.download_button("Baixar CSV - Todas as Vendas", csv, file_name="vendas_todas.csv")

# ================= Sidebar (menu) =================
menu_principal = ["Dashboard", "Vendas", "Caixa"]
menu_expansivo = {
    "Estoque": ["Cadastrar Produto", "Produtos"],
    "Funcionários": ["Cadastrar Funcionário", "Funcionários", "Remover Funcionário"],
    "Clientes": ["Histórico", "Conta"],
    "Fornecedores": ["Cadastrar Fornecedor", "Fornecedores"],
    "Relatórios": ["Diário", "Semanal", "Mensal"]
}

st.sidebar.header("📌 Menu")
for item in menu_principal:
    if st.sidebar.button(item):
        st.session_state["tela_selecionada"] = item
        st.session_state["submenu_selecionado"] = None

for item, submenus in menu_expansivo.items():
    exp = st.sidebar.expander(item, expanded=False)
    with exp:
        for sub in submenus:
            if st.button(sub, key=f"{item}_{sub}"):
                if item == "Relatórios":
                    st.session_state["tela_selecionada"] = "Caixa"
                    st.session_state["submenu_selecionado"] = sub
                else:
                    st.session_state["tela_selecionada"] = item
                    st.session_state["submenu_selecionado"] = sub

# ================= Render principal =================
if st.session_state["tela_selecionada"] == "Dashboard":
    dashboard()
else:
    tela_funcional()
