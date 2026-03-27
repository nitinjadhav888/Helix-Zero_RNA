# Unified Pipeline API (Python)

## Base App
Run Flask app from `Helix-Zero6.0/web_app`.

## 1) End-to-End Pipeline
Endpoint: `POST /api/pipeline/e2e`

Sample request:
```json
{
  "targetSequence": "ATGCGTACGTTAGCTAGCTAGCTAGCTAGCTA",
  "nonTargetSequence": "TTTAAAGGGCCCATATATATATAGCGCGCGCG",
  "geneName": "actin",
  "siLength": 21,
  "modType": "2_ome",
  "objective": "balanced"
}
```

Response includes:
- `pipelineSummary`
- `selectedCandidate`
- `topCandidates`
- `modification`
- `essentiality`
- `deepLearning`

## 2) Standalone CMS Module Proxy
These endpoints forward requests to a separate CMS server.

- `POST /api/cms/predict` -> `${CMS_MODULE_URL}/predict`
- `POST /api/cms/optimize` -> `${CMS_MODULE_URL}/optimize`

Environment variable:
- `CMS_MODULE_URL` (default: `http://127.0.0.1:5001`)

## 3) Deep Learning Backend Proxy
- `POST /api/predict` -> `${DL_BACKEND_URL}/predict/efficacy/batch`
- `DL_BACKEND_URL` default: `http://127.0.0.1:8000`

## 4) Existing Utilities Still Available
- `POST /api/first_model`
- `POST /api/chem_modify`
- `POST /api/chem_ai`
- `POST /api/rna_structure`
- `POST /api/rna_accessibility`
- `POST /api/tissue_filter`
- `POST /api/essentiality`
