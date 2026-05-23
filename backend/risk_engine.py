"""
TechRx Risk Engine - Fully CPIC Compliant
Sources: CPIC Guidelines (cpicpgx.org), PharmGKB
Covers: CYP2D6, CYP2C19, CYP2C9, VKORC1, SLCO1B1, TPMT, NUDT15, DPYD
"""

from typing import Dict, Optional

# ─────────────────────────────────────────────────────────────
# DIPLOTYPE → PHENOTYPE MAPPINGS
# Source: CPIC/PharmGKB diplotype-phenotype tables
# ─────────────────────────────────────────────────────────────

DIPLOTYPE_TO_PHENOTYPE = {
    "CYP2D6": {
        # Ultrarapid Metabolizer (URM) — gene duplication
        "*1/*1xN": "Ultrarapid Metabolizer",
        "*1/*2xN": "Ultrarapid Metabolizer",
        "*2/*2xN": "Ultrarapid Metabolizer",
        "*2xN/*2xN": "Ultrarapid Metabolizer",
        # Normal Metabolizer (NM)
        "*1/*1": "Normal Metabolizer",
        "*1/*2": "Normal Metabolizer",
        "*2/*2": "Normal Metabolizer",
        "*1/*9": "Normal Metabolizer",
        "*1/*10": "Normal Metabolizer",
        "*1/*41": "Intermediate Metabolizer",
        # Intermediate Metabolizer (IM)
        "*4/*10": "Intermediate Metabolizer",
        "*4/*41": "Intermediate Metabolizer",
        "*5/*10": "Intermediate Metabolizer",
        "*1/*4": "Intermediate Metabolizer",
        "*1/*5": "Intermediate Metabolizer",
        "*1/*6": "Intermediate Metabolizer",
        "*2/*4": "Intermediate Metabolizer",
        "*2/*5": "Intermediate Metabolizer",
        "*2/*41": "Intermediate Metabolizer",
        "*10/*10": "Intermediate Metabolizer",
        "*41/*41": "Intermediate Metabolizer",
        # Poor Metabolizer (PM)
        "*4/*4": "Poor Metabolizer",
        "*4/*5": "Poor Metabolizer",
        "*4/*6": "Poor Metabolizer",
        "*5/*5": "Poor Metabolizer",
        "*5/*6": "Poor Metabolizer",
        "*6/*6": "Poor Metabolizer",
        "*3/*4": "Poor Metabolizer",
        "*3/*5": "Poor Metabolizer",
        "*3/*3": "Poor Metabolizer",
        "default": "Normal Metabolizer"
    },
    "CYP2C19": {
        # Ultrarapid Metabolizer
        "*17/*17": "Ultrarapid Metabolizer",
        # Rapid Metabolizer
        "*1/*17": "Rapid Metabolizer",
        "*2/*17": "Rapid Metabolizer",  # Note: controversial, treated as IM by some guidelines
        # Normal Metabolizer
        "*1/*1": "Normal Metabolizer",
        # Intermediate Metabolizer
        "*1/*2": "Intermediate Metabolizer",
        "*1/*3": "Intermediate Metabolizer",
        "*2/*17": "Intermediate Metabolizer",
        # Poor Metabolizer
        "*2/*2": "Poor Metabolizer",
        "*2/*3": "Poor Metabolizer",
        "*3/*3": "Poor Metabolizer",
        "default": "Normal Metabolizer"
    },
    "CYP2C9": {
        # Normal Metabolizer
        "*1/*1": "Normal Metabolizer",
        # Intermediate Metabolizer
        "*1/*2": "Intermediate Metabolizer",
        "*1/*3": "Intermediate Metabolizer",
        "*1/*5": "Intermediate Metabolizer",
        "*1/*6": "Intermediate Metabolizer",
        "*1/*8": "Intermediate Metabolizer",
        "*1/*11": "Intermediate Metabolizer",
        "*2/*2": "Intermediate Metabolizer",
        "*2/*3": "Poor Metabolizer",
        # Poor Metabolizer
        "*3/*3": "Poor Metabolizer",
        "*2/*3": "Poor Metabolizer",
        "*3/*5": "Poor Metabolizer",
        "*3/*6": "Poor Metabolizer",
        "default": "Normal Metabolizer"
    },
    "VKORC1": {
        # VKORC1 uses haplotypes based on rs9923231 (-1639G>A)
        # GG = low sensitivity (need higher warfarin dose)
        # GA = intermediate sensitivity
        # AA = high sensitivity (need lower warfarin dose)
        "GG": "Low Sensitivity",       # Wild type, needs higher dose
        "GA": "Intermediate Sensitivity",
        "AG": "Intermediate Sensitivity",
        "AA": "High Sensitivity",       # High risk of over-anticoagulation
        "*1/*1": "Low Sensitivity",
        "*1/*2": "Intermediate Sensitivity",
        "*2/*2": "High Sensitivity",
        "default": "Intermediate Sensitivity"
    },
    "SLCO1B1": {
        "*1a/*1a": "Normal Function",
        "*1a/*1b": "Normal Function",
        "*1b/*1b": "Normal Function",
        "*1/*1": "Normal Function",
        "*1/*5": "Decreased Function",
        "*1/*15": "Decreased Function",
        "*1/*17": "Decreased Function",
        "*5/*5": "Poor Function",
        "*5/*15": "Poor Function",
        "*15/*15": "Poor Function",
        "default": "Normal Function"
    },
    "TPMT": {
        "*1/*1": "Normal Metabolizer",
        "*1/*2": "Intermediate Metabolizer",
        "*1/*3A": "Intermediate Metabolizer",
        "*1/*3B": "Intermediate Metabolizer",
        "*1/*3C": "Intermediate Metabolizer",
        "*1/*4": "Intermediate Metabolizer",
        "*2/*3A": "Poor Metabolizer",
        "*2/*3C": "Poor Metabolizer",
        "*3A/*3A": "Poor Metabolizer",
        "*3A/*3C": "Poor Metabolizer",
        "*3C/*3C": "Poor Metabolizer",
        "*3A/*4": "Poor Metabolizer",
        "default": "Normal Metabolizer"
    },
    "NUDT15": {
        "*1/*1": "Normal Metabolizer",
        "*1/*2": "Intermediate Metabolizer",
        "*1/*3": "Intermediate Metabolizer",
        "*1/*4": "Intermediate Metabolizer",
        "*1/*5": "Intermediate Metabolizer",
        "*2/*2": "Poor Metabolizer",
        "*2/*3": "Poor Metabolizer",
        "*3/*3": "Poor Metabolizer",
        "*3/*4": "Poor Metabolizer",
        "default": "Normal Metabolizer"
    },
    "DPYD": {
        "*1/*1": "Normal Metabolizer",
        "*1/*2A": "Intermediate Metabolizer",
        "*1/*13": "Intermediate Metabolizer",
        "*1/*B3": "Intermediate Metabolizer",
        "*2A/*2A": "Poor Metabolizer",
        "*2A/*13": "Poor Metabolizer",
        "*13/*13": "Poor Metabolizer",
        "default": "Normal Metabolizer"
    },
    "CYP2B6": {
        # Normal Metabolizer
        "*1/*1": "Normal Metabolizer",
        "*1/*4": "Normal Metabolizer",
        "*1/*22": "Normal Metabolizer",
        # Intermediate Metabolizer
        "*1/*6": "Intermediate Metabolizer",
        "*1/*9": "Intermediate Metabolizer",
        "*1/*18": "Intermediate Metabolizer",
        "*4/*6": "Intermediate Metabolizer",
        "*6/*22": "Intermediate Metabolizer",
        "*1/*16": "Intermediate Metabolizer",
        # Slow Metabolizer (equivalent to Poor in CYP2B6 terminology)
        "*6/*6": "Slow Metabolizer",
        "*6/*9": "Slow Metabolizer",
        "*6/*18": "Slow Metabolizer",
        "*6/*16": "Slow Metabolizer",
        "*9/*9": "Slow Metabolizer",
        "*18/*18": "Slow Metabolizer",
        "default": "Normal Metabolizer"
    }
}


