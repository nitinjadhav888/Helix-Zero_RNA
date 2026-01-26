/**
 * Bloom Filter Implementation for Memory-Efficient Genome Indexing
 * 
 * A Bloom filter is a space-efficient probabilistic data structure that tests
 * whether an element is a member of a set. False positives are possible, but
 * false negatives are not.
 * 
 * For 50M k-mers with 0.1% false positive rate:
 * - Hash Set would need: ~2-3 GB memory
 * - Bloom Filter needs: ~120 MB memory
 * 
 * Scientific Basis:
 * - Uses multiple hash functions to reduce false positive rate
 * - Optimal number of hash functions k = (m/n) * ln(2)
 * - False positive rate p ≈ (1 - e^(-kn/m))^k
 */

export class BloomFilter {
  private bitArray: Uint32Array;
  private size: number;
  private hashCount: number;
  private itemCount: number = 0;

  /**
   * Create a Bloom filter optimized for expected number of elements
   * @param expectedElements - Expected number of elements to store
   * @param falsePositiveRate - Desired false positive rate (default 0.001 = 0.1%)
   */
  constructor(expectedElements: number, falsePositiveRate: number = 0.001) {
    // Calculate optimal size: m = -n * ln(p) / (ln(2)^2)
    this.size = Math.ceil(
      (-expectedElements * Math.log(falsePositiveRate)) / (Math.log(2) ** 2)
    );
    
    // Ensure size is reasonable (max 500MB for browser)
    const maxSize = 500 * 1024 * 1024 * 8; // 500MB in bits
    this.size = Math.min(this.size, maxSize);
    
    // Calculate optimal number of hash functions: k = (m/n) * ln(2)
    this.hashCount = Math.ceil((this.size / expectedElements) * Math.log(2));
    this.hashCount = Math.max(3, Math.min(this.hashCount, 10)); // Clamp between 3-10
    
    // Initialize bit array (using Uint32Array for efficiency)
    const arraySize = Math.ceil(this.size / 32);
    this.bitArray = new Uint32Array(arraySize);
    
    console.log(`BloomFilter initialized: ${(this.size / 8 / 1024 / 1024).toFixed(2)} MB, ${this.hashCount} hash functions`);
  }

  /**
   * MurmurHash3-inspired hash function
   * Fast, well-distributed hash for strings
   */
  private hash(str: string, seed: number): number {
    let h1 = seed;
    const c1 = 0xcc9e2d51;
    const c2 = 0x1b873593;

    for (let i = 0; i < str.length; i++) {
      let k1 = str.charCodeAt(i);
      k1 = Math.imul(k1, c1);
      k1 = (k1 << 15) | (k1 >>> 17);
      k1 = Math.imul(k1, c2);
      h1 ^= k1;
      h1 = (h1 << 13) | (h1 >>> 19);
      h1 = Math.imul(h1, 5) + 0xe6546b64;
    }

    h1 ^= str.length;
    h1 ^= h1 >>> 16;
    h1 = Math.imul(h1, 0x85ebca6b);
    h1 ^= h1 >>> 13;
    h1 = Math.imul(h1, 0xc2b2ae35);
    h1 ^= h1 >>> 16;

    return Math.abs(h1) % this.size;
  }

  /**
   * Generate multiple hash values using double hashing technique
   * h(i) = h1(x) + i * h2(x) mod m
   */
  private getHashValues(item: string): number[] {
    const hashes: number[] = [];
    const h1 = this.hash(item, 0);
    const h2 = this.hash(item, h1);

    for (let i = 0; i < this.hashCount; i++) {
      hashes.push(Math.abs(h1 + i * h2) % this.size);
    }
    return hashes;
  }

  /**
   * Add an item to the filter
   */
  add(item: string): void {
    const hashes = this.getHashValues(item);
    for (const hash of hashes) {
      const arrayIndex = Math.floor(hash / 32);
      const bitIndex = hash % 32;
      this.bitArray[arrayIndex] |= (1 << bitIndex);
    }
    this.itemCount++;
  }

  /**
   * Check if an item might be in the filter
   * Returns true if possibly present, false if definitely not present
   */
  contains(item: string): boolean {
    const hashes = this.getHashValues(item);
    for (const hash of hashes) {
      const arrayIndex = Math.floor(hash / 32);
      const bitIndex = hash % 32;
      if ((this.bitArray[arrayIndex] & (1 << bitIndex)) === 0) {
        return false; // Definitely not present
      }
    }
    return true; // Possibly present
  }

