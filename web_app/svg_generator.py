"""
Helix-Zero V8 :: SVG-based RNA Chemical Modification Visualization
Generates 2D SVG visualizations of siRNA structures showing:
- Native vs Modified comparison
- Modification positions with color-coded markers
- Base composition with sugar-phosphate backbone
- Interactive SVG with hover effects
"""

import os
import base64
from typing import Dict, List, Tuple, Optional


MODIFICATION_COLORS = {
    "native": {
        "fill": "#4A5568",
        "stroke": "#2D3748",
        "text": "#FFFFFF",
        "label": "Native",
    },
    "2_ome": {
        "fill": "#3182CE",
        "stroke": "#2B6CB0",
        "text": "#FFFFFF",
        "label": "2'-O-Methyl (2'-OMe)",
        "symbol": "CH₃",
        "description": "Methyl group added to 2'-OH",
    },
    "2_f": {
        "fill": "#DD6B20",
        "stroke": "#C05621",
        "text": "#FFFFFF",
        "label": "2'-Fluoro (2'-F)",
        "symbol": "F",
        "description": "Fluorine replaces 2'-OH",
    },
    "ps": {
        "fill": "#805AD5",
        "stroke": "#6B46C1",
        "text": "#FFFFFF",
        "label": "Phosphorothioate (PS)",
        "symbol": "S",
        "description": "Sulfur replaces non-bridging oxygen",
    },
}

BASE_COLORS = {
    "A": {"fill": "#38A169", "stroke": "#276749"},
    "U": {"fill": "#E53E3E", "stroke": "#C53030"},
    "G": {"fill": "#D69E2E", "stroke": "#B7791F"},
    "C": {"fill": "#3182CE", "stroke": "#2B6CB0"},
    "T": {"fill": "#E53E3E", "stroke": "#C53030"},
}

COMPLEMENT = {"A": "U", "U": "A", "G": "C", "C": "G"}


