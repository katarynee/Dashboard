import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(layout="wide")

relatorio_notas_completo = pd.read_csv("relatorio_notas_completo.csv")
dados_alunos_md = pd.read_csv("dados_alunos_md.csv")
#relatorio_alunos_notas = pd.read_csv

st.title("Panorama Geral por Curso")
nivel_ensino = st.radio('Selecione o Nível de Ensino', ['Técnico', 'Superior', 'Graduação', 'Pós-Graduação'])
cursos = relatorio_notas_completo[relatorio_notas_completo['NIVEL_ENSINO'] == nivel_ensino]['curso'].unique()

if nivel_ensino == 'Técnico':
    modalidades = ['Integrado', 'Concomitante', 'Subsequente']
    modalidade_selecionada = st.selectbox("Escolha a modalidade:", modalidades)

    cursos_filtrados = dados_alunos_md[
        (dados_alunos_md['modalidade'] == modalidade_selecionada) &
        (dados_alunos_md['curso'].isin(cursos))
    ]['curso'].unique()

    d_alunos = dados_alunos_md[
        (dados_alunos_md['modalidade'] == modalidade_selecionada) &
        (dados_alunos_md['curso'].isin(cursos))
    ]
    
else:
    cursos_filtrados = cursos
    d_alunos = dados_alunos_md[dados_alunos_md['curso'].isin(cursos)]

curso_selecionado = st.selectbox("Escolha o curso:", cursos_filtrados)

df_alunos = d_alunos[d_alunos['curso'] == curso_selecionado]
df_notas = relatorio_notas_completo[relatorio_notas_completo['ALUNO_ID'].isin(df_alunos['alunoid'])]

tab1, tab2, tab3 = st.tabs(["Visão Geral", "Análise de Notas", "Análise Socioeconômica"])

limite_maximo = 100000
dados_alunos_md_renda = dados_alunos_md[dados_alunos_md['rendabruta'] <= limite_maximo]
df_alunos_renda = df_alunos[df_alunos['rendabruta'] <= limite_maximo]


#quantidade de alunos matriculados
qt_matriculados = df_alunos[df_alunos['situacao'] == "Matriculado"].shape[0]
#taxa de evasao
qt_evadidos = df_alunos[df_alunos['situacao'] == "Evasão"].shape[0]
qt_alunos = df_alunos['alunoid'].count()
taxa_evasao = qt_evadidos/qt_alunos
#ira medio
ira_medio = df_alunos['ira'].mean()
#renda bruta media
renda_media = df_alunos_renda['rendabruta'].mean()

#ranking de disciplinas
df_situacao_disciplina = df_notas[df_notas['SITUACAO'].isin(['Aprovado', 'Reprovado'])]
df_situacao_disciplina = df_situacao_disciplina.groupby(['DISCIPLINA', 'SITUACAO']).size().unstack(fill_value=0)

df_situacao_disciplina['Taxa_Reprovacao'] = (
    df_situacao_disciplina['Reprovado'] / 
    (df_situacao_disciplina['Aprovado'] + df_situacao_disciplina['Reprovado'])
) * 100

df_situacao_disciplina = df_situacao_disciplina[df_situacao_disciplina['Taxa_Reprovacao'] < 100]

df_situacao_disciplina = df_situacao_disciplina.sort_values(by='Taxa_Reprovacao', ascending=False)
top10_taxa_reprovacao = df_situacao_disciplina.head(10).reset_index()
disciplina_maior_reprovacao = df_situacao_disciplina.index[0]
#nome_d_maior_rep = disciplina_maior_reprovacao['DISCIPLINA'].unique()
taxa_maior_reprovacao = df_situacao_disciplina.iloc[0]['Taxa_Reprovacao']

df_disciplina_maior_reprovacao = df_notas[df_notas['DISCIPLINA'] == disciplina_maior_reprovacao]
media_disciplina_maior_reprovacao = df_disciplina_maior_reprovacao['MEDIA_FINAL_DISCIPLINA'].mean()

fig_ranking = go.Figure()

fig_ranking.add_trace(go.Bar(
    y=top10_taxa_reprovacao['DISCIPLINA'],
    x=top10_taxa_reprovacao['Taxa_Reprovacao'],
    name='Top 10 Disciplinas',
    marker=dict(color='orange'),
    orientation='h'
))

