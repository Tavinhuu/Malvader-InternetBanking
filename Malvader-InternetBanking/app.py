from flask import Flask, request, render_template, redirect, flash, session
import mysql.connector
from datetime import datetime, timedelta
import random

app = Flask(__name__)
app.secret_key = 'chave'

def conectar_banco():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database=''
    )

def registrar_auditoria(id_usuario, acao, detalhes):
    try:
        conn = conectar_banco()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO auditoria (id_usuario, acao, detalhes) VALUES (%s, %s, %s)", (id_usuario, acao, detalhes))
        conn.commit()
    except Exception as e:
        print("Erro ao registrar auditoria:", e)
    finally:
        cursor.close()
        conn.close()

@app.route('/', methods=['GET', 'POST'])
def homepage():
    if request.method == 'POST':
    
        pass
    return render_template('index.html')

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nome = request.form.get('nome')
        cpf = request.form.get('cpf')
        senha = request.form.get('senha')
        telefone = request.form.get('telefone')
        data_nascimento = request.form.get('data_nascimento')

        try:
            conn = conectar_banco()
            cursor = conn.cursor()

            # Verifica se CPF já existe
            cursor.execute("SELECT * FROM usuario WHERE cpf = %s", (cpf,))
            if cursor.fetchone():
                flash("CPF já registrado.", "error")
                return redirect('/registro')

            # Insere novo usuário
            cursor.execute("""
                INSERT INTO usuario (nome, cpf, senha_hash, tipo_usuario, data_nascimento, telefone, tentativas_login)
                VALUES (%s, %s, MD5(%s), 'CLIENTE', %s, %s, 0)
            """, (nome, cpf, senha, data_nascimento, telefone))
            conn.commit()

            flash("Registro concluído! Faça login.", "success")
            return redirect('/')
        except Exception as e:
            print("Erro ao registrar usuário:", e)
            flash("Erro ao registrar.", "error")
        finally:
            cursor.close()
            conn.close()

    return render_template('auth/register.html')


# LOGIN
@app.route('/login', methods=['POST'])
def login():
    cpf = request.form.get('cpf')
    senha = request.form.get('senha')

    try:
        conn = conectar_banco()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM usuario WHERE cpf = %s", (cpf,))
        usuario = cursor.fetchone()

        if not usuario:
            flash('CPF não encontrado.', 'error')
            return redirect('/')

        if usuario['bloqueado_ate'] and usuario['bloqueado_ate'] > datetime.now():
            minutos_restantes = (usuario['bloqueado_ate'] - datetime.now()).seconds // 60 + 1
            flash(f'Conta bloqueada. Tente novamente em {minutos_restantes} minutos.', 'error')
            registrar_auditoria(None, 'LOGIN_BLOQUEADO', f'Tentativa durante bloqueio - CPF: {cpf}')
            return redirect('/')

        cursor.execute("SELECT * FROM usuario WHERE cpf = %s AND senha_hash = MD5(%s)", (cpf, senha))
        usuario_valido = cursor.fetchone()

        if usuario_valido:
            cursor.execute("UPDATE usuario SET tentativas_login = 0, bloqueado_ate = NULL WHERE id_usuario = %s", (usuario_valido['id_usuario'],))
            conn.commit()

            session['id_usuario_temp'] = usuario_valido['id_usuario']

            cursor.callproc('gerar_otp', [usuario_valido['id_usuario']])
            conn.commit()

            for result in cursor.stored_results():
                resultado = result.fetchone()
                if resultado and 'otp_gerado' in resultado:
                    print(f"[DEBUG] OTP gerado: {resultado['otp_gerado']}")

            flash('Código OTP enviado. Verifique seu dispositivo.', 'success')
            return redirect('/verificar-otp')
        else:
            novas_tentativas = usuario['tentativas_login'] + 1
            if novas_tentativas >= 3:
                bloqueio = datetime.now() + timedelta(minutes=10)
                cursor.execute("UPDATE usuario SET tentativas_login = 3, bloqueado_ate = %s WHERE cpf = %s", (bloqueio, cpf))
                registrar_auditoria(None, 'LOGIN_BLOQUEADO', f'CPF {cpf} bloqueado após 3 falhas')
                flash('Bloqueado por 10 minutos.', 'error')
            else:
                cursor.execute("UPDATE usuario SET tentativas_login = %s WHERE cpf = %s", (novas_tentativas, cpf))
                flash(f'Tentativa {novas_tentativas}/3 incorreta.', 'error')
                registrar_auditoria(None, 'LOGIN_FALHA', f'Tentativa {novas_tentativas} para CPF: {cpf}')

            conn.commit()
            return redirect('/')
    except Exception as e:
        print("Erro:", e)
        flash('Erro ao conectar ao banco.', 'error')
        return redirect('/')
    finally:
        cursor.close()
        conn.close()

