# -*- coding: utf-8 -*-
"""Generador de reportes PDF para listados de consultas SIDEGEDUC."""

import io
from datetime import datetime

try:
    from fpdf import FPDF
    FPDF_AVAILABLE = True
except ImportError:
    FPDF_AVAILABLE = False


class ReportPDF(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 10)
        self.set_text_color(6, 167, 125)
        self.cell(0, 8, 'SIDEGEDUC - Sistema de Gestion Educativa', ln=True, align='C')
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Pagina {self.page_no()}/{{nb}}', align='C')


def _row_persona(r, role_display):
    def _v(r, key, *idx):
        if hasattr(r, '_mapping') and r._mapping:
            v = r._mapping.get(key, '')
            return str(v) if v is not None else ''
        for i in idx:
            if len(r) > i and r[i] is not None:
                return str(r[i])
        return ''
    n1 = _v(r, 'primer_nombre', 1)
    n2 = _v(r, 'segundo_nombre', 2)
    a1 = _v(r, 'primer_apellido', 3)
    a2 = _v(r, 'segundo_apellido', 4)
    nombre = f"{n1} {n2} {a1} {a2}".strip() or '-'
    tipo = _v(r, 'tipo_persona', -1) or _v(r, 'rol', -1) or role_display or '-'
    return nombre[:50], tipo[:20]


def generar_pdf_personas(rows, role_display, title):
    """Genera PDF del listado de personas."""
    if not FPDF_AVAILABLE:
        return None, "Modulo fpdf2 no instalado. Ejecute: pip install fpdf2"

    pdf = ReportPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, title or f"Listado de {role_display}", ln=True, align='C')
    pdf.set_font('Helvetica', '', 9)
    pdf.cell(0, 6, f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True, align='C')
    pdf.ln(6)

    if not rows:
        pdf.cell(0, 8, "No hay registros para mostrar.", ln=True)
    else:
        col_w = [12, 100, 55]
        pdf.set_font('Helvetica', 'B', 9)
        pdf.set_fill_color(6, 167, 125)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(col_w[0], 8, '#', border=1, fill=True)
        pdf.cell(col_w[1], 8, 'Nombre', border=1, fill=True)
        pdf.cell(col_w[2], 8, 'Tipo', border=1, fill=True, ln=True)
        pdf.set_font('Helvetica', '', 9)
        pdf.set_text_color(0, 0, 0)
        fill = False
        for i, r in enumerate(rows, 1):
            nombre, tipo = _row_persona(r, role_display)
            if fill:
                pdf.set_fill_color(248, 249, 250)
            pdf.cell(col_w[0], 7, str(i), border=1, fill=fill)
            pdf.cell(col_w[1], 7, nombre, border=1, fill=fill)
            pdf.cell(col_w[2], 7, tipo, border=1, fill=fill, ln=True)
            fill = not fill

    buf = io.BytesIO()
    pdf.output(buf)
    buf.seek(0)
    return buf.getvalue(), None


def generar_pdf_planteles(rows):
    """Genera PDF del listado de planteles."""
    if not FPDF_AVAILABLE:
        return None, "Modulo fpdf2 no instalado. Ejecute: pip install fpdf2"

    pdf = ReportPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_font('Helvetica', 'B', 14)
    pdf.cell(0, 10, "Listado de Planteles", ln=True, align='C')
    pdf.set_font('Helvetica', '', 9)
    pdf.cell(0, 6, f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True, align='C')
    pdf.ln(6)

    if not rows:
        pdf.cell(0, 8, "No hay registros para mostrar.", ln=True)
    else:
        col_w = [12, 120, 55]
        pdf.set_font('Helvetica', 'B', 9)
        pdf.set_fill_color(6, 167, 125)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(col_w[0], 8, '#', border=1, fill=True)
        pdf.cell(col_w[1], 8, 'Nombre', border=1, fill=True)
        pdf.cell(col_w[2], 8, 'Codigo PA', border=1, fill=True, ln=True)
        pdf.set_font('Helvetica', '', 9)
        pdf.set_text_color(0, 0, 0)
        fill = False
        for i, r in enumerate(rows, 1):
            nom = str(r[1] if len(r) > 1 else '')[:45]
            cod = str(r[2] if len(r) > 2 else '')[:15]
            if fill:
                pdf.set_fill_color(248, 249, 250)
            pdf.cell(col_w[0], 7, str(i), border=1, fill=fill)
            pdf.cell(col_w[1], 7, nom, border=1, fill=fill)
            pdf.cell(col_w[2], 7, cod, border=1, fill=fill, ln=True)
            fill = not fill

    buf = io.BytesIO()
    pdf.output(buf)
    buf.seek(0)
    return buf.getvalue(), None


def generar_pdf_secciones(rows):
    """Genera PDF del listado de secciones."""
    if not FPDF_AVAILABLE:
        return None, "Modulo fpdf2 no instalado. Ejecute: pip install fpdf2"

    pdf = ReportPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_font('Helvetica', 'B', 14)
    pdf.cell(0, 10, "Listado de Secciones", ln=True, align='C')
    pdf.set_font('Helvetica', '', 9)
    pdf.cell(0, 6, f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True, align='C')
    pdf.ln(6)

    if not rows:
        pdf.cell(0, 8, "No hay registros para mostrar.", ln=True)
    else:
        col_w = [10, 25, 30, 25, 85]
        pdf.set_font('Helvetica', 'B', 9)
        pdf.set_fill_color(6, 167, 125)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(col_w[0], 8, '#', border=1, fill=True)
        pdf.cell(col_w[1], 8, 'ID', border=1, fill=True)
        pdf.cell(col_w[2], 8, 'Grado', border=1, fill=True)
        pdf.cell(col_w[3], 8, 'Letra', border=1, fill=True)
        pdf.cell(col_w[4], 8, 'Nivel', border=1, fill=True, ln=True)
        pdf.set_font('Helvetica', '', 9)
        pdf.set_text_color(0, 0, 0)
        fill = False
        for i, r in enumerate(rows, 1):
            row = r._mapping if hasattr(r, '_mapping') else {}
            sid = str(row.get('id_seccion', r[0] if len(r) > 0 else ''))
            grado = str(row.get('numero_grado', r[1] if len(r) > 1 else '') or 'N/A')
            letra = str(row.get('letra', r[2] if len(r) > 2 else '') or 'N/A')
            nivel = str(row.get('nombre_nivel', r[3] if len(r) > 3 else '') or 'N/A')[:30]
            if fill:
                pdf.set_fill_color(248, 249, 250)
            pdf.cell(col_w[0], 7, str(i), border=1, fill=fill)
            pdf.cell(col_w[1], 7, sid, border=1, fill=fill)
            pdf.cell(col_w[2], 7, grado, border=1, fill=fill)
            pdf.cell(col_w[3], 7, letra, border=1, fill=fill)
            pdf.cell(col_w[4], 7, nivel, border=1, fill=fill, ln=True)
            fill = not fill

    buf = io.BytesIO()
    pdf.output(buf)
    buf.seek(0)
    return buf.getvalue(), None
