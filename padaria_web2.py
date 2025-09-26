# padaria_profissional_completo.py
import os
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from PIL import Image

# ================= Classes =================
class Produto:
    def __init__(self, codigo, nome, qtd, preco, estoque_min=5, data_fab=None, validade=None, lote=""):
        self.codigo = codigo
        self.nome = nome.title()
        self.qtd = qtd
        self.preco = preco
        self.estoque_min = estoque_min
        self.data_fab = data_fab
        self.validade = validade
        self.lote = lote

class Funcionario:
    def __init__(self, nome):
        self.nome = nome.title().strip()

class Cliente:
    def __init__(self, nome):
        self.nome = nome.title().strip()
        self.historico = []  # [produto, qtd, total, data_hora, funcionario, tipo]

class Fornecedor:
    def __init__(self, nome, contato="", produto="", preco=0.0, prazo=0):
        self.nome = nome.title().strip()
        self.contato = contato
        self.produto = produto
        self.preco = preco
        self.prazo = prazo

# ================= Inicialização =================
for key, default in [
    ("produtos", []), ("funcionarios", []), ("clientes", []),
    ("vendas", []), ("fornecedores", []), ("codigo_produto", 1)
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ================= Funções =================
def box_title(texto, icone="📌"):
    st.markdown(f"""
        <div style='padding: 10px; background-color: #f9f9f9;
                    border-radius: 10px; box-shadow: 2px 2px 10px rgba(0,0,0,0.15);
                    margin-bottom: 12px;'>
            <h3 style='text-align: center; color: #4B2E2E; margin:6px 0;'>{icone} {texto}</h3>
        </div>""", unsafe_allow_html=True)

def try_load_logo():
    for path in ["logo.png", "./logo.png", "images/logo.png"]:
        if os.path.exists(path):
            try:
                return Image.open(path)
            except:
                continue
    return None

def cadastrar_produto(nome,qtd,preco):
    codigo = str(st.session_state["codigo_produto"]).zfill(3)
    st.session_state["produtos"].append(Produto(codigo,nome,int(qtd),float(preco)))
    st.session_state["codigo_produto"] += 1
    st.success(f"Produto {nome} cadastrado com código {codigo}.")

def cadastrar_funcionario(nome):
    if nome.strip() == "":
        st.error("Digite o nome.")
        return
    if nome.title() in [f.nome for f in st.session_state["funcionarios"]]:
        st.warning("Funcionário já cadastrado.")
    else:
        st.session_state["funcionarios"].append(Funcionario(nome))
        st.success(f"Funcionário {nome} cadastrado.")

def cadastrar_cliente(nome):
    if nome.strip() == "":
        st.error("Digite o nome do cliente.")
        return
    for c in st.session_state["clientes"]:
        if c.nome.lower() == nome.lower():
            return c
    novo = Cliente(nome)
    st.session_state["clientes"].append(novo)
    st.success(f"Cliente {nome} cadastrado.")
    return novo

def registrar_venda(produto_obj, funcionario_obj, cliente_obj, qtd, tipo):
    qtd = int(qtd)
    if qtd <= 0:
        st.error("Quantidade inválida.")
        return
    if tipo=="imediata" and qtd>produto_obj.qtd:
        st.error("Quantidade insuficiente no estoque!")
        return
    # Atualiza estoque se venda imediata
    if tipo=="imediata":
        produto_obj.qtd -= qtd
    total = qtd*produto_obj.preco
    data_hora = datetime.now()
    st.session_state["vendas"].append([produto_obj.codigo,produto_obj.nome,qtd,produto_obj.preco,total,tipo,data_hora,cliente_obj.nome])
    cliente_obj.historico.append([produto_obj.nome,qtd,total,data_hora,funcionario_obj.nome,tipo])
    st.success(f"Venda registrada: {qtd}x {produto_obj.nome} para {cliente_obj.nome} ({tipo}).")
    if produto_obj.qtd <= produto_obj.estoque_min:
        st.warning(f"⚠ Estoque baixo de {produto_obj.nome}: {produto_obj.qtd} unidades restantes!")

def zerar_conta_cliente(cliente_obj):
    for compra in cliente_obj.historico:
        if compra[5]=="reserva":
            compra[5]="pago"
    st.success(f"Conta do cliente {cliente_obj.nome} zerada (pagamentos realizados).")

# ================= Cabeçalho =================
logo = try_load_logo()
if logo:
    cols = st.columns([1,2,1])
    cols[1].image(logo,width=260)
else:
    st.markdown("<h1 style='text-align:center; color:#4B2E2E;'>🥖 Lucio Pães</h1>", unsafe_allow_html=True)

# ================= Menu lateral =================
st.sidebar.header("📌 Menu")

with st.sidebar.expander("Estoque"):
    estoque_opcao = st.radio("Escolha", ["Cadastrar Produto","Produtos"], key="menu_estoque")
with st.sidebar.expander("Funcionários"):
    func_opcao = st.radio("Escolha", ["Cadastrar Funcionário","Funcionários"], key="menu_funcionarios")
with st.sidebar.expander("Clientes"):
    cliente_opcao = st.radio("Escolha", ["Histórico","Conta"], key="menu_clientes")
venda_opcao = st.sidebar.button("Venda")
caixa_opcao = st.sidebar.button("Caixa")
with st.sidebar.expander("Fornecedores"):
    fornecedor_opcao = st.radio("Escolha", ["Cadastrar Fornecedor"], key="menu_fornecedor")
with st.sidebar.expander("Relatórios"):
    relatorio_opcao = st.radio("Escolha", ["Diário","Semanal","Mensal"], key="menu_relatorios")

# ================= Telas =================
if 'estoque_opcao' in locals():
    if estoque_opcao=="Cadastrar Produto":
        box_title("Cadastrar Produto")
        nome = st.text_input("Nome do Produto")
        qtd = st.number_input("Quantidade",min_value=1,step=1)
        preco = st.number_input("Preço unitário",min_value=0.01,step=0.01,format="%.2f")
        if st.button("Cadastrar"):
            cadastrar_produto(nome,qtd,preco)
    else:
        box_title("Produtos")
        if st.session_state["produtos"]:
            df = pd.DataFrame([[p.codigo,p.nome,p.qtd,p.preco] for p in st.session_state["produtos"]],
                              columns=["Código","Produto","Qtd","Preço"])
            st.table(df)
        else:
            st.info("Nenhum produto cadastrado.")

if 'func_opcao' in locals():
    if func_opcao=="Cadastrar Funcionário":
        box_title("Cadastrar Funcionário")
        nome = st.text_input("Nome do Funcionário")
        if st.button("Cadastrar Funcionário"):
            cadastrar_funcionario(nome)
    else:
        box_title("Funcionários")
        if st.session_state["funcionarios"]:
            for f in st.session_state["funcionarios"]:
                st.write(f.nome)
        else:
            st.info("Nenhum funcionário cadastrado.")

if 'cliente_opcao' in locals():
    if cliente_opcao=="Histórico":
        box_title("Histórico Clientes")
        for c in st.session_state["clientes"]:
            st.markdown(f"### {c.nome}")
            if c.historico:
                df = pd.DataFrame([[h[0],h[1],h[2],h[3].strftime('%d/%m %H:%M'),h[4],h[5]] for h in c.historico],
                                  columns=["Produto","Qtd","Total","Data/Hora","Funcionário","Tipo"])
                st.table(df)
            else:
                st.info("Sem histórico.")
    else:
        box_title("Conta Clientes")
        for c in st.session_state["clientes"]:
            saldo = sum(h[2] for h in c.historico if h[5]=="reserva")
            st.write(f"{c.nome}: R$ {saldo:.2f}")
            if saldo>0:
                if st.button(f"Zerar conta {c.nome}"):
                    zerar_conta_cliente(c)

if venda_opcao:
    box_title("Registrar Venda")
    if not st.session_state["produtos"] or not st.session_state["funcionarios"]:
        st.info("Cadastre produtos e funcionários antes.")
    else:
        nome_cliente = st.text_input("Nome do Cliente")
        cliente_obj = cadastrar_cliente(nome_cliente)
        produtos_display = [f"{p.codigo} - {p.nome}" for p in st.session_state["produtos"]]
        prod_sel = st.selectbox("Produto",produtos_display)
        prod_obj = next(p for p in st.session_state["produtos"] if p.codigo==prod_sel.split(" - ")[0])
        func_sel = st.selectbox("Funcionário",[f.nome for f in st.session_state["funcionarios"]])
        func_obj = next(f for f in st.session_state["funcionarios"] if f.nome==func_sel)
        qtd = st.number_input("Quantidade",min_value=1,step=1)
        tipo = st.radio("Tipo de venda",["imediata","reserva"])
        if st.button("Registrar Venda"):
            registrar_venda(prod_obj,func_obj,cliente_obj,qtd,tipo)

if caixa_opcao:
    box_title("Caixa do Dia")
    hoje = datetime.now().date()
    vendas_dia = [v for v in st.session_state["vendas"] if v[5]=="imediata" and v[6].date()==hoje]
    if vendas_dia:
        df = pd.DataFrame([[v[1],v[2],v[3],v[4],v[7],v[4]] for v in vendas_dia],
                          columns=["Produto","Qtd","Preço Unit","Total","Cliente","Total"])
        st.table(df)
        total_dia = sum(v[4] for v in vendas_dia)
        st.markdown(f"### TOTAL DO DIA: R$ {total_dia:.2f}")
    else:
        st.info("Nenhuma venda hoje.")

if 'fornecedor_opcao' in locals():
    if fornecedor_opcao=="Cadastrar Fornecedor":
        box_title("Cadastrar Fornecedor")
        nome = st.text_input("Nome do Fornecedor")
        contato = st.text_input("Contato")
        produto_f = st.text_input("Produto fornecido")
        preco_f = st.number_input("Preço",min_value=0.0,step=0.01)
        prazo = st.number_input("Prazo entrega (dias)",min_value=0,step=1)
        if st.button("Cadastrar Fornecedor"):
            st.session_state["fornecedores"].append(Fornecedor(nome,contato,produto_f,preco_f,prazo))
            st.success(f"Fornecedor {nome} cadastrado.")

if 'relatorio_opcao' in locals():
    box_title(f"Relatório {relatorio_opcao}")
    if relatorio_opcao=="Diário":
        inicio = datetime.now() - timedelta(days=1)
    elif relatorio_opcao=="Semanal":
        inicio = datetime.now() - timedelta(days=7)
    else:
        inicio = datetime.now() - timedelta(days=30)
    vendas_rel = [v for v in st.session_state["vendas"] if v[6]>=inicio]
    if vendas_rel:
        df = pd.DataFrame([[v[1],v[2],v[3],v[4],v[7],v[4]] for v in vendas_rel],
                          columns=["Produto","Qtd","Preço Unit","Total","Cliente","Total"])
        st.table(df)
        total = sum(v[4] for v in vendas_rel)
        st.markdown(f"### Total: R$ {total:.2f}")
    else:
        st.info("Nenhuma venda nesse período.")
