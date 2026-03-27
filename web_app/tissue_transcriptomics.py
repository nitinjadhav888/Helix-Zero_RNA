"""
Helix-Zero V8 :: Tissue-Specific Off-Target Filter
Transcriptomics-Aware Safety Analysis

Theory:
  The standard Bloom Filter homology check flags a sequence as "risky" if it
  matches any gene in the non-target genome — regardless of WHERE or WHETHER
  that gene is even expressed. This is overly conservative and can cause us
  to discard excellent candidates.

  Real pharmaceutical developers check transcriptomic expression data:
  if an off-target gene is only expressed in the heart tissue, but our
  siRNA is delivered to the liver, the off-target risk is effectively 0.

  This module implements that logic using the tissue_expression.json atlas.
"""

import json
import os

_DATA_DIR = os.path.join(os.path.dirname(__file__), "static", "data")
_TISSUE_DB_PATH = os.path.join(_DATA_DIR, "tissue_expression.json")

_tissue_db = None

def _load_db() -> dict:
    global _tissue_db
    if _tissue_db is None:
        with open(_TISSUE_DB_PATH, "r") as f:
            _tissue_db = json.load(f)
    return _tissue_db


def get_organisms() -> list:
    """Return list of available organisms in the database."""
    db = _load_db()
    return [{"id": k, "name": v["description"]} for k, v in db.items()]


def get_tissues(organism: str) -> list:
    """Return list of tissues for an organism."""
    db = _load_db()
    org_data = db.get(organism, {})
    tissues_dict = org_data.get("tissues", {})
    return [{"id": k, "notes": v["notes"]} for k, v in tissues_dict.items()]


def check_tissue_off_target(
    gene_name: str,
    off_target_gene: str,
    organism: str,
    delivery_tissue: str
) -> dict:
    """
    Check whether an off-target gene match is actually biologically relevant,
    given the organism and the tissue where the siRNA will be delivered.

    Args:
        gene_name       : The target gene being silenced.
        off_target_gene : The off-target gene that matched the siRNA.
        organism        : "homo_sapiens", "apis_mellifera", etc.
        delivery_tissue : The tissue where the siRNA drug will be administered.

    Returns:
        dict with:
          - isExpressedInDeliveryTissue : True if the off-target gene is
                                          expressed where we deliver the drug.
          - effectiveThreatLevel: "None", "Low", "Moderate", "High"
          - otherTissuesExpressed: List of other tissues where the gene IS expressed.
          - interpretation: Human-readable explanation.
    """
    db = _load_db()
    org_data = db.get(organism, {})
    tissues = org_data.get("tissues", {})

    delivery_tissue_data = tissues.get(delivery_tissue, {})
    delivery_expressed = delivery_tissue_data.get("expressed_genes", [])

    # Normalize gene name for comparison (case-insensitive)
    off_target_upper = off_target_gene.upper()
    expressed_upper = [g.upper() for g in delivery_expressed]

    in_delivery_tissue = off_target_upper in expressed_upper

    # Find OTHER tissues where it is expressed
    other_tissues = []
    for tissue_id, tissue_data in tissues.items():
        if tissue_id == delivery_tissue:
            continue
        t_genes = [g.upper() for g in tissue_data.get("expressed_genes", [])]
        if off_target_upper in t_genes:
            other_tissues.append(tissue_id)

    # Threat level calculation
    if in_delivery_tissue:
        threat = "High"
        interp = (
            f"⚠️ OFF-TARGET RISK: '{off_target_gene}' IS expressed in the delivery tissue "
            f"({delivery_tissue}). This off-target match poses a real biological risk."
        )
    elif other_tissues:
        threat = "Low"
        interp = (
            f"✅ SAFE: '{off_target_gene}' is NOT expressed in {delivery_tissue}. "
            f"It IS expressed in: {', '.join(other_tissues)} — but these tissues "
            f"won't receive the siRNA. Risk is effectively zero."
        )
    else:
        threat = "None"
        interp = (
            f"✅ NO RISK: '{off_target_gene}' is not expressed in any tracked tissue "
            f"for {organism}. This off-target match can be safely ignored."
        )

    return {
        "targetGene":                gene_name,
        "offTargetGene":             off_target_gene,
        "organism":                  organism,
        "deliveryTissue":            delivery_tissue,
        "isExpressedInDeliveryTissue": in_delivery_tissue,
        "otherTissuesExpressed":     other_tissues,
        "effectiveThreatLevel":      threat,
        "interpretation":            interp,
    }


def batch_filter_off_targets(
    candidate_sequence: str,
    off_target_genes: list,
    organism: str,
    delivery_tissue: str
) -> dict:
    """
    Batch-filter a list of off-target gene matches for a given siRNA candidate.

    Returns a filtered analysis showing which off-target matches are genuine
    threats vs which are "ghost" matches that can be ignored.
    """
    results = []
    genuine_threats = 0
    cleared = 0

    for gene in off_target_genes:
        r = check_tissue_off_target(
            gene_name=candidate_sequence,
            off_target_gene=gene,
            organism=organism,
            delivery_tissue=delivery_tissue
        )
        results.append(r)
        if r["effectiveThreatLevel"] == "High":
            genuine_threats += 1
        else:
            cleared += 1

    return {
        "candidateSequence":    candidate_sequence,
        "totalOffTargets":      len(off_target_genes),
        "genuineThreats":       genuine_threats,
        "clearedAsSafe":        cleared,
        "adjustedSafetyRating": "CLEAR" if genuine_threats == 0 else (
            "CAUTION" if genuine_threats <= 2 else "REJECT"
        ),
        "details":              results,
    }