fig_ranking.update_layout(
    xaxis_title='Taxa de Reprovação (%)',
    yaxis_title='Disciplina',
    yaxis=dict(categoryorder='total ascending')
)

fig_ranking.update_traces(textposition='auto', texttemplate='%{x:.2f}%')

#g maiores medias
df_medias_disciplina = df_notas.groupby('DISCIPLINA')['MEDIA_FINAL_DISCIPLINA'].mean().reset_index()
df_medias_disciplina = df_medias_disciplina.sort_values(by='MEDIA_FINAL_DISCIPLINA', ascending=False)
top10_maiores_medias = df_medias_disciplina.head(10)

disciplina_maior_media = df_medias_disciplina.iloc[0]['DISCIPLINA']
maior_media = df_medias_disciplina.iloc[0]['MEDIA_FINAL_DISCIPLINA']


fig_medias = go.Figure()

fig_medias.add_trace(go.Bar(
    y=top10_maiores_medias['DISCIPLINA'],
    x=top10_maiores_medias['MEDIA_FINAL_DISCIPLINA'],
    name='Top 10 Maiores Médias',
    marker=dict(color='#007bff'),
    orientation='h'
))

fig_medias.update_layout(
    xaxis_title='Média Final',
    yaxis_title='Disciplina',
    yaxis=dict(categoryorder='total ascending')
)

fig_medias.update_traces(textposition='auto', texttemplate='%{x:.2f}')

fig_genero = px.pie(df_alunos, 
                    names = 'genero', 
                    labels = {'genero' : 'Gênero'}, 
                    hole = 0.3
                   )

fig_genero.update_layout(
    legend_title='Gênero',
    margin=dict(l=0, r=0, t=0, b=0),
    height=400
)

fig_raca = px.pie(df_alunos,
                   names = 'raca',
                   labels = {'raça' : 'Raça'},
                   hole = 0.3
                  )

fig_raca.update_layout(
    legend_title='Raça',
    margin=dict(l=0, r=0, t=0, b=0),
    height=400
)

with tab1:
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="Quantidade de Alunos Matriculados", value=qt_matriculados)
    with col2:
        st.metric(label="Taxa de Evasão (%)", value=f"{taxa_evasao:.2%}")
    with col3:
        st.metric(label="IRA Médio", value=f"{ira_medio:.2f}")
    with col4:
        st.metric(label="Renda Bruta Média (R$)", value=f"R$ {renda_media:.2f}")

    col1, col2 = st.columns(2)
    with col1:
        st.header("Distribuição por Gênero")
        st.plotly_chart(fig_genero, use_container_width=False)
    with col2:
        st.header("Distribuição por Etnia")
        st.plotly_chart(fig_raca, use_container_width=False)
        
    
    st.header("Ranking disciplinas com maior taxa de Reprovação")
    col5, col6 = st.columns([3,1])
    with col5:
        st.metric(label="Disciplina com Maior Taxa de Reprovação", value=disciplina_maior_reprovacao)
    with col6:
        st.metric(label=f"Média Final da Disciplina", value=f"{media_disciplina_maior_reprovacao:.2f}")
    st.plotly_chart(fig_ranking, use_container_width=False)
    

    st.header("Disciplinas com maiores médias")
    col1, col2 = st.columns([3,1])
    with col1:
        st.metric(label="Disciplina com Maior Média", value=disciplina_maior_media)
    with col2:
        st.metric(label="Média Final da Disciplina", value=f"{maior_media:.2f}")
    st.plotly_chart(fig_medias)
    

