# Importação das bibliotecas necessárias
import mysql.connector  # Para conectar e interagir com o banco de dados MySQL
import tkinter as tk  # Para a interface gráfica com Tkinter
from tkinter import ttk, messagebox as msgbx  # Para criar botões, caixas de mensagem e outros widgets do Tkinter
from datetime import datetime  # Para trabalhar com data e hora (não utilizado diretamente aqui, mas pode ser útil)
from PIL import Image, ImageTk  # Para carregar e manipular imagens usando a biblioteca PIL (Python Imaging Library)
from dados_quiz import *  # Importa os dados do quiz de um módulo externo (presumivelmente contém as perguntas e respostas)

# Função para conectar ao banco de dados MySQL
def conectar_db():
    return mysql.connector.connect(
        host='localhost',  # Define o host do banco de dados
        user='root',  # Define o usuário do banco de dados
        password='root',  # Define a senha do banco de dados (neste caso, vazia)
        database='quiz_game'  # Define o nome do banco de dados a ser usado
    )

# Função para salvar a pontuação do usuário no banco de dados
def salvar_pontuacao(usuario_id, pontuacao, tipo_quiz):
    conn = conectar_db()  # Estabelece a conexão com o banco de dados
    cursor = conn.cursor()  # Cria um cursor para executar as consultas no banco de dados
    data_atual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Obtém a data e hora atual no formato adequado
    query = """
        INSERT INTO pontos (usuario_id, pontuacao, data, tipo_quiz)
        VALUES (%s, %s, %s, %s)
    """  # Definindo a consulta SQL para inserir a pontuação do usuário
    cursor.execute(query, (usuario_id, pontuacao, data_atual, tipo_quiz))  # Executa a consulta com os dados fornecidos
    conn.commit()  # Confirma a execução da consulta
    cursor.close()  # Fecha o cursor
    conn.close()  # Fecha a conexão com o banco de dados

# Função para obter o ID do usuário a partir do e-mail
def obter_id_usuario(email):
    conn = conectar_db()  # Estabelece a conexão com o banco de dados
    cursor = conn.cursor()  # Cria um cursor para executar as consultas no banco de dados
    query = "SELECT id FROM usuarios WHERE email = %s"  # Consulta SQL para buscar o ID do usuário pelo e-mail
    cursor.execute(query, (email,))  # Executa a consulta passando o e-mail como parâmetro
    resultado = cursor.fetchone()  # Obtém o primeiro resultado da consulta (se houver)
    cursor.close()  # Fecha o cursor
    conn.close()  # Fecha a conexão com o banco de dados
    return resultado[0] if resultado else None  # Retorna o ID do usuário, ou None se não encontrado (operador ternário)

# Função para salvar os dados do usuário no banco de dados
def salvar_usuario(nome, email, senha):
    conn = conectar_db()  # Estabelece a conexão com o banco de dados
    cursor = conn.cursor()  # Cria um cursor para executar as consultas no banco de dados
    cursor.execute(''' 
        INSERT INTO usuarios (nome, email, senha)
        VALUES (%s, %s, %s)
    ''', (nome, email, senha))  # Executa a consulta SQL para inserir os dados do usuário no banco de dados
    conn.commit()  # Confirma a execução da consulta
    cursor.close()  # Fecha o cursor
    conn.close()  # Fecha a conexão com o banco de dados

# Função para carregar o ranking de pontuações
def carregar_ranking():
    conn = conectar_db()  # Estabelece a conexão com o banco de dados
    cursor = conn.cursor()  # Cria um cursor para executar as consultas no banco de dados
    
    # Consulta para pegar o nome do usuário, a pontuação, a data e o tipo do quiz, ordenado pela pontuação
    cursor.execute(''' 
        SELECT u.nome, p.pontuacao, p.data, p.tipo_quiz
        FROM pontos p
        JOIN usuarios u ON p.usuario_id = u.id
        ORDER BY p.pontuacao DESC  # Ordena os resultados pela pontuação de forma decrescente
        LIMIT 10  # Limita a consulta aos 10 melhores resultados
    ''')

    ranking = cursor.fetchall()  # Obtém todos os resultados da consulta
    cursor.close()  # Fecha o cursor
    conn.close()  # Fecha a conexão com o banco de dados
    return ranking  # Retorna os resultados obtidos (ranking)

# Função para verificar o login do usuário
def verificar_login(email, senha):
    conn = conectar_db()  # Estabelece a conexão com o banco de dados
    cursor = conn.cursor()  # Cria um cursor para executar as consultas no banco de dados
    cursor.execute(''' 
        SELECT id, nome FROM usuarios WHERE email = %s AND senha = %s
    ''', (email, senha))  # Executa a consulta para buscar o usuário pelo e-mail e senha fornecidos
    usuario = cursor.fetchone()  # Obtém o primeiro resultado da consulta (se houver)
    cursor.close()  # Fecha o cursor
    conn.close()  # Fecha a conexão com o banco de dados
    return usuario  # Retorna os dados do usuário (ID e nome) ou None se não encontrado

