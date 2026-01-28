// Helix-Zero v6.3 - React Edition
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
  VERSION: '6.3',
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
  // Agricultural Pests - Lepidoptera
  SPODOPTERA = 'Spodoptera frugiperda (Fall Armyworm)',
  PLUTELLA = 'Plutella xylostella (Diamondback Moth)',
  HELICOVERPA = 'Helicoverpa armigera (Cotton Bollworm)',
  MYTHIMNA = 'Mythimna separata (Oriental Armyworm)',
  CHILO = 'Chilo suppressalis (Striped Rice Borer)',
  OSTRINIA = 'Ostrinia nubilalis (European Corn Borer)',
  PECTINOPHORA = 'Pectinophora gossypiella (Pink Bollworm)',
  AGROTIS = 'Agrotis ipsilon (Black Cutworm)',
  
  // Agricultural Pests - Coleoptera
  DIABROTICA = 'Diabrotica virgifera (Western Corn Rootworm)',
  LEPTINOTARSA = 'Leptinotarsa decemlineata (Colorado Potato Beetle)',
  TRIBOLIUM = 'Tribolium castaneum (Red Flour Beetle)',
  ANTHONOMUS = 'Anthonomus grandis (Boll Weevil)',
  SITOPHILUS = 'Sitophilus oryzae (Rice Weevil)',
  ORYZAEPHILUS = 'Oryzaephilus surinamensis (Saw-toothed Grain Beetle)',
  
  // Agricultural Pests - Hemiptera
  BEMISIA = 'Bemisia tabaci (Silverleaf Whitefly)',
  NILAPARVATA = 'Nilaparvata lugens (Brown Planthopper)',
  APHIS = 'Aphis gossypii (Cotton Aphid)',
  MYZUS = 'Myzus persicae (Green Peach Aphid)',
  LAODELPHAX = 'Laodelphax striatellus (Small Brown Planthopper)',
  
  // Agricultural Pests - Diptera
  DROSOPHILA = 'Drosophila suzukii (Spotted Wing Drosophila)',
  BACTROCERA = 'Bactrocera dorsalis (Oriental Fruit Fly)',
  CERATITIS = 'Ceratitis capitata (Mediterranean Fruit Fly)',
  
  // Legacy categories
  LEPIDOPTERA = 'Lepidoptera (General)',
  COLEOPTERA = 'Coleoptera (General)',
  GENERIC = 'Generic Insect',
}

export enum RegulatoryFramework {
  EPA_USA = 'EPA (United States)',
  CIBRC_INDIA = 'CIBRC (India)',
  EFSA_EU = 'EFSA (European Union)',
  PMRA_CANADA = 'PMRA (Canada)',
  APVMA_AUSTRALIA = 'APVMA (Australia)',
  JMAFF_JAPAN = 'JMAFF (Japan)',
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
  speciesSafety?: Record<string, number>; // Per-species safety scores
  seedSequence?: string;         // The seed region (positions 2-8)
  hasSeedMatch?: boolean;        // Whether seed matches non-target
  seedMatchCount?: number;       // Number of seed matches in non-target
  hasPalindrome?: boolean;       // Whether palindromic region exists
  palindromeLength?: number;     // Length of palindrome if found
  hasCpGMotif?: boolean;         // CpG immune motif detected
  hasPolyRun?: boolean;          // Poly-nucleotide run detected
  riskFactors?: string[];        // List of identified risk factors
  safetyNotes?: string[];        // Safety notes and recommendations
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
  accession?: string; // NCBI Accession for auto-fetch
  isCached?: boolean; // Whether genome is pre-loaded
  phylogeneticWeight?: number; // Evolutionary distance weight (0-1)
}

// Phylogenetic distance weights based on evolutionary proximity to key pollinators
// Higher weight = more critical for safety assessment
// Research basis: EPA/PMRA require evolutionary distance documentation
export const PHYLOGENETIC_WEIGHTS: Record<string, number> = {
  'apis_mellifera': 1.0,        // Honeybee (Apidae) - Most critical, reference species
  'bombus_terrestris': 0.95,    // Bumblebee (Apidae) - Same family, very close
  'megachile_rotundata': 0.90,  // Leafcutter bee (Megachilidae) - Different family, same superfamily
  'osmia_lignaria': 0.90,       // Mason bee (Megachilidae)
  'danaus_plexippus': 0.75,     // Monarch (Lepidoptera) - Different order
  'coccinella': 0.70,           // Ladybird (Coleoptera) - Predator, different order
  'trichogramma': 0.65,         // Parasitoid wasp (Hymenoptera) - Same order as bees but different biology
  'daphnia': 0.50,              // Water flea (Crustacea) - Different class
  'eisenia': 0.45,              // Earthworm (Annelida) - Different phylum
};