class RNASVGenerator:
    """
    Generates SVG visualizations for RNA chemical modification patterns.
    """

    def __init__(self, width: int = 900, height: int = 500):
        self.width = width
        self.height = height
        self.padding = 40
        self.nucleotide_radius = 18
        self.backbone_y = height // 2
        self.strand_spacing = 120

    def _generate_defs(self) -> str:
        """Generate SVG definitions for gradients and filters."""
        defs = """<defs>
            <!-- Gradients -->
            <linearGradient id="nativeGrad" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" style="stop-color:#4A5568;stop-opacity:1" />
                <stop offset="100%" style="stop-color:#2D3748;stop-opacity:1" />
            </linearGradient>
            <linearGradient id="omeGrad" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" style="stop-color:#4299E1;stop-opacity:1" />
                <stop offset="100%" style="stop-color:#3182CE;stop-opacity:1" />
            </linearGradient>
            <linearGradient id="fGrad" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" style="stop-color:#ED8936;stop-opacity:1" />
                <stop offset="100%" style="stop-color:#DD6B20;stop-opacity:1" />
            </linearGradient>
            <linearGradient id="psGrad" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" style="stop-color:#9F7AEA;stop-opacity:1" />
                <stop offset="100%" style="stop-color:#805AD5;stop-opacity:1" />
            </linearGradient>
            
            <!-- Filters -->
            <filter id="glow">
                <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
                <feMerge>
                    <feMergeNode in="coloredBlur"/>
                    <feMergeNode in="SourceGraphic"/>
                </feMerge>
            </filter>
            <filter id="shadow">
                <feDropShadow dx="2" dy="2" stdDeviation="2" flood-opacity="0.3"/>
            </filter>
        </defs>"""
        return defs

    def _generate_nucleotide(
        self,
        x: float,
        y: float,
        base: str,
        mod_type: str = "native",
        position: int = 0,
        is_top: bool = True,
    ) -> str:
        """Generate SVG for a single nucleotide with optional modification."""

        # Base circle
        base_color = BASE_COLORS.get(base, BASE_COLORS["A"])
        radius = self.nucleotide_radius

        svg_parts = []

        # Shadow and circle for base
        svg_parts.append(f'''<circle cx="{x}" cy="{y}" r="{radius}" fill="{base_color["fill"]}" 
            stroke="{base_color["stroke"]}" stroke-width="2" filter="url(#shadow)"/>''')

        # Base letter
        svg_parts.append(f'''<text x="{x}" y="{y + 5}" text-anchor="middle" 
            font-family="Arial, sans-serif" font-size="14" font-weight="bold" 
            fill="white">{base}</text>''')

        # Position number
        svg_parts.append(f'''<text x="{x}" y="{y + radius + 12}" text-anchor="middle" 
            font-family="Arial, sans-serif" font-size="9" fill="#718096">{position + 1}</text>''')

        # Modification badge
        if mod_type != "native":
            mod_color = MODIFICATION_COLORS.get(mod_type, MODIFICATION_COLORS["native"])

            # Modification marker (small circle above/below)
            badge_y = y - radius - 15 if is_top else y + radius + 15
            badge_x = x

            svg_parts.append(f'''<circle cx="{badge_x}" cy="{badge_y}" r="10" 
                fill="url(#{mod_type.replace("-", "")}Grad)" stroke="{mod_color["stroke"]}" 
                stroke-width="2" filter="url(#glow)">
                <title>{mod_color["label"]}: {mod_color["description"]}</title>
            </circle>''')

            # Modification symbol
            symbol = mod_color.get("symbol", "X")
            svg_parts.append(f'''<text x="{badge_x}" y="{badge_y + 4}" text-anchor="middle" 
                font-family="Arial, sans-serif" font-size="10" font-weight="bold" 
                fill="white"><tspan font-size="8">{symbol}</tspan></text>''')

            # Connecting line
            line_y1 = y - radius if is_top else y + radius
            line_y2 = badge_y + 10 if is_top else badge_y - 10
            svg_parts.append(f'''<line x1="{x}" y1="{line_y1}" x2="{x}" y2="{line_y2}" 
                stroke="{mod_color["stroke"]}" stroke-width="1" stroke-dasharray="2,1"/>''')

        return "\n            ".join(svg_parts)

    def _generate_backbone(
        self,
        start_x: float,
        y: float,
        length: int,
        modifications: Dict[int, str] = None,
    ) -> str:
        """Generate the sugar-phosphate backbone."""
        mod = modifications or {}
        parts = []

        # Backbone line
        end_x = start_x + (length - 1) * 40
        parts.append(f"""<path d="M {start_x} {y} L {end_x} {y}" 
            stroke="#A0AEC0" stroke-width="3" fill="none" stroke-linecap="round"/>""")

        # Phosphate markers
        for i in range(0, length, 3):
            px = start_x + i * 40
            parts.append(f'''<circle cx="{px}" cy="{y}" r="4" fill="#718096">
                <title>Phosphate {i + 1}</title>
            </circle>''')

        return "\n            ".join(parts)

    def _generate_legend(self) -> str:
        """Generate the legend for modification types."""
        legend_items = []
        y_start = self.height - 80

        legend_items.append(f'''<rect x="{self.width - 280}" y="{y_start - 10}" 
            width="260" height="130" fill="#1A202C" stroke="#4A5568" rx="5" opacity="0.9"/>''')

        legend_items.append(f'''<text x="{self.width - 270}" y="{y_start + 10}" 
            font-family="Arial, sans-serif" font-size="12" font-weight="bold" fill="#E2E8F0">
            Modification Legend
        </text>''')

        y_offset = 35
        for i, (key, color) in enumerate(
            [
                ("native", MODIFICATION_COLORS["native"]),
                ("2_ome", MODIFICATION_COLORS["2_ome"]),
                ("2_f", MODIFICATION_COLORS["2_f"]),
                ("ps", MODIFICATION_COLORS["ps"]),
            ]
        ):
            y = y_start + y_offset + i * 22
            legend_items.append(f'''<circle cx="{self.width - 260}" cy="{y}" r="8" 
                fill="{color["fill"]}" stroke="{color["stroke"]}" stroke-width="1"/>''')
            legend_items.append(f'''<text x="{self.width - 245}" y="{y + 4}" 
                font-family="Arial, sans-serif" font-size="10" fill="#CBD5E0">
                {color["label"]}
            </text>''')

        return "\n        ".join(legend_items)

    def _generate_title(self, title: str, subtitle: str = None) -> str:
        """Generate title section."""
        parts = []
        parts.append(f'''<text x="{self.width // 2}" y="25" text-anchor="middle" 
            font-family="Arial, sans-serif" font-size="18" font-weight="bold" fill="#E2E8F0">
            {title}
        </text>''')
        if subtitle:
            parts.append(f'''<text x="{self.width // 2}" y="45" text-anchor="middle" 
                font-family="Arial, sans-serif" font-size="11" fill="#A0AEC0">
                {subtitle}
            </text>''')
        return "\n        ".join(parts)

    def generate_native_svg(self, sequence: str, output_path: str = None) -> str:
        """Generate SVG for native (unmodified) RNA structure."""
        seq = sequence.upper().replace("T", "U")
        length = len(seq)

        # Calculate positions
        start_x = self.padding + 50
        top_y = self.backbone_y - self.strand_spacing // 2
        bottom_y = self.backbone_y + self.strand_spacing // 2

        nucleotides = []
        nucleotides.append(self._generate_backbone(start_x, top_y, length))
        nucleotides.append(self._generate_backbone(start_x, bottom_y, length))

        for i, base in enumerate(seq):
            x = start_x + i * 40
            nucleotides.append(
                self._generate_nucleotide(x, top_y, base, "native", i, True)
            )

            # Complement base
            comp = COMPLEMENT.get(base, "A")
            nucleotides.append(
                self._generate_nucleotide(x, bottom_y, comp, "native", i, False)
            )

            # Hydrogen bond (dotted line)
            nucleotides.append(f'''<line x1="{x}" y1="{top_y + self.nucleotide_radius}" 
                x2="{x}" y2="{bottom_y - self.nucleotide_radius}" 
                stroke="#718096" stroke-width="1" stroke-dasharray="2,2" opacity="0.5"/>''')

        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.width} {self.height}" 
            style="background-color: #1A202C; border-radius: 8px;">
            {self._generate_defs()}
            
            {self._generate_title("Native siRNA Structure", f"Sequence: {seq} ({length} nt)")}
            
            <!-- 5' and 3' labels -->
            <text x="{start_x - 25}" y="{top_y + 5}" font-family="Arial" font-size="10" fill="#48BB78">5'</text>
            <text x="{start_x + length * 40 + 10}" y="{top_y + 5}" font-family="Arial" font-size="10" fill="#48BB78">3'</text>
            <text x="{start_x - 25}" y="{bottom_y + 5}" font-family="Arial" font-size="10" fill="#F56565">3'</text>
            <text x="{start_x + length * 40 + 10}" y="{bottom_y + 5}" font-family="Arial" font-size="10" fill="#F56565">5'</text>
            
            <!-- Guide strand label -->
            <text x="{self.padding}" y="{top_y + 5}" font-family="Arial" font-size="9" fill="#4299E1">Guide</text>
            
            <g id="nucleotides">
            {"\n            ".join(nucleotides)}
            </g>
            
            {self._generate_legend()}
        </svg>'''

        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(svg)

        return svg

    def generate_modified_svg(
        self, sequence: str, modifications: Dict[int, str], output_path: str = None
    ) -> str:
        """Generate SVG for modified RNA structure."""
        seq = sequence.upper().replace("T", "U")
        length = len(seq)

        start_x = self.padding + 50
        top_y = self.backbone_y - self.strand_spacing // 2
        bottom_y = self.backbone_y + self.strand_spacing // 2

        nucleotides = []
        nucleotides.append(
            self._generate_backbone(start_x, top_y, length, modifications)
        )
        nucleotides.append(self._generate_backbone(start_x, bottom_y, length))

        for i, base in enumerate(seq):
            x = start_x + i * 40
            mod_type = modifications.get(i, "native")
            nucleotides.append(
                self._generate_nucleotide(x, top_y, base, mod_type, i, True)
            )

            comp = COMPLEMENT.get(base, "A")
            nucleotides.append(
                self._generate_nucleotide(x, bottom_y, comp, "native", i, False)
            )

            nucleotides.append(f'''<line x1="{x}" y1="{top_y + self.nucleotide_radius}" 
                x2="{x}" y2="{bottom_y - self.nucleotide_radius}" 
                stroke="#718096" stroke-width="1" stroke-dasharray="2,2" opacity="0.5"/>''')

        # Generate modification summary
        mod_summary = self._generate_mod_summary(modifications)

        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.width} {self.height}" 
            style="background-color: #1A202C; border-radius: 8px;">
            {self._generate_defs()}
            
            {self._generate_title("Modified siRNA Structure", f"Sequence: {seq} | {mod_summary}")}
            
            <text x="{start_x - 25}" y="{top_y + 5}" font-family="Arial" font-size="10" fill="#48BB78">5'</text>
            <text x="{start_x + length * 40 + 10}" y="{top_y + 5}" font-family="Arial" font-size="10" fill="#48BB78">3'</text>
            <text x="{start_x - 25}" y="{bottom_y + 5}" font-family="Arial" font-size="10" fill="#F56565">3'</text>
            <text x="{start_x + length * 40 + 10}" y="{bottom_y + 5}" font-family="Arial" font-size="10" fill="#F56565">5'</text>
            
            <g id="nucleotides">
            {"\n            ".join(nucleotides)}
            </g>
            
            {self._generate_legend()}
        </svg>'''

        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(svg)

        return svg

    def _generate_mod_summary(self, modifications: Dict[int, str]) -> str:
        """Generate a summary of modifications."""
        if not modifications:
            return "No modifications"

        counts = {}
        for mod in modifications.values():
            counts[mod] = counts.get(mod, 0) + 1

        parts = []
        for mod, count in counts.items():
            label = MODIFICATION_COLORS.get(mod, {}).get("label", mod)
            parts.append(f"{count} {label}")

        return " | ".join(parts)

    def generate_comparison_svg(
        self, sequence: str, modifications: Dict[int, str], output_path: str = None
    ) -> str:
        """Generate side-by-side comparison SVG (Native vs Modified)."""
        seq = sequence.upper().replace("T", "U")
        length = len(seq)

        # Two panels side by side
        panel_width = self.width // 2 - 20
        native_start_x = self.padding
        modified_start_x = self.width // 2 + 20
        top_y = 70
        bottom_y = top_y + 100

        elements = []

        # Panel backgrounds
        elements.append(f'''<rect x="10" y="55" width="{panel_width}" height="150" 
            fill="#2D3748" stroke="#4A5568" rx="5"/>''')
        elements.append(f'''<rect x="{self.width // 2 + 10}" y="55" width="{panel_width}" height="150" 
            fill="#2D3748" stroke="#4A5568" rx="5"/>''')

        # Panel titles
        elements.append(f'''<text x="{panel_width // 2 + 10}" y="75" text-anchor="middle" 
            font-family="Arial" font-size="12" font-weight="bold" fill="#48BB78">NATIVE (Unmodified)</text>''')
        elements.append(f'''<text x="{self.width // 2 + panel_width // 2 + 10}" y="75" text-anchor="middle" 
            font-family="Arial" font-size="12" font-weight="bold" fill="#DD6B20">MODIFIED</text>''')

        # Generate nucleotides for both panels
        for i, base in enumerate(seq):
            # Native panel
            nx = native_start_x + 30 + i * ((panel_width - 60) / max(length - 1, 1))
            mod_type = modifications.get(i, "native")
            elements.append(
                self._generate_nucleotide_compact(nx, top_y + 50, base, "native", i)
            )
            comp = COMPLEMENT.get(base, "A")
            elements.append(
                self._generate_nucleotide_compact(nx, bottom_y + 50, comp, "native", i)
            )
            elements.append(f'''<line x1="{nx}" y1="{top_y + 50 + 12}" x2="{nx}" y2="{bottom_y + 50 - 12}" 
                stroke="#718096" stroke-width="1" stroke-dasharray="2,2" opacity="0.5"/>''')

            # Modified panel
            mx = modified_start_x + 30 + i * ((panel_width - 60) / max(length - 1, 1))
            elements.append(
                self._generate_nucleotide_compact(mx, top_y + 50, base, mod_type, i)
            )
            elements.append(
                self._generate_nucleotide_compact(mx, bottom_y + 50, comp, "native", i)
            )
            elements.append(f'''<line x1="{mx}" y1="{top_y + 50 + 12}" x2="{mx}" y2="{bottom_y + 50 - 12}" 
                stroke="#718096" stroke-width="1" stroke-dasharray="2,2" opacity="0.5"/>''')

        # Modification summary box
        mod_count = len(modifications)
        mod_types = set(modifications.values())
        summary_text = f"{mod_count} modifications: {', '.join(MODIFICATION_COLORS.get(m, {}).get('label', m) for m in mod_types)}"

        elements.append(f'''<rect x="{self.width // 2 + 20}" y="220" width="{panel_width - 20}" height="30" 
            fill="#2B6CB0" stroke="#4299E1" rx="3"/>''')
        elements.append(f'''<text x="{self.width // 2 + panel_width // 2 + 10}" y="240" text-anchor="middle" 
            font-family="Arial" font-size="10" fill="white">{summary_text}</text>''')

        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.width} {self.height}" 
            style="background-color: #1A202C; border-radius: 8px;">
            {self._generate_defs()}
            
            {self._generate_title("RNA Chemical Modification Comparison", f"siRNA: {seq} ({length} nt)")}
            
            {"\n        ".join(elements)}
            
            {self._generate_legend()}
        </svg>"""

        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(svg)

        return svg

    def _generate_nucleotide_compact(
        self, x: float, y: float, base: str, mod_type: str = "native", position: int = 0
    ) -> str:
        """Generate compact nucleotide for comparison view."""
        base_color = BASE_COLORS.get(base, BASE_COLORS["A"])
        radius = 12

        parts = []
        parts.append(f'''<circle cx="{x}" cy="{y}" r="{radius}" fill="{base_color["fill"]}" 
            stroke="{base_color["stroke"]}" stroke-width="1.5"/>''')
        parts.append(f'''<text x="{x}" y="{y + 4}" text-anchor="middle" 
            font-family="Arial" font-size="10" font-weight="bold" fill="white">{base}</text>''')

        if mod_type != "native":
            mod_color = MODIFICATION_COLORS.get(mod_type, MODIFICATION_COLORS["native"])
            parts.append(f'''<circle cx="{x + 10}" cy="{y - 10}" r="7" 
                fill="{mod_color["fill"]}" stroke="{mod_color["stroke"]}" stroke-width="1">
                <title>{mod_color["label"]}</title>
            </circle>''')
            symbol = mod_color.get("symbol", "X")
            parts.append(f'''<text x="{x + 10}" y="{y - 7}" text-anchor="middle" 
                font-family="Arial" font-size="7" font-weight="bold" fill="white">{symbol}</text>''')

        return "\n                ".join(parts)

    def generate_linear_view_svg(
        self, sequence: str, modifications: Dict[int, str], output_path: str = None
    ) -> str:
        """Generate linear view with modification markers."""
        seq = sequence.upper().replace("T", "U")
        length = len(seq)

        row_height = 60
        width = max(900, length * 45 + 100)
        height = 350

        lines = []
        lines.append(f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" 
            style="background-color: #1A202C; border-radius: 8px;">""")
        lines.append(self._generate_defs())

        # Title
        lines.append(f'''<text x="{width // 2}" y="30" text-anchor="middle" 
            font-family="Arial" font-size="16" font-weight="bold" fill="#E2E8F0">
            RNA Sequence with Chemical Modifications
        </text>''')

        # Position header
        pos_y = 55
        for i in range(length):
            x = 60 + i * 45
            lines.append(f'''<text x="{x}" y="{pos_y}" text-anchor="middle" 
                font-family="Arial" font-size="9" fill="#A0AEC0">{i + 1}</text>''')

        # Base sequence row
        base_y = 90
        lines.append(
            f'''<text x="15" y="{base_y + 5}" font-family="Arial" font-size="10" fill="#718096">Seq:</text>'''
        )
        for i, base in enumerate(seq):
            x = 60 + i * 45
            base_color = BASE_COLORS.get(base, BASE_COLORS["A"])
            lines.append(f'''<rect x="{x - 10}" y="{base_y - 12}" width="20" height="24" 
                fill="{base_color["fill"]}" stroke="{base_color["stroke"]}" rx="3"/>''')
            lines.append(f'''<text x="{x}" y="{base_y + 5}" text-anchor="middle" 
                font-family="Arial" font-size="12" font-weight="bold" fill="white">{base}</text>''')

        # Modification row
        mod_y = 140
        lines.append(
            f'''<text x="15" y="{mod_y + 5}" font-family="Arial" font-size="10" fill="#718096">Mod:</text>'''
        )

        for i in range(length):
            x = 60 + i * 45
            mod_type = modifications.get(i, "native")

            if mod_type != "native":
                mod_color = MODIFICATION_COLORS.get(
                    mod_type, MODIFICATION_COLORS["native"]
                )
                symbol = mod_color.get("symbol", "X")
                label = mod_color.get("label", mod_type)

                lines.append(f'''<circle cx="{x}" cy="{mod_y}" r="12" fill="{mod_color["fill"]}" 
                    stroke="{mod_color["stroke"]}" stroke-width="2" filter="url(#glow)">
                    <title>{label}</title>
                </circle>''')
                lines.append(f'''<text x="{x}" y="{mod_y + 4}" text-anchor="middle" 
                    font-family="Arial" font-size="9" font-weight="bold" fill="white">{symbol}</text>''')
                lines.append(f'''<line x1="{x}" y1="{base_y + 12}" x2="{x}" y2="{mod_y - 12}" 
                    stroke="{mod_color["stroke"]}" stroke-width="1" stroke-dasharray="2,1"/>''')
            else:
                lines.append(
                    f'''<circle cx="{x}" cy="{mod_y}" r="3" fill="#4A5568" opacity="0.3"/>'''
                )

        # Ago2 Cleavage Zone indicator
        zone_y = 180
        lines.append(
            f'''<text x="15" y="{zone_y + 5}" font-family="Arial" font-size="10" fill="#E53E3E">⚠</text>'''
        )
        lines.append(f'''<rect x="60 + 8 * 45" y="{zone_y - 10}" width="4 * 45" height="25" 
            fill="#E53E3E" opacity="0.2" rx="3"/>
            <text x="{60 + 8 * 45 + 2 * 45}" y="{zone_y + 5}" text-anchor="middle" 
                font-family="Arial" font-size="9" fill="#FC8181">Ago2 Cleavage Zone (9-12)</text>''')

        # Legend
        legend_y = 220
        lines.append(f'''<rect x="60" y="{legend_y}" width="{width - 120}" height="80" 
            fill="#2D3748" stroke="#4A5568" rx="5"/>''')
        lines.append(f'''<text x="75" y="{legend_y + 20}" font-family="Arial" font-size="11" 
            font-weight="bold" fill="#E2E8F0">Modification Types:</text>''')

        col = 0
        for key, color in [
            ("2_ome", MODIFICATION_COLORS["2_ome"]),
            ("2_f", MODIFICATION_COLORS["2_f"]),
            ("ps", MODIFICATION_COLORS["ps"]),
        ]:
            lx = 75 + col * 250
            ly = legend_y + 45
            lines.append(
                f'''<circle cx="{lx}" cy="{ly}" r="8" fill="{color["fill"]}" stroke="{color["stroke"]}"/>'''
            )
            lines.append(f'''<text x="{lx + 15}" y="{ly + 4}" font-family="Arial" font-size="10" fill="#CBD5E0">
                {color["label"]}
            </text>''')
            col += 1

        # Cleavage zone note
        lines.append(f'''<text x="{width - 80}" y="{legend_y + 65}" font-family="Arial" font-size="9" 
            fill="#FC8181" text-anchor="end">⚠ Cleavage zone positions 9-12 should NOT be modified</text>''')

        lines.append("</svg>")

        svg = "\n".join(lines)

        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(svg)

        return svg


