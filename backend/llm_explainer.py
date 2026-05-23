"""
LLM Explainer for PharmaGuard
Generates clinical explanations using OpenAI GPT-4
"""

import os
import json
from typing import Dict, Optional
from datetime import datetime


def generate_explanation(
    drug: str,
    gene: str,
    diplotype: str,
    phenotype: str,
    risk_label: str,
    severity: str,
    recommendation: str,
    detected_variants: list,
    api_key: Optional[str] = None
) -> Dict:
    """
    Generate LLM-based clinical explanation for the pharmacogenomic risk.
    Falls back to rule-based explanation if API key not available.
    """
    key = api_key or os.environ.get("OPENAI_API_KEY")

    if key:
        return _generate_openai_explanation(
            drug, gene, diplotype, phenotype,
            risk_label, severity, recommendation, detected_variants, key
        )
    else:
        return _generate_fallback_explanation(
            drug, gene, diplotype, phenotype,
            risk_label, severity, recommendation, detected_variants
        )


def _generate_openai_explanation(
    drug, gene, diplotype, phenotype,
    risk_label, severity, recommendation, detected_variants, api_key
) -> Dict:
    try:
        import openai
        client = openai.OpenAI(api_key=api_key)

        variant_str = ", ".join([v.get("rsid", "") for v in detected_variants]) if detected_variants else "none detected"

        prompt = f"""You are a clinical pharmacogenomics expert. Generate a concise clinical explanation for the following:

Patient Pharmacogenomic Data:
- Drug: {drug}
- Primary Gene: {gene}
- Diplotype: {diplotype}
- Phenotype: {phenotype}
- Risk Assessment: {risk_label} (Severity: {severity})
- Detected Variants: {variant_str}
- Clinical Recommendation: {recommendation}

Please provide:
1. A brief summary (2-3 sentences) explaining why this patient has this risk
2. The biological mechanism (how this gene variant affects drug metabolism)
3. Clinical implications for this specific patient
4. Any monitoring parameters the clinician should watch

Be specific, cite the variants and diplotype in your explanation. Use clear, professional medical language."""

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a clinical pharmacogenomics expert providing actionable medical guidance."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.3
        )

        full_text = response.choices[0].message.content

        # Split into sections
        lines = full_text.strip().split("\n")
        summary = lines[0] if lines else full_text[:200]

        return {
            "summary": summary,
            "mechanism": _extract_section(full_text, "mechanism", "biological"),
            "clinical_implications": _extract_section(full_text, "clinical implications", "implications"),
            "monitoring": _extract_section(full_text, "monitoring", "watch"),
            "full_explanation": full_text,
            "generated_by": "gpt-4",
            "generated_at": datetime.utcnow().isoformat()
        }

    except Exception as e:
        # Fall back to rule-based if OpenAI fails
        fallback = _generate_fallback_explanation(
            drug, gene, diplotype, phenotype,
            risk_label, severity, recommendation, detected_variants
        )
        fallback["error"] = str(e)
        return fallback


def _extract_section(text: str, *keywords) -> str:
    """Extract a section from LLM response based on keywords."""
    lines = text.split("\n")
    for i, line in enumerate(lines):
        if any(kw.lower() in line.lower() for kw in keywords):
            # Return next non-empty line(s)
            result = []
            for j in range(i + 1, min(i + 4, len(lines))):
                if lines[j].strip():
                    result.append(lines[j].strip())
            if result:
                return " ".join(result)
    return ""