# VERIFICAR OTP
@app.route('/verificar-otp')
def verificar_otp():
    return render_template('auth/otpverify.html')

@app.route('/verificar-otp', methods=['POST'])
def verificar_otp_post():
    otp_digitado = request.form.get('otp')
    id_usuario = session.get('id_usuario_temp')

    if not id_usuario:
        flash('Sessão expirada.', 'error')
        return redirect('/')

    try:
        conn = conectar_banco()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuario WHERE id_usuario = %s", (id_usuario,))
        usuario = cursor.fetchone()

        if usuario and usuario['otp_ativo'] == otp_digitado:
            if usuario['otp_expiracao'] > datetime.now():
                flash('Login completo com sucesso!', 'success')
                session['usuario_logado'] = True
                session['id_usuario'] = id_usuario  # armazenar id definitivo para uso
                session['tipo_usuario'] = usuario['tipo_usuario']  # salvar tipo na sessão para controle

                registrar_auditoria(id_usuario, 'LOGIN_OTP', 'OTP validado')

                # Redireciona para menu conforme tipo
                if usuario['tipo_usuario'] == 'FUNCIONARIO':
                    return redirect('/main_funcionario')
                else:
                    return redirect('/main_usuario')

            else:
                flash('OTP expirado.', 'error')
        else:
            flash('OTP inválido.', 'error')
        registrar_auditoria(id_usuario, 'LOGIN_OTP', 'Falha no OTP')
        return redirect('/verificar-otp')
    except Exception as e:
        print("Erro ao validar OTP:", e)
        flash('Erro na validação.', 'error')
        return redirect('/verificar-otp')
    finally:
        cursor.close()
        conn.close()

# Rota menu principal funcionário
@app.route('/main_funcionario', methods=['GET', 'POST'])
def main_funcionario():
    if not session.get('usuario_logado') or session.get('tipo_usuario') != 'FUNCIONARIO':
        flash('Acesso negado.', 'error')
        return redirect('/')

    id_usuario = session.get('id_usuario')
    resultado_busca = None

    conn = conectar_banco()
    cursor = conn.cursor(dictionary=True)

    # Buscar nome do funcionário logado
    cursor.execute("SELECT nome FROM usuario WHERE id_usuario = %s", (id_usuario,))
    funcionario = cursor.fetchone()

    # Dados do painel
    cursor.execute("SELECT COUNT(*) AS total FROM conta")
    total_contas = cursor.fetchone()['total']

    cursor.execute("SELECT COUNT(*) AS total FROM conta WHERE saldo < 0")
    total_inadimplentes = cursor.fetchone()['total']

    cursor.execute("SELECT COUNT(*) AS total FROM usuario WHERE tipo_usuario = 'FUNCIONARIO'")
    total_funcionarios = cursor.fetchone()['total']

    # Se houve envio do formulário
    if request.method == 'POST':
        cpf_digitado = request.form.get('cpf_busca')
        if cpf_digitado:
            cursor.execute("SELECT id_usuario, nome FROM usuario WHERE cpf = %s", (cpf_digitado,))
            resultado_busca = cursor.fetchone() or {}

    cursor.execute("""SELECT acao, detalhes, data_hora FROM auditoria WHERE id_usuario = %s ORDER BY data_hora DESC LIMIT 5 """, (id_usuario,))
    ultimas_auditorias = cursor.fetchall()        

    cursor.close()
    conn.close()

    return render_template('main/main_funcionario.html',
    nome_usuario=funcionario['nome'],
    total_contas=total_contas,
    total_inadimplentes=total_inadimplentes,
    total_funcionarios=total_funcionarios,
    resultado_busca=resultado_busca,
    ultimas_auditorias=ultimas_auditorias
)