# ─────────────────────────────────────────────────────────────
# DRUG RISK TABLE — CPIC Aligned
# Each drug has primary gene, optional secondary gene,
# and per-phenotype risk/recommendation
# ─────────────────────────────────────────────────────────────

DRUG_RISK_TABLE = {
    "CODEINE": {
        "primary_gene": "CYP2D6",
        "cpic_guideline_url": "https://cpicpgx.org/guidelines/guideline-for-codeine-and-cyp2d6/",
        "risks": {
            "Ultrarapid Metabolizer": {
                "risk_label": "Toxic",
                "severity": "critical",
                "confidence_score": 0.97,
                "recommendation": (
                    "CONTRAINDICATED. Patient is an Ultrarapid Metabolizer — CYP2D6 converts codeine "
                    "to morphine at an accelerated rate, causing dangerously high morphine plasma levels. "
                    "Risk of life-threatening respiratory depression, especially in children and breastfeeding infants. "
                    "Use a non-opioid analgesic (e.g., acetaminophen, NSAIDs) or a non-CYP2D6-metabolized opioid "
                    "(e.g., morphine, oxymorphone, buprenorphine)."
                ),
                "cpic_recommendation": "Avoid codeine. Use an alternative analgesic not metabolized by CYP2D6."
            },
            "Normal Metabolizer": {
                "risk_label": "Safe",
                "severity": "none",
                "confidence_score": 0.92,
                "recommendation": (
                    "Standard codeine dosing is appropriate. Patient metabolizes codeine to morphine at a "
                    "normal rate. Use label-recommended age- or weight-specific dosing. "
                    "Standard monitoring for opioid side effects applies."
                ),
                "cpic_recommendation": "Use label-recommended age- or weight-specific dosing."
            },
            "Intermediate Metabolizer": {
                "risk_label": "Adjust Dosage",
                "severity": "moderate",
                "confidence_score": 0.82,
                "recommendation": (
                    "Use with caution. Patient has reduced CYP2D6 activity, resulting in lower-than-normal "
                    "morphine conversion. Analgesic effect may be reduced. Consider using label-recommended "
                    "dosing and monitor for reduced efficacy. If inadequate pain control, consider an "
                    "alternative analgesic not metabolized by CYP2D6."
                ),
                "cpic_recommendation": "Use label-recommended dosing. If no adequate response, consider alternative analgesic."
            },
            "Poor Metabolizer": {
                "risk_label": "Ineffective",
                "severity": "moderate",
                "confidence_score": 0.95,
                "recommendation": (
                    "Codeine will be ineffective. Patient lacks functional CYP2D6 enzyme and cannot convert "
                    "codeine to its active metabolite morphine. No meaningful analgesia will be achieved. "
                    "Use a non-opioid analgesic (acetaminophen, NSAIDs) or a non-CYP2D6-metabolized opioid "
                    "(morphine, oxymorphone, buprenorphine, fentanyl)."
                ),
                "cpic_recommendation": "Avoid codeine. Use alternative non-opioid or non-CYP2D6-metabolized opioid analgesic."
            }
        }
    },

    "WARFARIN": {
        "primary_gene": "CYP2C9",
        "secondary_gene": "VKORC1",
        "cpic_guideline_url": "https://cpicpgx.org/guidelines/guideline-for-warfarin-and-cyp2c9-and-vkorc1/",
        "risks": {
            # CYP2C9 NM + VKORC1 combinations
            "Normal Metabolizer_Low Sensitivity": {
                "risk_label": "Safe",
                "severity": "none",
                "confidence_score": 0.88,
                "recommendation": (
                    "Standard warfarin initiation is appropriate (typically 5–10 mg/day). "
                    "CYP2C9 normal metabolizer status and VKORC1 low sensitivity (GG genotype) indicate "
                    "standard warfarin requirements. Initiate with standard dose and titrate based on INR. "
                    "Target INR 2.0–3.0 for most indications."
                ),
                "cpic_recommendation": "Initiate warfarin with standard 5-10 mg/day. Titrate based on INR."
            },
            "Normal Metabolizer_Intermediate Sensitivity": {
                "risk_label": "Adjust Dosage",
                "severity": "low",
                "confidence_score": 0.85,
                "recommendation": (
                    "Initiate with slightly reduced dose (4–6 mg/day). VKORC1 intermediate sensitivity "
                    "indicates moderate warfarin sensitivity. Monitor INR closely during first 2 weeks. "
                    "Target INR 2.0–3.0."
                ),
                "cpic_recommendation": "Initiate with 4-6 mg/day. Monitor INR frequently."
            },
            "Normal Metabolizer_High Sensitivity": {
                "risk_label": "Adjust Dosage",
                "severity": "moderate",
                "confidence_score": 0.87,
                "recommendation": (
                    "Reduce initiation dose by ~25% (3–5 mg/day). VKORC1 AA genotype indicates high "
                    "warfarin sensitivity — standard doses risk over-anticoagulation and bleeding. "
                    "Frequent INR monitoring during initiation is essential."
                ),
                "cpic_recommendation": "Initiate with 3-5 mg/day. Frequent INR monitoring required."
            },
            "Intermediate Metabolizer_Low Sensitivity": {
                "risk_label": "Adjust Dosage",
                "severity": "moderate",
                "confidence_score": 0.86,
                "recommendation": (
                    "Reduce warfarin initiation dose by 25% (3–5 mg/day). CYP2C9 intermediate metabolizer "
                    "status means warfarin is cleared more slowly than normal, increasing bleeding risk. "
                    "Monitor INR every 3–5 days during initiation."
                ),
                "cpic_recommendation": "Initiate with 25% dose reduction. Frequent INR monitoring."
            },
            "Intermediate Metabolizer_Intermediate Sensitivity": {
                "risk_label": "Adjust Dosage",
                "severity": "moderate",
                "confidence_score": 0.88,
                "recommendation": (
                    "Reduce warfarin initiation dose by 25–40% (2–4 mg/day). Both CYP2C9 reduced "
                    "metabolism and VKORC1 intermediate sensitivity contribute to elevated warfarin "
                    "exposure. Close INR monitoring required during first month."
                ),
                "cpic_recommendation": "Initiate with 25-40% dose reduction. Weekly INR monitoring for first month."
            },
            "Intermediate Metabolizer_High Sensitivity": {
                "risk_label": "Toxic",
                "severity": "high",
                "confidence_score": 0.91,
                "recommendation": (
                    "Significant dose reduction required — initiate at 1.5–3 mg/day (50–60% reduction). "
                    "Combined CYP2C9 reduced metabolism and VKORC1 high sensitivity substantially increase "
                    "bleeding risk at standard doses. Twice-weekly INR monitoring during first month."
                ),
                "cpic_recommendation": "Initiate with 50-60% dose reduction. Twice-weekly INR monitoring."
            },
            "Poor Metabolizer_Low Sensitivity": {
                "risk_label": "Toxic",
                "severity": "high",
                "confidence_score": 0.93,
                "recommendation": (
                    "Major dose reduction required — initiate at 1.5–3 mg/day (50–70% reduction). "
                    "CYP2C9 poor metabolizer status severely impairs warfarin clearance, causing drug "
                    "accumulation and very high bleeding risk. Twice-weekly INR monitoring essential."
                ),
                "cpic_recommendation": "Initiate with 50-70% dose reduction. Twice-weekly INR monitoring."
            },
            "Poor Metabolizer_Intermediate Sensitivity": {
                "risk_label": "Toxic",
                "severity": "high",
                "confidence_score": 0.94,
                "recommendation": (
                    "Initiate at 1–2 mg/day (70–80% reduction from standard). CYP2C9 poor metabolizer "
                    "combined with VKORC1 intermediate sensitivity creates high risk of severe "
                    "over-anticoagulation. Daily INR monitoring for first week, then twice-weekly."
                ),
                "cpic_recommendation": "Initiate with 70-80% dose reduction. Daily INR monitoring initially."
            },
            "Poor Metabolizer_High Sensitivity": {
                "risk_label": "Toxic",
                "severity": "critical",
                "confidence_score": 0.97,
                "recommendation": (
                    "Extreme caution — initiate at 0.5–1.5 mg/day (80–90% reduction). "
                    "CYP2C9 poor metabolizer AND VKORC1 high sensitivity is the highest-risk combination. "
                    "Standard doses will cause life-threatening hemorrhage. Consider alternative "
                    "anticoagulant (e.g., direct oral anticoagulants) if appropriate for indication. "
                    "If warfarin must be used, daily INR monitoring for at least 2 weeks."
                ),
                "cpic_recommendation": "Consider alternative anticoagulant. If warfarin required, initiate at 0.5-1.5 mg/day with daily INR monitoring."
            },
            # Fallback single-gene phenotypes (when VKORC1 not detected)
            "Normal Metabolizer": {
                "risk_label": "Safe",
                "severity": "none",
                "confidence_score": 0.85,
                "recommendation": "Standard warfarin dosing (5-10 mg/day). VKORC1 data unavailable — consider genotyping for complete assessment. Monitor INR regularly.",
                "cpic_recommendation": "Standard dosing with INR monitoring. VKORC1 genotyping recommended for optimal dosing."
            },
            "Intermediate Metabolizer": {
                "risk_label": "Adjust Dosage",
                "severity": "moderate",
                "confidence_score": 0.84,
                "recommendation": "Reduce warfarin dose by 25-50%. VKORC1 data unavailable — use clinical judgment. Frequent INR monitoring required.",
                "cpic_recommendation": "25-50% dose reduction. VKORC1 genotyping recommended."
            },
            "Poor Metabolizer": {
                "risk_label": "Toxic",
                "severity": "high",
                "confidence_score": 0.92,
                "recommendation": "Major dose reduction (50-75%). Very high bleeding risk. VKORC1 genotyping recommended for precise dosing. Frequent INR monitoring essential.",
                "cpic_recommendation": "50-75% dose reduction. VKORC1 genotyping strongly recommended."
            }
        }
    },

    "CLOPIDOGREL": {
        "primary_gene": "CYP2C19",
        "cpic_guideline_url": "https://cpicpgx.org/guidelines/guideline-for-clopidogrel-and-cyp2c19/",
        "risks": {
            "Ultrarapid Metabolizer": {
                "risk_label": "Safe",
                "severity": "none",
                "confidence_score": 0.87,
                "recommendation": (
                    "Standard clopidogrel dosing is appropriate. Ultrarapid CYP2C19 metabolism may "
                    "result in enhanced platelet inhibition — monitor for increased bleeding risk at "
                    "standard doses. No dose adjustment required per current CPIC guidelines."
                ),
                "cpic_recommendation": "Use label-recommended dosing. Monitor for enhanced antiplatelet effect."
            },
            "Rapid Metabolizer": {
                "risk_label": "Safe",
                "severity": "none",
                "confidence_score": 0.89,
                "recommendation": (
                    "Standard clopidogrel dosing is appropriate. Rapid metabolizer status ensures "
                    "adequate conversion to active thiol metabolite. Use label-recommended dosing."
                ),
                "cpic_recommendation": "Use label-recommended dosing."
            },
            "Normal Metabolizer": {
                "risk_label": "Safe",
                "severity": "none",
                "confidence_score": 0.92,
                "recommendation": (
                    "Standard clopidogrel dosing is appropriate (75 mg/day maintenance, "
                    "300–600 mg loading dose). Normal CYP2C19 activity ensures adequate "
                    "conversion of clopidogrel to its active metabolite."
                ),
                "cpic_recommendation": "Use label-recommended dosing (75 mg/day)."
            },
            "Intermediate Metabolizer": {
                "risk_label": "Ineffective",
                "severity": "high",
                "confidence_score": 0.88,
                "recommendation": (
                    "Clopidogrel may have reduced efficacy. Reduced CYP2C19 activity leads to "
                    "subtherapeutic levels of the active metabolite, increasing risk of adverse "
                    "cardiovascular events (stent thrombosis, MI). "
                    "Consider alternative antiplatelet therapy: prasugrel (if no contraindications) "
                    "or ticagrelor are preferred alternatives per CPIC guidelines."
                ),
                "cpic_recommendation": "Consider alternative antiplatelet therapy (prasugrel or ticagrelor) if clinically appropriate."
            },
            "Poor Metabolizer": {
                "risk_label": "Ineffective",
                "severity": "critical",
                "confidence_score": 0.97,
                "recommendation": (
                    "Clopidogrel is ineffective — CONTRAINDICATED in this patient. CYP2C19 poor "
                    "metabolizer status means clopidogrel cannot be adequately converted to its active "
                    "metabolite. High risk of treatment failure, stent thrombosis, and major adverse "
                    "cardiovascular events. "
                    "Use prasugrel 10 mg/day or ticagrelor 90 mg twice daily instead "
                    "(if no contraindications)."
                ),
                "cpic_recommendation": "Avoid clopidogrel. Use prasugrel 10mg/day or ticagrelor 90mg twice daily."
            }
        }
    },

    "SIMVASTATIN": {
        "primary_gene": "SLCO1B1",
        "cpic_guideline_url": "https://cpicpgx.org/guidelines/cpic-guideline-for-statins/",
        "risks": {
            "Normal Function": {
                "risk_label": "Safe",
                "severity": "none",
                "confidence_score": 0.90,
                "recommendation": (
                    "Standard simvastatin dosing is appropriate. Normal SLCO1B1 function ensures "
                    "adequate hepatic uptake and clearance. Prescribe desired starting dose per "
                    "disease-specific guidelines (typically 20–40 mg/day). "
                    "Routine CK monitoring not required."
                ),
                "cpic_recommendation": "Prescribe desired starting dose per guidelines."
            },
            "Decreased Function": {
                "risk_label": "Adjust Dosage",
                "severity": "moderate",
                "confidence_score": 0.86,
                "recommendation": (
                    "Limit simvastatin dose to ≤20 mg/day OR consider switching to an alternative "
                    "statin with lower myopathy risk. Decreased SLCO1B1 function impairs hepatic "
                    "uptake of simvastatin acid, increasing systemic exposure and myopathy risk. "
                    "Preferred alternatives: pravastatin 40 mg, rosuvastatin 10–20 mg, or "
                    "fluvastatin XL 80 mg (lower SLCO1B1 sensitivity). "
                    "If simvastatin is continued, monitor CK levels and report muscle symptoms."
                ),
                "cpic_recommendation": "Limit to ≤20mg/day or switch to pravastatin/rosuvastatin. Monitor for myopathy."
            },
            "Poor Function": {
                "risk_label": "Toxic",
                "severity": "high",
                "confidence_score": 0.93,
                "recommendation": (
                    "Avoid simvastatin — high risk of myopathy and rhabdomyolysis. "
                    "Severely impaired SLCO1B1 function causes markedly elevated simvastatin "
                    "plasma concentrations. Risk of severe muscle damage including rhabdomyolysis "
                    "and acute kidney injury. "
                    "Use an alternative statin: pravastatin 40–80 mg/day or "
                    "rosuvastatin 10–40 mg/day are preferred (not significantly affected by SLCO1B1)."
                ),
                "cpic_recommendation": "Avoid simvastatin. Use pravastatin or rosuvastatin instead."
            }
        }
    },

    "AZATHIOPRINE": {
        "primary_gene": "TPMT",
        "secondary_gene": "NUDT15",
        "cpic_guideline_url": "https://cpicpgx.org/guidelines/guideline-for-thiopurines-and-tpmt/",
        "risks": {
            # TPMT-based risks
            "Normal Metabolizer": {
                "risk_label": "Safe",
                "severity": "none",
                "confidence_score": 0.91,
                "recommendation": (
                    "Standard azathioprine dosing is appropriate (typically 2–3 mg/kg/day for "
                    "immunosuppression). Normal TPMT activity ensures balanced thiopurine metabolism. "
                    "Monitor CBC (complete blood count) every 1–3 months as per standard of care. "
                    "Note: NUDT15 genotype should also be checked if available."
                ),
                "cpic_recommendation": "Start with normal therapeutic dose. Monitor CBC regularly."
            },
            "Intermediate Metabolizer": {
                "risk_label": "Adjust Dosage",
                "severity": "moderate",
                "confidence_score": 0.89,
                "recommendation": (
                    "Reduce azathioprine starting dose by 30–70% of standard dose. "
                    "Intermediate TPMT activity leads to accumulation of cytotoxic thioguanine "
                    "nucleotides (TGNs), increasing risk of myelosuppression. "
                    "Start at 1–1.5 mg/kg/day (vs standard 2–3 mg/kg/day). "
                    "Allow 2–4 weeks to reach steady state before adjusting. "
                    "Weekly CBC monitoring for first month, then monthly."
                ),
                "cpic_recommendation": "Start at 30-70% of standard dose. Allow 2-4 weeks to steady state. Weekly CBC monitoring initially."
            },
            "Poor Metabolizer": {
                "risk_label": "Toxic",
                "severity": "critical",
                "confidence_score": 0.97,
                "recommendation": (
                    "Azathioprine is CONTRAINDICATED at standard doses. "
                    "TPMT poor metabolizer status causes severe accumulation of toxic thioguanine "
                    "nucleotides (TGNs), leading to life-threatening myelosuppression "
                    "(severe leukopenia, thrombocytopenia, pancytopenia). "
                    "If thiopurine therapy is absolutely required: use 10% of standard dose with "
                    "very frequent CBC monitoring, OR switch to a non-thiopurine immunosuppressant "
                    "(mycophenolate, cyclosporine, tacrolimus)."
                ),
                "cpic_recommendation": "Avoid azathioprine at standard doses. Consider non-thiopurine immunosuppressant or reduce dose to 10% with intensive monitoring."
            }
        }
    },

    "FLUOROURACIL": {
        "primary_gene": "DPYD",
        "cpic_guideline_url": "https://cpicpgx.org/guidelines/guideline-for-fluoropyrimidines-and-dpyd/",
        "risks": {
            "Normal Metabolizer": {
                "risk_label": "Safe",
                "severity": "none",
                "confidence_score": 0.90,
                "recommendation": (
                    "Standard fluorouracil dosing is appropriate. Normal DPYD activity ensures "
                    "adequate catabolism of fluorouracil. Use label-recommended dosing per "
                    "oncology protocol. Standard monitoring for fluorouracil toxicity applies "
                    "(mucositis, myelosuppression, hand-foot syndrome)."
                ),
                "cpic_recommendation": "Use label-recommended dosing per oncology protocol."
            },
            "Intermediate Metabolizer": {
                "risk_label": "Adjust Dosage",
                "severity": "high",
                "confidence_score": 0.92,
                "recommendation": (
                    "Reduce starting dose by 50%. Intermediate DPYD activity (one non-functional "
                    "allele) significantly impairs fluorouracil catabolism, leading to drug "
                    "accumulation and severe, potentially life-threatening toxicity at standard doses. "
                    "Initiate at 50% of standard dose. After tolerability is confirmed over the "
                    "first cycle, dose may be increased in subsequent cycles guided by toxicity "
                    "and therapeutic drug monitoring if available. "
                    "Monitor closely for severe mucositis, diarrhea, and myelosuppression."
                ),
                "cpic_recommendation": "Start at 50% of standard dose. Increase cautiously in subsequent cycles if tolerated."
            },
            "Poor Metabolizer": {
                "risk_label": "Toxic",
                "severity": "critical",
                "confidence_score": 0.98,
                "recommendation": (
                    "Fluorouracil is CONTRAINDICATED. DPYD poor metabolizer status causes near-complete "
                    "absence of fluorouracil catabolism. Standard doses will cause immediate, "
                    "life-threatening multi-organ toxicity including severe mucositis, profound "
                    "myelosuppression, neurotoxicity, and cardiotoxicity with high mortality. "
                    "Select an alternative chemotherapy regimen not dependent on DPYD metabolism. "
                    "Consult oncology for appropriate alternatives based on tumor type and indication."
                ),
                "cpic_recommendation": "Avoid fluorouracil and capecitabine. Select alternative chemotherapy regimen."
            }
        }
    },

    "EFAVIRENZ": {
        "primary_gene": "CYP2B6",
        "cpic_guideline_url": "https://cpicpgx.org/guidelines/cpic-guideline-for-efavirenz-based-on-cyp2b6-genotype/",
        "risks": {
            "Normal Metabolizer": {
                "risk_label": "Safe",
                "severity": "none",
                "confidence_score": 0.90,
                "recommendation": (
                    "Standard efavirenz dosing is appropriate (600 mg/day). Normal CYP2B6 activity "
                    "ensures adequate efavirenz metabolism. Standard CNS side effect monitoring applies "
                    "(dizziness, vivid dreams, insomnia — typically resolve within 2-4 weeks). "
                    "Administer at bedtime to minimize CNS effects."
                ),
                "cpic_recommendation": "Initiate with standard 600 mg/day dose at bedtime."
            },
            "Intermediate Metabolizer": {
                "risk_label": "Adjust Dosage",
                "severity": "moderate",
                "confidence_score": 0.85,
                "recommendation": (
                    "Consider efavirenz dose reduction to 400 mg/day. Intermediate CYP2B6 activity "
                    "results in moderately elevated efavirenz plasma concentrations, increasing risk "
                    "of CNS toxicity (severe dizziness, depression, suicidal ideation, psychosis). "
                    "Monitor for neuropsychiatric adverse effects closely during first 4 weeks. "
                    "Therapeutic drug monitoring (TDM) recommended — target trough concentration 1-4 mg/L."
                ),
                "cpic_recommendation": "Consider dose reduction to 400 mg/day. Therapeutic drug monitoring recommended."
            },
            "Slow Metabolizer": {
                "risk_label": "Toxic",
                "severity": "high",
                "confidence_score": 0.93,
                "recommendation": (
                    "Significant dose reduction required — reduce efavirenz to 400 mg/day OR "
                    "switch to an alternative antiretroviral. CYP2B6 slow metabolizer status "
                    "(*6/*6 or equivalent) causes 3-fold higher efavirenz plasma exposure than "
                    "normal metabolizers. High risk of severe neuropsychiatric toxicity including "
                    "depression, suicidal ideation, psychosis, and severe CNS effects. "
                    "Preferred alternatives: dolutegravir or raltegravir-based regimens "
                    "which are not CYP2B6-dependent. If efavirenz must continue: "
                    "therapeutic drug monitoring essential, target trough less than 4 mg/L."
                ),
                "cpic_recommendation": "Reduce to 400 mg/day or switch to dolutegravir/raltegravir-based regimen. TDM essential."
            }
        }
    },

    "ATOMOXETINE": {
        "primary_gene": "CYP2D6",
        "cpic_guideline_url": "https://cpicpgx.org/guidelines/cpic-guideline-for-atomoxetine-based-on-cyp2d6-genotype/",
        "risks": {
            "Ultrarapid Metabolizer": {
                "risk_label": "Ineffective",
                "severity": "moderate",
                "confidence_score": 0.88,
                "recommendation": (
                    "Atomoxetine may be ineffective at standard doses. Ultrarapid CYP2D6 metabolism "
                    "causes rapid atomoxetine clearance, resulting in subtherapeutic plasma levels "
                    "and reduced ADHD symptom control. "
                    "Consider using higher-than-standard doses with careful monitoring, or switch to "
                    "a non-CYP2D6-metabolized ADHD medication (e.g., methylphenidate, guanfacine)."
                ),
                "cpic_recommendation": "Consider alternative ADHD medication not metabolized by CYP2D6."
            },
            "Normal Metabolizer": {
                "risk_label": "Safe",
                "severity": "none",
                "confidence_score": 0.91,
                "recommendation": (
                    "Standard atomoxetine dosing is appropriate. Initiate at 0.5 mg/kg/day, "
                    "titrate to 1.2 mg/kg/day after minimum 3 days (max 1.4 mg/kg/day or 100 mg/day). "
                    "Normal CYP2D6 activity ensures appropriate atomoxetine plasma levels. "
                    "Monitor for standard side effects (appetite suppression, insomnia, "
                    "increased heart rate and blood pressure)."
                ),
                "cpic_recommendation": "Use label-recommended dosing. Titrate based on response and tolerability."
            },
            "Intermediate Metabolizer": {
                "risk_label": "Adjust Dosage",
                "severity": "moderate",
                "confidence_score": 0.84,
                "recommendation": (
                    "Initiate at standard dose but monitor carefully for elevated drug exposure. "
                    "Intermediate CYP2D6 activity results in moderately increased atomoxetine "
                    "plasma concentrations. Monitor closely for cardiovascular effects "
                    "(tachycardia, hypertension) and psychiatric effects. "
                    "Dose reduction may be required if adverse effects emerge."
                ),
                "cpic_recommendation": "Standard dosing with enhanced monitoring for adverse effects."
            },
            "Poor Metabolizer": {
                "risk_label": "Toxic",
                "severity": "high",
                "confidence_score": 0.94,
                "recommendation": (
                    "Reduce atomoxetine starting dose by 50% — initiate at 0.5 mg/kg/day and "
                    "do NOT exceed 1.2 mg/kg/day. "
                    "CYP2D6 poor metabolizer status causes 10-fold higher atomoxetine AUC compared "
                    "to normal metabolizers, dramatically increasing toxicity risk. "
                    "High risk of severe cardiovascular effects (marked tachycardia, hypertension, "
                    "QTc prolongation), psychiatric effects (anxiety, irritability), "
                    "and urinary retention. "
                    "Baseline and periodic ECG monitoring recommended. "
                    "Consider alternative ADHD therapy (methylphenidate, guanfacine) if toxicity occurs."
                ),
                "cpic_recommendation": "Reduce starting dose by 50%. Max dose 1.2 mg/kg/day. ECG monitoring recommended."
            }
        }
    }
}


