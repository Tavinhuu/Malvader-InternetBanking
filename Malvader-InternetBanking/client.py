from flask import Blueprint, render_template, request, redirect, session, flash
from datetime import datetime
from app import conectar_banco, registrar_auditoria
import mysql.connector as mysql

cliente_bp = Blueprint('cliente', __name__, template_folder='templates')


@cliente_bp.route('/deposito', methods=['GET', 'POST'])
def deposito():
    if not session.get('usuario_logado') or session.get('tipo_usuario') != 'CLIENTE':
        flash('Acesso negado.', 'error')
        return redirect('/')

    id_usuario = session['id_usuario']
    sucesso = False

    if request.method == 'POST':
        valor = float(request.form.get('valor'))

        try:
            conn = conectar_banco()
            cursor = conn.cursor(dictionary=True)

            # Buscar conta do cliente (por exemplo, conta corrente id_conta=1)
            cursor.execute("SELECT id_conta, saldo FROM conta WHERE id_cliente = %s AND tipo = 'CC'", (id_usuario,))
            conta = cursor.fetchone()

            if not conta:
                flash('Conta não encontrada.', 'error')
                cursor.close()
                conn.close()
                return redirect('/deposito')

            id_conta = conta['id_conta']
            saldo_atual = float(conta['saldo'])

            novo_saldo = saldo_atual + valor
            cursor.execute("UPDATE conta SET saldo = %s WHERE id_conta = %s", (novo_saldo, id_conta))

            conn.commit()

            flash('Depósito realizado com sucesso!', 'success')
            sucesso = True
        except Exception as e:
            print("Erro ao realizar depósito:", e)
            flash("Erro ao processar depósito.", 'error')
        finally:
            cursor.close()
            conn.close()

    return render_template('client/deposit.html', sucesso=sucesso)



@cliente_bp.route('/transferencia', methods=['GET', 'POST'])
def transferencia():
    if not session.get('usuario_logado') or session.get('tipo_usuario') != 'CLIENTE':
        flash("Acesso negado.", "error")
        return redirect('/')

    id_usuario = session['id_usuario']
    nome_usuario = "Usuário"  # valor padrão caso não encontre

    try:
        conn = conectar_banco()
        cursor = conn.cursor(dictionary=True)

        # Pega nome do usuário para mostrar no template
        cursor.execute("SELECT nome FROM usuario WHERE id_usuario = %s", (id_usuario,))
        usuario = cursor.fetchone()
        if usuario and 'nome' in usuario:
            nome_usuario = usuario['nome']

        if request.method == 'POST':
            numero_destino = request.form.get('numero_destino')
            valor = float(request.form.get('valor'))

            # Buscar a conta corrente do cliente (id_conta = 1 associada a ele)
            cursor.execute("SELECT id_conta, saldo FROM conta WHERE id_cliente = %s AND tipo = 'CC'", (id_usuario,))
            conta_origem = cursor.fetchone()

            if not conta_origem:
                flash("Sua conta corrente (id=1) não foi encontrada.", "error")
                cursor.close()
                conn.close()
                return redirect('/transferencia')

            # Conta de destino (sem filtro id_conta=1)
            cursor.execute("SELECT id_conta, saldo FROM conta WHERE numero_conta = %s", (numero_destino,))
            conta_destino = cursor.fetchone()

            if not conta_destino:
                flash("Conta de destino inválida.", "error")
                cursor.close()
                conn.close()
                return redirect('/transferencia')

            # Converter saldos para float
            saldo_origem = float(conta_origem['saldo'])
            saldo_destino = float(conta_destino['saldo'])

            # Verificar saldo suficiente
            if saldo_origem < valor:
                flash("Saldo insuficiente.", "error")
                cursor.close()
                conn.close()
                return redirect('/transferencia')

            # Atualizar saldo da conta origem (subtrair valor)
            novo_saldo_origem = saldo_origem - valor
            cursor.execute("UPDATE conta SET saldo = %s WHERE id_conta = %s", (novo_saldo_origem, conta_origem['id_conta']))

            # Atualizar saldo da conta destino (somar valor)
            novo_saldo_destino = saldo_destino + valor
            cursor.execute("UPDATE conta SET saldo = %s WHERE id_conta = %s", (novo_saldo_destino, conta_destino['id_conta']))

            # Registrar movimentações
            cursor.execute("""INSERT INTO movimentacao (id_conta, tipo, valor) VALUES (%s, 'TRANSFERENCIA', %s)""",
                           (conta_origem['id_conta'], -valor))  # débito na conta origem

            cursor.execute("""INSERT INTO movimentacao (id_conta, tipo, valor) VALUES (%s, 'TRANSFERENCIA', %s)""",
                           (conta_destino['id_conta'], valor))  # crédito na conta destino

            conn.commit()

            registrar_auditoria(id_usuario, 'TRANSFERENCIA', f'Enviou R$ {valor:.2f} para conta {numero_destino}')
            flash("Transferência realizada com sucesso!", "success")
            return redirect('/transferencia')

    except Exception as e:
        print("Erro ao transferir:", e)
        flash("Erro ao realizar transferência.", "error")

    finally:
        cursor.close()
        conn.close()

    return render_template('client/transfer.html', nome_usuario=nome_usuario)

