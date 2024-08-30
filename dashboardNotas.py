import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

df = pd.read_csv('relatorio_notas_completo.csv')
st.set_page_config(layout="wide")
st.title("Dashboard de Notas")

nivel_ensino = st.radio('Selecione o Nível de Ensino', ['Técnico', 'Superior'])
df = df[df['NIVEL_ENSINO'] == nivel_ensino]

disciplina = st.selectbox('Escolha uma disciplina', df['DISCIPLINA'].unique())
df_disciplina = df[df['DISCIPLINA'] == disciplina]

ano_letivo = st.selectbox('Selecione o Ano Letivo', df_disciplina['ANO_LETIVO'].unique()) #add opcao todo período
df_ano_letivo = df[df['ANO_LETIVO'] == ano_letivo]

df_disciplina_ano = df_ano_letivo[df_ano_letivo['DISCIPLINA']==disciplina]

#Gráfico Notas
media_notas = df_disciplina[['NOTA_1', 'NOTA_2', 'MEDIA_FINAL_DISCIPLINA']].mean()

st.header("Notas na disciplina")
anos = df_disciplina['ANO_LETIVO'].unique()
anos_selecionados = st.multiselect('Escolha os anos para análise', anos, default=[])

fig_notas = go.Figure()

fig_notas.add_trace(go.Scatter(x=['NOTA_1', 'NOTA_2', 'MEDIA_FINAL_DISCIPLINA'],
                               y=media_notas,
                               mode='lines+markers',
                               name='Média Geral',
                               line=dict(color='blue')))

df_linha_ano_selec = df_disciplina[df_disciplina['ANO_LETIVO'] == ano_letivo]
media_ano_selec = df_linha_ano_selec[['NOTA_1', 'NOTA_2', 'MEDIA_FINAL_DISCIPLINA']].mean()
fig_notas.add_trace(go.Scatter(x=['NOTA_1', 'NOTA_2', 'MEDIA_FINAL_DISCIPLINA'],
                                   y=media_ano_selec,
                                   mode='lines+markers',
                                   name=f'Média {ano_letivo}',
                                   line=dict(color='purple')))

anos_selecionados = [ano for ano in anos_selecionados if ano != ano_letivo]

for ano in anos_selecionados:
    df_ano = df_disciplina[df_disciplina['ANO_LETIVO'] == ano]
    media_ano = df_ano[['NOTA_1', 'NOTA_2', 'MEDIA_FINAL_DISCIPLINA']].mean()
    fig_notas.add_trace(go.Scatter(x=['NOTA_1', 'NOTA_2', 'MEDIA_FINAL_DISCIPLINA'],
                                   y=media_ano,
                                   mode='lines+markers',
                                   name=f'Média {ano}',
                                   line=dict(dash='dash')))

fig_notas.update_layout(yaxis_title='Média')

media_geral = media_notas.mean()
media_ano_selecionado = media_ano_selec.mean()
variacao_percentual = ((media_ano_selecionado - media_geral) / media_geral) * 100

#Gráfico Aprovações x Reprovações

df_situacao_ano = df_disciplina.groupby(['ANO_LETIVO', 'SITUACAO']).size().unstack(fill_value=0)

if 'Reprovado' in df_situacao_ano.columns:
    df_situacao_ano['Taxa_Reprovacao'] = (df_situacao_ano['Reprovado'] /
                                          df_situacao_ano.sum(axis=1)) * 100
else:
    st.warning("A coluna 'Reprovado' não está disponível para a disciplina, nível de ensino e ano letivo selecionados.")
    df_situacao_ano['Taxa_Reprovacao'] = 0

# 1. Ano com maior taxa de reprovação
ano_maior_reprovacao = df_situacao_ano['Taxa_Reprovacao'].idxmax()
maior_taxa_reprovacao = df_situacao_ano['Taxa_Reprovacao'].max()

# 2. Taxa média de reprovação
media_taxa_reprovacao = df_situacao_ano['Taxa_Reprovacao'].mean()

# 3. Taxa de reprovação do ano selecionado
taxa_reprovacao_ano_selecionado = df_situacao_ano.loc[ano_letivo, 'Taxa_Reprovacao']

# 4. Cálculo do aumento ou diminuição percentual em relação à média
percentual_variacao = ((taxa_reprovacao_ano_selecionado - media_taxa_reprovacao) / media_taxa_reprovacao) * 100


