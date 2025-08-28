# Manicure Dashboard

Visualização interativa de atendimentos e faturamento para um estúdio de manicure, construída com Streamlit e Plotly a partir do dataset `atendimentos_manicure_com_horario.json`.

## Visão geral
- O app principal é `dashboard.py`, um dashboard interativo com filtros por período, serviço, forma de pagamento e cliente frequente.

## Estrutura do projeto
```
./
├── atendimentos_manicure_com_horario.json   # Dataset de atendimentos
├── dashboard.py                              # App Streamlit (principal)
├── requirements.txt                          # Dependências mínimas
└── venv/                                     # (opcional) ambiente virtual local
```

## Dados (schema)
Cada item do arquivo `atendimentos_manicure_com_horario.json` contém:
- `id` (int): identificador do atendimento
- `data` (YYYY-MM-DD): data do atendimento
- `dia_semana` (str): dia da semana (pt-BR)
- `horario_atendimento` (HH:MM): horário
- `servico` (str): tipo de serviço
- `preco_base` (number): preço de tabela
- `desconto` (number): valor do desconto aplicado
- `preco_final` (number): preço pago após descontos
- `forma_pagamento` (str): Pix, Dinheiro, Cartão Crédito/Débito
- `cliente_idade` (int): idade da cliente
- `cliente_frequente` (bool): se é cliente recorrente

## Requisitos
- Python 3.10+
- Dependências (arquivo `requirements.txt`):
  - streamlit
  - plotly
  - pandas

Instalação das dependências (recomendado usar venv):
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Como executar o dashboard (recomendado)
Na raiz do projeto, rode:
```bash
streamlit run dashboard.py
```
Isso abrirá o app em http://localhost:8501 com:
- KPIs (atendimentos, faturamento, ticket médio, serviços únicos)
- Séries temporais (semanal/diária/mensal)
- Barras por serviço, dia da semana, hora do dia
- Distribuição das formas de pagamento
- Faixas etárias e descontos por serviço
- Heatmap dia × hora
- Faturamento por forma de pagamento e ticket médio por serviço
- Tabela de dados filtrados

## Dicas e problemas comuns
- Se o dashboard não abrir, verifique se o arquivo `atendimentos_manicure_com_horario.json` está na mesma pasta de `dashboard.py`.
- Para atualização automática do cache de dados no Streamlit, mude os filtros na barra lateral; o app utiliza `@st.cache_data` para otimizar leituras.

## License
Projeto sob a licença [MIT](../LICENSE).

