# Helix-Zero v7.0 - New Modules Documentation

## Overview

Helix-Zero v7.0 extends the platform with complete RNAi discovery capabilities, from raw genome ingestion through regulatory submission. This document provides usage examples and API documentation for the newly implemented modules.

---

## Quick Start

### Example 1: Parse a Genome and Extract Annotations

```typescript
import { parseFastaGenome, parseGFF3, extractTranscripts, buildAnnotationDatabase } from './lib/ingestion';

// Load genome sequence
const genomeResponse = await fetch('path/to/genome.fasta');
const genomeText = await genomeResponse.text();
const { sequence: genomeSequence, metadata } = parseFastaGenome(genomeText, 'Spodoptera frugiperda');

console.log(`Genome size: ${(metadata.genomeSize / 1_000_000).toFixed(2)} Mb`);
console.log(`GC content: ${metadata.gcContent.toFixed(2)}%`);

// Load annotations
const gff3Response = await fetch('path/to/annotations.gff3');
const gff3Text = await gff3Response.text();
const gff3Data = parseGFF3(gff3Text);

// Extract transcripts
const { transcripts, statistics } = extractTranscripts(gff3Data, genomeSequence);
console.log(`Extracted ${statistics.totalTranscripts} transcripts from ${statistics.totalGenes} genes`);
console.log(`Alternative splicing rate: ${(statistics.alternativeSplicingRate * 100).toFixed(1)}%`);

// Build annotation database
const annotationDB = buildAnnotationDatabase(gff3Data, transcripts);
console.log(`Indexed ${annotationDB.genes.size} genes`);
```

### Example 2: Analyze Gene Expression and Identify Tissue-Specific Genes

```typescript
import { parseExpressionMatrix, identifyTissueSpecificGenes, filterByExpression } from './lib/analysis';

// Load RNA-seq expression matrix
const expressionResponse = await fetch('path/to/expression_matrix.tsv');
const expressionText = await expressionResponse.text();
const expressionMatrices = parseExpressionMatrix(expressionText);

// Convert to TPM if you have raw counts and gene lengths
const geneLengths = new Map<string, number>();
// ... populate geneLengths from transcript data
const tpmValues = convertToTPM(rawCounts, geneLengths);

// Filter expressed genes (TPM > 1)
const expressedProfiles = filterByExpression(expressionProfiles, 1.0, 'tpm');

// Identify tissue-specific genes
const tissueSpecific = identifyTissueSpecificGenes(expressedProfiles, 2.0);
tissueSpecific.forEach(ts => {
  console.log(`${ts.geneId}: specific to ${ts.tissue} (score: ${ts.specificityScore.toFixed(2)})`);
});
```

### Example 3: Identify Essential Genes and Prioritize Targets

```typescript
import { 
  loadEssentialGeneDatabases, 
  calculateEssentialityScore, 
  prioritizeLethalTargets 
} from './lib/analysis';

// Load essential gene databases
const databases = await loadEssentialGeneDatabases();

// Calculate essentiality for each gene
const allGenes = Array.from(annotationDB.genes.values());
allGenes.forEach(gene => {
  const score = calculateEssentialityScore(gene, databases, 'Spodoptera frugiperda');
  gene.essentiality = score;
  
  if (score.finalScore >= 70) {
    console.log(`${gene.symbol}: ESSENTIAL (score: ${score.finalScore})`);
    console.log(`  Evidence: ${score.evidence.join(', ')}`);
  }
});

// Prioritize lethal targets for RNAi
const rankedTargets = prioritizeLethalTargets(allGenes, databases);
console.log('\nTop 10 Lethal Targets:');
rankedTargets.slice(0, 10).forEach((item, i) => {
  console.log(`${i+1}. ${item.gene.symbol} - Rank: ${item.priorityRank}`);
  console.log(`   Rationale: ${item.rationale}`);
});
```

### Example 4: Cluster Genes by Sequence Similarity

```typescript
import { clusterGenesBySimilarity, calculateSequenceIdentity } from './lib/analysis';

// Cluster all protein-coding genes at 90% identity
const proteinCodingGenes = allGenes.filter(g => g.biotype === 'protein_coding');
const { families, statistics } = clusterGenesBySimilarity(proteinCodingGenes, 0.9);

console.log(`Clustered ${statistics.clusteredGenes} genes into ${families.length} families`);
console.log(`Largest family: ${statistics.largestFamilySize} genes`);
console.log(`Singleton genes: ${statistics.singletonGenes}`);

// Find expanded families (potential species-specific adaptations)
const expandedFamilies = families.filter(f => f.expansionStatus === 'expanded');
console.log(`\nExpanded families (${expandedFamilies.length}):`);
expandedFamilies.forEach(family => {
  console.log(`${family.familyId}: ${family.genes.length} genes, function: ${family.functionalCategory}`);
});
```