# Função para carregar perguntas de uma categoria
def carregar_perguntas_por_categoria(categoria):
    if categoria not in dados_quiz:  # Verifica se a categoria existe nos dados do quiz
        msgbx.showerror("Erro", f"Categoria {categoria} não encontrada.")  # Exibe uma mensagem de erro se a categoria não existir
        return [], [], []  # Retorna listas vazias para perguntas, opções e respostas

    perguntas = dados_quiz[categoria]["question"]  # Obtém as perguntas da categoria especificada
    opcoes = dados_quiz[categoria]["options"]  # Obtém as opções de resposta da categoria
    respostas = dados_quiz[categoria]["answer"]  # Obtém as respostas corretas da categoria

    return perguntas, opcoes, respostas  # Retorna as perguntas, opções e respostas

# Função para iniciar o quiz
def iniciar_quiz(categoria, nome_usuario, email_usuario):
    perguntas, opcoes, respostas = carregar_perguntas_por_categoria(categoria)  # Carrega as perguntas, opções e respostas da categoria
    if not perguntas:  # Verifica se não há perguntas carregadas
        return  # Se não houver perguntas, a função é encerrada sem iniciar o quiz
    quiz = Quiz(nome_usuario, email_usuario, categoria, perguntas, opcoes, respostas)  # Cria um objeto Quiz com os dados carregados
    quiz.iniciar()  # Inicia o quiz


