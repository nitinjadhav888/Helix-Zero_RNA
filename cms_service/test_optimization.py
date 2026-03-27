import requests
import json

def test_optimization():
    url = "http://localhost:5000/optimize"
    
    sequence = "UCAAGAGACUGCUAAUUCAAU"  # example 21-mer sequence
    
    print(f"Testing Sequence: {sequence}")
    for objective in ['efficacy', 'survivability', 'immunogenicity']:
        print(f"\n--- Optimizing for: {objective.upper()} ---")
        
        payload = {
            "sequence": sequence,
            "objective": objective
        }
        
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            data = result['optimization_result']
            print(f"Winner Modification Type: {data['modification_type']}")
            print(f"Winner Positions: {data['positions']}")
            print(f"Model Predicted Final TI: {data['therapeutic_index']:.4f}")
            print(f"Model Predicted Stability: {data['stability']:.4f}")
            print(f"Model Predicted Immune Suppression: {data['immune_suppression']:.4f}")
        else:
            print(f"Error: {response.text}")

if __name__ == "__main__":
    test_optimization()
