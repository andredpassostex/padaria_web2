# padaria_erp_completo.py
import os
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from PIL import Image

# ================= Classes =================
class Produto:
    def __init__(self, codigo, nome, qtd, preco, estoque_min=5):
        self.codigo = codigo
        self.nome = nome.title()
        self.qtd = qtd
        self.preco = preco
        self.estoque_min = estoque_min

class Funcionario:
    def __init__(self, nome):
        self.nome = nome.title().strip()

class Cliente:
    def __init__(self, nome):
        self.nome = nome.title().strip()
        self.historico = []  # cada entrada: [produto, qtd, total, data_hora, funcionario, tipo]

class Fornecedor:
    def __init__(self, nome, contato="", produto="", preco=0.0, prazo=0):
        self.nome = nome.title().strip()
        self.contato = contato
        self.produto = produto
        self.preco = preco
        self.prazo = prazo

# ================= Inicialização do session_state =================
for key, default in [
    ("produtos", []), ("funcionarios", []), ("clientes", []),
    ("fornecedores", []), ("vendas", []), ("codigo_produto", 1)
]:
    if key not in st.session_state:
        st.session_state[key] = default

# telas e visibilidades
if "tela_selecionada" not in st.session_state:
    st.session_state["tela_selecionada"] = "Dashboard"
if "submenu_selecionado" not in st.session_state:
    st.session_state["submenu_selecionado"] = None
if "mostrar_caixa" not in st.session_state:
    st.session_state["mostrar_caixa"] = False
if "mostrar_contas" not in st.session_state:
    st.session_state["mostrar_contas"] = False

# ================= Utilitários visuais =================
def mostrar_logo(size):
    logo_path = "logo.png"
    if os.path.exists(logo_path):
        try:
            img = Image.open(logo_path)
            st.image(img, width=size)
        except Exception:
            st.markdown(f"<h1 style='text-align:center; color:#4B2E2E;'>🥖 Lucio Pães</h1>", unsafe_allow_html=True)
    else:
        st.markdown(f"<h1 style='text-align:center; color:#4B2E2E;'>🥖 Lucio Pães</h1>", unsafe_allow_html=True)

def box_title(texto, icone="📌"):
    st.markdown(f"""
        <div style='padding: 10px; background-color: #f9f9f9;
                    border-radius: 10px; box-shadow: 2px 2px 8px rgba(0,0,0,0.12);
                    margin-bottom: 12px;'>
            <h3 style='text-align:center; color:#4B2E2E; margin:6px 0;'>{icone} {texto}</h3>
        </div>
    """, unsafe_allow_html=True)

# ================= Funções de negócio (cadastros / operações) =================
def cadastrar_produto(nome, qtd, preco):
    if not nome or str(nome).strip() == "":
        st.error("Nome do produto inválido.")
        return
    codigo = str(st.session_state["codigo_produto"]).zfill(3)
    st.session_state["produtos"].append(Produto(codigo, nome, int(qtd), float(preco)))
    st.session_state["codigo_produto"] += 1
    st.success(f"Produto '{nome}' cadastrado com código {codigo}.")

def cadastrar_funcionario(nome):
    if not nome or str(nome).strip() == "":
        st.error("Nome do funcionário inválido.")
        return
    nome = nome.title().strip()
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
        st.error("Nome do cliente inválido.")
        return None
    nome = nome.title().strip()
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

def registrar_venda(produto, funcionario, cliente, quantidade, tipo="imediata"):
    # produto: objeto Produto, funcionario: objeto Funcionario, cliente: objeto Cliente or None
    quantidade = int(quantidade)
    if quantidade <= 0:
        st.error("Quantidade inválida.")
        return
    if tipo == "imediata" and quantidade > produto.qtd:
        st.error("Quantidade insuficiente no estoque.")
        return
    # decrementa estoque apenas em venda imediata
    if tipo == "imediata":
        produto.qtd -= quantidade
    total = quantidade * produto.preco
    data_hora = datetime.now()
    cliente_nome = cliente.nome if cliente else ""
    st.session_state["vendas"].append([
        produto.codigo, produto.nome, quantidade, produto.preco, total, tipo, data_hora, funcionario.nome, cliente_nome
    ])
    # registra no histórico do cliente apenas se for reserva
    if cliente and tipo == "reserva":
        cliente.historico.append([produto.nome, quantidade, total, data_hora, funcionario.nome, tipo])
    st.success(f"Venda registrada: {quantidade} x {produto.nome} — {tipo} — atendido por {funcionario.nome}")
    # alerta estoque baixo
    if produto.qtd <= produto.estoque_min:
        st.warning(f"⚠ Estoque baixo: {produto.nome} — {produto.qtd} unidades restantes.")