with tab2:
    #grafico de linhas notas
    disciplina = st.selectbox('Escolha uma disciplina', df_notas['DISCIPLINA'].unique())
    df_disciplina = df_notas[df_notas['DISCIPLINA'] == disciplina]

    ano_letivo = st.selectbox('Selecione o Ano Letivo', df_disciplina['ANO_LETIVO'].unique()) #add opcao todo período
    df_ano_letivo = df_notas[df_notas['ANO_LETIVO'] == ano_letivo]

    df_disciplina_ano = df_ano_letivo[df_ano_letivo['DISCIPLINA']==disciplina]

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

    #gráfico de aprovados e reprovados

    df_situacao_ano = df_disciplina.groupby(['ANO_LETIVO', 'SITUACAO']).size().unstack(fill_value=0)

    if 'Reprovado' in df_situacao_ano.columns:
        df_situacao_ano['Taxa_Reprovacao'] = (df_situacao_ano['Reprovado'] /
                                            df_situacao_ano.sum(axis=1)) * 100
    else:
        st.warning("A coluna 'Reprovado' não está disponível para a disciplina, nível de ensino e ano letivo selecionados.")
        df_situacao_ano['Taxa_Reprovacao'] = 0

    ano_maior_reprovacao = df_situacao_ano['Taxa_Reprovacao'].idxmax()
    maior_taxa_reprovacao = df_situacao_ano['Taxa_Reprovacao'].max()

    media_taxa_reprovacao = df_situacao_ano['Taxa_Reprovacao'].mean()

    taxa_reprovacao_ano_selecionado = df_situacao_ano.loc[ano_letivo, 'Taxa_Reprovacao']

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
                                yaxis_title='Quantidade de Alunos')

    #gráfico_ranking
    df_situacao_disciplina = df_ano_letivo[df_ano_letivo['SITUACAO'].isin(['Aprovado', 'Reprovado'])]

    df_situacao_disciplina = df_situacao_disciplina.groupby(['DISCIPLINA', 'SITUACAO']).size().unstack(fill_value=0)

    df_situacao_disciplina['Taxa_Reprovacao'] = (
        df_situacao_disciplina['Reprovado'] / 
        (df_situacao_disciplina['Aprovado'] + df_situacao_disciplina['Reprovado'])
    ) * 100

    df_situacao_disciplina = df_situacao_disciplina[df_situacao_disciplina['Taxa_Reprovacao'] < 100]
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

    #graficos pie
    #1
    df_situacao = df_disciplina_ano[df_disciplina_ano['SITUACAO'].isin(['Aprovado', 'Reprovado'])]

    situacao_counts = df_situacao['SITUACAO'].value_counts()

    fig_situacao = go.Figure(data=[go.Pie(
        labels=situacao_counts.index, 
        values=situacao_counts.values,
        hole=0.3, 
        marker=dict(colors=['#007bff', 'orange']) 
    )])
    #2
    df_final_not_null = df_disciplina_ano[df_disciplina_ano['FINAL'].notna()]

    situacao_final_counts = df_final_not_null[df_final_not_null['SITUACAO'].isin(['Aprovado', 'Reprovado'])]['SITUACAO'].value_counts()

    fig_prova_final = go.Figure(data=[go.Pie(
        labels=situacao_final_counts.index, 
        values=situacao_final_counts.values,
        hole=0.3, 
        marker=dict(colors=['#007bff', 'orange']) 
    )])
    #3
    aprovados_sem_final = df_disciplina_ano[(df_disciplina_ano['FINAL'].isna()) & (df_disciplina_ano['SITUACAO'] == 'Aprovado')].shape[0]
    alunos_com_final = df_disciplina_ano[df_disciplina_ano['FINAL'].notna()].shape[0]


    #ranking media
    #g maiores medias

    # Calcular a média final por disciplina
    df_medias_disciplina = df_ano_letivo.groupby('DISCIPLINA')['MEDIA_FINAL_DISCIPLINA'].mean().reset_index()

    # Ordenar as médias da maior para a menor
    df_medias_disciplina = df_medias_disciplina.sort_values(by='MEDIA_FINAL_DISCIPLINA', ascending=False).reset_index(drop=True)

    # Top 10 disciplinas com maiores médias
    top10_maiores_medias = df_medias_disciplina.head(10)

    # Obter os dados da disciplina selecionada
    disciplina_rank = df_medias_disciplina[df_medias_disciplina['DISCIPLINA'] == disciplina]

    # Verificar se a disciplina foi encontrada
    if not disciplina_rank.empty:
        # Se a disciplina foi encontrada, obtemos a posição
        posicao_disciplina_m = df_medias_disciplina[df_medias_disciplina['DISCIPLINA'] == disciplina].index[0] + 1
    else:
        posicao_disciplina_m = None

    disciplina_maior_media = df_medias_disciplina.iloc[0]['DISCIPLINA']
    maior_media = df_medias_disciplina.iloc[0]['MEDIA_FINAL_DISCIPLINA']

    fig_medias_n = go.Figure()

    fig_medias_n.add_trace(go.Bar(
        y=top10_maiores_medias['DISCIPLINA'],
        x=top10_maiores_medias['MEDIA_FINAL_DISCIPLINA'],
        name='Top 10 Maiores Médias',
        marker=dict(color='#007bff'),
        orientation='h'
    ))

    if not disciplina_rank.empty and disciplina not in top10_maiores_medias['DISCIPLINA'].values:
        fig_medias_n.add_trace(go.Bar(
            y=[disciplina],  # Adiciona a disciplina selecionada
            x=disciplina_rank['MEDIA_FINAL_DISCIPLINA'],
            name=f'{disciplina} (Posição: {posicao_disciplina_m}º)',
            marker=dict(color='red'),
            orientation='h'
        ))

    fig_medias_n.update_layout(
        xaxis_title='Média Final',
        yaxis_title='Disciplina',
        yaxis=dict(categoryorder='total ascending'),
        #title=f'Ranking de Maiores Médias por Disciplina - {disciplina} está na {posicao_disciplina}ª posição' if posicao_disciplina else f'Ranking de Maiores Médias por Disciplina'
    )

    fig_medias_n.update_traces(textposition='auto', texttemplate='%{x:.2f}')


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
        st.header(f"Ranking reprovações em {ano_letivo}")
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
        if alunos_com_final > 0:
            fig_direto = go.Figure(data=[go.Pie(
                labels=['Aprovados sem Prova Final', 'Alunos que Fizeram Prova Final'], 
                values=[aprovados_sem_final, alunos_com_final],
                hole=0.3, 
                marker=dict(colors=['#007bff', 'orange']) 
            )])
            st.plotly_chart(fig_direto)
        else:
            st.write("Não há registros de alunos que fizeram a prova final para esta disciplina.")
    
    st.header(f"Disciplinas com maiores médias em {ano_letivo}")
    col1, col2 = st.columns([3,1])
    with col1:
        st.plotly_chart(fig_medias_n)
    with col2:
        st.metric(f"Disciplina com maior média em {ano_letivo}", disciplina_maior_media, f"{maior_media}")
        st.metric(f"Posição de {disciplina} em {ano_letivo}", f"{posicao_disciplina_m}°")
        #st.metric(f"Média de {disciplina} em {ano_letivo}", f"{maior_media}")