# Classe para a tela inicial do quiz
class TelaInicial:
    def __init__(self):
        self.gui = tk.Tk()  # Cria a instância da janela principal do Tkinter
        self.carregar_imagem_fundo()  # Chama o método para carregar a imagem de fundo
        self.gui.attributes('-fullscreen', True)  # Define a janela como em tela cheia
        self.gui.title("Tela Inicial - Quiz")  # Define o título da janela
        self.gui.configure(bg="white")  # Configura a cor de fundo da tela principal
        self.exibir_interface()  # Chama o método para exibir a interface gráfica

    def carregar_imagem_fundo(self):
        # Carregar a imagem (substitua o caminho pelo caminho correto da sua imagem)
        caminho_imagem = "background3.png"  # Caminho da imagem de fundo
        imagem_fundo = Image.open(caminho_imagem)  # Abre a imagem de fundo
        imagem_fundo = imagem_fundo.resize((self.gui.winfo_screenwidth(), self.gui.winfo_screenheight()))  # Redimensiona a imagem para o tamanho da tela
        self.imagem_fundo_tk = ImageTk.PhotoImage(imagem_fundo)  # Converte a imagem para o formato utilizado pelo Tkinter

        # Criar um canvas para o fundo
        self.canvas = tk.Canvas(self.gui, width=self.gui.winfo_screenwidth(), height=self.gui.winfo_screenheight())  # Cria o canvas com o tamanho da tela
        self.canvas.pack(fill="both", expand=True)  # Adiciona o canvas à tela e faz ele expandir

        # Adicionar a imagem no canvas
        self.canvas.create_image(0, 0, image=self.imagem_fundo_tk, anchor="nw")  # Coloca a imagem no canvas com âncora no canto superior esquerdo

    def exibir_interface(self):
        # Mensagem de boas-vindas com fundo preto ocupando 100% da largura da tela
        mensagem_bem_vindo = tk.Label(self.gui, text="Bem Vindo ao Quiz, Tec e Dev de Algoritmos !", 
                                      font=('Arial', 24, 'bold'), fg="#ADD8E6", bg="black", width=100, height=3)  # Cria o rótulo de boas-vindas
        mensagem_bem_vindo.place(relx=0.5, rely=0.1, anchor="n")  # Centraliza na parte superior da tela

        # Frame para os botões de login e registro, com altura ajustada
        frame_botoes = tk.Frame(self.gui, bg=None)  # Cria um frame para os botões sem fundo
        frame_botoes.place(relx=0.5, rely=0.55, anchor="center", relheight=0.25, relwidth=0.45)  # Ajusta a posição e o tamanho do frame

        # Configura o grid para garantir o alinhamento
        frame_botoes.grid_rowconfigure(0, weight=1)  # Configura a primeira linha para ter peso
        frame_botoes.grid_rowconfigure(1, weight=1)  # Configura a segunda linha para ter peso
        frame_botoes.grid_columnconfigure(0, weight=1)  # Configura a primeira coluna para ter peso
        frame_botoes.grid_columnconfigure(1, weight=1)  # Configura a segunda coluna para ter peso

        # Aumentando o texto da label e colocando em negrito
        label_opcao = tk.Label(frame_botoes, text="Já possui registro?", font=('Arial', 16, 'bold'), fg="black")  # Cria a label de opção
        label_opcao.grid(row=0, column=0, columnspan=2, pady=20, sticky="nsew")  # Centraliza a label no grid

        # Botão de login
        botao_login = ttk.Button(frame_botoes, text="Login", command=self.tela_login)  # Cria o botão de login
        botao_login.grid(row=1, column=0, padx=10, sticky="nsew")  # Posiciona o botão no grid

        # Botão de registro
        botao_registro = ttk.Button(frame_botoes, text="Registrar", command=self.tela_registro)  # Cria o botão de registrar
        botao_registro.grid(row=1, column=1, padx=10, sticky="nsew")  # Posiciona o botão no grid

        # Exibir o ranking
        self.exibir_ranking()  # Chama o método para exibir o ranking

    def exibir_ranking(self):
        # Carregar os dados do ranking
        ranking = carregar_ranking()  # Obtém os dados do ranking

        # Frame para o ranking, com altura ajustada para ser igual ao frame dos botões
        frame_ranking = tk.Frame(self.gui, bg=None)  # Cria um frame para o ranking
        frame_ranking.place(relx=0.5, rely=0.8, anchor="center", relheight=0.25, relwidth=0.45)  # Ajusta a posição e o tamanho do frame

        # Configura o grid para garantir o alinhamento
        frame_ranking.grid_rowconfigure(0, weight=1)  # Configura a primeira linha do frame para ter peso
        frame_ranking.grid_rowconfigure(1, weight=1)  # Configura a segunda linha do frame para ter peso
        frame_ranking.grid_columnconfigure(0, weight=1)  # Configura a primeira coluna do frame para ter peso

        # Título do ranking
        tk.Label(frame_ranking, text="Ranking Geral de Pontuação", font=('Arial', 14, 'bold'), bg=None, fg="black").grid(row=0, column=0, pady=10, sticky="nsew")  # Cria o título do ranking

        # Treeview para mostrar o ranking
        treeview = ttk.Treeview(frame_ranking, columns=("Nome", "Pontuação", "Data", "Tipo Quiz"), show="headings")  # Cria a tabela para exibir o ranking
        treeview.grid(row=1, column=0, sticky="nsew")  # Posiciona a tabela no grid

        # Definir cabeçalhos da tabela
        treeview.heading("Nome", text="Nome")  # Define o cabeçalho para a coluna Nome
        treeview.heading("Pontuação", text="Pontuação")  # Define o cabeçalho para a coluna Pontuação
        treeview.heading("Data", text="Data")  # Define o cabeçalho para a coluna Data
        treeview.heading("Tipo Quiz", text="Tipo Quiz")  # Define o cabeçalho para a coluna Tipo Quiz

        # Inserir os dados do ranking na tabela
        for i, (nome, pontuacao, data, tipo_quiz) in enumerate(ranking, start=1):  # Percorre os dados do ranking
            treeview.insert("", "end", values=(nome, pontuacao, data, tipo_quiz))  # Insere os dados na tabela

        # Definir a largura das colunas da tabela
        treeview.column("Nome", width=200, anchor="center")  # Define a largura da coluna Nome
        treeview.column("Pontuação", width=100, anchor="center")  # Define a largura da coluna Pontuação
        treeview.column("Data", width=150, anchor="center")  # Define a largura da coluna Data
        treeview.column("Tipo Quiz", width=150, anchor="center")  # Define a largura da coluna Tipo Quiz

        # Botão de "Sair" abaixo do ranking
        botao_sair = ttk.Button(self.gui, text="Sair", command=self.gui.destroy, style="TButton")  # Cria o botão de sair
        botao_sair.place(relx=0.5, rely=0.95, anchor="center", y=10)  # Posiciona o botão de sair abaixo do ranking

    def tela_login(self):
        self.gui.destroy()  # Fecha a tela inicial
        TelaLogin()  # Abre a tela de login

    def tela_registro(self):
        self.gui.destroy()  # Fecha a tela inicial
        TelaRegistro()  # Abre a tela de registro

    def iniciar(self):
        self.gui.mainloop()  # Inicia o loop da interface gráfica para a tela inicial

