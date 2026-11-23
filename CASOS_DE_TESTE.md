# Casos de teste

| ID | Funcionalidade | Procedimento | Resultado esperado |
|---|---|---|---|
| CT01 | Login válido | Informar e-mail e senha corretos | Acesso ao painel |
| CT02 | Login inválido | Informar senha incorreta | Mensagem de erro e permanência no login |
| CT03 | Cadastro de aluno | Preencher nome, e-mail e senha inéditos | Conta criada com perfil de aluno |
| CT04 | Cadastro de livro | Administrador informar título, autor e quantidade | Livro aparece no acervo |
| CT05 | Pesquisa de livro | Pesquisar parte do título ou autor | Apenas resultados correspondentes aparecem |
| CT06 | Empréstimo | Administrador selecionar aluno e livro disponível | Empréstimo registrado e estoque reduzido |
| CT07 | Estoque indisponível | Tentar emprestar livro sem exemplares | Sistema impede o empréstimo |
| CT08 | Devolução | Administrador registrar devolução ativa | Status muda e estoque aumenta |
