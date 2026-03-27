"""
Helix-Zero V7 :: Essentiality Scoring Module
Cross-references target genes against DEG, OGEE, and RNAi phenotype databases
to determine if the siRNA target is biologically critical (essential for survival).
"""

import json
import os

# ── Database File Paths ──────────────────────────────────────────────────
DATA_DIR = os.path.join(os.path.dirname(__file__), "static", "data")

DEG_DB = {}       # { "actin": {"essentiality": "essential", "organism": "...", "evidence": "..."}, ... }
OGEE_DB = {}      # { "actin": {"score": 0.95, "context": "..."}, ... }
RNAI_DB = {}      # { "actin": "lethal", ... }

_loaded = False


def _load_databases():
    """Load all essentiality databases from JSON files (lazy, once)."""
    global DEG_DB, OGEE_DB, RNAI_DB, _loaded
    if _loaded:
        return

    # DEG Database (Database of Essential Genes)
    deg_path = os.path.join(DATA_DIR, "essential_genes.json")
    if os.path.exists(deg_path):
        with open(deg_path, "r") as f:
            genes = json.load(f)
            for g in genes:
                DEG_DB[g["geneId"].lower()] = g
        print(f"[Essentiality] DEG database loaded: {len(DEG_DB)} genes")

    # OGEE Database (Online Gene Essentiality)
    ogee_path = os.path.join(DATA_DIR, "ogee_essentiality.json")
    if os.path.exists(ogee_path):
        with open(ogee_path, "r") as f:
            raw = json.load(f)
            for gene_id, data in raw.items():
                OGEE_DB[gene_id.lower()] = data
        print(f"[Essentiality] OGEE database loaded: {len(OGEE_DB)} genes")

    # RNAi Phenotype Database
    rnai_path = os.path.join(DATA_DIR, "rnai_phenotypes.json")
    if os.path.exists(rnai_path):
        with open(rnai_path, "r") as f:
            raw = json.load(f)
            for gene_id, phenotype in raw.items():
                RNAI_DB[gene_id.lower()] = phenotype
        print(f"[Essentiality] RNAi database loaded: {len(RNAI_DB)} genes")
    else:
        # Create a default RNAi phenotype mapping from DEG data
        for gid in DEG_DB:
            RNAI_DB[gid] = "lethal"
        print(f"[Essentiality] RNAi database auto-generated from DEG: {len(RNAI_DB)} genes")

    _loaded = True


def calculate_essentiality(gene_name: str) -> dict:
    """
    Calculate the Essentiality Score for a target gene.

    Scoring Formula:
    ─────────────────────────────────────────
    DEG Match:           +40 points (gene exists in Database of Essential Genes)
    OGEE Score:          +0-30 points (ogee_score × 30)
    RNAi Phenotype:      +25 (lethal), +15 (sterile), +5 (viable), +0 (unknown)
    Conservation Bonus:  +5 baseline + up to +10 (if gene exists in multiple DBs)
    ─────────────────────────────────────────
    Maximum:             100 points (capped)

    Returns dict with score, breakdown, evidence, and classification.
    """
    _load_databases()

    # Handle comma/space-separated gene names — score each, pick the best
    raw_input = gene_name.strip()
    gene_names = [g.strip().lower() for g in raw_input.replace(',', ' ').split() if g.strip()]
    
    if len(gene_names) > 1:
        # Score each gene individually, return the highest-scoring one
        best_result = None
        for gn in gene_names:
            result = _score_single_gene(gn)
            if best_result is None or result["essentialityScore"] > best_result["essentialityScore"]:
                best_result = result
        best_result["geneName"] = raw_input
        best_result["evidence"].insert(0, f"Multi-gene input detected ({', '.join(gene_names)}) — showing best match: {best_result['_bestGene']}")
        return best_result
    
    gene = gene_names[0] if gene_names else raw_input.lower()
    return _score_single_gene(gene)


def _score_single_gene(gene: str) -> dict:
    """Score a single gene name against all databases."""
    score = 0.0
    evidence = []
    breakdown = {}

    # ── Layer 1: DEG Match (40 points) ──
    if gene in DEG_DB:
        score += 40.0
        breakdown["deg"] = 40.0
        entry = DEG_DB[gene]
        evidence.append(f"DEG match: {entry.get('essentiality', 'essential')} in {entry.get('organism', 'unknown')} ({entry.get('evidence', 'N/A')})")
    else:
        breakdown["deg"] = 0.0

    # ── Layer 2: OGEE Score (up to 30 points) ──
    if gene in OGEE_DB:
        ogee_score = OGEE_DB[gene].get("score", 0.0)
        ogee_points = round(ogee_score * 30, 1)
        score += ogee_points
        breakdown["ogee"] = ogee_points
        evidence.append(f"OGEE conservation score: {ogee_score} ({OGEE_DB[gene].get('context', 'N/A')})")
    else:
        breakdown["ogee"] = 0.0

    # ── Layer 3: RNAi Phenotype (up to 25 points) ──
    phenotype = RNAI_DB.get(gene, "unknown")
    phenotype_map = {
        "lethal": 25.0,
        "sterile": 15.0,
        "viable": 5.0,
        "unknown": 0.0
    }
    phenotype_points = phenotype_map.get(phenotype, 0.0)
    score += phenotype_points
    breakdown["rnai"] = phenotype_points
    if phenotype != "unknown":
        evidence.append(f"RNAi phenotype: {phenotype} (+{phenotype_points} pts)")

    # ── Layer 4: Conservation Baseline (5-15 points) ──
    # Genes found in multiple databases are highly conserved
    db_hits = sum([1 for db in [DEG_DB, OGEE_DB, RNAI_DB] if gene in db])
    conservation_bonus = 5.0 + min(db_hits * 3.0, 10.0)
    score += conservation_bonus
    breakdown["conservation"] = conservation_bonus
    if db_hits > 0:
        evidence.append(f"Found in {db_hits}/3 databases (conservation bonus: +{conservation_bonus})")
    else:
        evidence.append("Gene not found in any database — using baseline estimate")

    # ── Clamp and Classify ──
    score = min(100.0, max(0.0, score))

    if score >= 90:
        classification = "Ultra-Essential"
        priority = "CRITICAL TARGET"
    elif score >= 75:
        classification = "Highly Essential"
        priority = "HIGH PRIORITY"
    elif score >= 50:
        classification = "Moderately Essential"
        priority = "MODERATE"
    elif score >= 25:
        classification = "Low Essentiality"
        priority = "LOW"
    else:
        classification = "Non-Essential"
        priority = "NOT RECOMMENDED"

    return {
        "geneName": gene,
        "_bestGene": gene,
        "essentialityScore": round(score, 1),
        "classification": classification,
        "priority": priority,
        "breakdown": breakdown,
        "evidence": evidence,
        "databasesLoaded": {
            "deg": len(DEG_DB),
            "ogee": len(OGEE_DB),
            "rnai": len(RNAI_DB)
        }
    }


def get_available_genes() -> list:
    """Return a list of all gene IDs available across all databases."""
    _load_databases()
    all_genes = set(DEG_DB.keys()) | set(OGEE_DB.keys()) | set(RNAI_DB.keys())
    return sorted(list(all_genes))