# Rota menu principal usuário comum
@app.route('/main_usuario', methods=['GET', 'POST'])
def main_usuario():
    id_usuario = session.get('id_usuario')
    if not id_usuario:
        return "Usuário não logado ou id_usuario não encontrado na sessão."

    conn = conectar_banco()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT nome FROM usuario WHERE id_usuario = %s", (id_usuario,))
    usuario = cursor.fetchone()

    cursor.execute("SELECT saldo, id_conta, numero_conta FROM conta WHERE id_cliente = %s AND tipo = 'CC'", (id_usuario,))
    conta = cursor.fetchone()

    if not conta:
        cursor.close()
        conn.close()
        return "Conta não encontrada."

    id_conta = conta['id_conta']
    saldo = conta['saldo']
    numero_conta = conta['numero_conta']

    # Buscar últimas 5 movimentações
    cursor.execute("""
        SELECT tipo, valor, data_movimentacao
        FROM movimentacao
        WHERE id_conta = %s
        ORDER BY data_movimentacao DESC
        LIMIT 5
    """, (id_conta,))
    ultimas_movimentacoes = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('main/main_usuario.html',
                           nome=usuario['nome'],
                           saldo=saldo,
                           numeroconta=numero_conta,
                           movimentacoes=ultimas_movimentacoes)









# LOGOUT
@app.route('/logout')
def logout():
    session.clear()
    flash('Você saiu da sessão.', 'success')
    return redirect('/')

# GERADOR DE CONTA
def gerar_numero_conta():
    numero = random.randint(100000, 999999)
    digito = numero % 9
    return f"{numero}-{digito}"

# ABERTURA DE CONTA
@app.route('/abrir-conta', methods=['GET', 'POST'])
def abrir_conta():
    if not session.get('usuario_logado'):
        flash('Faça login primeiro.', 'error')
        return redirect('/')

    if session.get('tipo_usuario') != 'FUNCIONARIO':
        flash('Acesso restrito a funcionários.', 'error')
        return redirect('/')

    if request.method == 'POST':
        tipo = request.form.get('tipo')
        id_cliente = request.form.get('id_cliente')
        saldo = request.form.get('saldo')
        try:
            conn = conectar_banco()
            cursor = conn.cursor()
            numero_conta = gerar_numero_conta()
            id_funcionario = session['id_usuario']

            cursor.execute("""
                INSERT INTO conta (numero_conta, tipo, saldo, id_cliente, id_funcionario)
                VALUES (%s, %s, %s, %s, %s)
            """, (numero_conta, tipo, saldo, id_cliente, id_funcionario))
            conn.commit()

            flash(f'Conta {numero_conta} criada com sucesso!', 'success')
            return redirect('/abrir-conta')
        except Exception as e:
            print("Erro ao abrir conta:", e)
            flash('Erro ao criar a conta.', 'error')
            return redirect('/abrir-conta')
        finally:
            cursor.close()
            conn.close()
    return render_template('accounts/openaccount.html')

