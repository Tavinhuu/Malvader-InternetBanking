

<div align="center"> 
  <img height="100px" src="./Malvader-InternetBanking/static/img/logo.png"/>
</div>

<br>
<p align="center">
  <strong>Banco Malvader — Sistema Bancário com Flask + MySQL</strong><br/>
  Gerencie contas, operações e relatórios com controle total e autenticação robusta.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/plataforma-Web-blue?logo=google-chrome" />
  <img src="https://img.shields.io/badge/backend-Flask-blue?logo=python" />
  <img src="https://img.shields.io/badge/banco-MySQL-blue?logo=mysql" />
  <img src="https://img.shields.io/badge/frontend-Jinja2-yellow?logo=jinja" />
  <img src="https://img.shields.io/badge/projeto-Acadêmico-green" />
</p>

---

## Sobre o projeto

**Banco Malvader** é um sistema bancário web que simula um banco real, com controle de autenticação em duas etapas, abertura e encerramento de contas, movimentações financeiras (depósito, saque, transferência), relatórios e auditoria completa.

---

## Objetivo

Desenvolver um sistema completo que simule o funcionamento de uma instituição bancária, com foco em segurança, lógica de negócios e uso efetivo de banco de dados relacional.

---

## Tecnologias Utilizadas

- [Python 3.13](https://www.python.org/)
- [Flask](https://flask.palletsprojects.com/)
- [MySQL + MySQL Workbench](https://www.mysql.com/)
- [Jinja2](https://jinja.palletsprojects.com/)
- [Pandas](https://pandas.pydata.org/) + [Openpyxl](https://openpyxl.readthedocs.io/) (exportação Excel)
- [ReportLab](https://www.reportlab.com/) (exportação PDF)

---

## Pré-requisitos

- Python 3 instalado
- MySQL Server configurado
- MySQL Workbench (recomendado para visualizar e executar scripts)
- Pacotes: `Flask`, `mysql-connector-python`, `pandas`, `openpyxl`, `reportlab`

---


---

## ⚙️ Como rodar localmente

1. Clone o repositório:
   ```bash
   git clone https://github.com/seu-usuario/banco-malvader.git
   cd banco-malvader
   ```

2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure seu banco MySQL com o script do banco (tabelas, procedures e views)

4. Rode o sistema:
   ```bash
   python app.py
   ```

5. Acesse em: [http://localhost:5000](http://localhost:5000)

---

## ✅ Requisitos SQL

O banco de dados inclui:

- Tabelas: `usuario`, `conta`, `movimentacao`, `auditoria`, `historico_encerramento`
- Procedures: `gerar_otp`
- Views: `view_desempenho_func`, `view_inadimplencia`
- Triggers: para registro automático de abertura de conta, verificação de limite de funcionários, etc.

> Veja o script completo em `bancomalvader.sql`.