# Classe para a tela de login
class TelaLogin:
    def __init__(self):
        self.gui = tk.Tk()  # Cria a instância da janela principal do Tkinter
        self.gui.attributes('-fullscreen', True)  # Define a janela como em tela cheia
        self.gui.title("Login - Quiz")  # Define o título da janela
        self.exibir_interface()  # Chama o método para exibir a interface gráfica da tela de login

    def exibir_interface(self):
        # Adicionar a Label de Título "Tela de Login"
        titulo_label = tk.Label(self.gui, text="Tela de Login", 
                                font=('Arial', 24, 'bold'), fg="#ADD8E6", bg="black", width=100, height=3)  # Cria o rótulo de título
        titulo_label.place(relx=0.5, rely=0.1, anchor="n")  # Centraliza o título no topo da tela

        # Frame para os campos de email, senha e botões
        frame = tk.Frame(self.gui)  # Cria um frame para os campos de login
        frame.place(relx=0.5, rely=0.4, anchor="center")  # Posiciona o frame no centro da tela

        tk.Label(frame, text="E-mail:", font=('Arial', 12)).grid(row=0, column=0, pady=10, sticky="w")  # Cria o rótulo para o campo de e-mail
        self.entry_email = tk.Entry(frame, font=('Arial', 12))  # Cria o campo de entrada para o e-mail
        self.entry_email.grid(row=0, column=1, pady=10)  # Posiciona o campo de entrada no grid

        tk.Label(frame, text="Senha:", font=('Arial', 12)).grid(row=1, column=0, pady=10, sticky="w")  # Cria o rótulo para o campo de senha
        self.entry_senha = tk.Entry(frame, font=('Arial', 12), show="*")  # Cria o campo de entrada para a senha (com máscara)
        self.entry_senha.grid(row=1, column=1, pady=10)  # Posiciona o campo de entrada no grid

        ttk.Button(frame, text="Login", command=self.validar_login).grid(row=2, column=0, columnspan=2, pady=20)  # Cria o botão de login
        ttk.Button(self.gui, text="Voltar", command=self.voltar).place(relx=0.5, rely=0.85, anchor="center")  # Cria o botão de voltar

    def validar_login(self):
        email = self.entry_email.get()  # Obtém o valor do e-mail
        senha = self.entry_senha.get()  # Obtém o valor da senha

        if not email or not senha:  # Verifica se os campos estão preenchidos
            msgbx.showerror("Erro", "Por favor, preencha todos os campos.")  # Exibe erro se faltar dado
            return

        usuario = verificar_login(email, senha)  # Verifica o login com os dados fornecidos
        if usuario:  # Se o login for bem-sucedido
            msgbx.showinfo("Bem-vindo", f"Olá {usuario[1]}, você está logado.")  # Exibe a mensagem de boas-vindas
            self.gui.destroy()  # Fecha a tela de login
            TelaCategoria(usuario[1], email)  # Abre a tela da categoria com o nome e e-mail do usuário
        else:  # Se o login falhar
            msgbx.showerror("Erro", "E-mail ou senha inválidos.")  # Exibe erro de login

    def voltar(self):
        self.gui.destroy()  # Fecha a tela de login
        TelaInicial().iniciar()  # Abre a tela inicial novamente

# Classe para a tela de registro (cadastro) do usuário
class TelaRegistro:
    def __init__(self):
        self.gui = tk.Tk()  # Cria a janela principal do Tkinter
        self.gui.attributes('-fullscreen', True)  # Define a janela para o modo de tela cheia
        self.gui.title("Cadastro - Quiz")  # Define o título da janela
        self.exibir_interface()  # Chama o método para exibir a interface gráfica da tela de cadastro

    def exibir_interface(self):
        # Adiciona a Label de Título "Tela de Cadastro"
        titulo_label = tk.Label(self.gui, text="Tela de Cadastro", 
                                font=('Arial', 24, 'bold'), fg="#ADD8E6", bg="black", width=100, height=3)
        titulo_label.place(relx=0.5, rely=0.1, anchor="n")  # Centraliza a label na parte superior da tela

        # Frame para os campos de nome, e-mail, senha
        frame = tk.Frame(self.gui)  # Cria um frame onde os campos de entrada serão colocados
        frame.place(relx=0.5, rely=0.4, anchor="center")  # Posiciona o frame no centro da tela

        # Label e campo de entrada para o nome
        tk.Label(frame, text="Nome:", font=('Arial', 12)).grid(row=0, column=0, pady=10, sticky="w")
        self.entry_nome = tk.Entry(frame, font=('Arial', 12))  # Cria o campo de entrada para o nome
        self.entry_nome.grid(row=0, column=1, pady=10)  # Posiciona o campo de entrada no grid

        # Label e campo de entrada para o e-mail
        tk.Label(frame, text="E-mail:", font=('Arial', 12)).grid(row=1, column=0, pady=10, sticky="w")
        self.entry_email = tk.Entry(frame, font=('Arial', 12))  # Cria o campo de entrada para o e-mail
        self.entry_email.grid(row=1, column=1, pady=10)  # Posiciona o campo de entrada no grid

        # Label e campo de entrada para a senha
        tk.Label(frame, text="Senha:", font=('Arial', 12)).grid(row=2, column=0, pady=10, sticky="w")
        self.entry_senha = tk.Entry(frame, font=('Arial', 12), show="*")  # Cria o campo de entrada para a senha (com máscara)
        self.entry_senha.grid(row=2, column=1, pady=10)  # Posiciona o campo de entrada no grid

        # Frame para os botões "Registrar" e "Voltar"
        botao_frame = tk.Frame(self.gui)  # Cria o frame para os botões
        botao_frame.place(relx=0.5, rely=0.6, anchor="center")  # Posiciona o frame abaixo dos campos de entrada

        # Botão "Registrar" e "Voltar" lado a lado
        ttk.Button(botao_frame, text="Registrar", command=self.validar_registro).grid(row=0, column=0, padx=10, pady=20)
        ttk.Button(botao_frame, text="Voltar", command=self.voltar).grid(row=0, column=1, padx=10, pady=20)

    def validar_registro(self):
        # Obtém os valores dos campos de entrada
        nome = self.entry_nome.get()
        email = self.entry_email.get()
        senha = self.entry_senha.get()

        # Verifica se todos os campos estão preenchidos
        if not nome or not email or not senha:
            msgbx.showerror("Erro", "Por favor, preencha todos os campos.")  # Exibe erro se algum campo estiver vazio
            return

        salvar_usuario(nome, email, senha)  # Chama a função para salvar o novo usuário no banco de dados
        msgbx.showinfo("Sucesso", "Cadastro realizado com sucesso.")  # Exibe uma mensagem de sucesso
        self.gui.destroy()  # Fecha a tela de cadastro
        TelaCategoria(nome, email)  # Abre a tela de categoria após o cadastro

    def voltar(self):
        self.gui.destroy()  # Fecha a tela de cadastro
        TelaInicial().iniciar()  # Abre a tela inicial novamente

