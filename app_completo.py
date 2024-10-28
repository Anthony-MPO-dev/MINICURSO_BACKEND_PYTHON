from flask import Flask, request, jsonify, make_response, render_template, session, redirect, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from os import environ
import os
from werkzeug.security import generate_password_hash, check_password_hash

import pandas as pd
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24) 

# Inicializando o Dash
app_dash = Dash(__name__, server=app, url_base_pathname='/dash/')



# Verifica se está rodando em um ambiente Docker
if os.environ.get('DATABASE_URL'):
    # Configuração para Docker
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_URL')
else:
    # Configuração para ambiente local
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost:5432/postgres'


db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'DB_users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password_hash = generate_password_hash(password)

    def json(self):
        return {'id': self.id, 'username': self.username, 'email': self.email}

with app.app_context():
    db.create_all()

@app.route('/test', methods=['GET'])
def test():
    return make_response(jsonify({'message': 'test route'}), 200)

@app.route('/users', methods=['POST'])
def create_users():
    try:
        data = request.get_json()
        new_user = User(username=data['username'], email=data['email'], password=data['password'])
        db.session.add(new_user)
        db.session.commit()
        return make_response(jsonify({'message': 'user created'}), 201)
    except Exception as e:
        return make_response(jsonify({'message': f'error creating user: {e}'}), 500)

@app.route('/users', methods=['GET'])
def get_users():
    try:
        users = User.query.all()
        return make_response(jsonify({'users': [user.json() for user in users]}), 200)
    except Exception as e:
        return make_response(jsonify({'message': f'error retrieving users: {e}'}), 500)

@app.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    try:
        user = User.query.filter_by(id=id).first()
        if user:
            return make_response(jsonify({'user': user.json()}), 200)
        return make_response(jsonify({'message': 'user not found'}), 404)
    except Exception as e:
        return make_response(jsonify({'message': 'error getting user'}), 500)

@app.route('/users/<int:id>', methods=['PUT'])
def update_user(id):
    try:
        user = User.query.filter_by(id=id).first()
        if user:
            data = request.get_json()
            user.username = data['username'] if 'username' in data else user.username
            user.email = data['email'] if 'email' in data else user.email
            if 'password' in data:
                user.password_hash = generate_password_hash(data['password'])
            db.session.commit()
            return make_response(jsonify({'message': 'user updated'}), 200)
        return make_response(jsonify({'message': 'user not found'}), 404)
    except Exception as e:
        return make_response(jsonify({'message': 'error updating user'}), 500)

@app.route('/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    try:
        user = User.query.filter_by(id=id).first()
        if user:
            db.session.delete(user)
            db.session.commit()
            return make_response(jsonify({'message': 'user deleted'}), 200)
        return make_response(jsonify({'message': 'user not found'}), 404)
    except Exception as e:
        return make_response(jsonify({'message': 'error deleting user'}), 500)

@app.route('/', methods=['GET'])
def home():
    return render_template('home.html')

def validate_user(username, password):
    user = User.query.filter_by(username=username).first()  # Busca o usuário no banco de dados
    if user and check_password_hash(user.password_hash, password):  # Verifica a senha
        return user  # Retorna o objeto do usuário se a senha for válida
    return None

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].upper()
        password = request.form['password'].upper()

        user = validate_user(username, password)  # Função para validar usuário
        
        if user:
            session['username'] = user.username
            flash('Login bem-sucedido!')  # Mensagem de sucesso
            return redirect(url_for('dashboard'))  # Redireciona para o dashboard
        else:
            flash('Usuário ou senha incorretos.')

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.form
        new_user = User(username=data['username'].upper(), email=data['email'].upper(), password=data['password'].upper())
        db.session.add(new_user)
        db.session.commit()
        flash('Registro de usuário bem-sucedido!')  # Mensagem de sucesso
        return redirect('/login')
    return render_template('register.html')

@app.route('/logout', methods=['POST'])  # Certifique-se de que o método POST está permitido
def logout():
    session.pop('username', None)  # Remove o usuário da sessão
    flash('Você saiu com sucesso!', 'success')  # Mensagem de sucesso
    return redirect(url_for('login'))  # Redireciona para a página de login

# Função para ler os dados do CSV
def read_data():
    try:
        df = pd.read_csv('dados/tb_data.csv', sep=';', encoding='ISO-8859-1')
        # Exclui linhas onde 'AnoNotificacao' é nulo ou vazio
        df = df[df['AnoNotificacao'].notnull() & (df['AnoNotificacao'] != '')]

        # Substitui valores vazios ou não numéricos na coluna 'NumeroCasos' por 1
        df['NumeroCasos'] = pd.to_numeric(df['NumeroCasos'], errors='coerce').fillna(1).astype(int)

        df = df.groupby('AnoNotificacao', as_index=False)['NumeroCasos'].sum()

        df.to_csv('test.csv', sep=',')

        return df
    except Exception as e:
        flash(f'Erro na leitura do arquivo: {e}', 'warning')
        print(f'DEU RUIM {e}')
        return redirect(url_for('login'))

# Criando o layout do Dash
app_dash.layout = html.Div([
    dcc.Dropdown(
        id='dropdown',
        options=[{'label': str(ano), 'value': ano} for ano in range(2000, 2024)],
        value=list(range(2000, 2024)),  # Selecionando todos os anos por padrão
        multi=True  # Permite selecionar múltiplos anos
    ),
    dcc.Graph(id='tb-graph')
])

# Callback para atualizar o gráfico
@app_dash.callback(
    Output('tb-graph', 'figure'),
    Input('dropdown', 'value')
)
def update_graph(selected_years):
    df = read_data()  # Leitura dos dados

    # Se selected_years não for uma lista, transforme em lista
    if isinstance(selected_years, int):
        selected_years = [selected_years]
    
    # Filtrando o DataFrame pelos anos selecionados, mas permitindo todos os anos
    if selected_years:  # Verifica se algum ano foi selecionado
        filtered_df = df[df['AnoNotificacao'].isin(selected_years)]
    else:
        filtered_df = df  # Se nenhum ano for selecionado, use todos os dados

    # Verificando se há dados para os anos selecionados
    if filtered_df.empty:
        return px.line()  # Retorna um gráfico vazio se não houver dados
    
    # Criando o gráfico de linha
    fig = px.line(
        filtered_df, 
        x='AnoNotificacao', 
        y='NumeroCasos', 
        title='Número de Casos de TB por Ano',
        labels={'AnoNotificacao': 'Ano de Notificação', 'NumeroCasos': 'Número de Casos'},
        markers=True  # Adiciona marcadores nos pontos de dados
    )

    fig.update_xaxes(title='Ano de Notificação')  # Título do eixo X
    fig.update_yaxes(title='Número de Casos')  # Título do eixo Y
    
    return fig

@app.route('/dash/')
def dash():
    return app_dash.index()

@app.route('/dashboard')
def dashboard():
    username = session.get('username')  # Recupera o nome do usuário da sessão
    if username:
        return render_template('dashboard.html', username=username, app_dash=app_dash)
    else:
        flash('Você precisa estar logado para acessar o dashboard.', 'warning')
        return redirect(url_for('login'))  # Redireciona para a página de login se não estiver logado
        
if __name__ == '__main__':
    app.run(debug=True)
