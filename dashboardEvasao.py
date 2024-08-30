import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

#lightblue por #007bff ,  lightgrey por #f1f3f5 , mediumblue por #0056b3 , red por #dc3545

st.set_page_config(layout="wide")

df = pd.read_csv("dados_alunos_md.csv", decimal=".")
df['evasao'] = df['situacao'].apply(lambda x: 1 if x == 'Evasão' else 0)

total_alunos = df['alunoid'].count()
total_evadidos = df['evasao'].sum()
taxa_evasao_ifma = (total_evadidos / total_alunos) * 100

st.sidebar.title("Filtro")
modalidade_selecionada = st.sidebar.selectbox(
    "Selecione a modalidade",
    df['modalidade'].unique()
)

curso_selecionado = st.sidebar.selectbox(
    "Selecione o Curso",
    df[df['modalidade'] == modalidade_selecionada]['curso'].unique()
)

df_filtro = df[df['modalidade'] == modalidade_selecionada]
df_evadidos_curso = df_filtro[(df_filtro['curso'] == curso_selecionado) & (df_filtro['evasao'] == 1)]

df_evasao = df_filtro.groupby(['curso']).agg(
    total_alunos_curso=('alunoid', 'count'),
    total_evadidos_curso=('evasao', 'sum')
).reset_index()

df_evasao['taxa_evasao'] = (df_evasao['total_evadidos_curso'] / df_evasao['total_alunos_curso']) * 100

total_alunos_modalidade = df_filtro['alunoid'].count()
total_evadidos_modalidade = df_filtro['evasao'].sum()
taxa_evasao_modalidade = (total_evadidos_modalidade / total_alunos_modalidade) * 100

fig_evasao = px.bar(df_evasao, x='curso', y='taxa_evasao',
                    labels={'taxa_evasao': 'Taxa de Evasão (%)', 'curso': 'Curso'})

fig_evasao.update_traces(marker=dict(color=['lightgrey' if c != curso_selecionado else '#0056b3' for c in df_evasao['curso']]))
fig_evasao.add_shape(
    type="line",
    x0=-0.5,
    x1=len(df_evasao) - 0.5,
    y0=taxa_evasao_ifma,
    y1=taxa_evasao_ifma,
    line=dict(color="red", width=2, dash="dash"),
    showlegend= True,
    name="Taxa de Evasão da Instituição"
)

fig_evasao.add_shape(
    type="line",
    x0=-0.5,
    x1=len(df_evasao) - 0.5,
    y0=taxa_evasao_modalidade,
    y1=taxa_evasao_modalidade,
    line=dict(color="#007bff", width=2, dash="dash"),
    showlegend=True,
    name="Taxa de Evasão da Modalidade"
)
fig_evasao.update_layout(
    legend=dict(
        orientation='v',
        yanchor='top',
        y=1,
        xanchor='left',  
        x=0,  
        bgcolor='rgba(255,255,255,0.5)'  
    ),
    margin=dict(l=120, r=0, t=0, b=0)  
)

#GRÁFICO 2
df_ira = df_filtro.groupby('curso').agg(
    ira_medio_evadidos=('ira', lambda x: x[df_filtro.loc[x.index, 'evasao'] == 1].mean() if (df_filtro['evasao'] == 1).any() else None),
    ira_medio_nao_evadidos=('ira', lambda x: x[df_filtro.loc[x.index, 'evasao'] == 0].mean() if (df_filtro['evasao'] == 0).any() else None)
).reset_index()

ira_medio_ifma = df['ira'].mean()

fig_ira = go.Figure()

fig_ira.add_trace(go.Bar(
    y=df_ira['curso'],
    x=df_ira['ira_medio_evadidos'],
    name='IRA Médio Evadidos (Selecionado)',
    marker_color=['#0056b3' if c == curso_selecionado else 'darkgray' for c in df_ira['curso']],
    width=0.4,
    orientation='h',
    showlegend=False 
))

