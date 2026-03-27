from flask import Flask, render_template, jsonify, request
import requests
import os
from engine import run_first_model_pipeline
from chem_simulator import apply_modifications
from svg_generator import generate_modification_svg
from rnafold_svg import RNAfoldSVG
from essentiality import calculate_essentiality, get_available_genes
from bloom_filter import get_or_build_index, reset_index
from models import db, TargetSequenceLog

app = Flask(__name__)
# Vercel serverless filesystem is read-only except /tmp.
if os.getenv("VERCEL"):
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////tmp/helix_zero.db"
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///helix_zero.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

with app.app_context():
    db.create_all()

DL_BACKEND_URL = os.getenv("DL_BACKEND_URL", "http://127.0.0.1:8000")
CMS_MODULE_URL = os.getenv("CMS_MODULE_URL", "http://127.0.0.1:5001")


@app.route("/")
def index():
    """Render the main Helix-Zero Dashboard built on Bootstrap 5."""
    return render_template("index.html")


# ── First Model (V6) ─────────────────────────────────────────────────────
@app.route("/api/first_model", methods=["POST"])
def run_v6_model():
    """Run the 9-Layer bio-safety First Model pipeline."""
    try:
        data = request.json
        sequence = data.get("sequence", "")
        si_length = int(data.get("siLength", 21))
        non_target = data.get("nonTargetSequence", "")
        gene_name = data.get("geneName", "")

        candidates = run_first_model_pipeline(
            sequence,
            non_target_sequence=non_target,
            length=si_length,
            gene_name=gene_name,
        )
        return jsonify({"candidates": candidates}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── Deep Learning Proxy (V7) ─────────────────────────────────────────────
@app.route("/api/predict", methods=["POST"])
def proxy_predict():
    """Proxy requests to the FastAPI Deep Learning Backend."""
    try:
        data = request.json
        response = requests.post(f"{DL_BACKEND_URL}/predict/efficacy/batch", json=data)
        return jsonify(response.json()), response.status_code
    except requests.exceptions.ConnectionError:
        return jsonify(
            {"error": "Deep Learning Backend is offline or unreachable."}
        ), 503
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/cms/predict", methods=["POST"])
def proxy_cms_predict():
    """Proxy prediction requests to standalone Helix_Zero1 CMS module."""
    try:
        data = request.json or {}
        response = requests.post(f"{CMS_MODULE_URL}/predict", json=data, timeout=20)
        return jsonify(response.json()), response.status_code
    except requests.exceptions.ConnectionError:
        return jsonify({"error": "CMS module is offline or unreachable."}), 503
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/cms/optimize", methods=["POST"])
def proxy_cms_optimize():
    """Proxy optimization requests to standalone Helix_Zero1 CMS module."""
    try:
        data = request.json or {}
        response = requests.post(f"{CMS_MODULE_URL}/optimize", json=data, timeout=30)
        return jsonify(response.json()), response.status_code
    except requests.exceptions.ConnectionError:
        return jsonify({"error": "CMS module is offline or unreachable."}), 503
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── Chemical Modification Simulator ──────────────────────────────────────
@app.route("/api/chem_modify", methods=["POST"])
def run_chem_modification():
    """Apply chemical modifications (2'-OMe, 2'-F, PS) to a candidate sequence."""
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400

        sequence = data.get("sequence", "")
        mod_type = data.get("modType", "2_ome")
        mod_positions = data.get("positions", None)

        if not sequence:
            return jsonify({"error": "No sequence provided"}), 400

        if mod_type == "none":
            return jsonify({"error": "No modification selected"}), 400

        result = apply_modifications(
            sequence, mod_type=mod_type, mod_positions=mod_positions
        )
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def _candidate_rank_score(candidate: dict, objective: str = "balanced") -> float:
    """Rank candidates based on objective while favoring safety first."""
    safety = float(candidate.get("safetyScore", 0.0))
    efficacy = float(candidate.get("efficiency", 0.0))
    essentiality = float(candidate.get("essentialityScore", 0.0))

    if objective == "safety":
        return safety * 0.8 + efficacy * 0.15 + essentiality * 0.05
    if objective == "efficacy":
        return efficacy * 0.55 + safety * 0.35 + essentiality * 0.10
    if objective == "essentiality":
        return essentiality * 0.55 + safety * 0.30 + efficacy * 0.15
    return safety * 0.5 + efficacy * 0.35 + essentiality * 0.15


@app.route("/api/pipeline/e2e", methods=["POST"])
def run_end_to_end_pipeline():
    """Run a complete RNA pipeline: candidate generation -> ranking -> modification."""
    try:
        data = request.json or {}
        target_sequence = data.get("targetSequence", "")
        non_target_sequence = data.get("nonTargetSequence", "")
        gene_name = data.get("geneName", "")
        objective = data.get("objective", "balanced").lower()
        si_length = int(data.get("siLength", 21))
        mod_type = data.get("modType", "2_ome")

        if not target_sequence:
            return jsonify({"error": "targetSequence is required"}), 400

        candidates = run_first_model_pipeline(
            target_sequence,
            non_target_sequence=non_target_sequence,
            length=si_length,
            gene_name=gene_name,
        )

        if not candidates:
            return jsonify(
                {
                    "status": "no_candidates",
                    "message": "No valid siRNA candidates were generated for this input.",
                }
            ), 200

        ranked_candidates = sorted(
            candidates,
            key=lambda c: _candidate_rank_score(c, objective=objective),
            reverse=True,
        )

        best_candidate = ranked_candidates[0]
        best_sequence = best_candidate.get("sequence", "")

        modification = apply_modifications(best_sequence, mod_type=mod_type)

        essentiality_result = None
        if gene_name and gene_name.strip():
            essentiality_result = calculate_essentiality(gene_name)

        dl_prediction = None
        try:
            dl_payload = {"sequences": [best_sequence]}
            dl_response = requests.post(
                f"{DL_BACKEND_URL}/predict/efficacy/batch", json=dl_payload, timeout=10
            )
            if dl_response.ok:
                dl_prediction = dl_response.json()
            else:
                dl_prediction = {
                    "status": "unavailable",
                    "reason": f"backend returned HTTP {dl_response.status_code}",
                }
        except Exception:
            dl_prediction = {
                "status": "unavailable",
                "reason": "deep-learning backend not reachable",
            }

        return jsonify(
            {
                "status": "success",
                "objective": objective,
                "pipelineSummary": {
                    "inputLength": len(target_sequence),
                    "candidateCount": len(candidates),
                    "selectedCandidatePosition": best_candidate.get("position"),
                    "selectedCandidateSafety": best_candidate.get("safetyScore"),
                    "selectedCandidateEfficacy": best_candidate.get("efficiency"),
                    "modificationType": modification.get("modificationType"),
                    "therapeuticIndex": modification.get("therapeuticIndex"),
                },
                "steps": [
                    "Generated candidate siRNA windows from target input.",
                    "Applied multi-layer biosafety and homology checks.",
                    "Ranked candidates by objective-aware scoring.",
                    "Applied chemical modification strategy to best candidate.",
                    "Attached essentiality and deep-learning enrichment.",
                ],
                "selectedCandidate": best_candidate,
                "topCandidates": ranked_candidates[:5],
                "modification": modification,
                "essentiality": essentiality_result,
                "deepLearning": dl_prediction,
            }
        ), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── Multi-Target Cocktail Designer ───────────────────────────────────────
@app.route("/api/cocktail", methods=["POST"])
def design_cocktail():
    """Design a multi-target siRNA cocktail from top non-overlapping candidates."""
    try:
        data = request.json
        sequence = data.get("sequence", "")
        si_length = int(data.get("siLength", 21))
        non_target = data.get("nonTargetSequence", "")
        num_targets = int(data.get("numTargets", 3))

        all_candidates = run_first_model_pipeline(
            sequence, non_target_sequence=non_target, length=si_length
        )

        # Select top non-overlapping candidates for cocktail
        cocktail = []
        used_ranges = []

        for cand in all_candidates:
            if cand["safetyScore"] < 70:
                continue
            pos = cand["position"]
            overlaps = False
            for start, end in used_ranges:
                if not (pos + si_length <= start or pos >= end):
                    overlaps = True
                    break
            if not overlaps:
                cocktail.append(cand)
                used_ranges.append((pos, pos + si_length))
            if len(cocktail) >= num_targets:
                break

        # Calculate cocktail synergy score
        if cocktail:
            avg_safety = sum(c["safetyScore"] for c in cocktail) / len(cocktail)
            avg_efficacy = sum(c["efficiency"] for c in cocktail) / len(cocktail)
            coverage = len(cocktail) / num_targets * 100
            synergy = round((avg_safety * 0.4 + avg_efficacy * 0.4 + coverage * 0.2), 1)
        else:
            avg_safety = avg_efficacy = coverage = synergy = 0

        return jsonify(
            {
                "cocktail": cocktail,
                "numSelected": len(cocktail),
                "avgSafety": round(avg_safety, 1),
                "avgEfficacy": round(avg_efficacy, 1),
                "coveragePercent": round(coverage, 1),
                "synergyScore": synergy,
            }
        ), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── PDB Structure Generator (NEW!) ──────────────────────────────────────────
from pdb_generator import (
    RNAPDBGenerator,
    generate_comparison,
    generate_accessibility_visualization,
)
import os


@app.route("/api/pdb/generate", methods=["POST"])
def generate_pdb():
    """
    Generate PDB files for siRNA visualization.

    Generates:
    - Native (unmodified) structure
    - Modified structure with chemical modifications
    - Comparison structure (both models in one file)

    Request:
    {
        "sequence": "AUGGACUACAAGGACGACGA",
        "modifications": {0: "2_ome", 4: "2_f", 17: "ps"}
    }

    Returns:
    - native_pdb: Path to native PDB file
    - modified_pdb: Path to modified PDB file
    - comparison_pdb: Path to comparison PDB file
    - pdb_content: PDB file content for direct download
    """
    try:
        data = request.json
        sequence = data.get("sequence", "")
        modifications = data.get("modifications", {})

        if not sequence:
            return jsonify({"error": "No sequence provided"}), 400
        if len(sequence) < 6:
            return jsonify({"error": "Sequence too short (minimum 6nt)"}), 400

        output_dir = os.path.join(app.root_path, "static", "pdb_files")
        os.makedirs(output_dir, exist_ok=True)

        results = generate_comparison(sequence, modifications, output_dir)

        return jsonify(
            {
                "status": "success",
                "native_pdb": results["native_pdb"],
                "modified_pdb": results["modified_pdb"],
                "comparison_pdb": results["comparison_pdb"],
                "pdb_content": results["comparison_content"],
                "sequence": sequence,
                "modifications": modifications,
                "message": "PDB files generated successfully",
            }
        ), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/pdb/native", methods=["POST"])
def generate_native_pdb():
    """Generate only the native (unmodified) RNA structure PDB."""
    try:
        data = request.json
        sequence = data.get("sequence", "")

        if not sequence:
            return jsonify({"error": "No sequence provided"}), 400

        generator = RNAPDBGenerator()
        output_dir = os.path.join(app.root_path, "static", "pdb_files")
        os.makedirs(output_dir, exist_ok=True)

        filename = f"native_{sequence[:10]}_{len(sequence)}nt.pdb"
        filepath = os.path.join(output_dir, filename)

        pdb_content = generator.generate_native_pdb(sequence, filepath)

        return jsonify(
            {
                "status": "success",
                "pdb_path": filepath,
                "pdb_content": pdb_content,
                "filename": filename,
            }
        ), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/pdb/modified", methods=["POST"])
def generate_modified_pdb():
    """Generate PDB with chemical modifications."""
    try:
        data = request.json
        sequence = data.get("sequence", "")
        modifications = data.get("modifications", {})

        if not sequence:
            return jsonify({"error": "No sequence provided"}), 400

        generator = RNAPDBGenerator()
        output_dir = os.path.join(app.root_path, "static", "pdb_files")
        os.makedirs(output_dir, exist_ok=True)

        filename = f"modified_{sequence[:10]}_{len(sequence)}nt.pdb"
        filepath = os.path.join(output_dir, filename)

        pdb_content = generator.generate_modified_pdb(sequence, modifications, filepath)

        return jsonify(
            {
                "status": "success",
                "pdb_path": filepath,
                "pdb_content": pdb_content,
                "filename": filename,
                "modifications": modifications,
            }
        ), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/pdb/visualization_script", methods=["POST"])
def generate_visualization_script():
    """Generate PyMOL visualization script."""
    try:
        data = request.json
        sequence = data.get("sequence", "")
        modifications = data.get("modifications", {})

        if not sequence:
            return jsonify({"error": "No sequence provided"}), 400

        generator = RNAPDBGenerator()
        output_dir = os.path.join(app.root_path, "static", "pdb_files")
        os.makedirs(output_dir, exist_ok=True)

        native_path = os.path.join(output_dir, f"native_{sequence[:10]}.pdb")
        modified_path = os.path.join(output_dir, f"modified_{sequence[:10]}.pdb")

        generator.generate_native_pdb(sequence, native_path)
        generator.generate_modified_pdb(sequence, modifications, modified_path)

        script = generator.generate_pymol_script(
            sequence,
            modifications,
            native_path,
            modified_path,
            os.path.join(output_dir, f"visualize_{sequence[:10]}.pml"),
        )

        return jsonify(
            {
                "status": "success",
                "script_content": script,
                "script_path": os.path.join(
                    output_dir, f"visualize_{sequence[:10]}.pml"
                ),
                "instructions": "Run with: pymol visualize_sequence.pml",
            }
        ), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/chem_ai", methods=["POST"])
def ai_chem_optimize():
    """V8 AI chemical optimization routed to standalone Helix_Zero1 CMS module."""
    try:
        data = request.json or {}
        sequence = (
            data.get("sequence", "")
            .strip()
            .upper()
            .replace("T", "U")
        )
        sequence = "".join(ch for ch in sequence if ch in {"A", "U", "G", "C"})
        objective = data.get("objective", "efficacy").lower()

        if not sequence:
            return jsonify({"error": "No sequence provided"}), 400
        if len(sequence) < 15:
            return jsonify({"error": "Sequence too short (minimum 15nt)"}), 400

        response = requests.post(
            f"{CMS_MODULE_URL}/optimize",
            json={"sequence": sequence, "objective": objective},
            timeout=30,
        )
        try:
            cms_payload = response.json()
        except ValueError:
            cms_payload = {
                "error": "CMS optimization failed",
                "details": response.text[:400],
            }
        if not response.ok:
            return (
                jsonify(
                    {
                        "error": cms_payload.get("error", "CMS optimization failed"),
                        "details": cms_payload.get("details"),
                    }
                ),
                response.status_code,
            )

        optimization = cms_payload.get("optimization_result", {})
        if not optimization:
            return jsonify({"error": "CMS optimization returned no result"}), 502
        therapeutic_index = optimization.get(
            "therapeutic_index", optimization.get("therapeuticIndex", 0)
        )
        stability = optimization.get(
            "half_life",
            optimization.get("stabilityHalfLife", optimization.get("stability", 0)),
        )
        ago2_affinity = optimization.get("ago2_binding", optimization.get("ago2Affinity"))
        immune = optimization.get(
            "immune_suppression", optimization.get("immuneSuppression", 0)
        )

        # Enrich optimize output with CMS predict endpoint metrics for real half-life/Ago2.
        mod_type = optimization.get("modification_type", "OME")
        positions = optimization.get("positions", [])
        try:
            predict_response = requests.post(
                f"{CMS_MODULE_URL}/predict",
                json={
                    "sequence": sequence,
                    "modification_type": mod_type,
                    "positions": positions,
                },
                timeout=30,
            )
            if predict_response.ok:
                predict_payload = predict_response.json()
                predict_result = predict_payload.get("result", {})
                stability = predict_result.get("half_life", stability)
                ago2_affinity = predict_result.get("ago2_binding", ago2_affinity)
        except Exception:
            # Keep optimize-derived metrics when prediction enrichment is unavailable.
            pass

        # Build SVG visuals for native vs CMS-modified sequence.
        raw_positions = optimization.get("positions", [])
        if not isinstance(raw_positions, list):
            raw_positions = []

        mod_aliases = {
            "OME": "2_ome",
            "MOE": "2_ome",
            "2_OME": "2_ome",
            "2-OME": "2_ome",
            "2_OMe": "2_ome",
            "2F": "2_f",
            "2_F": "2_f",
            "2-F": "2_f",
            "F": "2_f",
            "PS": "ps",
        }
        canonical_mod = mod_aliases.get(str(mod_type).upper(), "2_ome")
        svg_modifications = {}
        for pos in raw_positions:
            try:
                idx = int(pos)
            except (TypeError, ValueError):
                continue
            if 0 <= idx < len(sequence):
                svg_modifications[idx] = canonical_mod

        svg_files = {}
        try:
            svg_results = generate_modification_svg(sequence, svg_modifications)
            svg_files = {
                "native": svg_results.get("native_path", ""),
                "modified": svg_results.get("modified_path", ""),
                "comparison": svg_results.get("compare_path", ""),
                "linear": svg_results.get("linear_path", ""),
                "nativeSvgContent": svg_results.get("native_svg", ""),
                "modifiedSvgContent": svg_results.get("modified_svg", ""),
                "comparisonSvgContent": svg_results.get("comparison_svg", ""),
                "linearSvgContent": svg_results.get("linear_svg", ""),
            }
        except Exception as svg_error:
            svg_files = {
                "error": str(svg_error),
                "message": "SVG generation encountered an error",
            }

        return jsonify(
            {
                "status": "success",
                "aiSummary": "Optimization powered by Helix_Zero1 CMS module.",
                "objective": cms_payload.get("objective_requested", objective),
                "originalSequence": sequence,
                "modifiedDisplay": optimization.get(
                    "modified_sequence", optimization.get("sequence", sequence)
                ),
                "modificationType": optimization.get("modification_type", "CMS-optimized"),
                "modifiedPositions": optimization.get("positions", []),
                "therapeuticIndex": therapeutic_index,
                "ago2Affinity": ago2_affinity,
                "stabilityHalfLife": stability,
                "immuneSuppression": immune,
                "warnings": optimization.get("warnings", []),
                "searchStats": optimization.get("search_stats", {}),
                "svgFiles": svg_files,
                "rawCmsResponse": cms_payload,
            }
        ), 200
    except requests.exceptions.ConnectionError:
        return jsonify({"error": "CMS module is offline or unreachable."}), 503
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── 3D RNA Target Accessibility ──────────────────────────────────────────────
from rna_accessibility import calculate_accessibility


@app.route("/api/rna_accessibility", methods=["POST"])
def rna_accessibility():
    """Calculate thermodynamic accessibility score for an siRNA target site."""
    try:
        data = request.json
        sequence = data.get("sequence", "")
        context = data.get("targetContext", None)
        if not sequence:
            return jsonify({"error": "No sequence provided"}), 400
        result = calculate_accessibility(sequence, target_context=context)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── RNA Secondary Structure Prediction (NEW!) ─────────────────────────────────
from rna_structure import compare_sites


@app.route("/api/rna_structure", methods=["POST"])
def rna_structure():
    """V8 RNA structure endpoint backed by Helix_Zero1 CMS structure predictor."""
    try:
        data = request.json or {}
        sequence = (
            data.get("sequence", "")
            .strip()
            .upper()
            .replace("T", "U")
        )
        sequence = "".join(ch for ch in sequence if ch in {"A", "U", "G", "C"})
        if not sequence:
            return jsonify({"error": "No sequence provided"}), 400
        if len(sequence) < 6:
            return jsonify({"error": "Sequence too short (minimum 6nt)"}), 400

        cms_response = requests.post(
            f"{CMS_MODULE_URL}/predict",
            json={
                "sequence": sequence,
                "modification_type": "MOE",
                "positions": [],
            },
            timeout=30,
        )
        try:
            cms_payload = cms_response.json()
        except ValueError:
            cms_payload = {
                "error": "CMS structure prediction failed",
                "details": cms_response.text[:400],
            }
        if not cms_response.ok:
            return (
                jsonify(
                    {
                        "error": cms_payload.get(
                            "error", "CMS structure prediction failed"
                        ),
                        "details": cms_payload.get("details"),
                    }
                ),
                cms_response.status_code,
            )

        cms_result = cms_payload.get("result", {})
        native = cms_result.get("structure_native", {})
        seq = sequence.upper().replace("T", "U")
        dot_bracket = native.get("structure", "." * len(seq))
        mfe = float(native.get("mfe", 0.0))

        stack = []
        base_pairs = []
        for idx, ch in enumerate(dot_bracket):
            if ch == "(":
                stack.append(idx)
            elif ch == ")" and stack:
                left = stack.pop()
                base_pairs.append([left, idx])

        pair_density = (len(base_pairs) / max(len(seq), 1)) * 100
        accessibility_score = round(max(0.0, 100.0 - pair_density), 1)

        if accessibility_score >= 70:
            acc_class = "Highly Accessible"
            acc_reason = "Low base-pair density supports target exposure."
        elif accessibility_score >= 45:
            acc_class = "Moderately Accessible"
            acc_reason = "Balanced folding; target likely accessible with optimization."
        else:
            acc_class = "Low Accessibility"
            acc_reason = "Dense structure may reduce siRNA target accessibility."

        elements = []
        if base_pairs:
            elements.append(
                {
                    "type": "stem",
                    "start": base_pairs[0][0],
                    "end": base_pairs[-1][1],
                    "description": f"Stem helix ({len(base_pairs)} base pairs)",
                }
            )
        elements.append(
            {
                "type": "loop",
                "start": 0,
                "end": len(seq),
                "description": "CMS-derived global structure",
            }
        )

        svg_files = {}
        try:
            renderer = RNAfoldSVG()
            native_svg = renderer.generate_native_svg(seq, dot_bracket)
            modified_svg = renderer.generate_modified_svg(seq, dot_bracket, {})
            comparison_svg = renderer.generate_comparison_svg(seq, dot_bracket, {})
            svg_files = {
                "nativeSvgContent": native_svg,
                "modifiedSvgContent": modified_svg,
                "comparisonSvgContent": comparison_svg,
                "linearSvgContent": native_svg,
            }
        except Exception as svg_error:
            svg_files = {
                "error": str(svg_error),
                "message": "RNA structure SVG generation failed",
            }

        return jsonify(
            {
                "sequence": seq,
                "length": len(seq),
                "gc_content": round(
                    ((seq.count("G") + seq.count("C")) / max(len(seq), 1)) * 100, 1
                ),
                "dot_bracket": dot_bracket,
                "mfe_estimate": round(mfe, 2),
                "num_base_pairs": len(base_pairs),
                "base_pairs": base_pairs,
                "structure_score": round(max(0.0, min(100.0, 100.0 + mfe)), 1),
                "accessibility_prediction": {
                    "score": accessibility_score,
                    "classification": acc_class,
                    "reason": acc_reason,
                    "num_base_pairs": len(base_pairs),
                    "base_pair_density": round(pair_density, 1),
                },
                "elements": elements,
                "visual": generate_ascii_structure(seq, dot_bracket),
                "svgFiles": svg_files,
                "method": "Helix_Zero1 CMS Structure Predictor",
                "rawCmsResponse": cms_payload,
            }
        ), 200

    except requests.exceptions.ConnectionError:
        return jsonify({"error": "CMS module is offline or unreachable."}), 503

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def generate_ascii_structure(sequence: str, dot_bracket: str) -> str:
    """Generate ASCII visualization of RNA structure."""
    lines = []
    lines.append(f"Sequence:  {sequence}")
    lines.append(f"Structure: {dot_bracket}")
    lines.append("")
    lines.append("ASCII Representation:")
    lines.append("-" * len(sequence))

    # Simple ASCII structure
    n = len(dot_bracket)
    seq_line = list(sequence[:n])
    struct_line = list(dot_bracket)

    # Add positions
    pos_line = []
    for i in range(n):
        pos_line.append(f"{(i + 1) % 10}")

    lines.append("".join(pos_line))
    lines.append("".join(seq_line))
    lines.append("".join(struct_line))

    return "\n".join(lines)


@app.route("/api/rna_structure/compare", methods=["POST"])
def rna_structure_compare():
    """
    Compare RNA structure accessibility across multiple target sites.
    Useful for selecting the most accessible siRNA target site.
    """
    try:
        data = request.json
        sequences = data.get("sequences", [])
        positions = data.get("positions", [])
        if not sequences:
            return jsonify({"error": "No sequences provided"}), 400

        result = compare_sites(sequences, positions)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── Tissue-Specific Off-Target Filter ────────────────────────────────────────
from tissue_transcriptomics import get_organisms, get_tissues, batch_filter_off_targets


@app.route("/api/tissue/organisms", methods=["GET"])
def list_organisms():
    """Return available organisms in the transcriptomics database."""
    return jsonify({"organisms": get_organisms()}), 200


@app.route("/api/tissue/tissues", methods=["GET"])
def list_tissues():
    """Return available tissues for an organism."""
    organism = request.args.get("organism", "homo_sapiens")
    return jsonify({"tissues": get_tissues(organism)}), 200


@app.route("/api/tissue_filter", methods=["POST"])
def tissue_filter():
    """Filter off-target gene matches by delivery tissue expression."""
    try:
        data = request.json
        sequence = data.get("sequence", "")
        off_targets = data.get("offTargetGenes", [])
        organism = data.get("organism", "homo_sapiens")
        delivery_tissue = data.get("deliveryTissue", "liver")
        if not sequence:
            return jsonify({"error": "No sequence provided"}), 400
        result = batch_filter_off_targets(
            sequence, off_targets, organism, delivery_tissue
        )
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── Essentiality Scoring ─────────────────────────────────────────────────
@app.route("/api/essentiality", methods=["POST"])
def score_essentiality():
    """Calculate essentiality score for a target gene."""
    try:
        data = request.json
        gene_name = data.get("geneName", "")
        if not gene_name:
            return jsonify({"error": "No gene name provided"}), 400
        result = calculate_essentiality(gene_name)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/essentiality/genes", methods=["GET"])
def list_genes():
    """Return list of all gene IDs in the essentiality databases."""
    try:
        return jsonify({"genes": get_available_genes()}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── Bloom Filter Genome Index ────────────────────────────────────────────
@app.route("/api/bloom/build", methods=["POST"])
def build_bloom_index():
    """Build a Bloom Filter index from the uploaded non-target genome."""
    try:
        data = request.json
        genome = data.get("genome", "")
        if not genome or len(genome) < 100:
            return jsonify({"error": "Genome sequence too short or missing"}), 400

        reset_index()
        idx = get_or_build_index(genome)
        return jsonify(
            {"status": "Bloom index built successfully", "stats": idx.get_index_stats()}
        ), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/bloom/status", methods=["GET"])
def bloom_status():
    """Check current Bloom Filter index status."""
    try:
        idx = get_or_build_index()
        if idx and idx.is_built:
            return jsonify({"built": True, "stats": idx.get_index_stats()}), 200
        return jsonify({"built": False}), 200
    except Exception as e:
        return jsonify({"built": False, "error": str(e)}), 200


# ── Agentic RAG ──────────────────────────────────────────────────────────
from rag_agent import generate_rag_explanation


@app.route("/api/rag", methods=["POST"])
def run_rag_explanation():
    """Agentic RAG endpoint for explaining sequence configurations."""
    try:
        candidate = request.json
        if not candidate:
            return jsonify({"error": "No candidate provided"}), 400
        explanation = generate_rag_explanation(candidate)
        return jsonify({"explanation": explanation}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── SQL Database Operations ──────────────────────────────────────────────
@app.route("/api/save_sequence", methods=["POST"])
def save_sequence():
    """Save a validated sequence to the SQL archive."""
    try:
        cand = request.json
        if not cand:
            return jsonify({"error": "No data"}), 400

        exists = TargetSequenceLog.query.filter_by(
            audit_hash=cand.get("auditHash", "")
        ).first()
        if exists:
            return jsonify({"message": "Sequence already tracked."}), 200

        log = TargetSequenceLog(
            audit_hash=cand.get("auditHash", "N/A"),
            sequence=cand.get("sequence", ""),
            gc_content=cand.get("gcContent", 0.0),
            efficacy=cand.get("efficiency", 0.0),
            safety_score=cand.get("safetyScore", 0.0),
            risk_factors=",".join(cand.get("riskFactors", [])),
        )
        db.session.add(log)
        db.session.commit()
        return jsonify({"message": "Sequence securely committed to SQL Database."}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@app.route("/api/history", methods=["GET"])
def get_history():
    """Retrieve the generated sequence history."""
    try:
        logs = (
            TargetSequenceLog.query.order_by(TargetSequenceLog.timestamp.desc())
            .limit(100)
            .all()
        )
        return jsonify({"history": [l.to_dict() for l in logs]}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(port=5000, debug=True)
