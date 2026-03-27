
import sys
import os

# Ensure we can import from current directory
sys.path.append(os.getcwd())

from src.data_structures import siRNAsequence, ModificationType
from src.structure import StructurePredictor
import traceback

try:
    print("Initializing...")
    seq_str = "AAGUAGUAAGCUAAGCUAAG"
    # Ensure this matches what frontend sends
    mod_str = "2_ome" 
    positions = [0, 1, 5, 6, 19, 20]
    
    print(f"Sequence: {seq_str}")
    print(f"Mod String: {mod_str}")
    
    # Simulate app.py logic
    try:
        mod_enum = ModificationType(mod_str)
        print(f"Enum: {mod_enum}")
    except ValueError:
        print(f"Invalid modification type: {mod_str}")
        sys.exit(1)
        
    sequence = siRNAsequence(seq_str)
    modifications = [(p, mod_enum) for p in positions]
    
    print("Running Structure Predictor...")
    predictor = StructurePredictor()
    
    native = predictor.predict(sequence)
    print(f"Native: {native}")
    
    modified = predictor.predict_modified(sequence, modifications)
    print(f"Modified: {modified}")
    
    print("Success!")
except Exception:
    traceback.print_exc()