# ================= Dashboard =================
def dashboard():
    mostrar_logo(600)
    box_title("📊 Dashboard")

    total_caixa = sum(v[4] for v in st.session_state["vendas"] if v[5] == "imediata")
    display_valor = f"R$ {total_caixa:.2f}" if st.session_state["mostrar_caixa"] else "R$ ****"

    vendas_hoje = [v for v in st.session_state["vendas"] if v[5] == "imediata" and v[6].date() == datetime.now().date()]
    produtos_baixos = [p for p in st.session_state["produtos"] if p.qtd <= p.estoque_min]
    clientes_conta = [c for c in st.session_state["clientes"] if sum(x[2] for x in c.historico if x[5] == "reserva") > 0]
    total_contas = sum(sum(x[2] for x in c.historico if x[5] == "reserva") for c in clientes_conta)

    display_conta = f"R$ {total_contas:.2f}" if st.session_state["mostrar_contas"] else "R$ ****"

    col1, col2, col3, col4 = st.columns(4)

    # Card estilizado
    def card(col, titulo, valor, cor, toggle_key=None, toggle_state=None):
        with col:
            st.markdown(
                f"""
                <div style="background-color:{cor}; padding:18px; border-radius:12px; 
                            box-shadow:2px 2px 10px rgba(0,0,0,0.15); text-align:center; color:white;">
                    <h4 style="margin:0;">{titulo}</h4>
                    <p style="font-size:22px; font-weight:bold; margin:8px 0;">{valor}</p>
                </div>
                """,
                unsafe_allow_html=True
            )
            if toggle_key:
                if st.button("👁️", key=toggle_key):
                    st.session_state[toggle_state] = not st.session_state[toggle_state]

    # Cards
    card(col1, "💰 Total Caixa", display_valor, "#27ae60", "btn_caixa", "mostrar_caixa")
    card(col2, "🛒 Vendas Hoje", len(vendas_hoje), "#2980b9")
    card(col3, "⚠️ Produtos Baixos", len(produtos_baixos), "#e67e22")
    card(col4, "📂 Clientes com Conta", display_conta, "#c0392b", "btn_conta", "mostrar_contas")


