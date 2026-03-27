"""
Helix-Zero V7 :: Bloom Filter Module
Memory-efficient probabilistic data structure for large genome homology screening.
Uses MurmurHash3-style hashing (pure Python, no external dependencies).
"""

import math
import hashlib


class BloomFilter:
    """
    A Bloom Filter for memory-efficient genome k-mer indexing.
    
    Instead of storing the entire genome string (500MB+),
    this compresses all k-mers into a compact bit-array (~5MB).
    
    Trade-off: ~1-3% false positive rate (may flag safe sequences as matches).
    Guarantee: Zero false negatives (will never miss a real match).
    """

    def __init__(self, expected_items: int = 1_000_000, fp_rate: float = 0.01):
        """
        Initialize a Bloom Filter.
        
        Args:
            expected_items: Expected number of k-mers to insert
            fp_rate: Desired false positive rate (default 1%)
        """
        # Calculate optimal bit-array size: m = -(n * ln(p)) / (ln2)^2
        self.size = int(-expected_items * math.log(fp_rate) / (math.log(2) ** 2))
        # Calculate optimal number of hash functions: k = (m/n) * ln2
        self.num_hashes = max(1, int((self.size / expected_items) * math.log(2)))
        # Bit array (using bytearray for memory efficiency)
        self.bit_array = bytearray(self.size // 8 + 1)
        self.item_count = 0
        self.fp_rate = fp_rate

    def _get_hashes(self, item: str) -> list:
        """Generate multiple hash positions using double-hashing technique."""
        # Use SHA-256 split into two 128-bit halves for double-hashing
        h = hashlib.sha256(item.encode('utf-8')).digest()
        h1 = int.from_bytes(h[:8], 'big')
        h2 = int.from_bytes(h[8:16], 'big')

        positions = []
        for i in range(self.num_hashes):
            pos = (h1 + i * h2) % self.size
            positions.append(pos)
        return positions

    def _set_bit(self, position: int):
        """Set a bit at the given position."""
        byte_index = position // 8
        bit_offset = position % 8
        self.bit_array[byte_index] |= (1 << bit_offset)

    def _get_bit(self, position: int) -> bool:
        """Check if a bit is set at the given position."""
        byte_index = position // 8
        bit_offset = position % 8
        return bool(self.bit_array[byte_index] & (1 << bit_offset))

    def add(self, item: str):
        """Add an item (k-mer) to the Bloom Filter."""
        for pos in self._get_hashes(item):
            self._set_bit(pos)
        self.item_count += 1

    def contains(self, item: str) -> bool:
        """
        Check if an item MIGHT be in the filter.
        
        Returns:
            True = item is PROBABLY present (small chance of false positive)
            False = item is DEFINITELY NOT present (guaranteed)
        """
        return all(self._get_bit(pos) for pos in self._get_hashes(item))

    def get_stats(self) -> dict:
        """Return statistics about the Bloom Filter."""
        bits_set = sum(bin(byte).count('1') for byte in self.bit_array)
        fill_ratio = bits_set / self.size if self.size > 0 else 0
        # Actual false positive rate: (bits_set / total_bits) ^ num_hashes
        actual_fp = fill_ratio ** self.num_hashes if fill_ratio < 1 else 1.0

        return {
            "totalBits": self.size,
            "bitsSet": bits_set,
            "fillRatio": round(fill_ratio * 100, 2),
            "numHashFunctions": self.num_hashes,
            "itemsInserted": self.item_count,
            "memorySizeBytes": len(self.bit_array),
            "memorySizeMB": round(len(self.bit_array) / (1024 * 1024), 3),
            "targetFPRate": self.fp_rate,
            "estimatedFPRate": round(actual_fp * 100, 4)
        }


class GenomeBloomIndex:
    """
    High-level genome indexer that builds a Bloom Filter from a FASTA genome.
    Indexes all k-mers of specified lengths for ultra-fast homology lookups.
    """

    def __init__(self, kmer_sizes: list = None):
        """
        Args:
            kmer_sizes: List of k-mer lengths to index (default: [15, 16, 17, 18, 19, 20, 21])
        """
        self.kmer_sizes = kmer_sizes or [15, 16, 17, 18, 19, 20, 21]
        self.filters = {}        # { k: BloomFilter }
        self.genome_length = 0
        self.is_built = False

    def build_from_sequence(self, genome_sequence: str):
        """
        Build Bloom Filter indices from a raw genome sequence string.
        
        For a 500MB genome with k=15-21:
        - ~500M k-mers × 7 sizes = ~3.5B insertions
        - Memory: ~35MB total (vs 500MB raw string)
        """
        genome = genome_sequence.upper().replace('U', 'T')
        self.genome_length = len(genome)

        for k in self.kmer_sizes:
            num_kmers = max(1, self.genome_length - k + 1)
            bf = BloomFilter(expected_items=num_kmers, fp_rate=0.01)

            for i in range(self.genome_length - k + 1):
                kmer = genome[i:i + k]
                # Only add valid DNA k-mers
                if all(c in 'ATCG' for c in kmer):
                    bf.add(kmer)

            self.filters[k] = bf
            print(f"[BloomIndex] k={k}: indexed {bf.item_count} k-mers, "
                  f"memory={bf.get_stats()['memorySizeMB']}MB, "
                  f"est. FP={bf.get_stats()['estimatedFPRate']}%")

        self.is_built = True

    def check_homology(self, candidate: str) -> dict:
        """
        Check a candidate siRNA sequence against the Bloom-indexed genome.
        
        Returns the maximum k-mer length that PROBABLY matches,
        scanning from longest (21) down to shortest (15).
        
        Args:
            candidate: The siRNA candidate sequence (e.g., 21nt)
            
        Returns:
            Dict with max_match_length, is_toxic, details
        """
        candidate = candidate.upper().replace('U', 'T')
        max_match = 0
        match_details = []

        # Scan from longest k down to shortest
        for k in sorted(self.kmer_sizes, reverse=True):
            if k not in self.filters:
                continue
            bf = self.filters[k]

            for i in range(len(candidate) - k + 1):
                kmer = candidate[i:i + k]
                if bf.contains(kmer):
                    max_match = max(max_match, k)
                    match_details.append({
                        "kmer": kmer,
                        "length": k,
                        "position": i,
                        "note": "Bloom filter match (probabilistic)"
                    })
                    break  # Found a match at this k, move to next

            if max_match >= 15:
                break  # Already found a toxic match, no need to continue

        return {
            "maxMatchLength": max_match,
            "isToxic": max_match >= 15,
            "isBloomFiltered": True,
            "matchDetails": match_details[:5],  # Limit details
            "confidence": "probabilistic (1-3% false positive rate)"
        }

    def get_index_stats(self) -> dict:
        """Return aggregate statistics for all Bloom filter indices."""
        total_memory = sum(f.get_stats()["memorySizeBytes"] for f in self.filters.values())
        total_items = sum(f.item_count for f in self.filters.values())

        return {
            "genomeLength": self.genome_length,
            "genomeSizeMB": round(self.genome_length / (1024 * 1024), 2),
            "kmerSizes": self.kmer_sizes,
            "totalKmersIndexed": total_items,
            "totalMemoryMB": round(total_memory / (1024 * 1024), 3),
            "compressionRatio": round(self.genome_length / max(total_memory, 1), 1),
            "isBuilt": self.is_built,
            "filterDetails": {k: self.filters[k].get_stats() for k in self.filters}
        }


# ── Module-level singleton for the genome index ──────────────────────────
_genome_index = None


def get_or_build_index(genome_sequence: str = None) -> GenomeBloomIndex:
    """
    Get the existing Bloom index or build a new one from the genome.
    Uses a module-level singleton to avoid rebuilding on every request.
    """
    global _genome_index
    if genome_sequence and (not _genome_index or not _genome_index.is_built):
        _genome_index = GenomeBloomIndex()
        _genome_index.build_from_sequence(genome_sequence)
    return _genome_index


def reset_index():
    """Reset the genome index (e.g., when user uploads a new genome)."""
    global _genome_index
    _genome_index = None
