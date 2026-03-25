from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
import json
import os
from datetime import datetime, date
from functools import wraps
import uuid
import hashlib

app = Flask(__name__)
app.secret_key = 'quadras_secret_key_2024'

# ─── Caminhos dos arquivos JSON ───────────────────────────────────────────────
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
USUARIOS_FILE  = os.path.join(DATA_DIR, 'usuarios.json')
QUADRAS_FILE   = os.path.join(DATA_DIR, 'quadras.json')
RESERVAS_FILE  = os.path.join(DATA_DIR, 'reservas.json')
HORARIOS_FILE  = os.path.join(DATA_DIR, 'horarios.json')

# ─── Helpers JSON ─────────────────────────────────────────────────────────────
def ler(arquivo):
    if not os.path.exists(arquivo):
        return []
    with open(arquivo, 'r', encoding='utf-8') as f:
        return json.load(f)

def salvar(arquivo, dados):
    os.makedirs(os.path.dirname(arquivo), exist_ok=True)
    with open(arquivo, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

# ─── Inicialização dos dados ───────────────────────────────────────────────────
def inicializar_dados():
    if not os.path.exists(USUARIOS_FILE):
        admin = {
            "id": str(uuid.uuid4()),
            "nome": "Administrador",
            "email": "admin@quadras.com",
            "senha": hash_senha("admin123"),
            "papel": "admin",
            "criado_em": datetime.now().isoformat()
        }
        salvar(USUARIOS_FILE, [admin])

    if not os.path.exists(QUADRAS_FILE):
        quadras = [
            {"id": "1", "nome": "Quadra de Futebol Society", "tipo": "Futebol", "descricao": "Gramado sintético de alta qualidade, iluminação LED", "capacidade": 14, "preco": 120.00, "ativa": True, "imagem": "futebol"},
            {"id": "2", "nome": "Quadra de Tênis Central", "tipo": "Tênis", "descricao": "Piso de saibro, cercada com alambrado", "capacidade": 4, "preco": 80.00, "ativa": True, "imagem": "tenis"},
            {"id": "3", "nome": "Quadra de Basquete", "tipo": "Basquete", "descricao": "Piso de madeira emborrachada, tabelas oficiais", "capacidade": 10, "preco": 90.00, "ativa": True, "imagem": "basquete"},
            {"id": "4", "nome": "Quadra de Vôlei", "tipo": "Vôlei", "descricao": "Areia fina importada, rede oficial", "capacidade": 12, "preco": 70.00, "ativa": True, "imagem": "volei"},
        ]
        salvar(QUADRAS_FILE, quadras)

    if not os.path.exists(HORARIOS_FILE):
        horarios = [
            {"id": "1", "inicio": "07:00", "fim": "08:00"},
            {"id": "2", "inicio": "08:00", "fim": "09:00"},
            {"id": "3", "inicio": "09:00", "fim": "10:00"},
            {"id": "4", "inicio": "10:00", "fim": "11:00"},
            {"id": "5", "inicio": "11:00", "fim": "12:00"},
            {"id": "6", "inicio": "13:00", "fim": "14:00"},
            {"id": "7", "inicio": "14:00", "fim": "15:00"},
            {"id": "8", "inicio": "15:00", "fim": "16:00"},
            {"id": "9", "inicio": "16:00", "fim": "17:00"},
            {"id": "10", "inicio": "17:00", "fim": "18:00"},
            {"id": "11", "inicio": "18:00", "fim": "19:00"},
            {"id": "12", "inicio": "19:00", "fim": "20:00"},
            {"id": "13", "inicio": "20:00", "fim": "21:00"},
            {"id": "14", "inicio": "21:00", "fim": "22:00"},
        ]
        salvar(HORARIOS_FILE, horarios)

    if not os.path.exists(RESERVAS_FILE):
        salvar(RESERVAS_FILE, [])

inicializar_dados()

# ─── Decorators ───────────────────────────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'usuario_id' not in session:
            flash('Faça login para continuar.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'usuario_id' not in session:
            return redirect(url_for('login'))
        if session.get('papel') != 'admin':
            flash('Acesso restrito a administradores.', 'danger')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated

# ─── Rotas públicas ───────────────────────────────────────────────────────────
@app.route('/')
def index():
    if 'usuario_id' in session:
        return redirect(url_for('home'))
    return render_template('index.html')

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome  = request.form.get('nome', '').strip()
        email = request.form.get('email', '').strip().lower()
        senha = request.form.get('senha', '')
        conf  = request.form.get('confirmar_senha', '')

        usuarios = ler(USUARIOS_FILE)

        if not nome or not email or not senha:
            flash('Preencha todos os campos.', 'danger')
        elif senha != conf:
            flash('As senhas não conferem.', 'danger')
        elif len(senha) < 6:
            flash('A senha deve ter ao menos 6 caracteres.', 'danger')
        elif any(u['email'] == email for u in usuarios):
            flash('E-mail já cadastrado.', 'danger')
        else:
            novo = {
                "id": str(uuid.uuid4()),
                "nome": nome,
                "email": email,
                "senha": hash_senha(senha),
                "papel": "usuario",
                "criado_em": datetime.now().isoformat()
            }
            usuarios.append(novo)
            salvar(USUARIOS_FILE, usuarios)
            flash('Cadastro realizado! Faça login.', 'success')
            return redirect(url_for('login'))

    return render_template('cadastro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        senha = request.form.get('senha', '')
        usuarios = ler(USUARIOS_FILE)
        usuario = next((u for u in usuarios if u['email'] == email and u['senha'] == hash_senha(senha)), None)

        if usuario:
            session['usuario_id'] = usuario['id']
            session['nome'] = usuario['nome']
            session['email'] = usuario['email']
            session['papel'] = usuario['papel']
            flash(f'Bem-vindo, {usuario["nome"]}!', 'success')
            return redirect(url_for('admin_dashboard') if usuario['papel'] == 'admin' else url_for('home'))
        else:
            flash('E-mail ou senha incorretos.', 'danger')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Você saiu com sucesso.', 'info')
    return redirect(url_for('index'))

# ─── Rotas do usuário ─────────────────────────────────────────────────────────
@app.route('/home')
@login_required
def home():
    quadras = [q for q in ler(QUADRAS_FILE) if q['ativa']]
    return render_template('home.html', quadras=quadras)

@app.route('/quadra/<quadra_id>')
@login_required
def quadra_detalhe(quadra_id):
    quadras = ler(QUADRAS_FILE)
    quadra  = next((q for q in quadras if q['id'] == quadra_id), None)
    if not quadra:
        flash('Quadra não encontrada.', 'danger')
        return redirect(url_for('home'))
    return render_template('quadra_detalhe.html', quadra=quadra)

@app.route('/api/horarios-livres')
@login_required
def horarios_livres():
    quadra_id = request.args.get('quadra_id')
    data_str  = request.args.get('data')

    if not quadra_id or not data_str:
        return jsonify([])

    todos    = ler(HORARIOS_FILE)
    reservas = ler(RESERVAS_FILE)

    ocupados = {
        r['horario_id']
        for r in reservas
        if r['quadra_id'] == quadra_id
        and r['data'] == data_str
        and r['status'] != 'cancelado'
    }

    livres = [h for h in todos if h['id'] not in ocupados]
    return jsonify(livres)

@app.route('/agendar', methods=['GET', 'POST'])
@login_required
def agendar():
    if request.method == 'POST':
        quadra_id  = request.form.get('quadra_id')
        data_str   = request.form.get('data')
        horario_id = request.form.get('horario_id')

        quadras  = ler(QUADRAS_FILE)
        horarios = ler(HORARIOS_FILE)
        reservas = ler(RESERVAS_FILE)

        quadra  = next((q for q in quadras  if q['id'] == quadra_id),  None)
        horario = next((h for h in horarios if h['id'] == horario_id), None)

        if not quadra or not horario:
            flash('Dados inválidos.', 'danger')
            return redirect(url_for('home'))

        # Verifica se já está ocupado
        conflito = any(
            r['quadra_id'] == quadra_id and r['data'] == data_str
            and r['horario_id'] == horario_id and r['status'] != 'cancelado'
            for r in reservas
        )
        if conflito:
            flash('Este horário já está reservado.', 'danger')
            return redirect(url_for('home'))

        # Valida data mínima (hoje)
        try:
            data_reserva = datetime.strptime(data_str, '%Y-%m-%d').date()
            if data_reserva < date.today():
                flash('Não é possível agendar para datas passadas.', 'danger')
                return redirect(url_for('home'))
        except ValueError:
            flash('Data inválida.', 'danger')
            return redirect(url_for('home'))

        nova = {
            "id": str(uuid.uuid4()),
            "usuario_id": session['usuario_id'],
            "usuario_nome": session['nome'],
            "quadra_id": quadra_id,
            "quadra_nome": quadra['nome'],
            "horario_id": horario_id,
            "horario_inicio": horario['inicio'],
            "horario_fim": horario['fim'],
            "data": data_str,
            "preco": quadra['preco'],
            "status": "confirmado",
            "criado_em": datetime.now().isoformat()
        }
        reservas.append(nova)
        salvar(RESERVAS_FILE, reservas)
        flash(f'Reserva confirmada! {quadra["nome"]} em {data_str} às {horario["inicio"]}.', 'success')
        return redirect(url_for('historico'))

    quadras = [q for q in ler(QUADRAS_FILE) if q['ativa']]
    quadra_selecionada = request.args.get('quadra_id', '')
    return render_template('agendar.html', quadras=quadras, quadra_selecionada=quadra_selecionada)

@app.route('/historico')
@login_required
def historico():
    reservas = ler(RESERVAS_FILE)
    minhas   = [r for r in reservas if r['usuario_id'] == session['usuario_id']]
    minhas.sort(key=lambda r: (r['data'], r['horario_inicio']), reverse=True)
    return render_template('historico.html', reservas=minhas)

@app.route('/cancelar/<reserva_id>', methods=['POST'])
@login_required
def cancelar(reserva_id):
    reservas = ler(RESERVAS_FILE)
    for r in reservas:
        if r['id'] == reserva_id and r['usuario_id'] == session['usuario_id']:
            if r['status'] == 'confirmado':
                data_reserva = datetime.strptime(r['data'], '%Y-%m-%d').date()
                if data_reserva >= date.today():
                    r['status'] = 'cancelado'
                    r['cancelado_em'] = datetime.now().isoformat()
                    salvar(RESERVAS_FILE, reservas)
                    flash('Reserva cancelada com sucesso.', 'success')
                else:
                    flash('Não é possível cancelar reservas passadas.', 'warning')
            break
    return redirect(url_for('historico'))

# ─── Rotas do administrador ───────────────────────────────────────────────────
@app.route('/admin')
@admin_required
def admin_dashboard():
    reservas  = ler(RESERVAS_FILE)
    quadras   = ler(QUADRAS_FILE)
    usuarios  = ler(USUARIOS_FILE)

    total_reservas    = len([r for r in reservas if r['status'] == 'confirmado'])
    total_canceladas  = len([r for r in reservas if r['status'] == 'cancelado'])
    receita_total     = sum(r['preco'] for r in reservas if r['status'] == 'confirmado')
    total_usuarios    = len([u for u in usuarios if u['papel'] == 'usuario'])

    # Reservas por quadra
    uso_quadras = {}
    for r in reservas:
        if r['status'] == 'confirmado':
            uso_quadras[r['quadra_nome']] = uso_quadras.get(r['quadra_nome'], 0) + 1

    # Próximas reservas (hoje em diante)
    hoje = date.today().isoformat()
    proximas = sorted(
        [r for r in reservas if r['data'] >= hoje and r['status'] == 'confirmado'],
        key=lambda r: (r['data'], r['horario_inicio'])
    )[:10]

    return render_template('admin/dashboard.html',
        total_reservas=total_reservas,
        total_canceladas=total_canceladas,
        receita_total=receita_total,
        total_usuarios=total_usuarios,
        uso_quadras=uso_quadras,
        proximas=proximas,
        quadras=quadras
    )

# ── Quadras ──
@app.route('/admin/quadras')
@admin_required
def admin_quadras():
    return render_template('admin/quadras.html', quadras=ler(QUADRAS_FILE))

@app.route('/admin/quadras/nova', methods=['GET', 'POST'])
@admin_required
def admin_quadra_nova():
    if request.method == 'POST':
        quadras = ler(QUADRAS_FILE)
        nova = {
            "id": str(uuid.uuid4()),
            "nome": request.form.get('nome', '').strip(),
            "tipo": request.form.get('tipo', '').strip(),
            "descricao": request.form.get('descricao', '').strip(),
            "capacidade": int(request.form.get('capacidade', 0)),
            "preco": float(request.form.get('preco', 0)),
            "ativa": True,
            "imagem": request.form.get('tipo', 'futebol').lower()
        }
        quadras.append(nova)
        salvar(QUADRAS_FILE, quadras)
        flash('Quadra cadastrada!', 'success')
        return redirect(url_for('admin_quadras'))
    return render_template('admin/quadra_form.html', quadra=None)

@app.route('/admin/quadras/editar/<quadra_id>', methods=['GET', 'POST'])
@admin_required
def admin_quadra_editar(quadra_id):
    quadras = ler(QUADRAS_FILE)
    quadra  = next((q for q in quadras if q['id'] == quadra_id), None)
    if not quadra:
        flash('Quadra não encontrada.', 'danger')
        return redirect(url_for('admin_quadras'))

    if request.method == 'POST':
        quadra['nome']       = request.form.get('nome', '').strip()
        quadra['tipo']       = request.form.get('tipo', '').strip()
        quadra['descricao']  = request.form.get('descricao', '').strip()
        quadra['capacidade'] = int(request.form.get('capacidade', 0))
        quadra['preco']      = float(request.form.get('preco', 0))
        quadra['ativa']      = request.form.get('ativa') == 'on'
        salvar(QUADRAS_FILE, quadras)
        flash('Quadra atualizada!', 'success')
        return redirect(url_for('admin_quadras'))

    return render_template('admin/quadra_form.html', quadra=quadra)

@app.route('/admin/quadras/remover/<quadra_id>', methods=['POST'])
@admin_required
def admin_quadra_remover(quadra_id):
    quadras = ler(QUADRAS_FILE)
    quadras = [q for q in quadras if q['id'] != quadra_id]
    salvar(QUADRAS_FILE, quadras)
    flash('Quadra removida.', 'success')
    return redirect(url_for('admin_quadras'))

# ── Horários ──
@app.route('/admin/horarios')
@admin_required
def admin_horarios():
    return render_template('admin/horarios.html', horarios=ler(HORARIOS_FILE))

@app.route('/admin/horarios/novo', methods=['POST'])
@admin_required
def admin_horario_novo():
    horarios = ler(HORARIOS_FILE)
    novo = {
        "id": str(uuid.uuid4()),
        "inicio": request.form.get('inicio'),
        "fim": request.form.get('fim')
    }
    horarios.append(novo)
    horarios.sort(key=lambda h: h['inicio'])
    salvar(HORARIOS_FILE, horarios)
    flash('Horário adicionado!', 'success')
    return redirect(url_for('admin_horarios'))

@app.route('/admin/horarios/remover/<horario_id>', methods=['POST'])
@admin_required
def admin_horario_remover(horario_id):
    horarios = [h for h in ler(HORARIOS_FILE) if h['id'] != horario_id]
    salvar(HORARIOS_FILE, horarios)
    flash('Horário removido.', 'success')
    return redirect(url_for('admin_horarios'))

# ── Reservas ──
@app.route('/admin/reservas')
@admin_required
def admin_reservas():
    reservas = sorted(ler(RESERVAS_FILE), key=lambda r: (r['data'], r['horario_inicio']), reverse=True)
    return render_template('admin/reservas.html', reservas=reservas)

@app.route('/admin/reservas/cancelar/<reserva_id>', methods=['POST'])
@admin_required
def admin_cancelar_reserva(reserva_id):
    reservas = ler(RESERVAS_FILE)
    for r in reservas:
        if r['id'] == reserva_id:
            r['status'] = 'cancelado'
            r['cancelado_em'] = datetime.now().isoformat()
            break
    salvar(RESERVAS_FILE, reservas)
    flash('Reserva cancelada pelo administrador.', 'success')
    return redirect(url_for('admin_reservas'))

# ── Usuários ──
@app.route('/admin/usuarios')
@admin_required
def admin_usuarios():
    usuarios = ler(USUARIOS_FILE)
    reservas = ler(RESERVAS_FILE)
    for u in usuarios:
        u['total_reservas'] = len([r for r in reservas if r['usuario_id'] == u['id']])
    return render_template('admin/usuarios.html', usuarios=usuarios)

@app.route('/admin/usuarios/remover/<usuario_id>', methods=['POST'])
@admin_required
def admin_usuario_remover(usuario_id):
    if usuario_id == session['usuario_id']:
        flash('Você não pode remover sua própria conta.', 'danger')
        return redirect(url_for('admin_usuarios'))
    usuarios = [u for u in ler(USUARIOS_FILE) if u['id'] != usuario_id]
    salvar(USUARIOS_FILE, usuarios)
    flash('Usuário removido.', 'success')
    return redirect(url_for('admin_usuarios'))

# ── Relatórios ──
@app.route('/admin/relatorios')
@admin_required
def admin_relatorios():
    reservas = ler(RESERVAS_FILE)
    quadras  = ler(QUADRAS_FILE)

    # Uso por quadra
    uso_quadras = {}
    for q in quadras:
        rs = [r for r in reservas if r['quadra_id'] == q['id'] and r['status'] == 'confirmado']
        uso_quadras[q['nome']] = {
            'total': len(rs),
            'receita': sum(r['preco'] for r in rs)
        }

    # Uso por mês
    uso_mes = {}
    for r in reservas:
        if r['status'] == 'confirmado':
            mes = r['data'][:7]
            uso_mes[mes] = uso_mes.get(mes, 0) + 1
    uso_mes = dict(sorted(uso_mes.items()))

    # Horários mais usados
    uso_horario = {}
    for r in reservas:
        if r['status'] == 'confirmado':
            h = r['horario_inicio']
            uso_horario[h] = uso_horario.get(h, 0) + 1
    uso_horario = dict(sorted(uso_horario.items(), key=lambda x: x[1], reverse=True))

    return render_template('admin/relatorios.html',
        uso_quadras=uso_quadras,
        uso_mes=uso_mes,
        uso_horario=uso_horario
    )

if __name__ == '__main__':
    app.run(debug=True)
