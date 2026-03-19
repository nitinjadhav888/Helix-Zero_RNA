# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
npm run dev      # Start development server (Vite)
npm run build    # Production build
npm run preview  # Preview production build
```

## Architecture

Helix-Zero is a computational biology platform for designing species-specific RNA interference (RNAi) pesticides with mathematical safety guarantees for pollinators.

### Tech Stack
- React 19 + TypeScript + Vite 7
- Tailwind CSS 4
- Recharts for data visualization
- Path alias: `@/*` → `src/*`

### Core Modules

**Existing Core (`src/lib/`):**
- `engine.ts` (1823 lines) - Core safety analysis engine with DeepTechSearch (O(1) hash-based), BloomBasedSearch, MultiSpeciesEngine, and 5-layer safety firewall
- `bloomFilter.ts` - Memory-efficient indexing for 500MB genome support
- `genomeProcessor.ts` - Chunked file processing

**Phase 1 Implemented (v7.0):**
- `ingestion/` - Genome parsing (FASTA/GFF3), transcript extraction, annotation processing
- `analysis/` - Expression analysis, gene family clustering, essential gene filtering
- `types.ts` - 324 biological interfaces (GOTerm, OrthologGroup, EssentialityScore, etc.)

### Data Flow
```
FASTA/GFF3 → [Module 1: Ingestion] → Annotated Genes
           → [Module 2: Analysis] → Expression Profiles + Gene Families
           → [Module 3: Essential Filter] → Ranked Essential Genes
           → [Existing engine.ts] → Safety Screening → Regulatory Certificates
```

### Key Configuration
- `tsconfig.json`: Strict mode, ES2020 target, path aliases configured
- `vite.config.ts`: React, Tailwind, vite-plugin-singlefile plugins
- Deployment: `netlify.toml` and `vercel.json` present

### Scientific Core
- **15-Nucleotide Rule**: Hard safety threshold - any candidate with ≥15nt match to non-target is rejected
- **5-Layer Safety Firewall**: 15-mer exclusion, seed region analysis (2-8), extended seed (2-13), palindrome detection, biological exceptions
- **12-Parameter Efficacy Scoring**: Based on Reynolds, Ui-Tei, Schwarz research

### Documentation
- `README.md` - Project overview
- `IMPLEMENTATION_STATUS.md` - Phase 1 completion report, architecture details
- `DEPLOYMENT_GUIDE.md` - Vercel/Netlify/GitHub Pages deployment
- `public/HELIX_ZERO_WHITEPAPER.md` - Technical documentation

### Development Notes
- No test framework configured (opportunity for Jest/Vitest)
- No lint script in package.json
- Modules 4-12 (conservation, structure, delivery, ML, regulatory) are pending
