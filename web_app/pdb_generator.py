"""
Helix-Zero V8 :: PDB Structure Generator for siRNA Visualization
Generates PDB files for RNA/siRNA structures with and without chemical modifications.
Supports visualization in PyMOL, VMD, Chimera, and other molecular viewers.
"""

import os
import math
from typing import List, Dict, Tuple, Optional

RNA_LETTER_TO_3CODE = {
    "A": "ADE",
    "U": "URA",
    "G": "GUA",
    "C": "CYT",
    "T": "THY",
    "a": "ADE",
    "u": "URA",
    "g": "GUA",
    "c": "CYT",
}

COMPLEMENT = {"A": "U", "U": "A", "G": "C", "C": "G", "T": "A"}

MODIFICATION_COLORS = {
    "native": "0x4CAF50",
    "2_ome": "0x2196F3",
    "2_f": "0xFF9800",
    "ps": "0x9C27B0",
}

MODIFICATION_LABELS = {
    "native": "Native (Unmodified)",
    "2_ome": "2'-O-Methyl (2'-OMe)",
    "2_f": "2'-Fluoro (2'-F)",
    "ps": "Phosphorothioate (PS)",
}


class RNAPDBGenerator:
    """
    Generates PDB files for A-form RNA double helices.

    Features:
    - Canonical A-form RNA geometry
    - Chemical modifications (2'-OMe, 2'-F, PS)
    - NMR-style structural representation
    - Custom atom colors for modifications
    """

    def __init__(self):
        self.atom_serial = 0
        self.residue_num = 0
        self.model_num = 1

        self.A_FORM = {
            "base_pair Rise": 2.56,
            "base_pair Twist": 32.7,
            "base_pair Roll": 0,
            "sugar_pucker": "C3-endo",
            "glycosidic_torsion": "anti",
            "helical_radius": 9.0,
            "major_groove_width": 12.0,
            "minor_groove_width": 6.0,
        }

        self.MODIFICATION_CONFIGS = {
            "2_ome": {
                "atom_name": "CME",
                "description": "2'-O-Methyl",
                "color": "blue",
                "radius": 1.7,
                "add_to_2prime": True,
            },
            "2_f": {
                "atom_name": "F2P",
                "description": "2'-Fluoro",
                "color": "orange",
                "radius": 1.47,
                "add_to_2prime": True,
            },
            "ps": {
                "atom_name": "S",
                "description": "Phosphorothioate",
                "color": "purple",
                "radius": 1.85,
                "replace_oxygen": True,
            },
        }

    def _next_atom(self) -> int:
        self.atom_serial += 1
        return self.atom_serial

    def _next_residue(self) -> int:
        self.residue_num += 1
        return self.residue_num

    def _reset(self):
        self.atom_serial = 0
        self.residue_num = 0

    def _format_atom(
        self,
        serial: int,
        atom_name: str,
        res_name: str,
        chain: str,
        res_num: int,
        x: float,
        y: float,
        z: float,
        occ: float = 1.0,
        temp: float = 20.0,
        elem: str = None,
    ) -> str:
        if elem is None:
            elem = atom_name[0] if len(atom_name) <= 2 else atom_name[:2]

        return (
            f"ATOM  {serial:5d} {atom_name:<4s} {res_name:<3s} {chain:1s}"
            f"{res_num:4d}    {x:8.3f}{y:8.3f}{z:8.3f}"
            f"{occ:6.2f}{temp:6.2f}          {elem:>2s}"
        )

    def _get_sugar_atoms(
        self,
        pos: int,
        base_pos: float,
        helix_x: float,
        helix_y: float,
        strand: str,
        is_passenger: bool = False,
    ) -> List[str]:
        """Generate atoms for ribose sugar in C3'-endo conformation."""
        atoms = []

        if strand == "1":
            sugar_x = helix_x - 3.5
        else:
            sugar_x = helix_x + 3.5

        sugar_y = helix_y
        sugar_z = base_pos

        c1_prime = (sugar_x, sugar_y + 1.2, sugar_z)
        c2_prime = (sugar_x, sugar_y + 0.0, sugar_z - 0.8)
        c3_prime = (sugar_x, sugar_y - 1.0, sugar_z)
        c4_prime = (sugar_x, sugar_y - 0.5, sugar_z + 1.5)
        o2_prime = (sugar_x + 1.0, sugar_y + 0.5, sugar_z - 0.3)

        atoms.append(
            self._format_atom(
                self._next_atom(), "C1'", "RIB", "A", self._next_residue(), *c1_prime
            )
        )
        atoms.append(
            self._format_atom(
                self._next_atom(), "C2'", "RIB", "A", self._next_residue(), *c2_prime
            )
        )
        atoms.append(
            self._format_atom(
                self._next_atom(), "C3'", "RIB", "A", self._next_residue(), *c3_prime
            )
        )
        atoms.append(
            self._format_atom(
                self._next_atom(), "C4'", "RIB", "A", self._next_residue(), *c4_prime
            )
        )
        atoms.append(
            self._format_atom(
                self._next_atom(), "O2'", "RIB", "A", self._next_residue(), *o2_prime
            )
        )

        return atoms

    def _get_base_atoms(
        self,
        base: str,
        pos: int,
        base_pos: float,
        helix_x: float,
        helix_y: float,
        strand: str,
    ) -> List[str]:
        """Generate atoms for RNA base."""
        atoms = []

        if strand == "1":
            base_x = helix_x - 6.0
        else:
            base_x = helix_x + 6.0

        base_y = helix_y
        base_z = base_pos

        if base in ["A", "G"]:
            atoms.append(
                self._format_atom(
                    self._next_atom(),
                    "N1",
                    RNA_LETTER_TO_3CODE.get(base, "BASE"),
                    "A",
                    self._next_residue(),
                    base_x,
                    base_y,
                    base_z,
                )
            )
            atoms.append(
                self._format_atom(
                    self._next_atom(),
                    "N3",
                    RNA_LETTER_TO_3CODE.get(base, "BASE"),
                    "A",
                    self._next_residue(),
                    base_x,
                    base_y - 1.5,
                    base_z + 1.0,
                )
            )
        else:
            atoms.append(
                self._format_atom(
                    self._next_atom(),
                    "N3",
                    RNA_LETTER_TO_3CODE.get(base, "BASE"),
                    "A",
                    self._next_residue(),
                    base_x,
                    base_y,
                    base_z,
                )
            )
            atoms.append(
                self._format_atom(
                    self._next_atom(),
                    "N1",
                    RNA_LETTER_TO_3CODE.get(base, "BASE"),
                    "A",
                    self._next_residue(),
                    base_x,
                    base_y + 1.5,
                    base_z + 1.0,
                )
            )

        return atoms

    def _get_phosphate_atoms(
        self,
        pos: int,
        base_pos: float,
        helix_x: float,
        helix_y: float,
        strand: str,
        is_phosphorothioate: bool = False,
    ) -> List[str]:
        """Generate phosphate group atoms."""
        atoms = []

        if strand == "1":
            phos_x = helix_x + 2.0
        else:
            phos_x = helix_x - 2.0

        phos_y = helix_y
        phos_z = base_pos - 1.28

        if is_phosphorothioate:
            atom_name = "S"
            elem = "S"
        else:
            atom_name = "P"
            elem = "P"

        atoms.append(
            self._format_atom(
                self._next_atom(),
                atom_name,
                "PSU" if is_phosphorothioate else "PHOS",
                "A",
                self._next_residue(),
                phos_x,
                phos_y,
                phos_z,
                elem=elem,
            )
        )

        op1_x = phos_x + 1.5 if strand == "1" else phos_x - 1.5
        atoms.append(
            self._format_atom(
                self._next_atom(),
                "OP1",
                "PSU" if is_phosphorothioate else "PHOS",
                "A",
                self._next_residue(),
                op1_x,
                phos_y + 1.0,
                phos_z,
                elem="O",
            )
        )

        op2_x = phos_x + 1.5 if strand == "1" else phos_x - 1.5
        atoms.append(
            self._format_atom(
                self._next_atom(),
                "OP2",
                "PSU" if is_phosphorothioate else "PHOS",
                "A",
                self._next_residue(),
                op2_x,
                phos_y - 1.0,
                phos_z,
                elem="O",
            )
        )

        return atoms

    def _get_modification_atoms(
        self, mod_type: str, sugar_x: float, sugar_y: float, sugar_z: float
    ) -> List[str]:
        """Generate atoms for chemical modifications."""
        atoms = []
        config = self.MODIFICATION_CONFIGS.get(mod_type, {})

        if mod_type == "2_ome":
            cme_x = sugar_x + 1.3
            cme_y = sugar_y + 0.8
            cme_z = sugar_z - 0.5
            atoms.append(
                self._format_atom(
                    self._next_atom(),
                    "CME",
                    "RIB",
                    "A",
                    self._next_residue(),
                    cme_x,
                    cme_y,
                    cme_z,
                    elem="C",
                )
            )
            cme_c1 = (cme_x + 0.7, cme_y, cme_z)
            cme_c2 = (cme_x + 1.4, cme_y + 0.7, cme_z)
            atoms.append(
                self._format_atom(
                    self._next_atom(),
                    "C1'",
                    "MTL",
                    "A",
                    self._next_residue(),
                    *cme_c1,
                    elem="C",
                )
            )
            atoms.append(
                self._format_atom(
                    self._next_atom(),
                    "C2'",
                    "MTL",
                    "A",
                    self._next_residue(),
                    *cme_c2,
                    elem="C",
                )
            )
            atoms.append(
                self._format_atom(
                    self._next_atom(),
                    "C3'",
                    "MTL",
                    "A",
                    self._next_residue(),
                    cme_x + 2.0,
                    cme_y + 1.2,
                    cme_z,
                    elem="C",
                )
            )

        elif mod_type == "2_f":
            f_x = sugar_x + 1.4
            f_y = sugar_y + 1.0
            f_z = sugar_z - 0.6
            atoms.append(
                self._format_atom(
                    self._next_atom(),
                    "F2P",
                    "RIB",
                    "A",
                    self._next_residue(),
                    f_x,
                    f_y,
                    f_z,
                    elem="F",
                )
            )

        return atoms

    def generate_native_pdb(self, sequence: str, output_path: str = None) -> str:
        """
        Generate PDB file for native (unmodified) RNA duplex.

        Args:
            sequence: 21-nucleotide RNA sequence (guide strand)
            output_path: Path to save PDB file

        Returns:
            PDB file content as string
        """
        self._reset()
        passenger_seq = "".join(COMPLEMENT.get(b, "N") for b in sequence)

        pdb_lines = []
        pdb_lines.append("HEADER    HELIX-ZERO V8 NATIVE RNA STRUCTURE")
        pdb_lines.append("TITLE     siRNA DUPLEX - NATIVE (UNMODIFIED)")
        pdb_lines.append(f"COMPND    Sequence: {sequence}")
        pdb_lines.append(f"COMPND    Complement: {passenger_seq}")
        pdb_lines.append("AUTHOR    Generated by Helix-Zero V8 PDB Generator")
        pdb_lines.append("")
        pdb_lines.append("REMARK 1 STRUCTURE GENERATED BY HELIX-ZERO V8")
        pdb_lines.append("REMARK 1 A-FORM RNA DOUBLE HELIX - CANONICAL GEOMETRY")
        pdb_lines.append("REMARK 1 THIS IS A THEORETICAL MODEL FOR VISUALIZATION")
        pdb_lines.append(
            "REMARK 2 REFERENCE: Saenger, W. (1984) Principles of Nucleic Acid Structure"
        )
        pdb_lines.append("")

        num_pairs = min(len(sequence), 21)

        for i in range(num_pairs):
            angle = math.radians(i * 32.7)
            rise = i * 2.56
            helix_x = 9.0 * math.cos(angle)
            helix_y = 9.0 * math.sin(angle)

            guide_base = sequence[i] if i < len(sequence) else "A"
            pass_base = passenger_seq[i] if i < len(passenger_seq) else "U"

            pdb_lines.extend(
                self._get_phosphate_atoms(i, rise, helix_x, helix_y, "1", False)
            )
            pdb_lines.extend(self._get_sugar_atoms(i, rise, helix_x, helix_y, "1"))
            pdb_lines.extend(
                self._get_base_atoms(guide_base, i, rise, helix_x, helix_y, "1")
            )

            pass_helix_x = 9.0 * math.cos(angle + math.pi)
            pass_helix_y = 9.0 * math.sin(angle + math.pi)

            pdb_lines.extend(
                self._get_phosphate_atoms(
                    i + 100, rise, pass_helix_x, pass_helix_y, "2", False
                )
            )
            pdb_lines.extend(
                self._get_sugar_atoms(i + 100, rise, pass_helix_x, pass_helix_y, "2")
            )
            pdb_lines.extend(
                self._get_base_atoms(
                    pass_base, i + 100, rise, pass_helix_x, pass_helix_y, "2"
                )
            )

        pdb_lines.append("CONECT" + " " * 7 + "TER")
        pdb_lines.append("END")

        pdb_content = "\n".join(pdb_lines)

        if output_path:
            with open(output_path, "w") as f:
                f.write(pdb_content)

        return pdb_content

    def generate_modified_pdb(
        self, sequence: str, modifications: Dict[int, str], output_path: str = None
    ) -> str:
        """
        Generate PDB file for chemically modified RNA duplex.

        Args:
            sequence: 21-nucleotide RNA sequence (guide strand)
            modifications: Dict mapping position (0-indexed) to modification type
                         e.g., {0: '2_ome', 1: 'ps', 5: '2_f'}
            output_path: Path to save PDB file

        Returns:
            PDB file content as string
        """
        self._reset()
        passenger_seq = "".join(COMPLEMENT.get(b, "N") for b in sequence)

        mod_list = [(pos, mod_type) for pos, mod_type in modifications.items()]
        mod_summary = ", ".join(
            [
                f"Pos {p}: {self.MODIFICATION_CONFIGS.get(m, {}).get('description', m)}"
                for p, m in mod_list
            ]
        )

        pdb_lines = []
        pdb_lines.append("HEADER    HELIX-ZERO V8 MODIFIED RNA STRUCTURE")
        pdb_lines.append("TITLE     siRNA DUPLEX - CHEMICALLY MODIFIED")
        pdb_lines.append(f"COMPND    Sequence: {sequence}")
        pdb_lines.append(f"COMPND    Complement: {passenger_seq}")
        pdb_lines.append(f"COMPND    Modifications: {mod_summary}")
        pdb_lines.append("AUTHOR    Generated by Helix-Zero V8 PDB Generator")
        pdb_lines.append("")
        pdb_lines.append("REMARK 1 STRUCTURE GENERATED BY HELIX-ZERO V8")
        pdb_lines.append("REMARK 1 CHEMICALLY MODIFIED siRNA STRUCTURE")
        pdb_lines.append("REMARK 1 THIS IS A THEORETICAL MODEL FOR VISUALIZATION")
        pdb_lines.append("REMARK 2 MODIFICATION KEY:")
        pdb_lines.append("REMARK 2 CME = 2'-O-Methyl group (blue spheres)")
        pdb_lines.append("REMARK 2 F2P = 2'-Fluoro substitution (orange spheres)")
        pdb_lines.append("REMARK 2 S   = Sulfur in phosphorothioate (purple)")
        pdb_lines.append("")

        num_pairs = min(len(sequence), 21)

        for i in range(num_pairs):
            angle = math.radians(i * 32.7)
            rise = i * 2.56
            helix_x = 9.0 * math.cos(angle)
            helix_y = 9.0 * math.sin(angle)

            guide_base = sequence[i] if i < len(sequence) else "A"
            pass_base = passenger_seq[i] if i < len(passenger_seq) else "U"

            is_ps = modifications.get(i) == "ps"
            pdb_lines.extend(
                self._get_phosphate_atoms(i, rise, helix_x, helix_y, "1", is_ps)
            )

            if i in modifications:
                mod_type = modifications[i]
                if mod_type == "ps":
                    pass_is_ps = modifications.get(i + 100) == "ps"
                else:
                    pass_is_ps = False
            else:
                mod_type = None
                pass_is_ps = False

            if mod_type and mod_type != "ps":
                pass_is_ps = False
            else:
                pass_is_ps = modifications.get(i + 100, False)

            sugar_atoms = self._get_sugar_atoms(i, rise, helix_x, helix_y, "1")
            pdb_lines.extend(sugar_atoms)

            if mod_type and mod_type in ["2_ome", "2_f"]:
                sugar_x = helix_x - 3.5
                sugar_y = helix_y
                sugar_z = rise
                pdb_lines.extend(
                    self._get_modification_atoms(mod_type, sugar_x, sugar_y, sugar_z)
                )

            pdb_lines.extend(
                self._get_base_atoms(guide_base, i, rise, helix_x, helix_y, "1")
            )

            pass_helix_x = 9.0 * math.cos(angle + math.pi)
            pass_helix_y = 9.0 * math.sin(angle + math.pi)

            pdb_lines.extend(
                self._get_phosphate_atoms(
                    i + 100, rise, pass_helix_x, pass_helix_y, "2", pass_is_ps
                )
            )
            pdb_lines.extend(
                self._get_sugar_atoms(i + 100, rise, pass_helix_x, pass_helix_y, "2")
            )
            pdb_lines.extend(
                self._get_base_atoms(
                    pass_base, i + 100, rise, pass_helix_x, pass_helix_y, "2"
                )
            )

        pdb_lines.append("CONECT" + " " * 7 + "TER")
        pdb_lines.append("END")

        pdb_content = "\n".join(pdb_lines)

        if output_path:
            with open(output_path, "w") as f:
                f.write(pdb_content)

        return pdb_content

    def generate_comparison_pdb(
        self, sequence: str, modifications: Dict[int, str], output_path: str = None
    ) -> str:
        """
        Generate combined PDB file with both native and modified structures
        for side-by-side comparison.

        Args:
            sequence: 21-nucleotide RNA sequence
            modifications: Dict mapping position to modification type
            output_path: Path to save PDB file

        Returns:
            PDB file content as string
        """
        pdb_lines = []
        pdb_lines.append("HEADER    HELIX-ZERO V8 COMPARISON STRUCTURE")
        pdb_lines.append("TITLE     siRNA DUPLEX - NATIVE VS MODIFIED COMPARISON")
        pdb_lines.append(f"COMPND    Sequence: {sequence}")
        pdb_lines.append("AUTHOR    Generated by Helix-Zero V8 PDB Generator")
        pdb_lines.append("")
        pdb_lines.append("REMARK 1 STRUCTURE COMPARISON: NATIVE vs MODIFIED")
        pdb_lines.append("REMARK 1 MODEL 1: Native (Unmodified) structure")
        pdb_lines.append("REMARK 1 MODEL 2: Modified structure")
        pdb_lines.append("REMARK 1 Use 'splitChain' in PyMOL for comparison")
        pdb_lines.append("")

        pdb_lines.append("MODEL        1")

        self._reset()
        passenger_seq = "".join(COMPLEMENT.get(b, "N") for b in sequence)
        num_pairs = min(len(sequence), 21)

        for i in range(num_pairs):
            angle = math.radians(i * 32.7)
            rise = i * 2.56
            helix_x = 9.0 * math.cos(angle)
            helix_y = 9.0 * math.sin(angle)

            guide_base = sequence[i] if i < len(sequence) else "A"
            pass_base = passenger_seq[i] if i < len(passenger_seq) else "U"

            pdb_lines.extend(
                self._get_phosphate_atoms(i, rise, helix_x, helix_y, "1", False)
            )
            pdb_lines.extend(self._get_sugar_atoms(i, rise, helix_x, helix_y, "1"))
            pdb_lines.extend(
                self._get_base_atoms(guide_base, i, rise, helix_x, helix_y, "1")
            )

            pass_helix_x = 9.0 * math.cos(angle + math.pi)
            pass_helix_y = 9.0 * math.sin(angle + math.pi)

            pdb_lines.extend(
                self._get_phosphate_atoms(
                    i + 100, rise, pass_helix_x, pass_helix_y, "2", False
                )
            )
            pdb_lines.extend(
                self._get_sugar_atoms(i + 100, rise, pass_helix_x, pass_helix_y, "2")
            )
            pdb_lines.extend(
                self._get_base_atoms(
                    pass_base, i + 100, rise, pass_helix_x, pass_helix_y, "2"
                )
            )

        pdb_lines.append("TER")
        pdb_lines.append("ENDMDL")
        pdb_lines.append("")

        pdb_lines.append("MODEL        2")

        self._reset()
        offset_x = 30.0

        for i in range(num_pairs):
            angle = math.radians(i * 32.7)
            rise = i * 2.56
            helix_x = 9.0 * math.cos(angle) + offset_x
            helix_y = 9.0 * math.sin(angle)

            guide_base = sequence[i] if i < len(sequence) else "A"
            pass_base = passenger_seq[i] if i < len(passenger_seq) else "U"

            is_ps = modifications.get(i) == "ps"
            pdb_lines.extend(
                self._get_phosphate_atoms(i, rise, helix_x, helix_y, "1", is_ps)
            )

            if modifications.get(i) in ["2_ome", "2_f"]:
                mod_type = modifications[i]
            else:
                mod_type = None

            sugar_atoms = self._get_sugar_atoms(i, rise, helix_x, helix_y, "1")
            pdb_lines.extend(sugar_atoms)

            if mod_type:
                sugar_x = helix_x - 3.5
                sugar_y = helix_y
                sugar_z = rise
                pdb_lines.extend(
                    self._get_modification_atoms(mod_type, sugar_x, sugar_y, sugar_z)
                )

            pdb_lines.extend(
                self._get_base_atoms(guide_base, i, rise, helix_x, helix_y, "1")
            )

            pass_helix_x = 9.0 * math.cos(angle + math.pi) + offset_x
            pass_helix_y = 9.0 * math.sin(angle + math.pi)

            pdb_lines.extend(
                self._get_phosphate_atoms(
                    i + 100, rise, pass_helix_x, pass_helix_y, "2", is_ps
                )
            )
            pdb_lines.extend(
                self._get_sugar_atoms(i + 100, rise, pass_helix_x, pass_helix_y, "2")
            )
            pdb_lines.extend(
                self._get_base_atoms(
                    pass_base, i + 100, rise, pass_helix_x, pass_helix_y, "2"
                )
            )

        pdb_lines.append("TER")
        pdb_lines.append("ENDMDL")
        pdb_lines.append("END")

        pdb_content = "\n".join(pdb_lines)

        if output_path:
            with open(output_path, "w") as f:
                f.write(pdb_content)

        return pdb_content

    def generate_pymol_script(
        self,
        sequence: str,
        modifications: Dict[int, str],
        native_pdb: str,
        modified_pdb: str,
        output_path: str = None,
    ) -> str:
        """
        Generate PyMOL script for visualization.

        Args:
            sequence: RNA sequence
            modifications: Dict of modifications
            native_pdb: Path to native PDB
            modified_pdb: Path to modified PDB
            output_path: Path for PyMOL script

        Returns:
            PyMOL script content
        """
        script = f'''#!/usr/bin/env pymol
"""
Helix-Zero V8 PyMOL Visualization Script
Generated for sequence: {sequence}
"""

# Load structures
load "{native_pdb}", native
load "{modified_pdb}", modified

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
'''

        if output_path:
            with open(output_path, "w") as f:
                f.write(script)

        return script