fig_ira.add_trace(go.Bar(
    y=df_ira['curso'],
    x=df_ira['ira_medio_nao_evadidos'],
    name='IRA Médio Não Evadidos (Selecionado)',
    marker_color=['#007bff' if c == curso_selecionado else 'lightgray' for c in df_ira['curso']],
    width=0.4,
    orientation='h',
    showlegend=False 
))

if curso_selecionado:
    fig_ira.add_trace(go.Scatter(
        x=[None], y=[None],
        mode='markers',
        marker=dict(size=10, color='#0056b3'),
        name='IRA Médio Evadidos (Selecionado)'
    ))
    fig_ira.add_trace(go.Scatter(
        x=[None], y=[None],
        mode='markers',
        marker=dict(size=10, color='#007bff'),
        name='IRA Médio Não Evadidos (Selecionado)'
    ))

fig_ira.add_trace(go.Scatter(
    y=df_ira['curso'],
    x=[ira_medio_ifma] * len(df_ira['curso']),
    mode='lines',
    name='Média do IRA da Instituição',
    line=dict(color='red', dash='dash'),
    showlegend=True,
))

fig_ira.update_layout(
    title=f'Comparação de IRA Médio - Modalidade: {modalidade_selecionada}',
    yaxis_title='Curso',
    xaxis_title='IRA Médio',
    barmode='group',
    yaxis={'categoryorder': 'total descending'},  # Ordenar por total se desejar
    legend=dict(
        title='Legenda',
        traceorder='normal',
        orientation='v',
        x=0.8,
        y=1,
        bgcolor='rgba(0,0,0,0)',
    ),
    margin=dict(l=0, r=0, t=0, b=0),
    height=500
)

#GRÁFICO 3

fig_hist = px.histogram(df_evadidos_curso, 
                        x='reprovacoes', 
                        nbins=len(df_evadidos_curso['reprovacoes'].unique()), 
                        labels={'reprovacoes':'Número de Reprovações', 'count':'Número de Evadidos'})


fig_hist.update_layout(
    xaxis_title='Número de Reprovações',
    yaxis_title='Número de Evadidos',
    bargap=0.2,
)

#GRAFICO 4

frequencia_contagem = df_evadidos_curso.groupby('frequencia').size().reset_index(name='quantidade_alunos')

fig_frequencia = px.scatter(
    frequencia_contagem,
    x='frequencia',
    y='quantidade_alunos',
    labels={"quantidade_alunos": "Quantidade de Alunos", "frequencia": "Frequência (%)"},
    title=f"Análise de Frequência dos Evadidos - Curso: {curso_selecionado}"
)

fig_frequencia.update_layout(
    xaxis_title="Frequência (%)",
    yaxis_title="Quantidade de Alunos",
)

#GRAFICOS 5 E 6 E 7

fig_genero = px.pie(df_evadidos_curso, 
                         names='genero', 
                         title='Distribuição de Evasão por Gênero',
                         labels={'genero': 'Gênero'},
                         hole=0.3)
fig_genero.update_layout(
    legend_title='Gênero',
    margin=dict(l=0, r=0, t=0, b=0),
    height=400
)

fig_raca = px.pie(df_evadidos_curso, 
                       names='raca', 
                       title='Distribuição de Evasão por Raça',
                       labels={'raca': 'Raça'},
                       hole=0.3)

fig_raca.update_layout(
    legend_title='Raça',
    margin=dict(l=0, r=0, t=0, b=0),
    height=400
)

df_evadidos_not_null = df_evadidos_curso[df_evadidos_curso['forma_acesso_seletivo'].notnull()]

# Gráfico de Evasão por Forma de Acesso (Cotas x Ampla Concorrência)
fig_acesso_seletivo = px.pie(df_evadidos_not_null, 
                             names='forma_acesso_seletivo', 
                             title='Distribuição de Evasão por Forma de Acesso',
                             labels={'forma_acesso_seletivo': 'Forma de Acesso'},
                             hole=0.3)

