# Sistema de Biblioteca Escolar — Biblioteca Horizonte

Segunda versão visual do sistema de biblioteca escolar. Mantém as funcionalidades da primeira versão, mas utiliza uma identidade visual diferente: tons de verde, creme e laranja, menu lateral e cartões de informação.

## Funcionalidades
- Cadastro e login de usuários
- Perfil de administrador e perfil de aluno
- Painel com indicadores da biblioteca
- Cadastro, edição, exclusão e pesquisa de livros
- Registro de empréstimos com prazo padrão de 7 dias
- Registro de devoluções e atualização automática do estoque
- Histórico de empréstimos
- Listagem de alunos cadastrados
- Banco de dados SQLite

## Requisitos
- Python 3.10 ou superior
- Flask
- Navegador atualizado

## Como executar no Windows
1. Abra a pasta do projeto no VS Code.
2. Abra o terminal integrado.
3. Crie o ambiente virtual:
   ```bash
   python -m venv venv
   ```
4. Ative o ambiente:
   ```bash
   venv\Scripts\activate
   ```
5. Instale as dependências:
   ```bash
   python -m pip install -r requirements.txt
   ```
6. Execute:
   ```bash
   python app.py
   ```
7. Acesse `http://127.0.0.1:5000`.

## Acesso inicial de administrador
- E-mail: `admin@biblioteca.com`
- Senha: `admin123`

Altere a senha inicial antes de qualquer uso real. Este projeto foi desenvolvido para fins didáticos.

## Estrutura
- `app.py`: rotas, autenticação e regras de negócio
- `schema.sql`: estrutura das tabelas
- `templates/`: páginas HTML
- `static/style.css`: identidade visual
- `biblioteca.db`: banco SQLite criado automaticamente na primeira execução