# Classe para exibir os dados do usuário após o login
class TelaDadosUsuario:
    def __init__(self, nome_usuario, email_usuario):
        self.nome_usuario = nome_usuario  # Nome do usuário
        self.email_usuario = email_usuario  # E-mail do usuário
        self.gui = tk.Tk()  # Cria a janela principal do Tkinter
        self.gui.attributes('-fullscreen', True)  # Define a janela para o modo de tela cheia
        self.gui.title("Meus Dados")  # Define o título da janela
        self.exibir_interface()  # Chama o método para exibir a interface gráfica

    def exibir_interface(self):
        # Frame para exibir as informações do usuário
        frame = tk.Frame(self.gui)
        frame.place(relx=0.5, rely=0.4, anchor="center")  # Posiciona o frame no centro da tela

        # Exibir nome e e-mail do usuário
        tk.Label(frame, text=f"Nome: {self.nome_usuario}", font=('Arial', 14)).pack(pady=10)
        tk.Label(frame, text=f"E-mail: {self.email_usuario}", font=('Arial', 14)).pack(pady=10)

        # Obter ID do usuário para acessar a pontuação
        usuario_id = obter_id_usuario(self.email_usuario)  # Chama a função para obter o ID do usuário com base no e-mail
        if usuario_id:
            # Carregar as pontuações do usuário
            pontuacoes = self.carregar_pontuacoes(usuario_id)
            
            # Título da seção de pontuação
            tk.Label(frame, text="Sua(s) Pontuação", font=('Arial', 14, 'bold')).pack(pady=10)

            # Treeview para exibir a tabela de pontuação
            treeview = ttk.Treeview(frame, columns=("Pontuação", "Tipo Quiz", "Data"), show="headings")
            treeview.pack()  # Exibe a treeview na interface

            # Definir cabeçalhos da tabela
            treeview.heading("Pontuação", text="Pontuação")
            treeview.heading("Tipo Quiz", text="Tipo Quiz")
            treeview.heading("Data", text="Data")

            # Inserir os dados de pontuação na tabela
            for pontuacao in pontuacoes:
                treeview.insert("", "end", values=(pontuacao[0], pontuacao[1], pontuacao[2]))

            # Definir a largura das colunas da tabela
            treeview.column("Pontuação", width=100, anchor="center")
            treeview.column("Tipo Quiz", width=150, anchor="center")
            treeview.column("Data", width=150, anchor="center")

        # Botões para voltar à tela de categoria ou sair
        frame_botoes = tk.Frame(self.gui)
        frame_botoes.place(relx=0.5, rely=0.9, anchor="center")  # Posiciona o frame de botões abaixo da tabela de pontuação

        ttk.Button(frame_botoes, text="Voltar", command=self.voltar).grid(row=0, column=0, padx=20)
        ttk.Button(frame_botoes, text="Sair", command=self.sair).grid(row=0, column=1, padx=20)

    def carregar_pontuacoes(self, usuario_id):
        # Função para carregar as pontuações do usuário a partir do banco de dados
        conn = conectar_db()  # Conecta ao banco de dados
        cursor = conn.cursor()
        query = '''
            SELECT pontuacao, tipo_quiz, data FROM pontos WHERE usuario_id = %s ORDER BY data DESC
        '''  # Consulta SQL para obter as pontuações do usuário
        cursor.execute(query, (usuario_id,))  # Executa a consulta
        pontuacoes = cursor.fetchall()  # Obtém todas as pontuações
        cursor.close()  # Fecha o cursor
        conn.close()  # Fecha a conexão com o banco de dados
        return pontuacoes

    def voltar(self):
        self.gui.destroy()  # Fecha a tela de dados do usuário
        TelaCategoria(self.nome_usuario, self.email_usuario)  # Abre a tela de categoria com os dados do usuário

    def sair(self):
        self.gui.destroy()  # Fecha a tela de dados do usuário