fig_aprov_reprov = go.Figure()

if 'Aprovado' in df_situacao_ano:
    fig_aprov_reprov.add_trace(go.Scatter(x=df_situacao_ano.index,
                                          y=df_situacao_ano['Aprovado'],
                                          mode='lines+markers',
                                          name='Aprovados',
                                          line=dict(color='green')))

if 'Reprovado' in df_situacao_ano:
    fig_aprov_reprov.add_trace(go.Scatter(x=df_situacao_ano.index,
                                          y=df_situacao_ano['Reprovado'],
                                          mode='lines+markers',
                                          name='Reprovados',
                                          line=dict(color='red')))

fig_aprov_reprov.update_layout(xaxis_title='Ano Letivo',
                               yaxis_title='Quantidade de Alunos') #mudar eixo x para aceitar somente os valores dos anos

#Gráfico Ranking de Reprovações
df_situacao_disciplina = df_ano_letivo[df_ano_letivo['SITUACAO'].isin(['Aprovado', 'Reprovado'])]

df_situacao_disciplina = df_situacao_disciplina.groupby(['DISCIPLINA', 'SITUACAO']).size().unstack(fill_value=0)

df_situacao_disciplina['Taxa_Reprovacao'] = (
    df_situacao_disciplina['Reprovado'] / 
    (df_situacao_disciplina['Aprovado'] + df_situacao_disciplina['Reprovado'])
) * 100

df_situacao_disciplina = df_situacao_disciplina.sort_values(by='Taxa_Reprovacao', ascending=False)

top10_taxa_reprovacao = df_situacao_disciplina.head(10).reset_index()

disciplina_rank = df_situacao_disciplina[df_situacao_disciplina.index == disciplina]

disciplina_maior_reprovacao = df_situacao_disciplina.index[0]
taxa_maior_reprovacao = df_situacao_disciplina.iloc[0]['Taxa_Reprovacao']

posicao_disciplina = df_situacao_disciplina.index.get_loc(disciplina) + 1  # Posição 1-based

posicao_anterior = posicao_disciplina - 2 if posicao_disciplina > 2 else posicao_disciplina
var_posicao = posicao_disciplina - posicao_anterior

fig_ranking = go.Figure()

# Adicionar as top 10 disciplinas ao gráfico
fig_ranking.add_trace(go.Bar(
    y=top10_taxa_reprovacao['DISCIPLINA'],
    x=top10_taxa_reprovacao['Taxa_Reprovacao'],
    name='Top 10 Disciplinas',
    marker=dict(color='orange'),
    orientation='h'
))

# Adicionar a barra correspondente à disciplina selecionada, se não estiver no Top 10
if not disciplina_rank.empty and disciplina not in top10_taxa_reprovacao['DISCIPLINA'].values:
    fig_ranking.add_trace(go.Bar(
        y=disciplina_rank.index,
        x=disciplina_rank['Taxa_Reprovacao'],
        name=f'{disciplina} (Posição: {posicao_disciplina}º)',
        marker=dict(color='red'),
        orientation='h'
    ))

# Atualizar o layout do gráfico
fig_ranking.update_layout(
    xaxis_title='Taxa de Reprovação (%)',
    yaxis_title='Disciplina',
    yaxis=dict(categoryorder='total ascending')
)

fig_ranking.update_traces(textposition='auto', texttemplate='%{x:.2f}%')



#gráfico pizza comparação aprovados e reprovados na disciplina

df_situacao = df_disciplina_ano[df_disciplina_ano['SITUACAO'].isin(['Aprovado', 'Reprovado'])]

situacao_counts = df_situacao['SITUACAO'].value_counts()

fig_situacao = go.Figure(data=[go.Pie(
    labels=situacao_counts.index, 
    values=situacao_counts.values,
    hole=0.3, 
    marker=dict(colors=['#007bff', 'orange']) 
)])

#gráfico pizza que analisa qual a chance de um aluno se recuperar após a prova final
df_final_not_null = df_disciplina_ano[df_disciplina_ano['FINAL'].notna()]

situacao_final_counts = df_final_not_null[df_final_not_null['SITUACAO'].isin(['Aprovado', 'Reprovado'])]['SITUACAO'].value_counts()

