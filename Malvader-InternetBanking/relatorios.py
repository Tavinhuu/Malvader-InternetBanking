from flask import Blueprint, render_template, send_file
from app import conectar_banco
import pandas as pd
from io import BytesIO
from reportlab.pdfgen import canvas

relatorios_bp = Blueprint('relatorios', __name__)

# -------------------- RELATÓRIO MOVIMENTAÇÕES ---------------------

@relatorios_bp.route('/reports')
def reports():
    return render_template('reports/reports.html')

@relatorios_bp.route('/relatorio-movimentacoes')
def relatorio_movimentacoes():
    conn = conectar_banco()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM view_movimentacoes")
    dados = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('reports/movereport.html', dados=dados)

@relatorios_bp.route('/exportar-movimentacoes-excel')
def exportar_movimentacoes_excel():
    conn = conectar_banco()
    df = pd.read_sql("SELECT * FROM view_movimentacoes", conn)
    conn.close()

    output = BytesIO()
    df.to_excel(output, index=False, engine='openpyxl')
    output.seek(0)
    return send_file(output, download_name="relatorio_movimentacoes.xlsx", as_attachment=True)

@relatorios_bp.route('/exportar-movimentacoes-pdf')
def exportar_movimentacoes_pdf():
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute("SELECT id_movimentacao, tipo, valor FROM view_movimentacoes")
    dados = cursor.fetchall()
    cursor.close()
    conn.close()

    output = BytesIO()
    c = canvas.Canvas(output)
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(295, 800, "Relatório de Movimentações")
    y = 750
    for row in dados:
        c.drawString(50, y, f"ID: {row[0]} - Tipo: {row[1]} - Valor: R${row[2]:.2f}")
        y -= 20
        if y < 50:
            c.showPage()
            c.setFont("Helvetica-Bold", 16)
            c.drawCentredString(295, 800, "Relatório de Movimentações")
            y = 750
    c.save()
    output.seek(0)
    return send_file(output, download_name="relatorio_movimentacoes.pdf", as_attachment=True)

# -------------------- RELATÓRIO INADIMPLÊNCIA ---------------------

@relatorios_bp.route('/relatorio-inadimplencia')
def relatorio_inadimplencia():
    conn = conectar_banco()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM view_inadimplencia")
    dados = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('reports/defaultreport.html', dados=dados)

@relatorios_bp.route('/exportar-inadimplencia-excel')
def exportar_inadimplencia_excel():
    conn = conectar_banco()
    df = pd.read_sql("SELECT * FROM view_inadimplencia", conn)
    conn.close()

    output = BytesIO()
    df.to_excel(output, index=False, engine='openpyxl')
    output.seek(0)
    return send_file(output, download_name="relatorio_inadimplencia.xlsx", as_attachment=True)

@relatorios_bp.route('/exportar-inadimplencia-pdf')
def exportar_inadimplencia_pdf():
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute("SELECT id_conta, numero_conta, saldo FROM view_inadimplencia")
    dados = cursor.fetchall()
    cursor.close()
    conn.close()

    output = BytesIO()
    c = canvas.Canvas(output)
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(295, 800, "Relatório de Inadimplência")
    y = 750
    for row in dados:
        c.drawString(50, y, f"Conta: {row[0]} - Número: {row[1]} - Saldo: R${row[2]:.2f}")
        y -= 20
        if y < 50:
            c.showPage()
            c.setFont("Helvetica-Bold", 16)
            c.drawCentredString(295, 800, "Relatório de Inadimplência")
            y = 750
    c.save()
    output.seek(0)
    return send_file(output, download_name="relatorio_inadimplencia.pdf", as_attachment=True)

# -------------------- RELATÓRIO DESEMPENHO FUNCIONÁRIOS ---------------------

@relatorios_bp.route('/relatorio-desempenho')
def relatorio_desempenho():
    conn = conectar_banco()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM view_desempenho_func")
    dados = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('reports/performreport.html', dados=dados)

@relatorios_bp.route('/exportar-desempenho-excel')
def exportar_desempenho_excel():
    conn = conectar_banco()
    df = pd.read_sql("SELECT * FROM view_desempenho_func", conn)
    conn.close()

    output = BytesIO()
    df.to_excel(output, index=False, engine='openpyxl')
    output.seek(0)
    return send_file(output, download_name="relatorio_desempenho.xlsx", as_attachment=True)

@relatorios_bp.route('/exportar-desempenho-pdf')
def exportar_desempenho_pdf():
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute("SELECT nome, contas_criadas, contas_ativas FROM view_desempenho_func")
    dados = cursor.fetchall()
    cursor.close()
    conn.close()

    output = BytesIO()
    c = canvas.Canvas(output)
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(295, 800, "Relatório de Desempenho")
    y = 750
    for row in dados:
        c.drawString(50, y, f"Nome: {row[0]} - Criadas: {row[1]} - Ativas: {row[2]}")
        y -= 20
        if y < 50:
            c.showPage()
            c.setFont("Helvetica-Bold", 16)
            c.drawCentredString(295, 800, "Relatório de Desempenho")
            y = 750
    c.save()
    output.seek(0)
    return send_file(output, download_name="relatorio_desempenho.pdf", as_attachment=True)