class TelaDadosUsuario:
    # Inicializa a classe, configurando nome e email do usuário
    def __init__(self, nome_usuario, email_usuario):
        self.nome_usuario = nome_usuario  # Atribui o nome do usuário à variável de instância
        self.email_usuario = email_usuario  # Atribui o e-mail do usuário à variável de instância
        self.gui = tk.Tk()  # Cria a janela principal da interface gráfica
        self.gui.attributes('-fullscreen', True)  # Coloca a janela em modo de tela cheia
        self.gui.title("Meus Dados")  # Define o título da janela
        self.exibir_interface()  # Chama o método para exibir a interface gráfica

    # Exibe a interface com os dados do usuário
    def exibir_interface(self):
        frame = tk.Frame(self.gui)  # Cria um frame para organizar os widgets na tela
        frame.place(relx=0.5, rely=0.4, anchor="center")  # Posiciona o frame no centro da tela

        # Exibe o nome do usuário em um label
        tk.Label(frame, text=f"Nome: {self.nome_usuario}", font=('ariel', 14)).pack(pady=10)
        # Exibe o e-mail do usuário em um label
        tk.Label(frame, text=f"E-mail: {self.email_usuario}", font=('ariel', 14)).pack(pady=10)

        # Chama a função para obter o ID do usuário a partir do e-mail
        usuario_id = obter_id_usuario(self.email_usuario)
        if usuario_id:  # Verifica se o ID do usuário foi encontrado
            # Carrega as pontuações do usuário no banco de dados
            pontuacoes = self.carregar_pontuacoes(usuario_id)

            # Adiciona um título para a lista de pontuações
            tk.Label(frame, text="Sua(s) Pontuação", font=('ariel', 14, 'bold')).pack(pady=10)

            # Cria uma treeview (tabela) para exibir as pontuações
            treeview = ttk.Treeview(frame, columns=("Pontuação", "Tipo Quiz", "Data"), show="headings")
            treeview.pack()  # Exibe a treeview na tela

            # Define o cabeçalho da coluna "Pontuação" na tabela
            treeview.heading("Pontuação", text="Pontuação")
            # Define o cabeçalho da coluna "Tipo Quiz" na tabela
            treeview.heading("Tipo Quiz", text="Tipo Quiz")
            # Define o cabeçalho da coluna "Data" na tabela
            treeview.heading("Data", text="Data")

            # Preenche a tabela com os dados das pontuações
            for pontuacao in pontuacoes:
                treeview.insert("", "end", values=(pontuacao[0], pontuacao[1], pontuacao[2]))

            # Ajusta a largura da coluna "Pontuação"
            treeview.column("Pontuação", width=100, anchor="center")
            # Ajusta a largura da coluna "Tipo Quiz"
            treeview.column("Tipo Quiz", width=150, anchor="center")
            # Ajusta a largura da coluna "Data"
            treeview.column("Data", width=150, anchor="center")

        # Cria um frame para os botões de navegação (Voltar e Sair)
        frame_botoes = tk.Frame(self.gui)
        frame_botoes.place(relx=0.5, rely=0.9, anchor="center")  # Posiciona o frame no centro da tela

        # Cria o botão "Voltar" que chama a função voltar quando clicado
        ttk.Button(frame_botoes, text="Voltar", command=self.voltar).grid(row=0, column=0, padx=20)
        # Cria o botão "Sair" que chama a função sair quando clicado
        ttk.Button(frame_botoes, text="Sair", command=self.sair).grid(row=0, column=1, padx=20)

    # Carrega as pontuações do banco de dados com base no ID do usuário
    def carregar_pontuacoes(self, usuario_id):
        conn = conectar_db()  # Conecta ao banco de dados
        cursor = conn.cursor()  # Cria um cursor para executar a consulta no banco de dados
        query = '''
            SELECT pontuacao, tipo_quiz, data FROM pontos WHERE usuario_id = %s ORDER BY data DESC
        '''  # Consulta SQL para buscar as pontuações do usuário
        cursor.execute(query, (usuario_id,))  # Executa a consulta passando o ID do usuário como parâmetro
        pontuacoes = cursor.fetchall()  # Obtém todas as pontuações do usuário
        cursor.close()  # Fecha o cursor após a execução da consulta
        conn.close()  # Fecha a conexão com o banco de dados
        return pontuacoes  # Retorna a lista de pontuações

    # Função chamada quando o botão "Voltar" é clicado
    def voltar(self):
        self.gui.destroy()  # Fecha a janela atual
        TelaCategoria(self.nome_usuario, self.email_usuario)  # Abre a tela de categorias

    # Função chamada quando o botão "Sair" é clicado
    def sair(self):
        self.gui.destroy()  # Fecha a janela atual