# ================= Função principal de telas =================
def tela_funcional():
    mostrar_logo(200)
    tela = st.session_state["tela_selecionada"]
    submenu = st.session_state["submenu_selecionado"]

    # ----------------- Estoque -----------------
    if tela == "Estoque":
        if submenu == "Cadastrar Produto":
            box_title("Cadastrar Produto")
            nome = st.text_input("Nome do Produto", key="cad_prod_nome")
            qtd = st.number_input("Quantidade", min_value=1, value=1, key="cad_prod_qtd")
            preco = st.number_input("Preço Unitário", min_value=0.01, value=1.0, format="%.2f", key="cad_prod_preco")
            if st.button("Cadastrar Produto", key="btn_cad_prod"):
                cadastrar_produto(nome, qtd, preco)

        elif submenu == "Produtos":
            box_title("Lista de Produtos")
            if st.session_state["produtos"]:
                df = pd.DataFrame([[p.codigo, p.nome, p.qtd, p.preco] for p in st.session_state["produtos"]],
                                  columns=["Código", "Produto", "Quantidade", "Preço"])
                st.table(df)
            else:
                st.info("Nenhum produto cadastrado")

    # ----------------- Funcionários -----------------
    elif tela == "Funcionários":
        if submenu == "Cadastrar Funcionário":
            box_title("Cadastrar Funcionário")
            nome = st.text_input("Nome do Funcionário", key="cad_func_nome")
            if st.button("Cadastrar Funcionário", key="btn_cad_func"):
                cadastrar_funcionario(nome)

        elif submenu == "Funcionários":
            box_title("Lista de Funcionários")
            if st.session_state["funcionarios"]:
                df = pd.DataFrame([[f.nome] for f in st.session_state["funcionarios"]], columns=["Funcionário"])
                st.table(df)
            else:
                st.info("Nenhum funcionário cadastrado")

        elif submenu == "Remover Funcionário":
            box_title("Remover Funcionário")
            if st.session_state["funcionarios"]:
                nomes = [f.nome for f in st.session_state["funcionarios"]]
                sel = st.selectbox("Escolha o funcionário para remover", nomes, key="select_remover_func")
                if st.button("Remover Funcionário", key="btn_remove_func"):
                    remover_funcionario(sel)
            else:
                st.info("Nenhum funcionário cadastrado")

    # ----------------- Clientes -----------------
    elif tela == "Clientes":
        if submenu == "Histórico":
            box_title("Histórico de Clientes")
            if not st.session_state["clientes"]:
                st.info("Nenhum cliente cadastrado")
            else:
                # expander geral contendo selectbox dos clientes ordenados
                with st.expander("Clientes", expanded=True):
                    nomes_clientes = sorted([c.nome for c in st.session_state["clientes"]])
                    sel_cliente = st.selectbox("Selecione o cliente", nomes_clientes, key="hist_sel_cliente")
                    cliente = next(c for c in st.session_state["clientes"] if c.nome == sel_cliente)
                    historico_reserva = [x for x in cliente.historico if x[5] == "reserva"]
                    if historico_reserva:
                        df = pd.DataFrame(
                            historico_reserva,
                            columns=["Produto", "Qtd", "Total", "Data/Hora", "Funcionário", "Tipo"]
                        )
                        st.table(df)
                    else:
                        st.info("Sem histórico de compras em aberto.")

        elif submenu == "Conta":
            box_title("Gerenciar Conta do Cliente")
            if st.session_state["clientes"]:
                nomes = [c.nome for c in st.session_state["clientes"]]
                sel = st.selectbox("Escolha o cliente", nomes, key="conta_sel_cliente")
                cliente = next(c for c in st.session_state["clientes"] if c.nome == sel)
                total_reserva = sum(x[2] for x in cliente.historico if x[5] == "reserva")
                st.markdown(f"**Total em Reserva:** R$ {total_reserva:.2f}")

                historico_reserva = [x for x in cliente.historico if x[5] == "reserva"]
                if historico_reserva:
                    df = pd.DataFrame(historico_reserva,
                                      columns=["Produto", "Qtd", "Total", "Data/Hora", "Funcionário", "Tipo"])
                    st.table(df)
                else:
                    st.info("Sem compras em aberto.")

                if st.button("Zerar Conta", key="btn_zerar_conta"):
                    for x in cliente.historico:
                        if x[5] == "reserva":
                            x[5] = "pago"
                    st.success(f"Conta de {cliente.nome} zerada.")
            else:
                st.info("Nenhum cliente cadastrado")

    # ----------------- Fornecedores -----------------
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
                df = pd.DataFrame([[f.nome, f.contato, f.produto, f.preco, f.prazo] for f in st.session_state["fornecedores"]],
                                  columns=["Fornecedor", "Contato", "Produto", "Preço", "Prazo"])
                st.table(df)
            else:
                st.info("Nenhum fornecedor cadastrado")

    # ----------------- Vendas -----------------
    elif tela == "Vendas":
        box_title("Registrar Venda")
        if not st.session_state["produtos"] or not st.session_state["funcionarios"]:
            st.info("Cadastre produtos e funcionários antes de registrar vendas.")
        else:
            produtos_display = [f"{p.codigo} - {p.nome}" for p in st.session_state["produtos"]]
            prod_sel = st.selectbox("Produto", produtos_display, key="venda_prod_sel")
            prod_codigo = prod_sel.split(" - ")[0]
            produto = next(p for p in st.session_state["produtos"] if p.codigo == prod_codigo)
            func_sel = st.selectbox("Funcionário", [f.nome for f in st.session_state["funcionarios"]], key="venda_func_sel")
            funcionario = next(f for f in st.session_state["funcionarios"] if f.nome == func_sel)
            cliente_nome = st.text_input("Nome do Cliente (opcional)", key="venda_cliente_nome")
            cliente = cadastrar_cliente(cliente_nome) if cliente_nome else None
            qtd = st.number_input("Quantidade", min_value=1, value=1, key="venda_qtd")
            tipo = st.radio("Tipo de Venda", ["imediata", "reserva"], key="venda_tipo")
            if st.button("Registrar Venda", key="btn_registrar_venda"):
                registrar_venda(produto, funcionario, cliente, qtd, tipo)

    # ----------------- Caixa / Relatórios -----------------
    elif tela == "Caixa":
        if submenu in ["Diário", "Semanal", "Mensal"]:
            box_title(f"Vendas - {submenu}")
            if not st.session_state["vendas"]:
                st.info("Nenhuma venda registrada.")
            else:
                now = datetime.now()
                if submenu == "Diário":
                    vendas_filtradas = [v for v in st.session_state["vendas"] if v[6].date() == now.date()]
                elif submenu == "Semanal":
                    today = now.date()
                    start_week = today - timedelta(days=today.weekday())  # segunda
                    end_week = start_week + timedelta(days=6)  # domingo
                    vendas_filtradas = [v for v in st.session_state["vendas"] if start_week <= v[6].date() <= end_week]
                elif submenu == "Mensal":
                    vendas_filtradas = [v for v in st.session_state["vendas"] if v[6].year == now.year and v[6].month == now.month]

                if vendas_filtradas:
                    df = pd.DataFrame(
                        [[v[1], v[2], v[6].strftime("%d/%m/%Y %H:%M"), v[7], v[5]] for v in vendas_filtradas],
                        columns=["Produto", "Quantidade", "Hora", "Funcionário", "Tipo"]
                    )
                    st.table(df)
                    total_vendas = sum(v[4] for v in vendas_filtradas)
                    st.markdown(f"**Total Vendas ({submenu}): R$ {total_vendas:.2f}**")
                else:
                    st.info(f"Nenhuma venda registrada no período {submenu.lower()}.")

        else:
            # Caixa principal: resumo do caixa
            box_title("Caixa")
            total_caixa = sum(v[4] for v in st.session_state["vendas"] if v[5] == "imediata")
            st.markdown(f"**Total em Caixa:** R$ {total_caixa:.2f}")

