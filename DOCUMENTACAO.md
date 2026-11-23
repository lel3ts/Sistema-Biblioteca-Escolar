# Documentação — Sistema de Biblioteca Escolar

## Objetivo
Organizar o acervo de uma biblioteca escolar e controlar o cadastro de usuários, empréstimos e devoluções.

## Perfis
- **Administrador:** gerencia livros, registra empréstimos e devoluções e consulta alunos.
- **Aluno:** cria uma conta, consulta o acervo e acompanha seus próprios empréstimos.

## Requisitos funcionais
- RF01: permitir login e logout.
- RF02: permitir cadastro de alunos.
- RF03: exibir painel com indicadores gerais.
- RF04: permitir cadastrar livros.
- RF05: permitir editar e excluir livros sem histórico de empréstimos.
- RF06: permitir pesquisar livros por título, autor ou categoria.
- RF07: permitir registrar empréstimos para alunos cadastrados.
- RF08: impedir empréstimo quando não houver exemplar disponível.
- RF09: definir prazo padrão de devolução de sete dias.
- RF10: permitir registrar devolução e atualizar o estoque.
- RF11: permitir consultar histórico de empréstimos.
- RF12: permitir ao administrador consultar os alunos cadastrados.

## Regras de negócio
- O sistema cria uma conta inicial de administrador na primeira execução.
- Senhas são armazenadas usando hash.
- Cada empréstimo reduz em uma unidade a quantidade disponível.
- Cada devolução aumenta em uma unidade a quantidade disponível.
- O sistema não permite excluir livros que possuam histórico de empréstimos.
- Alunos visualizam apenas seus próprios empréstimos.

## Modelo de dados
- **users:** armazena os usuários do sistema.
- **books:** armazena os livros do acervo.
- **loans:** relaciona usuários e livros emprestados.

## Requisitos mínimos de infraestrutura
- Processador Dual Core ou equivalente.
- 4 GB de memória RAM.
- 20 GB de espaço livre em disco.
- Monitor, teclado e mouse.
- Sistema operacional Windows, Linux ou macOS.
- Python 3.10 ou superior e navegador atualizado.

## Segurança e observações
O projeto utiliza hash de senha e consultas parametrizadas. A chave secreta padrão é apenas para desenvolvimento escolar; em implantação real deve ser substituída por uma variável de ambiente forte. Também devem ser adicionadas proteções CSRF e outras medidas de segurança antes de uso em produção.