# ENCERRAMENTO DE CONTA
@app.route('/encerrar-conta', methods=['GET', 'POST'])
def encerrar_conta():
    if not session.get('usuario_logado'):
        flash('Faça login primeiro.', 'error')
        return redirect('/')

    if session.get('tipo_usuario') != 'FUNCIONARIO':
        flash('Acesso restrito a funcionários.', 'error')
        return redirect('/')

    if request.method == 'POST':
        id_conta = request.form.get('id_conta')
        motivo = request.form.get('motivo')
        senha_admin = request.form.get('senha_admin')
        otp = request.form.get('otp')
        id_funcionario = session['id_usuario']

        try:
            conn = conectar_banco()
            cursor = conn.cursor(dictionary=True)

            cursor.execute("SELECT * FROM usuario WHERE id_usuario = %s", (id_funcionario,))
            funcionario = cursor.fetchone()

            if not funcionario or funcionario['otp_ativo'] != otp or funcionario['otp_expiracao'] < datetime.now():
                flash('OTP inválido ou expirado.', 'error')
                return redirect('/encerrar-conta')

            cursor.execute("""
                SELECT * FROM usuario
                WHERE tipo_usuario = 'FUNCIONARIO' AND senha_hash = MD5(%s) AND id_usuario = %s
            """, (senha_admin, id_funcionario))
            admin = cursor.fetchone()

            if not admin:
                flash('Senha de administrador inválida.', 'error')
                return redirect('/encerrar-conta')

            cursor.execute("SELECT * FROM conta WHERE id_conta = %s", (id_conta,))
            conta = cursor.fetchone()

            if not conta:
                flash('Conta não encontrada.', 'error')
                return redirect('/encerrar-conta')

            if conta['saldo'] < 0:
                flash('Conta com saldo negativo não pode ser encerrada.', 'error')
                return redirect('/encerrar-conta')

        
            cursor.execute("""INSERT INTO historico_encerramento (id_conta, id_funcionario, motivo) VALUES (%s, %s, %s) """, (id_conta, id_funcionario, motivo))

            cursor.execute("UPDATE conta SET ativa = FALSE WHERE id_conta = %s", (id_conta,))
            conn.commit()

            flash('Conta encerrada com sucesso!', 'success')
            registrar_auditoria(id_funcionario, 'ENCERRAMENTO_CONTA', f'Conta ID {id_conta} encerrada')
            return redirect('/encerrar-conta')

        except Exception as e:
            print("Erro ao encerrar conta:", e)
            flash('Erro ao encerrar a conta.', 'error')
            return redirect('/encerrar-conta')
        finally:
            cursor.close()
            conn.close()
    return render_template('accounts/deleteaccount.html')

@app.route('/consultar-contas')
def consultar_contas():
    if not session.get('usuario_logado'):
        flash('Faça login primeiro.', 'error')
        return redirect('/')

    try:
        conn = conectar_banco()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM view_contas_ativas")
        contas = cursor.fetchall()
    except Exception as e:
        print("Erro ao consultar contas:", e)
        flash('Erro ao buscar contas.', 'error')
        contas = []
    finally:
        cursor.close()
        conn.close()

    return render_template('reports/banksreport.html', contas=contas)


@app.route('/consultar-clientes')
def consultar_clientes():
    if not session.get('usuario_logado') or session.get('tipo_usuario') != 'FUNCIONARIO':
        flash('Acesso restrito.', 'error')
        return redirect('/')

    try:
        conn = conectar_banco()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM view_clientes")
        clientes = cursor.fetchall()
    except Exception as e:
        print("Erro ao consultar clientes:", e)
        flash('Erro ao buscar clientes.', 'error')
        clientes = []
    finally:
        cursor.close()
        conn.close()

    return render_template('reports/customersreport.html', clientes=clientes)


@app.route('/consultar-funcionarios')
def consultar_funcionarios():
    if not session.get('usuario_logado') or session.get('tipo_usuario') != 'FUNCIONARIO':
        flash('Acesso restrito.', 'error')
        return redirect('/')

    try:
        conn = conectar_banco()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM view_funcionarios")
        funcionarios = cursor.fetchall()
    except Exception as e:
        print("Erro ao consultar funcionários:", e)
        flash('Erro ao buscar funcionários.', 'error')
        funcionarios = []
    finally:
        cursor.close()
        conn.close()

    return render_template('reports/employeereports.html', funcionarios=funcionarios)

###################################################



if __name__ == '__main__':
    from changes import alteracoes_bp
    app.register_blueprint(alteracoes_bp)
    from relatorios import relatorios_bp
    app.register_blueprint(relatorios_bp)
    from client import cliente_bp
    app.register_blueprint(cliente_bp)
    app.run(debug=True)