### Example 5: Integrate with Existing Helix-Zero Safety Engine

```typescript
import { DeepTechSearch, runPipeline } from './lib/engine';
import { prioritizeLethalTargets } from './lib/analysis/essentialGeneFilter';

// Complete pipeline: target selection → safety screening
async function enhancedRNAiDiscovery(pestGenome, nonTargetGenome, gff3Data) {
  // Step 1: Parse and annotate
  const parsedGenome = parseFastaGenome(pestGenome, 'Spodoptera frugiperda');
  const gff3Parsed = parseGFF3(gff3Data);
  const { transcripts } = extractTranscripts(gff3Parsed, parsedGenome.sequence);
  const annotationDB = buildAnnotationDatabase(gff3Parsed, transcripts);
  
  // Step 2: Prioritize essential genes
  const databases = await loadEssentialGeneDatabases();
  const allGenes = Array.from(annotationDB.genes.values());
  const rankedTargets = prioritizeLethalTargets(allGenes, databases);
  
  // Step 3: Screen top candidates with safety engine
  const searchEngine = new DeepTechSearch(nonTargetGenome);
  const topCandidates = [];
  
  for (const target of rankedTargets.slice(0, 20)) {
    const gene = target.gene;
    
    // Get longest transcript for candidate generation
    const transcript = gene.transcripts.reduce((longest, current) => 
      current.sequence.length > longest.sequence.length ? current : longest
    );
    
    // Run existing safety pipeline on this transcript
    const { candidates } = runPipeline(
      transcript.sequence,
      searchEngine,
      70, // efficacy threshold
      TargetSpecies.LEPIDOPTERA
    );
    
    // Attach target context to candidates
    candidates.forEach(candidate => {
      candidate.targetGeneId = gene.geneId;
      candidate.targetTranscriptId = transcript.id;
      candidate.essentialityScore = gene.essentiality?.finalScore;
      candidate.priorityRank = target.priorityRank;
    });
    
    topCandidates.push(...candidates);
  }
  
  // Sort by combined score (safety + essentiality)
  topCandidates.sort((a, b) => {
    const scoreA = a.safetyScore * 0.6 + (a.essentialityScore || 0) * 0.4;
    const scoreB = b.safetyScore * 0.6 + (b.essentialityScore || 0) * 0.4;
    return scoreB - scoreA;
  });
  
  return {
    totalCandidates: topCandidates.length,
    topCandidate: topCandidates[0],
    allCandidates: topCandidates
  };
}
```

---

## API Reference

### Module 1: Genome Ingestion

#### `parseFastaGenome(fastaText: string, speciesName?: string): ParseResult`

Parses FASTA format genome files and extracts metadata.

**Parameters:**
- `fastaText`: Raw FASTA file content as string
- `speciesName` (optional): Scientific name of organism

**Returns:**
```typescript
{
  sequence: string;           // Full genome sequence
  metadata: GenomeMetadata;   // Quality metrics and annotations
  headers: string[];          // FASTA header lines
  warnings: string[];         // Parsing warnings
}
```

#### `parseGFF3(gff3Text: string): GFF3ParseResult`

Parses GFF3 annotation files into structured gene models.

**Returns:**
```typescript
{
  features: GFF3Feature[];
  genes: Map<string, GFF3Feature>;
  mrnas: Map<string, GFF3Feature>;
  exons: Map<string, GFF3Feature[]>;
  cds: Map<string, GFF3Feature[]>;
  warnings: string[];
}
```

#### `extractTranscripts(gff3Data: GFF3ParseResult, genomeSequence: string): TranscriptExtractionResult`

Extracts transcript sequences from GFF3 annotations.

**Returns:**
```typescript
{
  transcripts: Transcript[];
  statistics: {
    totalGenes: number;
    totalTranscripts: number;
    averageTranscriptLength: number;
    averageExonsPerTranscript: number;
    alternativeSplicingRate: number;
  };
  warnings: string[];
}
```

### Module 2: Transcriptome Analysis

#### `parseExpressionMatrix(tsvData: string): ExpressionMatrix[]`

Parses tab-delimited expression matrices.

**Expected Format:**
```
GeneID    Sample1    Sample2    Sample3
gene_001  123.5      45.2       89.1
gene_002  0.0        234.7      12.3
```

#### `identifyTissueSpecificGenes(profiles: ExpressionProfile[], specificityThreshold: number = 2.0)`

Identifies genes with tissue-specific expression patterns.

**Returns:**
```typescript
Array<{
  geneId: string;
  tissue: string;
  specificityScore: number;  // Fold enrichment over other tissues
}>
```

#### `clusterGenesBySimilarity(genes: AnnotatedGene[], identityThreshold: number = 0.9): ClusterResult`

