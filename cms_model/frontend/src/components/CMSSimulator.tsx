import React, { useState } from 'react';

interface CMSResult {
  originalSequence: string;
  modifiedDisplay: string;
  modificationType: string;
  modifiedPositions: number[];
  numModified: number;
  modificationDensity: number;
  isOverModified: boolean;
  stabilityHalfLife: number;
  ago2Affinity: number;
  immuneSuppression: number;
  therapeuticIndex: number;
  warnings: string[];
  aiOptimized?: boolean;
  modifications?: Record<number, string>;
  searchStats?: {
    totalIterations: number;
    layoutsEvaluated: number;
    bestModType: string;
    bestTherapeuticIndex: number;
  };
}

interface CMSSimulatorProps {
  apiUrl?: string;
}

const CMSSimulator: React.FC<CMSSimulatorProps> = ({ apiUrl = '/api/chem_modify' }) => {
  const [sequence, setSequence] = useState<string>('GUCAUCACGGUGUACCUCAUU');
  const [modType, setModType] = useState<string>('2_ome');
  const [modPositions, setModPositions] = useState<string>('');
  const [useAIOptimization, setUseAIOptimization] = useState<boolean>(true);
  const [loading, setLoading] = useState<boolean>(false);
  const [result, setResult] = useState<CMSResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const modTypes = [
    { value: '2_ome', label: "2'-O-Methyl (2'-OMe)", color: '#3b82f6' },
    { value: '2_f', label: "2'-Fluoro (2'-F)", color: '#f97316' },
    { value: 'ps', label: 'Phosphorothioate (PS)', color: '#a855f7' },
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const positions = modPositions
        ? modPositions.split(',').map(p => parseInt(p.trim())).filter(p => !isNaN(p))
        : null;

      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          sequence: sequence.toUpperCase().replace(/T/g, 'U'),
          modType,
          positions,
          useAIOptimization,
        }),
      });

      if (!response.ok) {
        throw new Error('API request failed');
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const getEfficacyColor = (ti: number): string => {
    if (ti >= 70) return 'text-green-400';
    if (ti >= 50) return 'text-yellow-400';
    if (ti >= 30) return 'text-orange-400';
    return 'text-red-400';
  };

  const getEfficacyLabel = (ti: number): string => {
    if (ti >= 70) return 'Excellent';
    if (ti >= 50) return 'Good';
    if (ti >= 30) return 'Moderate';
    return 'Poor';
  };

  return (
    <div className="bg-gray-900 text-white rounded-xl p-6 max-w-4xl mx-auto">
      <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
        <span className="text-2xl">🧪</span>
        AI Chemical Modification Simulator (CMS)
      </h2>
      <p className="text-gray-400 mb-6">
        Predict optimal chemical modification patterns for enhanced siRNA therapeutics.
      </p>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-2">
              siRNA Sequence (19-21 nt)
            </label>
            <input
              type="text"
              value={sequence}
              onChange={(e) => setSequence(e.target.value)}
              placeholder="Enter siRNA sequence..."
              className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg 
                         focus:ring-2 focus:ring-blue-500 focus:border-transparent
                         font-mono text-sm"
              maxLength={21}
            />
            <p className="text-xs text-gray-500 mt-1">
              Use A, U, C, G (T will be converted to U)
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">
              Modification Type
            </label>
            <select
              value={modType}
              onChange={(e) => setModType(e.target.value)}
              className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg 
                         focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              {modTypes.map((type) => (
                <option key={type.value} value={type.value}>
                  {type.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-2">
              Custom Positions (optional)
            </label>
            <input
              type="text"
              value={modPositions}
              onChange={(e) => setModPositions(e.target.value)}
              placeholder="e.g., 0,2,4,14,16,18"
              className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg 
                         focus:ring-2 focus:ring-blue-500 focus:border-transparent
                         font-mono text-sm"
            />
            <p className="text-xs text-gray-500 mt-1">
              Leave empty for auto-selection. Comma-separated 0-indexed positions.
            </p>
          </div>

          <div className="flex items-center">
            <label className="flex items-center gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={useAIOptimization}
                onChange={(e) => setUseAIOptimization(e.target.checked)}
                className="w-5 h-5 rounded bg-gray-800 border-gray-700 
                           text-blue-500 focus:ring-blue-500"
              />
              <span className="text-sm font-medium">
                Enable AI Monte-Carlo Optimization (2000 iterations)
              </span>
            </label>
          </div>
        </div>

        <button
          type="submit"
          disabled={loading || sequence.length < 19}
          className="w-full py-3 px-6 bg-gradient-to-r from-blue-600 to-purple-600 
                     hover:from-blue-700 hover:to-purple-700 
                     disabled:opacity-50 disabled:cursor-not-allowed
                     rounded-lg font-semibold transition-all duration-200
                     flex items-center justify-center gap-2"
        >
          {loading ? (
            <>
              <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" 
                        stroke="currentColor" strokeWidth="4" fill="none" />
                <path className="opacity-75" fill="currentColor" 
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
              </svg>
              Optimizing...
            </>
          ) : (
            <>
              <span>🧬</span>
              {useAIOptimization ? 'AI Optimize Modifications' : 'Apply Modifications'}
            </>
          )}
        </button>
      </form>

      {error && (
        <div className="mt-4 p-4 bg-red-900/50 border border-red-700 rounded-lg">
          <p className="text-red-400">Error: {error}</p>
        </div>
      )}

      {result && (
        <div className="mt-6 space-y-4">
          {/* Sequence Display */}
          <div className="bg-gray-800 rounded-lg p-4">
            <h3 className="text-lg font-semibold mb-3">Modification Pattern</h3>
            <div className="font-mono text-sm">
              <p className="text-gray-400 mb-2">
                <span className="font-bold">Original:</span> {result.originalSequence}
              </p>
              <p className="mb-2">
                <span className="font-bold">Modified:</span>{' '}
                {result.modifiedDisplay.split('').map((char, i) => {
                  const isModified = char.includes('*');
                  const color = result.modifications?.[i] === '2_ome' ? 'text-blue-400' :
                               result.modifications?.[i] === '2_f' ? 'text-orange-400' :
                               result.modifications?.[i] === 'ps' ? 'text-purple-400' :
                               isModified ? 'text-green-400' : 'text-gray-300';
                  return <span key={i} className={color}>{char}</span>;
                })}
              </p>
              <div className="flex flex-wrap gap-2 mt-2">
                {modTypes.map((type) => (
                  <span key={type.value} 
                        className="px-2 py-1 rounded text-xs font-medium"
                        style={{ backgroundColor: type.color + '33', color: type.color }}>
                    {type.label}
                  </span>
                ))}
              </div>
            </div>
          </div>

          {/* Metrics Grid */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <MetricCard
              title="Stability Half-Life"
              value={`${result.stabilityHalfLife.toFixed(1)}h`}
              subtitle="in serum"
              color="blue"
            />
            <MetricCard
              title="Ago2 Binding"
              value={`${result.ago2Affinity.toFixed(1)}%`}
              subtitle="RISC loading"
              color="green"
            />
            <MetricCard
              title="Immune Suppression"
              value={`${result.immuneSuppression.toFixed(1)}%`}
              subtitle="TLR reduction"
              color="purple"
            />
            <MetricCard
              title="Therapeutic Index"
              value={`${result.therapeuticIndex.toFixed(1)}`}
              subtitle={getEfficacyLabel(result.therapeuticIndex)}
              color={result.therapeuticIndex >= 50 ? 'green' : 'orange'}
            />
          </div>

          {/* Additional Info */}
          <div className="bg-gray-800 rounded-lg p-4">
            <h3 className="text-lg font-semibold mb-3">Details</h3>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
              <div>
                <span className="text-gray-400">Positions Modified:</span>
                <span className="ml-2 font-mono">{result.modifiedPositions.join(', ')}</span>
              </div>
              <div>
                <span className="text-gray-400">Modification Density:</span>
                <span className="ml-2">{result.modificationDensity.toFixed(1)}%</span>
              </div>
              <div>
                <span className="text-gray-400">Num Modified:</span>
                <span className="ml-2">{result.numModified}</span>
              </div>
            </div>
          </div>

          {/* AI Stats */}
          {result.aiOptimized && result.searchStats && (
            <div className="bg-blue-900/30 border border-blue-700 rounded-lg p-4">
              <h3 className="text-lg font-semibold mb-2 flex items-center gap-2">
                <span>🤖</span> AI Optimization Complete
              </h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div>
                  <span className="text-gray-400">Iterations:</span>
                  <span className="ml-2 font-bold">{result.searchStats.totalIterations.toLocaleString()}</span>
                </div>
                <div>
                  <span className="text-gray-400">Evaluated:</span>
                  <span className="ml-2 font-bold">{result.searchStats.layoutsEvaluated.toLocaleString()}</span>
                </div>
                <div>
                  <span className="text-gray-400">Best Type:</span>
                  <span className="ml-2">{result.searchStats.bestModType}</span>
                </div>
                <div>
                  <span className="text-gray-400">Best TI:</span>
                  <span className={`ml-2 font-bold ${getEfficacyColor(result.searchStats.bestTherapeuticIndex)}`}>
                    {result.searchStats.bestTherapeuticIndex.toFixed(1)}
                  </span>
                </div>
              </div>
            </div>
          )}

          {/* Warnings */}
          {result.warnings && result.warnings.length > 0 && (
            <div className="space-y-2">
              {result.warnings.map((warning, i) => (
                <div
                  key={i}
                  className={`p-3 rounded-lg text-sm ${
                    warning.includes('CRITICAL') ? 'bg-red-900/50 border border-red-700' :
                    warning.includes('CAUTION') || warning.includes('WARNING') ? 
                    'bg-yellow-900/50 border border-yellow-700' :
                    'bg-green-900/50 border border-green-700'
                  }`}
                >
                  {warning}
                </div>
              ))}
            </div>
          )}

          {/* Recommendation */}
          <div className="bg-gradient-to-r from-gray-800 to-gray-900 rounded-lg p-4">
            <h3 className="text-lg font-semibold mb-2">Recommendation</h3>
            <p className={getEfficacyColor(result.therapeuticIndex)}>
              {result.therapeuticIndex >= 70 
                ? '✅ Excellent candidate for in vivo application. High stability with maintained activity.'
                : result.therapeuticIndex >= 50
                ? '⚠️ Good candidate. Consider further optimization of modification positions.'
                : result.therapeuticIndex >= 30
                ? '⚠️ Moderate candidate. Review modification positions and consider alternative types.'
                : '❌ Poor candidate. Cleavage zone violation or excessive activity loss. Redesign recommended.'}
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

interface MetricCardProps {
  title: string;
  value: string;
  subtitle: string;
  color: 'blue' | 'green' | 'purple' | 'orange' | 'red';
}

const MetricCard: React.FC<MetricCardProps> = ({ title, value, subtitle, color }) => {
  const colorClasses = {
    blue: 'border-blue-500 bg-blue-900/20',
    green: 'border-green-500 bg-green-900/20',
    purple: 'border-purple-500 bg-purple-900/20',
    orange: 'border-orange-500 bg-orange-900/20',
    red: 'border-red-500 bg-red-900/20',
  };

  return (
    <div className={`rounded-lg p-4 border-2 ${colorClasses[color]}`}>
      <p className="text-xs text-gray-400 uppercase tracking-wide">{title}</p>
      <p className="text-2xl font-bold mt-1">{value}</p>
      <p className="text-xs text-gray-500">{subtitle}</p>
    </div>
  );
};

export default CMSSimulator;
