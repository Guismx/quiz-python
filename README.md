# Quiz Game - Python Application

Este projeto é um **jogo de perguntas e respostas (Quiz)** desenvolvido em Python com interface gráfica usando o **Tkinter** e integração com um banco de dados para registro de pontuações. 

---

## **📋 Funcionalidades**

- **Login e Cadastro de Usuários:** Sistema para autenticar ou registrar usuários.
- **Quiz Personalizado:** Escolha entre diferentes categorias, como `Java`, `Python`, `Lógica`, `HTML` e `PHP`.
- **Pontuação e Rankings:** O sistema armazena a pontuação dos jogadores no banco de dados e exibe o histórico.
- **Interface Gráfica Intuitiva:** Experiência visual amigável e interativa.
- **Persistência de Dados:** Usa banco de dados SQL para gerenciar informações dos usuários e resultados.

---

## **🚀 Tecnologias Utilizadas**

- **Linguagem:** Python 3.x  
- **Interface Gráfica:** Tkinter  
- **Banco de Dados:** MySQL  
- **ORM:** PyMySQL (ou qualquer biblioteca para conexão com MySQL)  

---

## **📂 Estrutura do Projeto**

📁 projeto-quiz <br>
│
├── 📁 src                
│   ├── 📄 main.py       
│   ├── 📄 tela_inicial.py  <br>
│   ├── 📄 tela_categoria.py  <br>
│   ├── 📄 tela_dados.py  
│   ├── 📄 quiz.py       
│   ├── 📄 banco_dados.py  <br>
│   └── 📄 utils.py <br>
│ <br>
├── 📁 assets  <br>
│   ├── 📄 styles.css  <br>
│   └── 📄 imagens/ <br>
│ <br>
├── 📄 requirements.txt <br>
├── 📄 README.md  <br>
└── 📄 LICENSE 



---

## **🛠️ Configuração do Ambiente**

### 1. **Pré-requisitos**
- Python 3.x instalado
- MySQL ou MariaDB  (Instale o PyMySQL (ou outra biblioteca de conexão com MySQL: pip install pymysql )
- Bibliotecas Python:
  - `tkinter` (nativo do Python)
  - `pymysql`

### 2. **Configuração do Banco de Dados**
Crie o banco de dados e as tabelas necessárias para o projeto. Exemplo de script SQL:

```sql
CREATE DATABASE quiz_game;
USE quiz_game;

CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    senha VARCHAR(100) NOT NULL
);

CREATE TABLE pontos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    pontuacao INT NOT NULL,
    tipo_quiz VARCHAR(50),
    data DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);


