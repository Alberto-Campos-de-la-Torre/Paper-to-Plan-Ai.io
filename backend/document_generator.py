import io
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

try:
    from fpdf import FPDF
    HAS_FPDF = True
except ImportError:
    HAS_FPDF = False
    logger.warning("fpdf2 not installed. PDF generation will not be available.")


class MedicalDocumentGenerator:
    """Generates PDF medical documents using fpdf2."""

    def generate_medical_note(self, consultation: Dict[str, Any], patient: Optional[Dict[str, Any]],
                               doctor: str = "Doctor") -> bytes:
        if not HAS_FPDF:
            raise RuntimeError("fpdf2 is not installed")

        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)

        # Header
        pdf.set_font("Helvetica", "B", 18)
        pdf.cell(0, 10, "MEGI Records", ln=True, align="C")
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 6, "Nota Medica", ln=True, align="C")
        pdf.ln(5)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(5)

        # Patient info
        if patient:
            pdf.set_font("Helvetica", "B", 12)
            pdf.cell(0, 8, "Datos del Paciente", ln=True)
            pdf.set_font("Helvetica", "", 10)
            pdf.cell(0, 6, f"Nombre: {patient.get('name', 'No especificado')}", ln=True)
            if patient.get('date_of_birth'):
                pdf.cell(0, 6, f"Fecha de Nacimiento: {patient['date_of_birth']}", ln=True)
            if patient.get('gender'):
                pdf.cell(0, 6, f"Genero: {patient['gender']}", ln=True)
            if patient.get('blood_type'):
                pdf.cell(0, 6, f"Tipo de Sangre: {patient['blood_type']}", ln=True)
            allergies = patient.get('allergies', [])
            if allergies and isinstance(allergies, list) and len(allergies) > 0:
                pdf.cell(0, 6, f"Alergias: {', '.join(allergies)}", ln=True)
            pdf.ln(3)

        # Doctor and date
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 6, f"Medico: {doctor}", ln=True)
        created = consultation.get('created_at', '')
        if created:
            pdf.cell(0, 6, f"Fecha: {created[:19] if len(str(created)) > 19 else created}", ln=True)
        pdf.ln(5)

        # Analysis content
        analysis = consultation.get('ai_analysis', {})
        if isinstance(analysis, str):
            try:
                import json
                analysis = json.loads(analysis)
            except Exception:
                analysis = {}

        # Summary
        summary = analysis.get('summary', '')
        if summary:
            pdf.set_font("Helvetica", "B", 12)
            pdf.cell(0, 8, "Resumen", ln=True)
            pdf.set_font("Helvetica", "", 10)
            pdf.multi_cell(0, 6, summary)
            pdf.ln(3)

        # Subjective
        subj = analysis.get('subjective', {})
        if isinstance(subj, dict):
            pdf.set_font("Helvetica", "B", 12)
            pdf.cell(0, 8, "Subjetivo", ln=True)
            pdf.set_font("Helvetica", "", 10)
            if subj.get('chief_complaint'):
                pdf.multi_cell(0, 6, f"Motivo de consulta: {subj['chief_complaint']}")
            symptoms = subj.get('symptoms', [])
            if symptoms:
                pdf.multi_cell(0, 6, f"Sintomas: {', '.join(symptoms)}")
            if subj.get('history'):
                pdf.multi_cell(0, 6, f"Antecedentes: {subj['history']}")
            pdf.ln(3)

        # Objective
        obj = analysis.get('objective', {})
        if isinstance(obj, dict):
            pdf.set_font("Helvetica", "B", 12)
            pdf.cell(0, 8, "Objetivo", ln=True)
            pdf.set_font("Helvetica", "", 10)
            vitals = obj.get('vitals', {})
            if isinstance(vitals, dict):
                vitals_str = []
                for k, v in vitals.items():
                    if v:
                        vitals_str.append(f"{k}: {v}")
                if vitals_str:
                    pdf.multi_cell(0, 6, "Signos Vitales: " + ", ".join(vitals_str))
            findings = obj.get('findings', [])
            if findings:
                pdf.multi_cell(0, 6, "Hallazgos: " + ", ".join(findings))
            pdf.ln(3)

        # Assessment
        assess = analysis.get('assessment', {})
        if isinstance(assess, dict):
            pdf.set_font("Helvetica", "B", 12)
            pdf.cell(0, 8, "Evaluacion", ln=True)
            pdf.set_font("Helvetica", "", 10)
            diagnoses = assess.get('diagnoses', [])
            for dx in diagnoses:
                if isinstance(dx, dict):
                    code = f" ({dx.get('cie10_code', '')})" if dx.get('cie10_code') else ""
                    pdf.multi_cell(0, 6, f"- {dx.get('description', '')}{code}")
            pdf.ln(3)

        # Plan
        plan = analysis.get('plan', {})
        if isinstance(plan, dict):
            pdf.set_font("Helvetica", "B", 12)
            pdf.cell(0, 8, "Plan", ln=True)
            pdf.set_font("Helvetica", "", 10)
            meds = plan.get('medications', [])
            if meds:
                pdf.cell(0, 6, "Medicamentos:", ln=True)
                for med in meds:
                    if isinstance(med, dict):
                        line = f"  - {med.get('drug_name', '')} {med.get('dose', '')} {med.get('frequency', '')} x {med.get('duration', '')}"
                        pdf.multi_cell(0, 6, line)
            if plan.get('follow_up'):
                pdf.multi_cell(0, 6, f"Seguimiento: {plan['follow_up']}")
            recs = plan.get('recommendations', [])
            if recs:
                pdf.cell(0, 6, "Recomendaciones:", ln=True)
                for r in recs:
                    pdf.multi_cell(0, 6, f"  - {r}")

        # Footer
        pdf.ln(10)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(3)
        pdf.set_font("Helvetica", "I", 8)
        pdf.cell(0, 5, "Documento generado por MEGI Records - Sistema de Expedientes Medicos Digitales", ln=True, align="C")

        return pdf.output()

    def generate_prescription(self, consultation: Dict[str, Any], patient: Optional[Dict[str, Any]],
                               prescriptions: List[Dict[str, Any]], doctor: str = "Doctor") -> bytes:
        if not HAS_FPDF:
            raise RuntimeError("fpdf2 is not installed")

        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)

        # Header
        pdf.set_font("Helvetica", "B", 18)
        pdf.cell(0, 10, "MEGI Records", ln=True, align="C")
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 6, "Receta Medica", ln=True, align="C")
        pdf.ln(5)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(5)

        # Patient info
        pdf.set_font("Helvetica", "B", 11)
        if patient:
            pdf.cell(0, 6, f"Paciente: {patient.get('name', 'No especificado')}", ln=True)
        pdf.cell(0, 6, f"Medico: {doctor}", ln=True)
        pdf.cell(0, 6, f"Fecha: {datetime.now().strftime('%Y-%m-%d')}", ln=True)
        pdf.ln(5)

        # Prescriptions
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, "Medicamentos", ln=True)
        pdf.ln(3)

        for i, rx in enumerate(prescriptions, 1):
            pdf.set_font("Helvetica", "B", 11)
            pdf.cell(0, 7, f"{i}. {rx.get('drug_name', 'Sin nombre')}", ln=True)
            pdf.set_font("Helvetica", "", 10)
            if rx.get('dose'):
                pdf.cell(0, 6, f"   Dosis: {rx['dose']}", ln=True)
            if rx.get('frequency'):
                pdf.cell(0, 6, f"   Frecuencia: {rx['frequency']}", ln=True)
            if rx.get('duration'):
                pdf.cell(0, 6, f"   Duracion: {rx['duration']}", ln=True)
            if rx.get('instructions'):
                pdf.cell(0, 6, f"   Instrucciones: {rx['instructions']}", ln=True)
            pdf.ln(3)

        # Footer
        pdf.ln(10)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(15)
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 6, f"Firma: ________________________", ln=True, align="C")
        pdf.cell(0, 6, f"Dr. {doctor}", ln=True, align="C")
        pdf.ln(5)
        pdf.set_font("Helvetica", "I", 8)
        pdf.cell(0, 5, "Documento generado por MEGI Records", ln=True, align="C")

        return pdf.output()