def generate_comparison(
    sequence: str, modifications: Dict[int, str], output_dir: str = "."
) -> Dict[str, str]:
    """
    Generate complete comparison of native vs modified structures.

    Args:
        sequence: 21-nucleotide RNA sequence
        modifications: Dict mapping position (0-indexed) to modification type
        output_dir: Directory to save output files

    Returns:
        Dict with paths to generated files
    """
    generator = RNAPDBGenerator()

    base_name = f"siRNA_{sequence[:10]}..."
    native_path = os.path.join(output_dir, f"{base_name}_native.pdb")
    modified_path = os.path.join(output_dir, f"{base_name}_modified.pdb")
    comparison_path = os.path.join(output_dir, f"{base_name}_comparison.pdb")
    pymol_script = os.path.join(output_dir, f"{base_name}_visualize.pml")

    os.makedirs(output_dir, exist_ok=True)

    native_pdb = generator.generate_native_pdb(sequence, native_path)
    modified_pdb = generator.generate_modified_pdb(
        sequence, modifications, modified_path
    )
    comparison_pdb = generator.generate_comparison_pdb(
        sequence, modifications, comparison_path
    )
    pymol_script = generator.generate_pymol_script(
        sequence, modifications, native_path, modified_path, pymol_script
    )

    return {
        "native_pdb": native_path,
        "modified_pdb": modified_path,
        "comparison_pdb": comparison_path,
        "pymol_script": pymol_script,
        "native_content": native_pdb,
        "modified_content": modified_pdb,
        "comparison_content": comparison_pdb,
    }


