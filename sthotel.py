import streamlit as st
import pandas as pd
import plotly.express as px

# Simulação do carregamento do DataFrame (o código de carregamento pode ser mantido conforme anterior)
url = "https://drive.google.com/uc?id=16ZHSEwBmZ3v1GcOmaQHcclZuf_sAKaZ3&export=download"
df_faturamento = pd.read_csv(url, engine='python', sep=';')

# Ajustar a coluna 'faturamento' para garantir que os valores estão no formato numérico correto (substituindo ',' por '.' e convertendo para float)
df_faturamento['faturamento'] = df_faturamento['faturamento'].str.replace(',', '.').astype('float')

# Filtrar os dados de 2023 e 2024 separadamente para cálculos e comparações
df_2023 = df_faturamento[df_faturamento['ano'] == 2023]
df_2024 = df_faturamento[df_faturamento['ano'] == 2024]

# Calcular o faturamento total de 2023, excluindo os meses de Novembro e Dezembro
faturamento_total_2023 = df_2023[df_2023["mês"] != "Novembro"]['faturamento'].sum() + df_2023[df_2023["mês"] != "Dezembro"]['faturamento'].sum()

# Calcular o faturamento total de 2024 até outubro
faturamento_total_2024 = df_2024['faturamento'].sum()

# Comparar o faturamento de 2024 com o de 2023 para calcular o crescimento médio
df_2024_comparacao = df_2024.copy()

# Alinhar os dados de faturamento de 2023 até outubro com os de 2024 para comparar mês a mês
df_2024_comparacao['faturamento_2023'] = df_2023['faturamento'][:10].values  # Garantir que estamos comparando apenas até outubro de 2023

# Calcular o crescimento percentual de 2024 em relação a 2023 para cada mês
df_2024_comparacao['crescimento'] = df_2024_comparacao['faturamento'] / df_2024_comparacao['faturamento_2023']

# Calcular o crescimento médio mensal de 2024 em relação a 2023
crescimento_medio = df_2024_comparacao['crescimento'].mean()

# Estimar a projeção para novembro e dezembro de 2024 com base no crescimento médio mensal calculado
faturamento_nov_dez_2023 = df_2023[df_2023["mês"].isin(["Novembro", "Dezembro"])]["faturamento"].mean()

# Projeção de faturamento para novembro de 2024
projecao_novembro_2024 = faturamento_nov_dez_2023 * crescimento_medio

# Ajustar a projeção de dezembro para ser 10% maior que a de novembro
projecao_dezembro_2024 = projecao_novembro_2024 * 1.10  # Dezembro é geralmente maior

# Criar novos DataFrames para os meses de Novembro e Dezembro de 2024 com as projeções ajustadas
df_novembro_2024 = pd.DataFrame({
    "mês": ["Novembro"],
    "ano": [2024],
    "faturamento": [projecao_novembro_2024]
})

df_dezembro_2024 = pd.DataFrame({
    "mês": ["Dezembro"],
    "ano": [2024],
    "faturamento": [projecao_dezembro_2024]
})

# Concatenar os novos meses de novembro e dezembro com o DataFrame de 2024
df_2024 = pd.concat([df_2024, df_novembro_2024, df_dezembro_2024], ignore_index=True)

# Criar o DataFrame de comparação final (2023 e 2024)
df_comparacao = pd.merge(df_2023[['mês', 'faturamento']], 
                          df_2024[['mês', 'faturamento']], 
                          on='mês', 
                          suffixes=(' 2023', ' 2024'))

# Aplicar a formatação monetária para as colunas 'faturamento 2023' e 'faturamento 2024'
df_comparacao['faturamento 2023'] = df_comparacao['faturamento 2023'].apply(lambda x: f"R$ {x:,.2f}")
df_comparacao['faturamento 2024'] = df_comparacao['faturamento 2024'].apply(lambda x: f"R$ {x:,.2f}")

st.write("### Dashboard Faturamento")
st.write("Segue abaixo graficos mostrando o possivel encerramento do ano de acordo com as projeções baseadas no ano passo, e a direita temos uma tabela com o sintetico mensal")


# Exibir o DataFrame no Streamlit
col1, col2 = st.columns([1, 1])  # Definir as colunas para exibir os gráficos e a tabela

# Exibir a tabela na coluna da direita
with col2:
    # Gráfico de 2024 com ondulação e rótulos de dados
    fig_2024 = px.line(df_2024, x='mês', y='faturamento', title="Faturamento 2024",
                       labels={'faturamento': 'Valor de Faturamento', 'mês': 'Mês'},
                       line_shape='spline')  # 'spline' cria uma linha suave com ondulação
    fig_2024.update_traces(
        text=df_2024['faturamento'].apply(lambda x: f"R$ {x:,.2f}"),
        textposition='top center',
        hoverinfo='x+y+text')
    fig_2024.update_layout(showlegend=False, xaxis_showgrid=False, yaxis_showgrid=False)  # Remover linhas de grade
    st.plotly_chart(fig_2024)

# Gráfico de linhas com ondulação suave para os dois anos
# Plotando os gráficos de 2023 e 2024 lado a lado
with col1:

    # Gráfico de 2023 com ondulação e rótulos de dados
    fig_2023 = px.line(df_2023, x='mês', y='faturamento', title="Faturamento 2023",
                       labels={'faturamento': 'Valor de Faturamento', 'mês': 'Mês'},
                       line_shape='spline')
    fig_2023.update_traces(
        text=df_2023['faturamento'].apply(lambda x: f"R$ {x:,.2f}" if isinstance(x, (int, float)) and pd.notnull(x) else ""),
        textposition='top center',
        hoverinfo='x+y+text'
    )
    fig_2023.update_layout(showlegend=False, xaxis_showgrid=False, yaxis_showgrid=False)  # Remover linhas de grade
    st.plotly_chart(fig_2023)

st.write("### Tabela de Faturamento")
st.dataframe(df_comparacao)