with tab3:

    d_alunos['evasao'] = d_alunos['situacao'].apply(lambda x: 1 if x == 'Evasão' else 0)
    dados_alunos_md['evasao'] = dados_alunos_md['situacao'].apply(lambda x: 1 if x == 'Evasão' else 0)

    total_alunos = dados_alunos_md['alunoid'].count()
    total_evadidos = dados_alunos_md['evasao'].sum()
    taxa_evasao_ifma = (total_evadidos / total_alunos) * 100

    df_evadidos_curso = d_alunos[(d_alunos['curso'] == curso_selecionado) & (d_alunos['evasao'] == 1)]

    df_evasao = d_alunos.groupby(['curso']).agg(
    total_alunos_curso=('alunoid', 'count'),
    total_evadidos_curso=('evasao', 'sum')
    ).reset_index()

    df_evasao['taxa_evasao'] = (df_evasao['total_evadidos_curso'] / df_evasao['total_alunos_curso']) * 100

    fig_evasao = px.bar(df_evasao, x='curso', y='taxa_evasao',
                    labels={'taxa_evasao': 'Taxa de Evasão (%)', 'curso': 'Curso'},
                    text_auto='.2f')
    
    fig_evasao.update_traces(marker=dict(color=['lightgrey' if c != curso_selecionado else '#007bff' for c in df_evasao['curso']]))
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

    df_ira = d_alunos.groupby('curso').agg(
        media_ira_curso=('ira', 'mean')
    ).reset_index()

    media_ira_ifma = dados_alunos_md['ira'].mean()

    fig_ira = px.bar(df_ira, 
                    x='media_ira_curso',
                    y='curso',
                    orientation='h',  
                    labels={'media_ira_curso': 'Média de IRA', 'curso': 'Curso'},
                    text_auto='.2f'
                    )

    fig_ira.update_traces(marker=dict(color=['lightgrey' if c != curso_selecionado else 'green' for c in df_ira['curso']]))

    fig_ira.add_shape(
        type="line",
        x0=media_ira_ifma,
        x1=media_ira_ifma,
        y0=-0.5,
        y1=len(df_ira) - 0.5,
        line=dict(color="red", width=2, dash="dash"),
        showlegend=True,
        name="Média de IRA da Instituição"
    )

    fig_ira.update_layout(
        legend=dict(
            orientation='v',
            yanchor='top',
            y=1,
            xanchor='left',
            x=0,
            bgcolor='rgba(255,255,255,0.5)'
        ),
        margin=dict(l=120, r=0, t=0, b=0),
        xaxis_tickformat='.2f'
    )

    d_alunos_renda = d_alunos[d_alunos['rendabruta'] <= limite_maximo]
    df_renda = d_alunos_renda.groupby('curso').agg(
    media_renda_curso=('rendabruta', 'mean')
    ).reset_index()

    media_renda_ifma = dados_alunos_md_renda['rendabruta'].mean()

    fig_renda = px.bar(df_renda, 
                    x='media_renda_curso',
                    y='curso',
                    orientation='h',  
                    labels={'media_renda_curso': 'Renda Bruta Média (R$)', 'curso': 'Curso'},
                    text_auto='.2f')

    # Destaca o curso selecionado com uma cor diferente
    fig_renda.update_traces(marker=dict(color=['lightgrey' if c != curso_selecionado else '#007bff' for c in df_renda['curso']]))

    # Adiciona uma linha de referência para a renda bruta média da instituição
    fig_renda.add_shape(
        type="line",
        x0=media_renda_ifma,
        x1=media_renda_ifma,
        y0=-0.5,
        y1=len(df_renda) - 0.5,
        line=dict(color="red", width=2, dash="dash"),
        showlegend=True,
        name="Renda Bruta Média da Instituição"
    )

    # Ajuste da aparência do layout
    fig_renda.update_layout(
        legend=dict(
            orientation='v',
            yanchor='top',
            y=1,
            xanchor='left',
            x=0,
            bgcolor='rgba(255,255,255,0.5)'
        ),
        margin=dict(l=120, r=0, t=0, b=0),
        xaxis_tickformat='.2f'
    )

    fig_idade = px.histogram(
        df_alunos, 
        x='idade', 
        nbins=20, 
        title=f'Distribuição de Idade no Curso {curso_selecionado}',
        color_discrete_sequence=['orange'] 
    )

    fig_idade.update_layout(
        xaxis=dict(
            dtick=1 
        ),
        bargap=0.003
    )

    
    st.header("Índice de Desempenho Acadêmico por Curso")
    col1, col2 = st.columns([4, 1])
    with col1: 
        st.plotly_chart(fig_ira)
    with col2:
        st.metric(label="IRA Médio", value=f"{ira_medio:.2f}")
        st.metric(label="IRA Médio da Instituição", value=f"{media_ira_ifma:.2f}")
    
    st.header("Taxa de Evasão por Curso")
    col3, col4 = st. columns([4,1])
    with col3:
        st.plotly_chart(fig_evasao)
    with col4: 
        st.metric(label=f"Taxa de Evasão (%)", value=f"{taxa_evasao:.2%}")
        st.metric(label="Taxa de Evasão da Instituição(%)", value=f"{taxa_evasao_ifma:.2f}%")

    st.header("Renda Bruta Média por Curso")
    col5, col6 = st.columns([4,1])
    with col5:
        st.plotly_chart(fig_renda)
    with col6:
        st.metric(label=f"Renda Bruta Média de (R$)", value=f"R$ {renda_media:.2f}")
        st.metric(label="Renda Bruta Média da Instituição (R$)", value=f"R${media_renda_ifma:.2f}")
    
    col7, col8, col9 = st.columns([4, 3, 3])
    with col7:
        st.header("Distribuição por Idade")
        st.plotly_chart(fig_idade)
    with col8:
        st.header("Distribuição por Etnia")
        st.plotly_chart(fig_raca)
    with col9:
        st.header("Distribuição por Gênero")
        st.plotly_chart(fig_genero)
        
    






