# ================= Sidebar (menu) =================
menu_principal = ["Dashboard", "Vendas", "Caixa"]
menu_expansivo = {
    "Estoque": ["Cadastrar Produto", "Produtos"],
    "Funcionários": ["Cadastrar Funcionário", "Funcionários", "Remover Funcionário"],
    "Clientes": ["Histórico", "Conta"],
    "Fornecedores": ["Cadastrar Fornecedor", "Fornecedores"],
    "Relatórios": ["Diário", "Semanal", "Mensal"]  # opcional — você pode mapear para Caixa ou criar tela própria
}

st.sidebar.header("📌 Menu")
for item in menu_principal:
    if st.sidebar.button(item):
        st.session_state["tela_selecionada"] = item
        st.session_state["submenu_selecionado"] = None

# Expanders (árvore) para os demais menus
for item, submenus in menu_expansivo.items():
    exp = st.sidebar.expander(item, expanded=False)
    with exp:
        for sub in submenus:
            # se for Relatórios e você quer que abram sob Caixa, trataremos no clique
            if st.button(sub, key=f"{item}_{sub}"):
                # Mapear Relatórios diretamente para Caixa
                if item == "Relatórios":
                    st.session_state["tela_selecionada"] = "Caixa"
                    # sub será "Diário"/"Semanal"/"Mensal"
                    st.session_state["submenu_selecionado"] = sub
                else:
                    st.session_state["tela_selecionada"] = item if item != "Relatórios" else "Caixa"
                    st.session_state["submenu_selecionado"] = sub

# ================= Render principal =================
if st.session_state["tela_selecionada"] == "Dashboard":
    dashboard()
else:
    tela_funcional()