fig_prova_final = go.Figure(data=[go.Pie(
    labels=situacao_final_counts.index, 
    values=situacao_final_counts.values,
    hole=0.3, 
    marker=dict(colors=['#007bff', 'orange']) 
)])

#gráfico pizza que analisa quantos alunos são aprovados sem precisar de prova final
aprovados_sem_final = df_disciplina_ano[(df_disciplina_ano['FINAL'].isna()) & (df_disciplina_ano['SITUACAO'] == 'Aprovado')].shape[0]
alunos_com_final = df_disciplina_ano[df_disciplina_ano['FINAL'].notna()].shape[0]

fig_direto = go.Figure(data=[go.Pie(
    labels=['Aprovados sem Prova Final', 'Alunos que Fizeram Prova Final'], 
    values=[aprovados_sem_final, alunos_com_final],
    hole=0.3, 
    marker=dict(colors=['#007bff', 'orange']) 
)])

reposicao = df_disciplina_ano[df_disciplina_ano['REPOSICAO'].notna()]

reposicao_nao_final = reposicao[reposicao['FINAL'].isna()].shape[0]

reposicao_final = reposicao[reposicao['FINAL'].notna()].shape[0]

fig_reposicao = go.Figure(data=[go.Pie(
    labels=['Fizeram Reposição e não ficaram de final', 'Fizeram Reposição e ficaram de final'],
    values=[reposicao_nao_final, reposicao_final],
    hole=0.3,
    marker=dict(colors=['#007bff', 'orange'])
)])

#gráfico de barras frequência
media_frequencia_por_ano = df_disciplina.groupby('ANO_LETIVO')['PERCENTUAL_CARGA_HORARIA_FREQUENTADA'].mean().reset_index()

# Gráfico de Barras da Frequência Média
fig_frequencia_media = px.bar(media_frequencia_por_ano,
                              x='ANO_LETIVO',
                              y='PERCENTUAL_CARGA_HORARIA_FREQUENTADA',
                              labels={'PERCENTUAL_CARGA_HORARIA_FREQUENTADA': 'Frequência Média (%)', 'ANO_LETIVO': 'Ano Letivo'},
                              text_auto='.2f')
fig_frequencia_media.update_traces(marker=dict(
    color=['#007bff' if ano == ano_letivo else 'lightgrey' for ano in media_frequencia_por_ano['ANO_LETIVO']]
))

#visualizacao na tela


col1, col2 = st.columns([3,1])
with col1:
    st.plotly_chart(fig_notas)
with col2:
    st.metric("Média Geral da Disciplina", f"{media_geral:.2f}")
    st.metric(f"Média do Ano {ano_letivo}", f"{media_ano_selecionado:.2f}", f"{variacao_percentual:.2f}%")

col1, col2 = st.columns([3,1])
with col1:
    st.header("Situação na disciplina ao longo do tempo")
    st.plotly_chart(fig_aprov_reprov)
with col2:
    st.metric(label="Ano com Maior Taxa de Reprovação", value=f"{ano_maior_reprovacao} ({maior_taxa_reprovacao:.2f}%)")
    st.metric(label="Taxa Média de Reprovação", value=f"{media_taxa_reprovacao:.2f}%")
    st.metric(label=f"Taxa de Reprovação de {ano_letivo}", value=f"{taxa_reprovacao_ano_selecionado:.2f}%", delta=f"{percentual_variacao:.2f}%")


col1, col2 = st.columns([3,1])
with col1:
    st.header("Ranking reprovações")
    st.plotly_chart(fig_ranking)
with col2:
    st.metric(f"Disciplina com Maior Taxa de Reprovação em {ano_letivo}", disciplina_maior_reprovacao, f"{taxa_maior_reprovacao:.2f}%")
    st.metric(f"Posição de {disciplina} em {ano_letivo}", f"{posicao_disciplina}º")

col3, col4 = st.columns(2)
with col3:
    st.header("Aprovados x Reprovados")
    st.plotly_chart(fig_situacao)
with col4:
    st.header("Aprovados sem prova final")
    st.plotly_chart(fig_direto)



col1, col2 = st.columns(2)
with col1:
    st.header("Tendência alunos que fazem prova final")
    st.plotly_chart(fig_prova_final)
with col2:
    st.header("Eficiência da Reposição")
    st.plotly_chart(fig_reposicao)
    
st.header("Frequência média ao longo dos anos")
st.plotly_chart(fig_frequencia_media)