# Classe para a tela de categorias
class TelaCategoria:

    # Inicializa a classe, configurando nome e email do usuário
    def __init__(self, nome_usuario, email_usuario):
        self.gui = tk.Tk()  # Cria a janela principal da interface gráfica
        self.gui.attributes('-fullscreen', True)  # Coloca a janela em modo de tela cheia
        self.gui.title("Escolha a Categoria")  # Define o título da janela
        self.nome_usuario = nome_usuario  # Atribui o nome do usuário à variável de instância
        self.email_usuario = email_usuario  # Atribui o e-mail do usuário à variável de instância
        self.exibir_interface()  # Chama o método para exibir a interface gráfica

    # Exibe a interface com a seleção de categorias
    def exibir_interface(self):
        # Exibe uma mensagem de boas-vindas no canto superior direito
        msg_bem_vindo = tk.Label(self.gui, text=f"Olá, bem-vindo {self.nome_usuario}!", font=('ariel', 12, 'bold'))
        msg_bem_vindo.place(relx=0.98, rely=0.02, anchor="ne")

        # Cria um link "Meus Dados" que chama a função abrir_perfil quando clicado
        link_perfil = tk.Label(self.gui, text="Meus Dados", fg="blue", cursor="hand2", font=('ariel', 12, 'underline'))
        link_perfil.place(relx=0.98, rely=0.06, anchor="ne")
        link_perfil.bind("<Button-1>", self.abrir_perfil)  # Quando clicado, abre a tela de dados do usuário

        frame = tk.Frame(self.gui)  # Cria um frame para organizar os widgets na tela
        frame.place(relx=0.5, rely=0.4, anchor="center")  # Posiciona o frame no centro da tela

        # Exibe o título "Escolha a categoria do quiz"
        tk.Label(frame, text="Escolha a categoria do quiz", font=('ariel', 14, 'bold')).grid(row=0, column=0, columnspan=5, pady=20)

        # Organiza os botões de categoria na linha horizontal
        categorias = ["Java", "Python", "Lógica", "HTML", "PHP"]
        for i, categoria in enumerate(categorias):  # Para cada categoria, cria um botão
            ttk.Button(frame, text=categoria, command=lambda cat=categoria: self.iniciar_quiz(cat)).grid(row=1, column=i, padx=10)

        # Cria o frame para os botões de navegação (Voltar e Sair)
        frame_botoes = tk.Frame(self.gui)
        frame_botoes.place(relx=0.5, rely=0.9, anchor="center")  # Posiciona o frame no centro da tela

        # Cria o botão "Voltar" que chama a função voltar quando clicado
        ttk.Button(frame_botoes, text="Voltar", command=self.voltar).grid(row=0, column=0, padx=20)
        # Cria o botão "Sair" que chama a função sair quando clicado
        ttk.Button(frame_botoes, text="Sair", command=self.sair).grid(row=0, column=1, padx=20)

    # Função chamada quando o link "Meus Dados" é clicado
    def abrir_perfil(self, event):
        # Chama a tela de dados do usuário
        TelaDadosUsuario(self.nome_usuario, self.email_usuario).iniciar()

    # Função chamada quando o botão de iniciar quiz é clicado
    def iniciar_quiz(self, categoria):
        self.gui.destroy()  # Fecha a janela atual
        iniciar_quiz(categoria, self.nome_usuario, self.email_usuario)  # Inicia o quiz com a categoria selecionada

    # Função chamada quando o botão "Voltar" é clicado
    def voltar(self):
        self.gui.destroy()  # Fecha a janela atual
        TelaInicial().iniciar()  # Abre a tela inicial

    # Função chamada quando o botão "Sair" é clicado
    def sair(self):
        self.gui.destroy()  # Fecha a janela atual
