import os
import dash
from dash import dcc, html
import pandas as pd
import plotly.express as px
from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate

# Configurações
FILE_PATH = os.getenv('FILE_PATH', 'nwg_1001.xlsx')
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'llama2')  # Exemplo: llama2
OLLAMA_URL = os.getenv('OLLAMA_URL', 'http://localhost:11434')

# Inicializa LLM local via Ollama
llm = OllamaLLM(
    model="deepseek-r1",
)

# Prompt para análise de dados e sugestões de gráficos
prompt_template = PromptTemplate(
    input_variables=["columns"],
    template=(
        "Você é um assistente de análise de dados. As colunas disponíveis são: {columns}. "
        "Sugira os melhores 5 gráficos para esses dados e explique brevemente cada um."
    )
)

# Função para gerar gráficos estáticos
def generate_charts(df):
    charts = []
    # 1. Distribuição por Status (pizza)
    if 'Status' in df:
        fig = px.pie(df, names='Status', title='Distribuição de Chamados por Status')
        charts.append(dcc.Graph(figure=fig))
    # 2. Chamados por Unidade
    if 'Unidade' in df:
        df_un = df['Unidade'].value_counts().reset_index()
        df_un.columns = ['Unidade','Qtd']
        fig = px.bar(df_un, x='Unidade', y='Qtd', title='Chamados por Unidade')
        charts.append(dcc.Graph(figure=fig))
    # 3. Evolução Mensal
    if 'Abertura' in df:
        df_ts = df.copy()
        df_ts['Abertura'] = pd.to_datetime(df_ts['Abertura'], errors='coerce')
        df_month = df_ts.groupby(df_ts['Abertura'].dt.to_period('M')).size().reset_index(name='Qtd')
        df_month['Abertura'] = df_month['Abertura'].dt.to_timestamp()
        fig = px.line(df_month, x='Abertura', y='Qtd', title='Chamados Abertos por Mês')
        charts.append(dcc.Graph(figure=fig))
    # 4. Top Usuários
    if 'Usuário' in df:
        top = df['Usuário'].value_counts().nlargest(10).reset_index()
        top.columns = ['Usuário','Qtd']
        fig = px.bar(top, x='Usuário', y='Qtd', title='Top 10 Usuários')
        charts.append(dcc.Graph(figure=fig))
    # 5. Material Utilizado (sim/não)
    if 'Material Utilizado' in df:
        df['MatUsed'] = df['Material Utilizado'].notna().map({True:'Sim',False:'Não'})
        fig = px.pie(df, names='MatUsed', title='Material Utilizado')
        charts.append(dcc.Graph(figure=fig))
    return charts

# Carrega e processa dados
df = pd.read_excel(FILE_PATH, header=17)
if 'Abertura' in df:
    df['Abertura'] = pd.to_datetime(df['Abertura'], errors='coerce')

# Obtem sugestões de gráficos via LLM local
columns = ", ".join(df.columns.tolist())
chain = prompt_template | llm
suggestions = chain.invoke({"columns": columns})
print("Sugestões de gráficos:", suggestions)

# Gera gráficos para exibição
charts = generate_charts(df)

# Monta app Dash
app = dash.Dash(__name__)
app.layout = html.Div([
    html.H1('Dashboard de Chamados com IA'),
    html.Div(html.Pre(suggestions), style={'whiteSpace': 'pre-wrap', 'margin': '20px 0'}),
    *charts
])

if __name__ == '__main__':
    app.run(debug=True)