@cliente_bp.route('/saque', methods=['GET', 'POST'])
def saque():
    if not session.get('usuario_logado') or session.get('tipo_usuario') != 'CLIENTE':
        flash("Acesso negado.", "error")
        return redirect('/')

    id_usuario = session['id_usuario']
    taxa_extra = 5.00  # taxa se passou de 5 saques

    if request.method == 'POST':
        valor = float(request.form.get('valor'))

        try:
            conn = conectar_banco()
            cursor = conn.cursor(dictionary=True)

            # Buscar conta do cliente
            cursor.execute("SELECT id_conta, saldo FROM conta WHERE id_cliente = %s AND tipo = 'CC'", (id_usuario,))
            conta = cursor.fetchone()

            if not conta:
                flash("Conta corrente não encontrada.", "error")
                return redirect('/saque')

            id_conta = conta['id_conta']
            saldo = conta['saldo']

            # Contar saques no mês
            cursor.execute("""
    SELECT COUNT(*) as total_saques
    FROM movimentacao
    WHERE id_conta = %s AND tipo = 'SAQUE'
    AND MONTH(data_movimentacao) = MONTH(CURDATE()) AND YEAR(data_movimentacao) = YEAR(CURDATE())
""", (id_conta,))

            total_saques = cursor.fetchone()['total_saques']

            aplicar_taxa = total_saques >= 5
            valor_final = valor + (taxa_extra if aplicar_taxa else 0)

            if saldo < valor_final:
                flash(f"Saldo insuficiente. Valor com taxa: R$ {valor_final:.2f}", "error")
                return redirect('/saque')

            # Debita da conta
            cursor.execute("UPDATE conta SET saldo = saldo - %s WHERE id_conta = %s", (valor_final, id_conta))
            cursor.execute("""
                INSERT INTO movimentacao (id_conta, tipo, valor)
                VALUES (%s, 'SAQUE', %s)
            """, (id_conta, valor))

            conn.commit()

            msg_auditoria = f"Saque de R$ {valor:.2f}"
            if aplicar_taxa:
                msg_auditoria += f" + taxa de R$ {taxa_extra:.2f}"
            registrar_auditoria(id_usuario, 'SAQUE', msg_auditoria)

            flash(f"Saque realizado com sucesso! Valor retirado: R$ {valor_final:.2f}", "success")
            return redirect('/saque')

        except Exception as e:
            print("Erro ao realizar saque:", e)
            flash("Erro ao realizar saque.", "error")
        finally:
            cursor.close()
            conn.close()

    return render_template('client/withdraw.html')

@cliente_bp.route('/extrato', methods=['GET', 'POST'])
def extrato():
    if not session.get('usuario_logado') or session.get('tipo_usuario') != 'CLIENTE':
        flash("Acesso negado.", "error")
        return redirect('/')

    id_usuario = session['id_usuario']
    transacoes = []
    data_inicio = None
    data_fim = None

    try:
        conn = conectar_banco()
        cursor = conn.cursor(dictionary=True)

        # Buscar conta do cliente
        cursor.execute("SELECT id_conta FROM conta WHERE id_cliente = %s AND tipo = 'CC'", (id_usuario,))
        conta = cursor.fetchone()
        if not conta:
            flash("Conta não encontrada.", "error")
            return redirect('/')

        id_conta = conta['id_conta']

        # Verifica filtro por data
        if request.method == 'POST':
            data_inicio = request.form.get('data_inicio')
            data_fim = request.form.get('data_fim')

            cursor.execute("""
                SELECT tipo, valor, data_movimentacao
                FROM movimentacao
                WHERE id_conta = %s AND DATE(data_movimentacao) BETWEEN %s AND %s
                ORDER BY data_movimentacao DESC
                LIMIT 50
            """, (id_conta, data_inicio, data_fim))
        else:
            cursor.execute("""
                SELECT tipo, valor, data_movimentacao
                FROM movimentacao
                WHERE id_conta = %s
                ORDER BY data_movimentacao DESC
                LIMIT 50
            """, (id_conta,))

        transacoes = cursor.fetchall()
        cursor.close()
        conn.close()

    except Exception as e:
        print("Erro ao buscar extrato:", e)
        flash("Erro ao carregar extrato.", "error")

    return render_template('client/statement.html', transacoes=transacoes)

@cliente_bp.route('/investimentos')
def investimentos():
    if not session.get('usuario_logado') or session.get('tipo_usuario') != 'CLIENTE':
        flash("Acesso negado.", "error")
        return redirect('/')

    id_usuario = session['id_usuario']
    saldo = None
    rendimento = None

    try:
        conn = conectar_banco()
        cursor = conn.cursor(dictionary=True)

    
        cursor.execute("""
            SELECT saldo FROM conta WHERE id_cliente = %s AND tipo = 'CP'
        """, (id_usuario,))
        conta = cursor.fetchone()

        if conta:
            from decimal import Decimal

            saldo = float(conta['saldo'])
            rendimento = round(saldo * 0.01, 2)


        cursor.close()
        conn.close()

    except Exception as e:
        print("Erro ao consultar investimentos:", e)
        flash("Erro ao carregar dados de investimento.", "error")

    return render_template('client/investments.html', saldo=saldo, rendimento=rendimento)