Clusters genes by sequence similarity using CD-HIT-like algorithm.

**Returns:**
```typescript
{
  families: GeneFamily[];
  statistics: {
    totalGenes: number;
    clusteredGenes: number;
    singletonGenes: number;
    averageFamilySize: number;
    largestFamilySize: number;
    expandedFamilies: number;
    contractedFamilies: number;
  };
}
```

### Module 3: Essential Gene Filtering

#### `loadEssentialGeneDatabases(): Promise<EssentialGeneDatabase>`

Loads DEG, OGEE, and RNAi phenotype databases.

**Required Data Files:**
- `/data/essential_genes.json`
- `/data/ogee_essentiality.json`
- `/data/rnai_phenotypes.json`

#### `calculateEssentialityScore(gene: AnnotatedGene, databases: EssentialGeneDatabase, organismName?: string): EssentialityScore`

Calculates comprehensive essentiality score for a gene.

**Scoring Components:**
- Direct DEG match: 40 points
- OGEE continuous score: 0-30 points
- RNAi phenotype: 0-25 points
- PPI network centrality: 0-10 points

**Returns:**
```typescript
{
  degMatch: boolean;
  ogeeScore: number;
  rnaiPhenotype: 'lethal' | 'sterile' | 'viable' | 'unknown';
  ppiCentrality: number;
  finalScore: number;  // 0-100
  evidence: string[];
}
```

#### `prioritizeLethalTargets(genes: AnnotatedGene[], databases: EssentialGeneDatabase)`

Ranks genes by lethality potential for RNAi targeting.

**Bonus Features:**
- +20 points: No pollinator orthologs
- +10 points: High expression (TPM > 10)
- +5 points per essential ortholog

**Returns:**
```typescript
Array<{
  gene: AnnotatedGene;
  priorityRank: number;
  rationale: string;  // Human-readable explanation
}>
```

---

## Data File Formats

### essential_genes.json
```json
[
  {
    "geneId": "FBgn0000001",
    "organism": "Drosophila melanogaster",
    "essentiality": "essential",
    "phenotype": "embryonic lethal",
    "mutationType": "deletion",
    "reference": "PMID:1234567"
  }
]
```

### ogee_essentiality.json
```json
{
  "FBgn0000001": {
    "score": 0.95,
    "context": "laboratory_condition"
  }
}
```

### rnai_phenotypes.json
```json
{
  "FBgn0000001": "lethal",
  "FBgn0000002": "sterile",
  "FBgn0000003": "viable"
}
```

---

## Best Practices

### 1. Memory Management for Large Genomes
```typescript
// For genomes > 100Mb, process in chunks
const CHUNK_SIZE = 1_000_000;
for (let i = 0; i < genomeSequence.length; i += CHUNK_SIZE) {
  const chunk = genomeSequence.substring(i, i + CHUNK_SIZE);
  // Process chunk...
  
  // Yield to event loop to prevent UI freezing
  await new Promise(resolve => setTimeout(resolve, 0));
}
```

### 2. Error Handling
```typescript
try {
  const result = parseGFF3(gff3Text);
  if (result.warnings.length > 0) {
    console.warn('GFF3 parsing warnings:', result.warnings);
  }
} catch (error) {
  console.error('Failed to parse GFF3:', error);
}
```

### 3. Performance Optimization
```typescript
// Use Web Workers for compute-intensive clustering
const worker = new Worker('./workers/clustering.worker.ts');
worker.postMessage({ genes: allGenes, threshold: 0.9 });
worker.onmessage = (event) => {
  const clusters = event.data;
  // Process results...
};
```

---

## Troubleshooting

### Issue: "Could not load DEG dataset" warning
**Solution:** Ensure `/data/essential_genes.json` exists and is accessible. Create a minimal test file:
```json
[]
```

### Issue: Slow clustering performance
**Solution:** Reduce dataset size or increase identity threshold:
```typescript
// Use higher threshold for faster clustering
const clusters = clusterGenesBySimilarity(genes, 0.95); // vs 0.9
```

### Issue: Memory errors with large genomes
**Solution:** Implement streaming parsers or use cloud backend for Module 4+.

---

## Citation

If you use Helix-Zero v7.0 in your research, please cite:

Jadhav, N. (2025). Helix-Zero: A Computational Framework for Safety-Aware RNAi Pesticide Design. *bioRxiv*. DOI: 10.1101/2025.12.28.697123

---

## Support

- **Documentation:** https://helix-zero.com/docs/v7.0
- **GitHub Issues:** https://github.com/helix-zero/helix-zero/issues
- **Email:** contact@helix-zero.com

---

**Last Updated:** March 6, 2026  
**Version:** 7.0.0-alpha