def _generate_fallback_explanation(
    drug, gene, diplotype, phenotype,
    risk_label, severity, recommendation, detected_variants
) -> Dict:
    """
    Rule-based fallback explanation when no LLM API is available.
    Still clinically accurate based on CPIC guidelines.
    """
    variant_str = ", ".join([v.get("rsid", "") for v in detected_variants]) if detected_variants else "no specific variants detected"

    # Mechanism templates per gene
    mechanisms = {
        "CYP2D6": f"CYP2D6 encodes a key hepatic enzyme responsible for metabolizing {drug}. "
                  f"The {diplotype} diplotype results in {phenotype.lower()} status, "
                  f"meaning the enzyme activity is {'absent or severely reduced' if 'Poor' in phenotype else 'reduced' if 'Intermediate' in phenotype else 'increased' if 'Ultra' in phenotype else 'normal'}.",

        "CYP2C19": f"CYP2C19 is responsible for activating or metabolizing {drug}. "
                   f"Variant(s) {variant_str} result in the {diplotype} diplotype, "
                   f"leading to {phenotype.lower()} status which {'prevents drug activation' if 'Poor' in phenotype else 'reduces drug activation' if 'Intermediate' in phenotype else 'enhances drug metabolism'}.",

        "CYP2C9": f"CYP2C9 is the primary enzyme metabolizing {drug}. "
                  f"The {diplotype} diplotype ({variant_str}) reduces enzyme activity, "
                  f"causing {drug} to accumulate to {'dangerous' if 'Poor' in phenotype else 'elevated'} levels in the bloodstream.",

        "SLCO1B1": f"SLCO1B1 encodes a hepatic uptake transporter that controls {drug} uptake into liver cells. "
                   f"The {diplotype} diplotype impairs this transporter, reducing {drug} clearance "
                   f"and increasing systemic exposure with risk of {'severe' if 'Poor' in phenotype else 'moderate'} muscle toxicity.",

        "TPMT": f"TPMT metabolizes {drug} into inactive metabolites. "
                f"The {diplotype} diplotype ({variant_str}) {'abolishes' if 'Poor' in phenotype else 'reduces'} TPMT activity, "
                f"causing toxic metabolites to accumulate and risk {'life-threatening' if 'Poor' in phenotype else 'significant'} bone marrow suppression.",

        "DPYD": f"DPYD is the rate-limiting enzyme in {drug} catabolism. "
                f"The {diplotype} diplotype ({variant_str}) {'severely impairs' if 'Poor' in phenotype else 'reduces'} DPYD activity, "
                f"leading to {drug} accumulation and {'potentially fatal' if 'Poor' in phenotype else 'serious'} toxicity."
    }

    mechanism = mechanisms.get(gene, f"The {gene} gene affects {drug} metabolism. Variant {diplotype} results in {phenotype.lower()} status.")

    summary = (
        f"Patient carries the {diplotype} diplotype in {gene}, resulting in {phenotype} status. "
        f"For {drug}, this translates to a '{risk_label}' risk assessment with {severity} severity. "
        f"{recommendation}"
    )

    clinical_implications = {
        "Toxic": f"This patient is at significant risk of {drug}-related toxicity. Dose modification or drug substitution is strongly recommended before prescribing.",
        "Ineffective": f"{drug} is unlikely to provide therapeutic benefit for this patient due to impaired drug activation or metabolism. An alternative therapy should be considered.",
        "Adjust Dosage": f"Standard dosing of {drug} may not be appropriate. A dose adjustment based on the patient's metabolizer status is recommended to optimize efficacy and minimize harm.",
        "Safe": f"This patient is expected to respond normally to standard {drug} dosing. No pharmacogenomic-based dose adjustments are necessary.",
        "Unknown": f"Insufficient evidence exists to make a pharmacogenomic recommendation for this drug-gene combination."
    }

    monitoring = {
        "Toxic": "Monitor closely for signs of drug toxicity. Consider therapeutic drug monitoring if available.",
        "Ineffective": "Monitor for lack of therapeutic response. Consider switching to an alternative medication.",
        "Adjust Dosage": "Monitor drug levels and clinical response after dose adjustment. Titrate based on therapeutic targets.",
        "Safe": "Routine clinical monitoring per standard of care.",
        "Unknown": "Standard clinical monitoring. Consult clinical pharmacist for additional guidance."
    }

    return {
        "summary": summary,
        "mechanism": mechanism,
        "clinical_implications": clinical_implications.get(risk_label, "Consult clinical pharmacist."),
        "monitoring": monitoring.get(risk_label, "Standard monitoring."),
        "full_explanation": f"{summary}\n\nMechanism: {mechanism}\n\nClinical Implications: {clinical_implications.get(risk_label, '')}\n\nMonitoring: {monitoring.get(risk_label, '')}",
        "generated_by": "rule-based-fallback",
        "generated_at": datetime.utcnow().isoformat()
    }
