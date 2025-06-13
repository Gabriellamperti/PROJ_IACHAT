import os
import json
from flask import Flask, request, jsonify, render_template
import pandas as pd
import plotly.express as px
from langchain_ollama import OllamaLLM

FILE_PATH = os.getenv('FILE_PATH', 'nwg_1001.xlsx')

# Carrega dados do Excel
DF = pd.read_excel(FILE_PATH, header=17)
if 'Abertura' in DF:
    DF['Abertura'] = pd.to_datetime(DF['Abertura'], errors='coerce')

# Inicializa o modelo LLM local (deepseek)
llm = OllamaLLM(model="deepseek-r1")

app = Flask(__name__)


def parse_request(text):
    tlower = text.lower()
    if 'pizza' in tlower or 'pie' in tlower:
        return 'pie', 'Status'
    if 'barra' in tlower or 'bar' in tlower:
        return 'bar', 'Unidade'
    if 'linha' in tlower or 'line' in tlower:
        return 'line', 'Abertura'
    return None, None


def generate_chart(chart_type, column):
    if chart_type == 'pie' and column in DF:
        fig = px.pie(DF, names=column, title=f'{column}')
        return fig
    if chart_type == 'bar' and column in DF:
        counts = DF[column].value_counts().reset_index()
        counts.columns = [column, 'Qtd']
        fig = px.bar(counts, x=column, y='Qtd', title=column)
        return fig
    if chart_type == 'line' and column in DF:
        df_copy = DF.dropna(subset=[column]).copy()
        df_copy[column] = pd.to_datetime(df_copy[column], errors='coerce')
        counts = (
            df_copy.groupby(df_copy[column].dt.to_period('M')).size().reset_index(name='Qtd')
        )
        counts[column] = counts[column].dt.to_timestamp()
        fig = px.line(counts, x=column, y='Qtd', title=column)
        return fig
    return None


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/chat', methods=['POST'])
def chat():
    message = request.json.get('message', '')
    response = llm.invoke(message)
    chart_type, column = parse_request(message)
    fig_json = None
    if chart_type and column:
        fig = generate_chart(chart_type, column)
        if fig:
            fig_json = fig.to_json()
    return jsonify({'response': response, 'figure': fig_json})


if __name__ == '__main__':
    app.run(debug=True)
