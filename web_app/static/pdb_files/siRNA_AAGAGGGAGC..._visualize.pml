#!/usr/bin/env pymol
"""
Helix-Zero V8 PyMOL Visualization Script
Generated for sequence: AAGAGGGAGCAGCAG
"""

# Load structures
load "D:\C-DAC\Helix-Zero6.0\web_app\static\pdb_files\siRNA_AAGAGGGAGC..._native.pdb", native
load "D:\C-DAC\Helix-Zero6.0\web_app\static\pdb_files\siRNA_AAGAGGGAGC..._modified.pdb", modified

# Separate chains
splitChain native
splitChain modified

# Color schemes
# Native: Green for backbone, white for bases
color green, chain A and name P
color green, chain B and name P
util.cnc("chain B")

# Modified: Highlight modifications
# 2'-OMe: Blue spheres
# 2'-F: Orange spheres  
# PS: Purple backbone

# Set representation
show cartoon
hide everything, resn HOH

# Zoom to fit
zoom (all)

# Labels for comparison
cmd.label("chain A and name P", 'resi')
cmd.label("chain C and name P", 'resi')

# Ray trace for publication quality
ray 1200, 800
png "helix_zero_comparison.png", dpi=300

print("PyMOL script executed successfully!")
print("Native structure: chain A (guide), chain B (passenger)")
print("Modified structure: chain C (guide), chain D (passenger)")