# Classe do Quiz
class Quiz:
    # Inicializa a classe com informações do usuário, categoria e dados do quiz
    def __init__(self, nome_usuario, email_usuario, categoria, perguntas, opcoes, respostas):
        self.nome_usuario = nome_usuario  # Atribui o nome do usuário à variável de instância
        self.email_usuario = email_usuario  # Atribui o e-mail do usuário à variável de instância
        self.categoria = categoria  # Atribui a categoria do quiz à variável de instância
        self.perguntas = perguntas  # Atribui as perguntas à variável de instância
        self.opcoes = opcoes  # Atribui as opções de resposta à variável de instância
        self.respostas = respostas  # Atribui as respostas corretas à variável de instância
        self.pontuacao = 0  # Inicializa a pontuação do usuário como 0
        self.indice_atual = 0  # Inicializa o índice da pergunta atual como 0
        self.gui = None  # Inicializa a variável gui como None (a interface gráfica será criada mais tarde)

    # Inicia o quiz criando a interface gráfica e exibindo a primeira pergunta
    def iniciar(self):
        self.gui = tk.Tk()  # Cria a janela principal da interface gráfica
        self.gui.attributes('-fullscreen', True)  # Coloca a janela em modo de tela cheia
        self.gui.title(f"Quiz - {self.categoria}")  # Define o título da janela com a categoria do quiz
        self.exibir_pergunta()  # Chama o método para exibir a primeira pergunta
        self.gui.mainloop()  # Inicia o loop principal da interface gráfica, aguardando ações do usuário

    # Exibe a pergunta atual e suas opções de resposta
    def exibir_pergunta(self):
        # Verifica se todas as perguntas foram respondidas
        if self.indice_atual >= len(self.perguntas):
            self.exibir_resultado()  # Se todas as perguntas foram respondidas, exibe o resultado final
            return

        # Remove widgets da tela anterior para exibir a nova pergunta
        for widget in self.gui.winfo_children():
            widget.destroy()

        pergunta = self.perguntas[self.indice_atual]  # Obtém a pergunta atual
        opcoes = self.opcoes[self.indice_atual]  # Obtém as opções de resposta para a pergunta atual

        # Cria um frame para organizar a pergunta e as opções
        frame = tk.Frame(self.gui)
        frame.place(relx=0.5, rely=0.4, anchor="center")  # Posiciona o frame no centro da tela

        # Exibe a pergunta
        tk.Label(frame, text=f"Pergunta {self.indice_atual + 1}:", font=('ariel', 14, 'bold')).pack(pady=10)
        tk.Label(frame, text=pergunta, font=('ariel', 12)).pack(pady=10)

        self.resposta_usuario = tk.StringVar()  # Variável para armazenar a resposta do usuário

        # Inicializa com a primeira opção como selecionada
        if opcoes:
            self.resposta_usuario.set(opcoes[0])  # Define a primeira opção como a resposta inicial

        # Exibe as opções de resposta
        for opcao in opcoes:
            tk.Radiobutton(
                frame, text=opcao, variable=self.resposta_usuario, value=opcao, font=('ariel', 12)
            ).pack(anchor="w")  # Cria um botão de opção para cada resposta

        # Cria um botão para avançar para a próxima pergunta
        ttk.Button(frame, text="Próximo", command=self.verificar_resposta).pack(pady=20)

    # Verifica se a resposta do usuário está correta e avança para a próxima pergunta
    def verificar_resposta(self):
        resposta_correta = str(self.respostas[self.indice_atual]).strip()  # Obtém a resposta correta (removendo espaços)
        resposta_usuario = str(self.resposta_usuario.get()).strip()  # Obtém a resposta do usuário (removendo espaços)

        # Verifica se a resposta do usuário está correta
        if resposta_usuario.lower() == resposta_correta.lower():
            self.pontuacao += 1  # Incrementa a pontuação se a resposta estiver correta

        # Avança para a próxima pergunta
        self.indice_atual += 1
        self.exibir_pergunta()  # Exibe a próxima pergunta

    # Exibe o resultado final do quiz
    def exibir_resultado(self):
        # Remove widgets da tela anterior
        for widget in self.gui.winfo_children():
            widget.destroy()

        # Exibe o resultado final
        frame = tk.Frame(self.gui)
        frame.place(relx=0.5, rely=0.4, anchor="center")  # Posiciona o frame no centro da tela

        resultado = f"Sua pontuação: {self.pontuacao}/{len(self.perguntas)}"  # Calcula o resultado
        tk.Label(frame, text="Fim do Quiz!", font=('ariel', 16, 'bold')).pack(pady=10)  # Exibe o título de fim de quiz
        tk.Label(frame, text=resultado, font=('ariel', 14)).pack(pady=10)  # Exibe a pontuação final

        # Obtém o ID do usuário e salva a pontuação no banco de dados
        usuario_id = obter_id_usuario(self.email_usuario)  # Obtém o ID do usuário com base no e-mail
        if usuario_id:  # Verifica se o ID do usuário foi encontrado
            salvar_pontuacao(usuario_id, self.pontuacao, self.categoria)  # Salva a pontuação no banco de dados

        # Cria um botão para voltar ao menu
        ttk.Button(frame, text="Voltar ao Menu", command=self.voltar_menu).pack(pady=20)

    # Função chamada quando o botão "Voltar ao Menu" é clicado
    def voltar_menu(self):
        self.gui.destroy()  # Fecha a janela do quiz
        TelaCategoria(self.nome_usuario, self.email_usuario)  # Abre a tela de categorias para o usuário

# Iniciar o programa
if __name__ == "__main__":
    TelaInicial().iniciar()  # Inicia a tela inicial do aplicativo
