# ==================================================
# PRUMO | SISTEMA DE GESTÃO DE VENDAS
# ==================================================
# Estrutura do código:
#   1. Importações
#   2. Login
#   3. Leitura da base e configuração da página
#   4. Seção: cadastrar vendas (barra lateral)
#   5. Seção: vendas cadastradas (tabela)
#   6. Seção: dashboard de vendas (indicadores e gráficos)

# ===============
# 1. Importações    
# ===============
import streamlit as st
import pandas as pd
import plotly.express as px
import hmac

# =========
# 2. Login
# =========
def verificar_login():
    if st.session_state.get("logado"):
        return True

    st.write("# 🔒Login | Prumo")
    st.write("### Sistema de gestão de vendas")
    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        usuarios = st.secrets["usuarios"]
        if usuario in usuarios and hmac.compare_digest(senha, usuarios[usuario]):
            st.session_state["logado"] = True
            st.session_state["usuario"] = usuario
            st.rerun()
        else:
            st.error("Usuário ou senha incorretos.")
    return False

# interrompe a execução do código se o usuário não estiver logado
if not verificar_login():
    st.stop()

# ===========================================
# 3. Leitura da base e configuração da página
# ===========================================
tabela_vendas = pd.read_csv("vendas.csv")

st.set_page_config(page_title="Prumo | Gestão de Vendas", page_icon="📐", layout="wide")

st.title("📐 Prumo")
st.caption("Gestão de vendas para serviços de fachada")
st.write(f"Olá, **{st.session_state['usuario']}**! 👋")

# ==========================================
# 4. Seção: cadastrar vendas (barra lateral)
# ==========================================
# campos do formulário:
st.sidebar.write("## CADASTRAR VENDAS")
data = st.sidebar.date_input("Data", max_value=pd.to_datetime("today"))
vendedor = st.sidebar.selectbox("Vendedor", ["Ana", "Camila", "Pedro"])
produto = st.sidebar.selectbox("Produto", ["Limpeza de Fachada", "Pintura", "Revitalização de Fachada"])
quantidade = st.sidebar.number_input("Quantidade", step=1)
valor = st.sidebar.number_input("Valor", step=0.01, format="%.2f")
cadastrar = st.sidebar.button("Cadastrar")

# botao de sair (retorna para a tela de login)
if st.sidebar.button("Sair"):
    st.session_state["logado"] = False
    st.rerun()

# valida todos os campos e cadastra a venda
if cadastrar:
    if valor == 0 or quantidade == 0 or not vendedor or not produto or not data:
        st.error("Preencha todos os campos corretamente!")
    else:
        nova_venda = pd.DataFrame({
            "data": [data],
            "vendedor": [vendedor],
            "produto": [produto],
            "quantidade": [quantidade],
            "valor": [valor]
    })
        tabela_vendas = pd.concat([tabela_vendas, nova_venda], ignore_index=True)
        tabela_vendas.to_csv("vendas.csv", index=False)
        st.success("Venda cadastrada com sucesso!")

# ======================================
# 5. Seção: vendas cadastradas (tabela)
# ======================================
st.write("## VENDAS CADASTRADAS")
st.dataframe(tabela_vendas)

# função para formatar valores em reais
def formatar_reais(valor):
    return "R$ " + f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

csv = tabela_vendas.to_csv(index=False).encode("utf-8")
st.download_button("📥 Baixar vendas", csv, "vendas.csv", "text/csv")

# ==============================
# 6. Seção: dashboard de vendas 
# ==============================
# função para formatar valores no padrão brasileiro (R$ 1.234,56)
def formatar_reais(valor):
    return "R$ " + f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# cálculo do faturamento (quantidade x valor unitário)
st.write("## DASHBOARD DE VENDAS")
tabela_vendas["total"] = tabela_vendas["quantidade"] * tabela_vendas["valor"]

# filtro por vendedor
opcoes_vendedor = ["Todos"] + list(tabela_vendas["vendedor"].unique())
vendedor_filtro = st.selectbox("Filtrar por vendedor", opcoes_vendedor)

if vendedor_filtro == "Todos":
    tabela_filtrada = tabela_vendas
else:
    tabela_filtrada = tabela_vendas[tabela_vendas["vendedor"] == vendedor_filtro]

faturamento_total = tabela_filtrada["total"].sum()

# indicadores lado a lado
col1, col2, col3 = st.columns(3)
col1.metric("Faturamento Total", formatar_reais(faturamento_total))
col2.metric("Vendas Realizadas", len(tabela_filtrada))
col3.metric("Ticket Médio", formatar_reais(faturamento_total / len(tabela_filtrada)))

# gráfico: vendas por vendedor (barra)
cores = ["#E8833A", "#3B82F6", "#14B8A6"]
grafico_vendedor = px.bar(tabela_filtrada, x="vendedor", y="valor", color="produto", color_discrete_sequence=cores, title="Vendas por Vendedor")
st.plotly_chart(grafico_vendedor)

# gráfico: vendas por produto (pizza)
grafico_produto = px.pie(tabela_filtrada, names="produto", values="quantidade", color_discrete_sequence=cores, title="Vendas por Produto")
st.plotly_chart(grafico_produto)