export const NON_TARGET_PANEL: NonTargetSpecies[] = [
  { id: 'apis_mellifera', name: 'Honeybee', scientificName: 'Apis mellifera', category: 'pollinator', enabled: true, accession: 'GCF_003254395.2', isCached: true, phylogeneticWeight: 1.0 },
  { id: 'bombus_terrestris', name: 'Bumblebee', scientificName: 'Bombus terrestris', category: 'pollinator', enabled: true, accession: 'GCF_000214255.1', isCached: true, phylogeneticWeight: 0.95 },
  { id: 'coccinella', name: 'Ladybird', scientificName: 'Coccinella septempunctata', category: 'predator', enabled: true, accession: 'GCA_013233215.1', phylogeneticWeight: 0.70 },
  { id: 'danaus_plexippus', name: 'Monarch Butterfly', scientificName: 'Danaus plexippus', category: 'pollinator', enabled: false, accession: 'GCF_000235995.1', phylogeneticWeight: 0.75 },
  { id: 'megachile_rotundata', name: 'Alfalfa Leafcutter Bee', scientificName: 'Megachile rotundata', category: 'pollinator', enabled: false, accession: 'GCF_000220905.1', phylogeneticWeight: 0.90 },
  { id: 'osmia_lignaria', name: 'Blue Orchard Bee', scientificName: 'Osmia lignaria', category: 'pollinator', enabled: false, accession: 'GCA_004114515.1', phylogeneticWeight: 0.90 },
  { id: 'trichogramma', name: 'Parasitoid Wasp', scientificName: 'Trichogramma spp.', category: 'parasitoid', enabled: false, phylogeneticWeight: 0.65 },
  { id: 'daphnia', name: 'Water Flea', scientificName: 'Daphnia magna', category: 'aquatic', enabled: false, phylogeneticWeight: 0.50 },
  { id: 'eisenia', name: 'Earthworm', scientificName: 'Eisenia fetida', category: 'soil', enabled: false, phylogeneticWeight: 0.45 },
];

export interface DeliverySystem {
  id: string;
  name: string;
  type: 'nanoparticle' | 'lipid' | 'polymer' | 'naked';
  optimalLength: [number, number]; // [min, max] in nucleotides
  optimalGC: [number, number];    // [min, max] in percentage
  deliveryEfficiency?: number;    // Relative delivery efficiency (0-1)
  stabilityScore?: number;       // Stability in physiological conditions (0-1)
}

export const DELIVERY_SYSTEMS: DeliverySystem[] = [
  { id: 'spc', name: 'Star Polycation (SPc)', type: 'polymer', optimalLength: [21, 25], optimalGC: [35, 55] },
  { id: 'lipid', name: 'Lipid Nanoparticle', type: 'lipid', optimalLength: [19, 23], optimalGC: [30, 50] },
  { id: 'chitosan', name: 'Chitosan Nanoparticle', type: 'polymer', optimalLength: [20, 27], optimalGC: [40, 60] },
  { id: 'naked', name: 'Naked dsRNA', type: 'naked', optimalLength: [21, 21], optimalGC: [30, 52] },
];

export function calculateDeliveryCompatibility(candidate: Candidate, deliverySystem: DeliverySystem): number {
  const lengthScore = calculateLengthCompatibility(candidate.sequence.length, deliverySystem.optimalLength);
  const gcScore = calculateGCCompatibility(candidate.gcContent, deliverySystem.optimalGC);
  
  // Weighted combination of length and GC compatibility
  const compatibility = (lengthScore * 0.6 + gcScore * 0.4);
  
  // Apply additional penalties if delivery system has specific requirements
  if (deliverySystem.deliveryEfficiency !== undefined) {
    return compatibility * deliverySystem.deliveryEfficiency;
  }
  
  return compatibility;
}

function calculateLengthCompatibility(length: number, optimalRange: [number, number]): number {
  const [min, max] = optimalRange;
  
  if (length >= min && length <= max) {
    // Perfect score if within optimal range
    return 100;
  } else {
    // Calculate penalty based on distance from optimal range
    const distance = length < min ? min - length : length - max;
    // Reduce score by 5 points per nucleotide away from optimal range
    const penalty = Math.min(distance * 5, 50); // Max 50% penalty
    return Math.max(100 - penalty, 0);
  }
}

function calculateGCCompatibility(gcContent: number, optimalRange: [number, number]): number {
  const [min, max] = optimalRange;
  
  if (gcContent >= min && gcContent <= max) {
    // Perfect score if within optimal range
    return 100;
  } else {
    // Calculate penalty based on distance from optimal range
    const distance = gcContent < min ? min - gcContent : gcContent - max;
    // Reduce score by 3 points per percent away from optimal range
    const penalty = Math.min(distance * 3, 50); // Max 50% penalty
    return Math.max(100 - penalty, 0);
  }
}
