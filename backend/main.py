"""
PharmaGuard - Main FastAPI Application
Pharmacogenomic Risk Prediction System
"""

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uuid
import json
from datetime import datetime
from typing import Optional, List

from vcf_parser import parse_vcf, get_sample_vcf
from risk_engine import assess_risk, get_supported_drugs, get_phenotype
from llm_explainer import generate_explanation

app = FastAPI(
    title="PharmaGuard API",
    description="Pharmacogenomic Risk Prediction System",
    version="1.0.0"
)

# CORS — allow frontend to call backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "PharmaGuard API is running", "version": "1.0.0"}


@app.get("/drugs")
def list_drugs():
    """Return list of supported drugs."""
    return {"supported_drugs": get_supported_drugs()}


@app.post("/analyze")
async def analyze(
    vcf_file: UploadFile = File(...),
    drugs: str = Form(...),
    patient_id: Optional[str] = Form(None),
    openai_api_key: Optional[str] = Form(None)
):
    """
    Main analysis endpoint.
    Accepts VCF file + drug names, returns pharmacogenomic risk assessment.
    """
    # Validate file type
    if not vcf_file.filename.endswith(".vcf"):
        raise HTTPException(status_code=400, detail="Only .vcf files are supported.")

    # Read file content
    content = await vcf_file.read()
    try:
        vcf_content = content.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="VCF file must be UTF-8 encoded text.")

    # Parse VCF
    parsed = parse_vcf(vcf_content)

    if not parsed["vcf_parsing_success"]:
        raise HTTPException(status_code=422, detail="VCF file could not be parsed. Please check the file format.")

    # Parse drug list
    drug_list = [d.strip().upper() for d in drugs.split(",") if d.strip()]
    if not drug_list:
        raise HTTPException(status_code=400, detail="Please provide at least one drug name.")

    # Generate results for each drug
    results = []
    pid = patient_id or f"PATIENT_{str(uuid.uuid4())[:6].upper()}"

    for drug in drug_list:
        result = build_result(
            patient_id=pid,
            drug=drug,
            parsed_vcf=parsed,
            api_key=openai_api_key
        )
        results.append(result)

    # Return single result if one drug, list if multiple
    if len(results) == 1:
        return JSONResponse(content=results[0])
    else:
        return JSONResponse(content={"patient_id": pid, "results": results})


@app.post("/analyze/sample")
async def analyze_sample(
    drugs: str = Form("CODEINE,WARFARIN"),
    openai_api_key: Optional[str] = Form(None)
):
    """
    Analyze using the built-in sample VCF file for demo/testing.
    """
    sample_vcf = get_sample_vcf()
    parsed = parse_vcf(sample_vcf)

    drug_list = [d.strip().upper() for d in drugs.split(",") if d.strip()]
    pid = "PATIENT_DEMO01"

    results = []
    for drug in drug_list:
        result = build_result(
            patient_id=pid,
            drug=drug,
            parsed_vcf=parsed,
            api_key=openai_api_key
        )
        results.append(result)

    if len(results) == 1:
        return JSONResponse(content=results[0])
    else:
        return JSONResponse(content={"patient_id": pid, "results": results})


def build_result(patient_id: str, drug: str, parsed_vcf: dict, api_key: Optional[str] = None) -> dict:
    """Build the full result JSON for a drug."""

    diplotypes = parsed_vcf.get("diplotypes", {})
    gene_variants = parsed_vcf.get("gene_variants", {})

    # Get risk assessment
    risk = assess_risk(drug, diplotypes)

    primary_gene = risk["primary_gene"]
    phenotype = risk["phenotype"]
    diplotype = risk["diplotype"]

    # Get detected variants for primary gene
    detected_variants = gene_variants.get(primary_gene, [])
    variant_list = [
        {
            "rsid": v.get("rsid", ""),
            "chromosome": v.get("chromosome", ""),
            "position": v.get("position", ""),
            "ref_allele": v.get("ref_allele", ""),
            "alt_allele": v.get("alt_allele", ""),
            "gene": v.get("gene", ""),
            "star_allele": v.get("star_allele", "")
        }
        for v in detected_variants
    ]

    # Generate LLM explanation
    explanation = generate_explanation(
        drug=drug,
        gene=primary_gene,
        diplotype=diplotype,
        phenotype=phenotype,
        risk_label=risk["risk_label"],
        severity=risk["severity"],
        recommendation=risk["recommendation"],
        detected_variants=variant_list,
        api_key=api_key
    )

    return {
        "patient_id": patient_id,
        "drug": drug,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "risk_assessment": {
            "risk_label": risk["risk_label"],
            "confidence_score": risk["confidence_score"],
            "severity": risk["severity"]
        },
        "pharmacogenomic_profile": {
            "primary_gene": primary_gene,
            "diplotype": diplotype,
            "phenotype": phenotype,
            "detected_variants": variant_list
        },
        "clinical_recommendation": {
            "recommendation": risk["recommendation"],
            "cpic_recommendation": risk["cpic_recommendation"],
            "requires_dose_adjustment": risk["risk_label"] in ["Adjust Dosage", "Toxic"],
            "contraindicated": risk["risk_label"] == "Toxic" and risk["severity"] == "critical"
        },
        "llm_generated_explanation": explanation,
        "quality_metrics": {
            "vcf_parsing_success": parsed_vcf.get("vcf_parsing_success", False),
            "total_variants_parsed": parsed_vcf.get("total_variants_found", 0),
            "genes_detected": parsed_vcf.get("genes_detected", []),
            "primary_gene_found": primary_gene in parsed_vcf.get("genes_detected", []),
            "explanation_source": explanation.get("generated_by", "unknown")
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
