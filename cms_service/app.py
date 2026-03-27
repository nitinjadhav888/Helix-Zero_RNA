from flask import Flask, render_template, request, jsonify
from src.data_structures import siRNAsequence, ModificationType, PredictionResult
from src.features import FeatureExtractor
from src.structure import StructurePredictor
from src.model import AdvancedCMSModel, create_advanced_model
from src.optimizer import ModificationOptimizer
import torch
import numpy as np
import traceback
import os

app = Flask(__name__)
struct_predictor = StructurePredictor()
feature_extractor = FeatureExtractor()

# Initialize advanced model
device = 'cuda' if torch.cuda.is_available() else 'cpu'
# Get actual feature dimension from feature extractor
sample_features = feature_extractor.extract(siRNAsequence("A" * 21), [])
actual_input_dim = len(sample_features)
model = create_advanced_model(input_dim=actual_input_dim, num_classes=4)
model = model.to(device)
model.eval()

# Load pre-trained weights if available
model_path = 'cms_model_advanced.pt'
if os.path.exists(model_path):
    try:
        model.load_state_dict(torch.load(model_path, map_location=device))
        print(f"Loaded pre-trained model from {model_path}")
    except Exception as e:
        print(f"Could not load model: {e}")
        print("Using untrained model - consider training first")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/favicon.ico')
def favicon():
    return '', 204

import sys

@app.route('/optimize', methods=['POST'])
def optimize():
    try:
        data = request.json
        sequence_str = data.get('sequence', '').strip().upper()
        objective = data.get('objective', 'efficacy').lower()  # efficacy, survivability, immunogenicity

        if not sequence_str:
            return jsonify({'error': 'Sequence is required'}), 400

        optimizer = ModificationOptimizer(model=model, feature_extractor=feature_extractor, device=device)
        best_result = optimizer.optimize(sequence_str, objective=objective)

        return jsonify({
            'success': True,
            'optimization_result': best_result,
            'objective_requested': objective
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': 'Optimization failed', 'details': str(e)}), 500

@app.route('/predict', methods=['POST'])
def predict():
    """
    Enhanced prediction endpoint using advanced CMS model.
    
    Returns predictions for:
    - Therapeutic Index
    - Efficacy Category
    - Component Scores (Half-life, AGO2, Immunogenicity, Stability)
    - Auxiliary properties (Nuclease resistance, RNase H sensitivity, etc.)
    """
    try:
        print("Request received", file=sys.stderr)
        data = request.json
        sequence_str = data.get('sequence', '').strip().upper()
        modification_type = data.get('modification_type', 'MOE')
        positions = data.get('positions', [])
        
        # Validation
        if not sequence_str:
            return jsonify({'error': 'Sequence is required'}), 400
            
        # Parse inputs
        try:
            # Handle both name and value formats for modification type
            if modification_type in ['OME', 'FLUORO', 'DNA', 'PS', 'LNA', 'UNA', 'HNA', 'ANA']:
                # If it's given as a name, use that directly
                mod_enum = ModificationType[modification_type]
            else:
                # Otherwise try to look it up by value
                mod_enum = ModificationType(modification_type)
        except (ValueError, KeyError):
            # Try alternate format
            mod_map = {'2_ome': 'OME', '2_f': 'FLUORO', 'ps': 'PS', 'MOE': 'OME', 'THF': 'FLUORO'}
            mapped_type = mod_map.get(modification_type, 'OME')
            mod_enum = ModificationType[mapped_type]
        
        sequence = siRNAsequence(sequence_str)
        modifications = [(int(p), mod_enum) for p in positions]
        full_positions = [int(p) for p in positions]
        
        # Run calculation pipeline (legacy)
        print("Running calculations...", file=sys.stderr)
        result = PredictionResult.from_calculation(
            sequence=sequence,
            mod_type=mod_enum,
            positions=full_positions
        )
        
        # Advanced model prediction
        print("Running advanced ML model prediction...", file=sys.stderr)
        features = feature_extractor.extract(sequence, full_positions)
        
        with torch.no_grad():
            features_tensor = torch.FloatTensor(features).unsqueeze(0).to(device)
            model_output = model(features_tensor, return_aux_tasks=True)
            
            # Extract predictions
            therapeutic_index = model_output['therapeutic_index'].cpu().numpy()[0][0]
            category_logits = model_output['category'].cpu().numpy()[0]
            category_idx = np.argmax(category_logits)
            components = model_output['components'].cpu().numpy()[0]
            
            # Auxiliary task predictions
            aux_predictions = {}
            if 'nuclease_resistance' in model_output:
                aux_predictions['nuclease_resistance'] = float(model_output['nuclease_resistance'].cpu().numpy()[0][0])
            if 'rnase_h_resistance' in model_output:
                aux_predictions['rnase_h_resistance'] = float(model_output['rnase_h_resistance'].cpu().numpy()[0][0])
            if 'immunogenicity' in model_output:
                aux_predictions['immunogenicity'] = float(model_output['immunogenicity'].cpu().numpy()[0][0])
            if 'ago2_accessibility' in model_output:
                aux_predictions['ago2_accessibility'] = float(model_output['ago2_accessibility'].cpu().numpy()[0][0])
        
        # Structure Prediction
        print("Running structure prediction...", file=sys.stderr)
        try:
            struct_native = struct_predictor.predict(sequence)
            struct_mod = struct_predictor.predict_modified(sequence, modifications)
        except Exception as e:
            print(f"Structure prediction failed: {e}", file=sys.stderr)
            traceback.print_exc()
            # Fallback for structure if it fails
            struct_native = {'structure': '.' * sequence.length, 'mfe': 0.0, 'method': 'Failed'}
            struct_mod = {'structure': '.' * sequence.length, 'mfe': 0.0, 'method': 'Failed', 'delta_g_modification': 0.0}

        print("Sending response", file=sys.stderr)
        return jsonify({
            'success': True,
            'result': {
                'sequence': result.modified_sequence,
                'therapeutic_index': float(therapeutic_index),
                'efficacy_category': int(category_idx),
                'components': {
                    'half_life': float(components[0]),
                    'ago2_binding': float(components[1]),
                    'immune_suppression': float(components[2]),
                    'stability': float(components[3])
                },
                'auxiliary_predictions': aux_predictions,
                'half_life': float(result.half_life_hours),
                'ago2_binding': float(result.ago2_binding_percent),
                'immune_suppression': float(result.immune_suppression_percent),
                'recommendation': str(result.recommendation),
                'stability_score': float(result.stability_score),
                'activity_score': float(result.activity_score),
                'cleavage_violations': int(result.cleavage_zone_violations),
                'structure_native': struct_native,
                'structure_modified': struct_mod,
                'model_info': {
                    'architecture': 'AdvancedCMSModel (Transformer-based)',
                    'device': device,
                    'input_features': int(actual_input_dim),
                    'num_heads': 8,
                    'transformer_layers': 4
                }
            }
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)