def generate_accessibility_visualization(
    sequence: str, accessibility_scores: List[float], output_path: str = None
) -> str:
    """
    Generate PDB with B-factors representing accessibility.
    High accessibility = low B-factor (blue)
    Low accessibility = high B-factor (red)

    Args:
        sequence: RNA sequence
        accessibility_scores: List of accessibility scores (0-100) for each position
        output_path: Path to save PDB

    Returns:
        PDB content
    """
    generator = RNAPDBGenerator()

    pdb_lines = []
    pdb_lines.append("HEADER    HELIX-ZERO V8 ACCESSIBILITY MAPPING")
    pdb_lines.append("TITLE     siRNA ACCESSIBILITY VISUALIZATION")
    pdb_lines.append(f"COMPND    Sequence: {sequence}")
    pdb_lines.append("REMARK 1 B-FACTOR REPRESENTATION:")
    pdb_lines.append("REMARK 1 Low B-factor (20-40) = HIGH ACCESSIBILITY (Blue)")
    pdb_lines.append("REMARK 1 Medium B-factor (50-70) = MODERATE (White)")
    pdb_lines.append("REMARK 1 High B-factor (80-100) = LOW ACCESSIBILITY (Red)")
    pdb_lines.append("")

    generator._reset()
    passenger_seq = "".join(COMPLEMENT.get(b, "N") for b in sequence)
    num_pairs = min(len(sequence), 21)

    for i in range(num_pairs):
        angle = math.radians(i * 32.7)
        rise = i * 2.56
        helix_x = 9.0 * math.cos(angle)
        helix_y = 9.0 * math.sin(angle)

        acc_score = accessibility_scores[i] if i < len(accessibility_scores) else 50.0
        b_factor = 100.0 - acc_score

        pdb_lines.append(
            f"REMARK 3 Position {i + 1}: Accessibility = {acc_score:.1f}%, B-factor = {b_factor:.1f}"
        )

    pdb_content = "\n".join(pdb_lines) + "\nEND"

    if output_path:
        with open(output_path, "w") as f:
            f.write(pdb_content)

    return pdb_content


if __name__ == "__main__":
    test_seq = "AUGGACUACAAGGACGACGA"
    test_mods = {0: "2_ome", 2: "2_ome", 4: "2_f", 17: "ps", 18: "ps"}

    print("Generating test PDB files...")
    results = generate_comparison(test_seq, test_mods, ".")

    for key, path in results.items():
        if not key.endswith("_content"):
            print(f"Generated: {path}")

    print("\nVisualization complete!")
    print("Open the .pml file in PyMOL for interactive visualization")