def generate_modification_svg(
    sequence: str, modifications: Dict[int, str], output_dir: str = None
) -> Dict[str, any]:
    """
    Generate all SVG visualizations for RNA chemical modification.

    Args:
        sequence: RNA sequence
        modifications: Dict of position -> modification type
        output_dir: Directory to save SVG files

    Returns:
        Dict with SVG content and paths
    """
    generator = RNASVGenerator()

    seq_safe = sequence[:15].replace(" ", "_")
    results = {}

    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    # Generate native SVG
    if output_dir:
        native_path = os.path.join(output_dir, f"native_{seq_safe}.svg")
    else:
        native_path = None
    results["native_svg"] = generator.generate_native_svg(sequence, native_path)
    results["native_path"] = native_path

    # Generate modified SVG
    if output_dir:
        modified_path = os.path.join(output_dir, f"modified_{seq_safe}.svg")
    else:
        modified_path = None
    results["modified_svg"] = generator.generate_modified_svg(
        sequence, modifications, modified_path
    )
    results["modified_path"] = modified_path

    # Generate comparison SVG
    if output_dir:
        compare_path = os.path.join(output_dir, f"compare_{seq_safe}.svg")
    else:
        compare_path = None
    results["comparison_svg"] = generator.generate_comparison_svg(
        sequence, modifications, compare_path
    )
    results["compare_path"] = compare_path

    # Generate linear view SVG
    if output_dir:
        linear_path = os.path.join(output_dir, f"linear_{seq_safe}.svg")
    else:
        linear_path = None
    results["linear_svg"] = generator.generate_linear_view_svg(
        sequence, modifications, linear_path
    )
    results["linear_path"] = linear_path

    return results


if __name__ == "__main__":
    # Test
    seq = "AUGGACUACAAGGACGACGA"
    mods = {0: "2_ome", 2: "2_ome", 4: "2_f", 17: "ps", 18: "ps"}

    results = generate_modification_svg(seq, mods, ".")

    print("SVG files generated:")
    for key, path in results.items():
        if path and not key.endswith("_svg"):
            print(f"  {path}")
