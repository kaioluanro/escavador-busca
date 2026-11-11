# Escavador

Motor de busca vertical para explorar o acervo do Diário Oficial do Município de Teresina. O projeto nasceu da dificuldade de encontrar informações em edições antigas, nas quais a qualidade do texto extraído por reconhecimento óptico de caracteres (OCR) pode variar. Seu nome reflete a ideia de escavar informações em documentos históricos.

O Escavador pesquisa **texto previamente extraído e armazenado**: este repositório não inclui o acervo nem um pipeline de OCR ou de alimentação do banco de dados. Os resultados são sugestões para conferência no documento original; erros de OCR e consultas pouco específicas podem produzir omissões ou falsos positivos.

## Funcionalidades

- Pesquisa textual com correspondência aproximada, destinada a lidar com variações no texto.
- Filtro por período e comandos para restringir a busca por diário, secretaria, número de documento ou identificador, conforme a disponibilidade dos metadados no acervo.
- Classificação experimental que considera proximidade entre palavras e formas linguísticas, além de busca aproximada.
- Interface web, indicadores de andamento via Socket.IO, links para páginas dos diários e exportação de resultados em CSV ou PDF.

## Como funciona

A aplicação Flask consulta registros de páginas no PostgreSQL e os carrega em um DataFrame conforme o intervalo escolhido. O módulo `ultraabs.py` interpreta a consulta e aplica filtros e métodos de recuperação. Entre os recursos empregados estão tokenização e lematização com spaCy, similaridade textual com FuzzyWuzzy e uma heurística de distâncias entre termos. A interface recebe os resultados e fornece acesso aos documentos de origem.

A pontuação e a taxa de impureza são heurísticas do projeto, não probabilidades de acerto. Não há avaliação reproduzível de precisão ou desempenho neste repositório. O comportamento depende do corpus, da qualidade do OCR e dos metadados disponíveis.

## Exemplos de pesquisa

Use termos específicos e um intervalo de datas curto. Exemplos ilustrativos:

```text
onde está a portaria 77 de 2023
id: 000480000000012023
dom: 3523
sec: semf
dom: 3523 num: 0001
portaria 77 sec: semf
```

Conforme a documentação original, os comandos podem ser combinados na ordem texto, `dom:`, `sec:`, `num:`; `num:` depende de `dom:` ou `sec:`. Os campos de identificação e secretaria dependem de metadados presentes no banco e podem não estar disponíveis para todas as edições. A aplicação limita o intervalo a quatro anos. Consulte o PDF original do diário para confirmar o conteúdo.

## Requisitos e execução local

Projeto histórico baseado em Python, Flask, Flask-SQLAlchemy, Flask-SocketIO, PostgreSQL, pandas, spaCy e FuzzyWuzzy. As dependências fixadas são antigas; recomenda-se experimentar em ambiente isolado com Python 3.10. É necessário fornecer um banco PostgreSQL próprio, com dados autorizados e compatíveis. Não há banco, dados de exemplo ou importador incluídos.

```bash
python -m venv .venv
# Linux/macOS: source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m spacy download pt_core_news_lg
```

Configure `DATABASE_URL` com a URL do seu próprio banco e `SECRET_KEY` com uma chave aleatória própria, fora do repositório. No PowerShell, por exemplo:

```powershell
$env:DATABASE_URL = 'postgresql://USUARIO:SENHA@localhost:5432/escavador'
$env:SECRET_KEY = 'SUBSTITUA_POR_UMA_CHAVE_ALEATORIA'
python app.py
```

Acesse `http://127.0.0.1:5000`. O modelo de dados em `app.py` espera a tabela `data_dom`, com `id`, `title`, `page`, `text`, `date`, `ids`, `nums` e `secs`. A criação e o preenchimento dessa tabela são de responsabilidade de quem instala. A instalação e a pesquisa de ponta a ponta não foram verificadas nesta publicação; podem ser necessários ajustes de dependências e dados.

## Estrutura

- `app.py`: aplicação web, acesso ao banco e eventos Socket.IO.
- `ultraabs.py`: interpretação de consultas, filtros e recuperação de texto.
- `templates/` e `static/`: interface web.
- `requirements.txt`: dependências da versão histórica.

## Limitações

Esta é uma versão de estudo de um projeto anterior, sem garantia de compatibilidade com versões atuais de bibliotecas. O acervo e as regras de acesso aos documentos não são distribuídos aqui. Antes de qualquer exposição em rede, revise autenticação, segurança, concorrência, tratamento de entrada e proteção dos dados; o projeto não está preparado como serviço público de produção. Links externos e disponibilidade dos diários podem mudar.

Desenvolvido por Kaio Luan Rodrigues Cardeal.
