import streamlit as st
import pandas as pd 
import plotly.express as px

# Definindo o título e o ícone da página 
# st.set_page_config(page_title="Análise de Vendas", page_icon=":bar_chart:", layout="wide")
st.set_page_config(
    page_title="Dashboard de Salários na Área de Dados",
    page_icon=":bar_chart:",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Carregar os dados
# df = pd.read_csv('https://raw.githubusercontent.com/guilhermeonrails/data-jobs/refs/heads/main/salaries.csv')
# Acima é o dataframe original, mas para este exemplo, vamos usar um CSV local.
# Aquele df_limpo que gerei com análise e limpeza de dados no meu Google Colab.
df = pd.read_csv('data/dados-imersao-python-final-2025.csv')

# Filtros do dashboard
st.sidebar.header("Filtros")

# Filtro de Ano
anos_disponiveis = sorted(df['ano'].unique())
anos_selecionados = st.sidebar.multiselect("Ano", anos_disponiveis, default=anos_disponiveis)

# Filtro de Senioridade
senioridades_disponiveis = sorted(df['senioridade'].unique())
senioridades_selecionadas = st.sidebar.multiselect("Senioridade", senioridades_disponiveis, default=senioridades_disponiveis)

# Filtro por Tipo de Contrato
contratos_disponiveis = sorted(df['contrato'].unique())
contratos_selecionados = st.sidebar.multiselect("Tipo de Contrato", contratos_disponiveis, default=contratos_disponiveis)

# Filtro por Tamanho da Empresa
tamanhos_disponiveis = sorted(df['tamanho_empresa'].unique())
tamanhos_selecionados = st.sidebar.multiselect("Tamanho da Empresa", tamanhos_disponiveis, default=tamanhos_disponiveis)

# --- Filtragem do DataFrame
# O dataframe principal é filtrado com base nas seleções feitas na barra lateral.
df_filtrado = df[
    (df['ano'].isin(anos_selecionados)) &
    (df['senioridade'].isin(senioridades_selecionadas)) &
    (df['contrato'].isin(contratos_selecionados)) &
    (df['tamanho_empresa'].isin(tamanhos_selecionados))
]

# --- Conteúdo Principal ---
st.title("Dashboard de Análise de Salários na Área de Dados")
st.markdown("Explore os dados salariais na área de dados nos últimos anos. Utilize os filtros à esquerda para refinar sua análise.")

# --- Métricas Principais (KPIs) ---
st.subheader("Métricas gerais (Salário anual em USD)")

if not df_filtrado.empty:
    salario_medio = df_filtrado['usd'].mean()
    salario_maximo = df_filtrado['usd'].max()
    total_registros = df_filtrado.shape[0]
    cargo_mais_frequente = df_filtrado['cargo'].mode()[0]
else:
    salario_medio, salario_maximo, total_registros, cargo_mais_comum = 0, 0, 0, ""

col1, col2, col3, col4 = st.columns(4)

col1.metric("Salário médio", f"${salario_medio:.0f}")
col2.metric("Salário máximo", f"${salario_maximo:.0f}")
col3.metric("Total de registros", f"{total_registros:,}")
col4.metric("Cargo mais frequente", cargo_mais_frequente)

st.markdown("---")

# --- Análises Visuais com Plotly ---
st.subheader("Gráficos")

col_graf1, col_graf2 = st.columns(2)
# col_graf1, col_graf2, col_graf3, col_graf4 = st.columns(4)  #st.columns(4) # Exibe os gráficos em 4 colunas no streamlit

# Gráficos de Análise
# Gráfico 1: Top 10 Cargos por Salário Médio
with col_graf1:
    if not df_filtrado.empty:
        top_cargos = df_filtrado.groupby('cargo')['usd'].mean().nlargest(10).sort_values(ascending=True).reset_index()
        grafico_cargos = px.bar(
            top_cargos,
            x='usd',
            y='cargo',
            orientation='h',
            title="Top 10 cargos por salário médio",
            labels={'usd': 'Média salarial anual (USD)', 'cargo': ''}
        )
        grafico_cargos.update_layout(title_x=0.1, yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(grafico_cargos, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de cargos.")

# Gráfico 2: Distribuição de Salários Anuais    
with col_graf2:
    if not df_filtrado.empty:
        grafico_hist = px.histogram(
            df_filtrado,
            x='usd',
            nbins=30,
            title="Distribuição de salários anuais",
            labels={'usd': 'Faixa salarial (USD)', 'count': ''}
        )
        grafico_hist.update_layout(title_x=0.1)
        st.plotly_chart(grafico_hist, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de distribuição.")

# Segunda linha - um gráfico abaixo do outro
st.markdown("---")
col_graf3, col_graf4 = st.columns(2)

# Gráfico 3: Proporção dos tipos de trabalho por profissionais
with col_graf3:
    if not df_filtrado.empty:
        remoto_contagem = df_filtrado['remoto'].value_counts().reset_index()
        remoto_contagem.columns = ['tipo_trabalho', 'quantidade']
        grafico_remoto = px.pie(
            remoto_contagem,
            names='tipo_trabalho',
            values='quantidade',
            title='Proporção dos tipos de trabalho',
            hole=0.5
        )
        grafico_remoto.update_traces(textinfo='percent+label')
        grafico_remoto.update_layout(title_x=0.1)
        st.plotly_chart(grafico_remoto, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico dos tipos de trabalho.")

# Gráfico 4: Salário médio de Data Scientists por país - Aqui pode ser substituído por outro cargo 
# se necessário, desde que o dataframe tenha a coluna 'cargo' e 'residencia_iso3'.
# Exemplo: df_filtrado[df_filtrado['cargo'] == 'Data Engineer']
with col_graf4:
    if not df_filtrado.empty:
        df_ds = df_filtrado[df_filtrado['cargo'] == 'Data Scientist']
        media_ds_pais = df_ds.groupby('residencia_iso3')['usd'].mean().reset_index()
        grafico_paises = px.choropleth(media_ds_pais,
                                    locations='residencia_iso3',
                                    color='usd',
                                    color_continuous_scale='rdylgn',
                                    title='Salário médio de Cientista de Dados por país',
                                    labels={'usd': 'Salário médio (USD)', 'residencia_iso3': 'País'})

        grafico_paises.update_layout(title_x=0.1)
        st.plotly_chart(grafico_paises, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de países.")

# --- Tabela de Dados Detalhados ---
st.markdown("---")
st.subheader("Dados Detalhados")
st.dataframe(df_filtrado)

# --- Conclusão ---
st.markdown("---")  
st.subheader("Conclusão")
st.markdown("""
Este dashboard fornece uma visão abrangente dos salários na área de dados, permitindo que os usuários explorem as tendências salariais ao longo dos anos, comparem cargos e analisem a distribuição de salários.
Utilize os filtros para personalizar a visualização e obter insights específicos sobre o mercado de trabalho na área de dados.
""")

# --- Rodapé ---
st.markdown("---")
st.markdown("Desenvolvido por Clairton da Silva Zerwes")
st.markdown("Fonte Original dos Dados: [https://github.com/guilhermeonrails/data-jobs]")
st.markdown("Código Fonte da Análise e Tratamento de Dados Disponível em: [https://github.com/ClairtonZerwes/projeto-dados-python-2025-analise-tratamento.git]")
st.markdown("Código Fonte para o Streamlit disponível em: [https://github.com/ClairtonZerwes/projeto-dados-python-2025-dashboard-streamlit.git]")
st.markdown("Para sugestões e melhorias, entre em contato: [clairtonzerwes@gmail.com]")

