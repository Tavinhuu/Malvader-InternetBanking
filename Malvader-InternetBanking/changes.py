from flask import Blueprint, render_template, request, redirect, session, flash
from datetime import datetime
import mysql.connector
from app import conectar_banco, registrar_auditoria

alteracoes_bp = Blueprint('alteracoes', __name__)

@alteracoes_bp.route('/alterar-cliente/<int:id_cliente>', methods=['GET', 'POST'])
def alterar_cliente(id_cliente):
    if not session.get('usuario_logado') or session.get('tipo_usuario') != 'FUNCIONARIO':
        flash('Acesso negado.', 'error')
        return redirect('/')

    conn = conectar_banco()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        nome = request.form.get('nome')
        telefone = request.form.get('telefone')
        senha_admin = request.form.get('senha_admin')
        id_funcionario = session.get('id_usuario')

        cursor.execute("""
            SELECT * FROM usuario
            WHERE id_usuario = %s AND senha_hash = MD5(%s)
        """, (id_funcionario, senha_admin))
        admin = cursor.fetchone()

        if not admin:
            flash('Senha de administrador incorreta.', 'error')
            return redirect(f'/alterar-cliente/{id_cliente}')

        cursor.execute("SELECT nome, telefone FROM usuario WHERE id_usuario = %s", (id_cliente,))
        cliente_atual = cursor.fetchone()

        if not cliente_atual:
            flash('Cliente não encontrado.', 'error')
            return redirect('/')

        if nome != cliente_atual['nome'] or telefone != cliente_atual['telefone']:
            detalhes = f"Alteração cliente ID {id_cliente}: "
            if nome != cliente_atual['nome']:
                detalhes += f"Nome: '{cliente_atual['nome']}' ➜ '{nome}'. "
            if telefone != cliente_atual['telefone']:
                detalhes += f"Telefone: '{cliente_atual['telefone']}' ➜ '{telefone}'."

            cursor.execute("""
                UPDATE usuario SET nome = %s, telefone = %s WHERE id_usuario = %s
            """, (nome, telefone, id_cliente))
            conn.commit()
            registrar_auditoria(id_funcionario, 'ALTERACAO_CLIENTE', detalhes)
            flash('Cliente atualizado com sucesso.', 'success')
        else:
            flash('Nenhuma alteração feita.', 'info')

        return redirect(f'/alterar-cliente/{id_cliente}')

    cursor.execute("SELECT id_usuario, nome, telefone FROM usuario WHERE id_usuario = %s AND tipo_usuario = 'CLIENTE'", (id_cliente,))
    cliente = cursor.fetchone()
    cursor.close()
    conn.close()

    if not cliente:
        flash('Cliente não encontrado.', 'error')
        return redirect('/')

    return render_template('employee/changeclient.html', cliente=cliente)

@alteracoes_bp.route('/selecionar-cliente', methods=['GET', 'POST'])
def selecionar_cliente():
    if not session.get('usuario_logado') or session.get('tipo_usuario') != 'FUNCIONARIO':
        flash('Acesso negado.', 'error')
        return redirect('/')

    clientes = []
    if request.method == 'POST':
        cpf = request.form.get('cpf')
        try:
            conn = conectar_banco()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id_usuario, nome, cpf FROM usuario WHERE tipo_usuario = 'CLIENTE' AND cpf LIKE %s", (f"%{cpf}%",))
            clientes = cursor.fetchall()
            cursor.close()
            conn.close()
        except Exception as e:
            print("Erro na busca:", e)
            flash("Erro ao buscar CPF.", "error")
    return render_template('employee/selectclient.html', clientes=clientes)