def get_phenotype(gene: str, diplotype: str) -> str:
    """Look up phenotype from gene + diplotype, trying both orientations."""
    gene_table = DIPLOTYPE_TO_PHENOTYPE.get(gene, {})
    if diplotype in gene_table:
        return gene_table[diplotype]
    # Try reversed diplotype
    parts = diplotype.split("/")
    if len(parts) == 2:
        reversed_dip = f"{parts[1]}/{parts[0]}"
        if reversed_dip in gene_table:
            return gene_table[reversed_dip]
    return gene_table.get("default", "Unknown")


def assess_risk(drug: str, diplotypes: Dict[str, str]) -> Dict:
    """
    Full CPIC-aligned risk assessment for a drug given patient diplotypes.
    Handles two-gene combinations (e.g., Warfarin: CYP2C9 + VKORC1).
    """
    drug_upper = drug.upper().strip()

    if drug_upper not in DRUG_RISK_TABLE:
        return {
            "risk_label": "Unknown",
            "severity": "none",
            "confidence_score": 0.0,
            "recommendation": f"'{drug}' is not in our pharmacogenomic database. Supported drugs: {', '.join(DRUG_RISK_TABLE.keys())}.",
            "cpic_recommendation": "Consult clinical pharmacist.",
            "primary_gene": "Unknown",
            "secondary_gene": None,
            "phenotype": "Unknown",
            "secondary_phenotype": None,
            "diplotype": "Unknown",
            "combined_key": None
        }

    drug_info = DRUG_RISK_TABLE[drug_upper]
    primary_gene = drug_info["primary_gene"]
    secondary_gene = drug_info.get("secondary_gene")

    diplotype = diplotypes.get(primary_gene, "*1/*1")
    phenotype = get_phenotype(primary_gene, diplotype)

    secondary_phenotype = None
    combined_key = None

    # Handle two-gene drugs (Warfarin, Azathioprine)
    if secondary_gene:
        secondary_diplotype = diplotypes.get(secondary_gene, "")
        if secondary_diplotype:
            secondary_phenotype = get_phenotype(secondary_gene, secondary_diplotype)
            combined_key = f"{phenotype}_{secondary_phenotype}"

    # Look up risk
    risks = drug_info["risks"]

    # Try combined key first (for two-gene drugs)
    if combined_key and combined_key in risks:
        risk_data = risks[combined_key]
    elif phenotype in risks:
        risk_data = risks[phenotype]
    else:
        risk_data = {
            "risk_label": "Unknown",
            "severity": "none",
            "confidence_score": 0.5,
            "recommendation": f"Phenotype '{phenotype}' not found in risk table for {drug}. Consult clinical pharmacist.",
            "cpic_recommendation": "Consult clinical pharmacist."
        }

    return {
        "risk_label": risk_data["risk_label"],
        "severity": risk_data["severity"],
        "confidence_score": risk_data["confidence_score"],
        "recommendation": risk_data["recommendation"],
        "cpic_recommendation": risk_data["cpic_recommendation"],
        "cpic_guideline_url": drug_info.get("cpic_guideline_url", "https://cpicpgx.org"),
        "primary_gene": primary_gene,
        "secondary_gene": secondary_gene,
        "phenotype": phenotype,
        "secondary_phenotype": secondary_phenotype,
        "diplotype": diplotype,
        "combined_key": combined_key
    }


def get_supported_drugs():
    return list(DRUG_RISK_TABLE.keys())