  /**
   * Get current false positive probability
   */
  getFalsePositiveRate(): number {
    const n = this.itemCount;
    const m = this.size;
    const k = this.hashCount;
    return Math.pow(1 - Math.exp(-k * n / m), k);
  }

  /**
   * Get memory usage in MB
   */
  getMemoryUsageMB(): number {
    return this.bitArray.byteLength / (1024 * 1024);
  }

  /**
   * Get item count
   */
  getItemCount(): number {
    return this.itemCount;
  }

  /**
   * Clear the filter
   */
  clear(): void {
    this.bitArray.fill(0);
    this.itemCount = 0;
  }

  /**
   * Rehydrate from a plain object (for Web Workers)
   */
  static fromObject(obj: any): BloomFilter {
    const filter = Object.create(BloomFilter.prototype);
    Object.assign(filter, obj);
    return filter;
  }
}

/**
 * Counting Bloom Filter - allows deletion and counting
 * Uses 4-bit counters instead of single bits
 */
export class CountingBloomFilter {
  private counters: Uint8Array;
  private size: number;
  private hashCount: number;

  constructor(expectedElements: number, falsePositiveRate: number = 0.001) {
    this.size = Math.ceil(
      (-expectedElements * Math.log(falsePositiveRate)) / (Math.log(2) ** 2)
    );
    
    // Max 200MB for counting filter (uses more memory)
    const maxSize = 200 * 1024 * 1024;
    this.size = Math.min(this.size, maxSize);
    
    this.hashCount = Math.ceil((this.size / expectedElements) * Math.log(2));
    this.hashCount = Math.max(3, Math.min(this.hashCount, 8));
    
    this.counters = new Uint8Array(this.size);
  }

  private hash(str: string, seed: number): number {
    let h = seed;
    for (let i = 0; i < str.length; i++) {
      h = Math.imul(h ^ str.charCodeAt(i), 0x5bd1e995);
      h ^= h >> 15;
    }
    return Math.abs(h) % this.size;
  }

  private getHashValues(item: string): number[] {
    const hashes: number[] = [];
    const h1 = this.hash(item, 0x12345678);
    const h2 = this.hash(item, 0x87654321);
    for (let i = 0; i < this.hashCount; i++) {
      hashes.push(Math.abs(h1 + i * h2) % this.size);
    }
    return hashes;
  }

  add(item: string): void {
    for (const hash of this.getHashValues(item)) {
      if (this.counters[hash] < 255) {
        this.counters[hash]++;
      }
    }
  }

  /**
   * Get minimum count across all hash positions
   * This estimates how many times the item was added
   */
  getCount(item: string): number {
    let minCount = 255;
    for (const hash of this.getHashValues(item)) {
      minCount = Math.min(minCount, this.counters[hash]);
    }
    return minCount;
  }

  contains(item: string): boolean {
    return this.getCount(item) > 0;
  }

  /**
   * Rehydrate from a plain object (for Web Workers)
   */
  static fromObject(obj: any): CountingBloomFilter {
    const filter = Object.create(CountingBloomFilter.prototype);
    Object.assign(filter, obj);
    return filter;
  }
}

/**
 * Partitioned Bloom Filter for very large datasets
 * Divides the bit array into partitions for better cache locality
 */
export class PartitionedBloomFilter {
  private filters: BloomFilter[];
  private partitionCount: number;

  constructor(expectedElements: number, partitionCount: number = 4) {
    this.partitionCount = partitionCount;
    this.filters = [];
    
    const elementsPerPartition = Math.ceil(expectedElements / partitionCount);
    for (let i = 0; i < partitionCount; i++) {
      this.filters.push(new BloomFilter(elementsPerPartition, 0.0001));
    }
  }

  private getPartitionIndex(item: string): number {
    let hash = 0;
    for (let i = 0; i < item.length; i++) {
      hash = ((hash << 5) - hash) + item.charCodeAt(i);
      hash |= 0;
    }
    return Math.abs(hash) % this.partitionCount;
  }

  add(item: string): void {
    const partition = this.getPartitionIndex(item);
    this.filters[partition].add(item);
  }

  contains(item: string): boolean {
    const partition = this.getPartitionIndex(item);
    return this.filters[partition].contains(item);
  }

  getMemoryUsageMB(): number {
    return this.filters.reduce((sum, f) => sum + f.getMemoryUsageMB(), 0);
  }
}
