// Helix-Zero v6.4 - React Edition
// Types and Configuration
// 
// Large File Support: Up to 500MB genomes using Bloom filter indexing
// Memory Efficient: ~100-200MB RAM for 50MB genome (vs 2-3GB with hash sets)

export const Config = {
  PATENT_EXCLUSION_LENGTH: 15,
  SEED_REGION_START: 1,
  SEED_REGION_END: 8,
  SEED_LENGTH: 7,
  SIRNA_LENGTH: 21,
  MAX_GENOME_SIZE: 500_000_000, // 500MB for large genome support
  MIN_GENOME_SIZE: 100,
  SCAN_LIMIT: 5000,
  GC_MIN: 30.0,
  GC_MAX: 52.0,
  GC_BUFFER: 60.0,
  DEFAULT_THRESHOLD: 70, // Lowered for better candidate distribution
  ALLOWED_NUCLEOTIDES: new Set(['A', 'C', 'G', 'T', 'U', 'N']),
  VERSION: '6.4',
  APP_NAME: 'Helix-Zero',
  // Large file thresholds
  LARGE_FILE_THRESHOLD: 10_000_000, // 10MB - use Bloom filter above this
  CHUNK_SIZE: 1_000_000, // 1MB chunks for processing
} as const;

export enum SafetyStatus {
  CLEARED = 'CLEARED',
  WARNING_SEED = 'WARNING (Seed Match)',
  TOXIC = 'TOXIC (15nt Match)',
}

export enum RNAiMode {
  DSRNA = 'dsRNA',
  AMIRNA = 'amiRNA',
  COCKTAIL = 'Multi-Target Cocktail',
}

export enum TargetSpecies {
  LEPIDOPTERA = 'Lepidoptera',
  COLEOPTERA = 'Coleoptera',
  GENERIC = 'Generic Insect',
}

export interface Candidate {
  sequence: string;
  position: number;
  efficiency: number;
  foldRisk: number;
  status: SafetyStatus;
  gcContent: number;
  matchLength: number;
  thermodynamicScore?: number;
  deliveryCompatibility?: number;
  // Enhanced safety metrics
  safetyScore: number;           // 0-100% overall pollinator safety
  seedSequence?: string;         // The seed region (positions 2-8)
  hasSeedMatch?: boolean;        // Whether seed matches non-target
  seedMatchCount?: number;       // Number of seed matches in non-target
  hasPalindrome?: boolean;       // Whether palindromic region exists
  palindromeLength?: number;     // Length of palindrome if found
  hasCpGMotif?: boolean;         // CpG immune motif detected
  hasPolyRun?: boolean;          // Poly-nucleotide run detected
  riskFactors?: string[];        // List of identified risk factors
  safetyNotes?: string[];        // Safety notes and recommendations
  explanations?: { factor: string; reasoning: string; impact: 'positive' | 'negative' | 'neutral' }[];
}

export interface RejectionMetrics {
  safety: number;
  folding: number;
  efficacy: number;
  dataQuality: number;
}

export interface AnalysisConfig {
  threshold: number;
  rnaiMode: RNAiMode;
  targetSpecies: TargetSpecies;
  homologyThreshold: number;
  multiSpeciesPanel: string[];
}

export interface NonTargetSpecies {
  id: string;
  name: string;
  scientificName: string;
  category: 'pollinator' | 'predator' | 'parasitoid' | 'aquatic' | 'soil';
  enabled: boolean;
}

export const NON_TARGET_PANEL: NonTargetSpecies[] = [
  { id: 'apis_mellifera', name: 'Honeybee', scientificName: 'Apis mellifera', category: 'pollinator', enabled: true },
  { id: 'bombus_terrestris', name: 'Bumblebee', scientificName: 'Bombus terrestris', category: 'pollinator', enabled: true },
  { id: 'coccinella', name: 'Ladybird', scientificName: 'Coccinella septempunctata', category: 'predator', enabled: true },
  { id: 'trichogramma', name: 'Parasitoid Wasp', scientificName: 'Trichogramma spp.', category: 'parasitoid', enabled: false },
  { id: 'daphnia', name: 'Water Flea', scientificName: 'Daphnia magna', category: 'aquatic', enabled: false },
  { id: 'eisenia', name: 'Earthworm', scientificName: 'Eisenia fetida', category: 'soil', enabled: false },
];

export interface DeliverySystem {
  id: string;
  name: string;
  type: 'nanoparticle' | 'lipid' | 'polymer' | 'naked';
  optimalLength: [number, number];
  optimalGC: [number, number];
}

export const DELIVERY_SYSTEMS: DeliverySystem[] = [
  { id: 'spc', name: 'Star Polycation (SPc)', type: 'polymer', optimalLength: [21, 25], optimalGC: [35, 55] },
  { id: 'lipid', name: 'Lipid Nanoparticle', type: 'lipid', optimalLength: [19, 23], optimalGC: [30, 50] },
  { id: 'chitosan', name: 'Chitosan Nanoparticle', type: 'polymer', optimalLength: [20, 27], optimalGC: [40, 60] },
  { id: 'naked', name: 'Naked dsRNA', type: 'naked', optimalLength: [21, 21], optimalGC: [30, 52] },
];
