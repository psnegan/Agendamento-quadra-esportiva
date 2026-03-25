# QuadraBook — Sistema de Agendamento de Quadras Esportivas

## 📋 Requisitos
- Python 3.8+
- pip

## 🚀 Como rodar

### 1. Instalar dependências
```bash
pip install -r requirements.txt
```

### 2. Iniciar o servidor
```bash
python app.py
```

### 3. Acessar no navegador
```
http://localhost:5000
```

---

## 🔑 Credenciais padrão

| Perfil        | E-mail              | Senha    |
|---------------|---------------------|----------|
| Administrador | admin@quadras.com   | admin123 |
| Usuário       | (cadastre-se)       | —        |

---

## 📁 Estrutura do projeto

```
quadras/
├── app.py                  # Aplicação principal Flask
├── requirements.txt        # Dependências Python
├── data/                   # Banco de dados JSON (criado automaticamente)
│   ├── usuarios.json
│   ├── quadras.json
│   ├── horarios.json
│   └── reservas.json
├── static/
│   ├── css/style.css       # Estilos modernos
│   └── js/main.js          # JavaScript auxiliar
└── templates/
    ├── base.html           # Template base
    ├── index.html          # Página inicial (landing)
    ├── login.html          # Login
    ├── cadastro.html       # Cadastro de usuário
    ├── home.html           # Lista de quadras
    ├── agendar.html        # Tela de agendamento
    ├── historico.html      # Histórico de reservas
    └── admin/
        ├── dashboard.html  # Painel do admin
        ├── quadras.html    # Gerenciar quadras
        ├── quadra_form.html# Formulário de quadra
        ├── horarios.html   # Gerenciar horários
        ├── reservas.html   # Ver todas as reservas
        ├── usuarios.html   # Controle de usuários
        └── relatorios.html # Relatórios de uso
```

---

## ✅ Funcionalidades implementadas

### Usuário
- [x] Cadastro com validação de e-mail único e senha mínima
- [x] Login com autenticação por hash SHA-256
- [x] Visualização de quadras disponíveis
- [x] Consulta de horários livres em tempo real (via API JSON)
- [x] Agendamento de quadra com verificação de conflito
- [x] Cancelamento de reservas futuras
- [x] Histórico completo de reservas

### Administrador
- [x] Dashboard com estatísticas gerais
- [x] Cadastro, edição e remoção de quadras
- [x] Gerenciamento de horários disponíveis
- [x] Visualização de todas as reservas
- [x] Cancelamento de reservas pelo admin
- [x] Controle de usuários cadastrados
- [x] Relatórios: uso por quadra, por mês, horários mais populares

---

## 🗄️ Armazenamento de dados

Todos os dados são armazenados em arquivos `.json` na pasta `data/`:

- **usuarios.json** — cadastro de usuários (senha em SHA-256)
- **quadras.json** — quadras disponíveis
- **horarios.json** — faixas de horário configuráveis
- **reservas.json** — todas as reservas realizadas

Os arquivos são criados automaticamente na primeira execução com dados de exemplo.
