"""
VCF Parser for TechRx
Parses VCF v4.2 files and extracts pharmacogenomic variants
Only includes variants where patient actually carries the alt allele (GT != 0/0)
"""

import re
from typing import Dict, List, Optional


# Target genes for pharmacogenomics analysis
TARGET_GENES = {"CYP2D6", "CYP2C19", "CYP2C9", "SLCO1B1", "TPMT", "DPYD", "CYP2B6"}


def is_variant_present(sample_field: str) -> bool:
    """
    Returns True only if patient actually carries the variant.
    0/0 and 0|0 = homozygous reference = patient does NOT carry this variant.
    0/1, 1/0, 1/1 etc = patient carries the variant.
    """
    if not sample_field:
        return False
    gt = sample_field.split(":")[0]  # GT is always first field
    gt = gt.replace("|", "/")        # handle phased genotypes
    return gt not in ("0/0", "./.", ".")


def parse_vcf(file_content: str) -> Dict:
    """
    Parse a VCF file and extract pharmacogenomic variants.
    Only includes variants where GT != 0/0 (patient actually carries the allele).
    Returns a dict with gene -> list of variants
    """
    variants = []
    metadata = {}
    gene_variants = {gene: [] for gene in TARGET_GENES}

    lines = file_content.strip().split("\n")

    for line in lines:
        line = line.strip()

        if not line:
            continue

        if line.startswith("##"):
            if "=" in line:
                key_val = line[2:].split("=", 1)
                if len(key_val) == 2:
                    metadata[key_val[0]] = key_val[1]
            continue

        if line.startswith("#CHROM"):
            continue

        parts = line.split("\t")
        if len(parts) < 8:
            continue

        chrom, pos, vid, ref, alt, qual, filt, info = parts[:8]

        # ── KEY FIX: Check genotype before including variant ──
        # If sample column exists, only include if patient carries the alt allele
        if len(parts) >= 10:
            sample_field = parts[9]  # sample data column
            if not is_variant_present(sample_field):
                continue  # 0/0 — patient doesn't carry this variant, skip it
        # If no sample column (simple VCF), include all variants

        # Parse INFO field
        info_dict = parse_info_field(info)

        gene = info_dict.get("GENE", "")
        star_allele = info_dict.get("STAR", "")
        rsid = info_dict.get("RS", vid if vid != "." else "")

        if gene in TARGET_GENES:
            variant = {
                "rsid": rsid if rsid.startswith("rs") else f"rs{rsid}" if rsid.isdigit() else rsid,
                "chromosome": chrom,
                "position": pos,
                "ref_allele": ref,
                "alt_allele": alt,
                "gene": gene,
                "star_allele": star_allele,
                "filter_status": filt,
                "raw_info": info_dict
            }
            variants.append(variant)
            gene_variants[gene].append(variant)

    # Determine diplotypes per gene
    diplotypes = {}
    for gene, gene_vars in gene_variants.items():
        if gene_vars:
            diplotypes[gene] = infer_diplotype(gene, gene_vars)

    return {
        "variants": variants,
        "gene_variants": gene_variants,
        "diplotypes": diplotypes,
        "metadata": metadata,
        "vcf_parsing_success": len(variants) > 0,
        "total_variants_found": len(variants),
        "genes_detected": [g for g in TARGET_GENES if gene_variants[g]]
    }


def parse_info_field(info: str) -> Dict:
    """Parse the INFO field of a VCF line into a dictionary."""
    info_dict = {}
    for item in info.split(";"):
        if "=" in item:
            k, v = item.split("=", 1)
            info_dict[k.strip()] = v.strip()
        else:
            info_dict[item.strip()] = True
    return info_dict


def infer_diplotype(gene: str, variants: List[Dict]) -> str:
    """
    Infer diplotype from list of variants for a gene.
    Only called with variants that passed the GT filter (patient actually carries them).
    """
    star_alleles = [v.get("star_allele", "") for v in variants if v.get("star_allele")]

    if not star_alleles:
        return "*1/*1"

    unique_alleles = list(set(star_alleles))

    if len(unique_alleles) == 1:
        # Homozygous for this allele
        return f"{unique_alleles[0]}/{unique_alleles[0]}"
    elif len(unique_alleles) >= 2:
        return f"{unique_alleles[0]}/{unique_alleles[1]}"
    else:
        return "*1/*1"


def get_sample_vcf() -> str:
    """Returns a sample VCF for testing — uses a high-risk patient profile."""
    return """##fileformat=VCFv4.2
##FILTER=<ID=PASS,Description="All filters passed">
##INFO=<ID=GENE,Number=1,Type=String,Description="Gene symbol">
##INFO=<ID=STAR,Number=1,Type=String,Description="Star allele">
##INFO=<ID=RS,Number=1,Type=String,Description="dbSNP rsID">
##FORMAT=<ID=GT,Number=1,Type=String,Description="Genotype">
#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO	FORMAT	SAMPLE
chr22	42522613	rs3892097	C	T	.	PASS	GENE=CYP2D6;STAR=*4;RS=rs3892097	GT	1/1
chr10	96541616	rs4244285	G	A	.	PASS	GENE=CYP2C19;STAR=*2;RS=rs4244285	GT	1/1
chr10	96702047	rs1799853	C	T	.	PASS	GENE=CYP2C9;STAR=*3;RS=rs1799853	GT	1/1
chr12	21331549	rs4149056	T	C	.	PASS	GENE=SLCO1B1;STAR=*5;RS=rs4149056	GT	1/1
chr6	18128556	rs1800462	G	A	.	PASS	GENE=TPMT;STAR=*3A;RS=rs1800462	GT	0/1
chr6	18138997	rs1800462	C	G	.	PASS	GENE=TPMT;STAR=*2;RS=rs1800462	GT	0/1
chr1	97981395	rs3918290	C	T	.	PASS	GENE=DPYD;STAR=*2A;RS=rs3918290	GT	1/1
"""
