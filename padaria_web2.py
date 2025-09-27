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
        self.historico = []

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

# login
if "usuario_logado" not in st.session_state:
    st.session_state["usuario_logado"] = None
if "perfil_logado" not in st.session_state:
    st.session_state["perfil_logado"] = None

# telas e visibilidades
if "tela_selecionada" not in st.session_state:
    st.session_state["tela_selecionada"] = "Dashboard"
if "submenu_selecionado" not in st.session_state:
    st.session_state["submenu_selecionado"] = None
if "mostrar_caixa" not in st.session_state:
    st.session_state["mostrar_caixa"] = False
if "mostrar_contas" not in st.session_state:
    st.session_state["mostrar_contas"] = False

# ================= Função Login =================
def tela_login():
    st.title("🔑 Login do Sistema")
    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        # Aqui você pode colocar um banco de usuários real ou JSON
        usuarios = {
            "gerente": {"senha": "123", "perfil": "Gerente"},
            "caixa": {"senha": "123", "perfil": "Caixa"}
        }
        if usuario in usuarios and senha == usuarios[usuario]["senha"]:
            st.session_state["usuario_logado"] = usuario
            st.session_state["perfil_logado"] = usuarios[usuario]["perfil"]
            st.success(f"Bem-vindo(a) {usuarios[usuario]['perfil']}!")
        else:
            st.error("Usuário ou senha incorretos")

def logoff():
    st.session_state["usuario_logado"] = None
    st.session_state["perfil_logado"] = None
    st.success("Desconectado com sucesso!")

# ================= Verifica login =================
if not st.session_state["usuario_logado"]:
    tela_login()
else:
    st.sidebar.markdown(f"**Usuário:** {st.session_state['usuario_logado']} | Perfil: {st.session_state['perfil_logado']}")
    if st.sidebar.button("🔓 Logoff"):
        logoff()
        st.experimental_rerun()

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

    # ================= Aqui entram todas as funções já existentes (cadastrar_produto, registrar_venda, etc.) =================
    # ... TODO: copiar todas as funções de negócio e telas do código original ...
    # ================= Render principal =================
    if st.session_state["tela_selecionada"] == "Dashboard":
        dashboard()
    else:
        tela_funcional()