fig_acesso_seletivo.update_layout(
    legend_title='Forma de Acesso',
    margin=dict(l=0, r=0, t=0, b=0),
    height=400
)
#GRAFICO 8

df_evadidos = df_filtro[df_filtro['evasao'] == 1]

df_renda_bruta_media = df_evadidos.groupby('curso').agg(
    renda_bruta_media=('rendabruta', 'mean')
).reset_index()

fig_renda_bruta = px.bar(df_renda_bruta_media, 
                         x='curso', 
                         y='renda_bruta_media', 
                         #title='Renda Bruta Média dos Evadidos por Curso',
                         labels={'renda_bruta_media': 'Renda Bruta Média', 'curso': 'Curso'},
                         text_auto = '.2f')

fig_renda_bruta.update_traces(marker=dict(color=['lightgrey' if c != curso_selecionado else '#0056b3' for c in df_renda_bruta_media['curso']]))

fig_renda_bruta.update_layout(
    xaxis_title='Curso',
    yaxis_title='Renda Bruta Média (R$)',
    bargap=0.2,
)

#TESTE KPIS
df_curso_selecionado = df_filtro[df_filtro['curso'] == curso_selecionado]

# Cálculos de Evasão por Modalidade e Curso
total_alunos_modalidade = df_filtro['alunoid'].count()
total_evadidos_modalidade = df_filtro['evasao'].sum()
taxa_evasao_modalidade = (total_evadidos_modalidade / total_alunos_modalidade) * 100

total_alunos_curso = df_curso_selecionado['alunoid'].count()
total_evadidos_curso = df_curso_selecionado['evasao'].sum()
taxa_evasao_curso = (total_evadidos_curso / total_alunos_curso) * 100

# Cursos com maior e menor evasão
df_evasao_modalidade = df_filtro.groupby('curso').agg(
    total_evadidos=('evasao', 'sum'),
    taxa_evasao=('evasao', lambda x: (x.sum() / len(x)) * 100)
).reset_index()

curso_maior_evasao = df_evasao_modalidade.loc[df_evasao_modalidade['taxa_evasao'].idxmax(), 'curso']
curso_menor_evasao = df_evasao_modalidade.loc[df_evasao_modalidade['taxa_evasao'].idxmin(), 'curso']


#VIEW

st.title('Dashboard de Evasão')
col1, col2, col3 = st.columns(3)
col1.metric("Taxa de Evasão IFMA", f"{taxa_evasao_ifma:.2f}%")
col2.metric("Taxa de Evasão da Modalidade", f"{taxa_evasao_modalidade:.2f}%")
col3.metric(f"Taxa de Evasão do {curso_selecionado}", f"{taxa_evasao_curso:.2f}%")

col4, col5 = st.columns(2)
col4.metric("Curso com Maior Evasão", curso_maior_evasao)
col5.metric("Curso com Menor Evasão", curso_menor_evasao)


st.subheader('Taxa de Evasão por Curso')
st.plotly_chart(fig_evasao, use_container_width=True)


st.subheader('Comparação de IRA Médio por Curso')
st.plotly_chart(fig_ira, use_container_width=True)


col1, col2 = st.columns(2)

with col1:
    st.subheader('Histograma de Reprovações dos Evadidos')
    st.plotly_chart(fig_hist, use_container_width=True)

with col2:
    st.subheader('Frequência dos Evadidos')
    st.plotly_chart(fig_frequencia, use_container_width=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader('Evasão por Gênero')
    st.plotly_chart(fig_genero, use_container_width=True)

with col2:
    st.subheader('Evasão por Raça')
    st.plotly_chart(fig_raca, use_container_width=True)

with col3:
    st.subheader('Evasão por Forma de Acesso no Seletivo')
    st.plotly_chart(fig_acesso_seletivo, use_container_width=True)



st.subheader('Renda Bruta Média dos Evadidos')
st.plotly_chart(fig_renda_bruta, use_container_width=True)

