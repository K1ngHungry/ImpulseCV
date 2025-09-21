import React, { useState } from 'react';
import { Settings, Play, Target, Ruler, Weight } from 'lucide-react';
import { AnalysisConfig as AnalysisConfigType } from '../types';

interface AnalysisConfigProps {
  onStartAnalysis: (config: AnalysisConfigType) => void;
  disabled?: boolean;
}

const OBJECT_CLASSES = [
  { id: 32, name: 'sports ball', description: 'Sports balls (basketball, soccer, etc.)' },
  { id: 0, name: 'person', description: 'Human person' },
  { id: 1, name: 'bicycle', description: 'Bicycle' },
  { id: 2, name: 'car', description: 'Automobile' },
  { id: 39, name: 'bottle', description: 'Bottle' },
];

export const AnalysisConfig: React.FC<AnalysisConfigProps> = ({
  onStartAnalysis,
  disabled = false
}) => {
  const [config, setConfig] = useState<AnalysisConfigType>({
    confidence: 0.15,
    objectClass: 32,
    pixelsPerMeter: undefined,
    objectMass: undefined,
    inputSize: 960,
    iouThreshold: 0.5
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onStartAnalysis(config);
  };

  const updateConfig = (key: keyof AnalysisConfigType, value: any) => {
    setConfig(prev => ({ ...prev, [key]: value }));
  };

  return (
    <div className="card">
      <div className="card-header">
        <h2 className="text-xl font-semibold text-secondary-900 flex items-center space-x-2">
          <Settings className="h-5 w-5 text-primary-600" />
          <span>Analysis Configuration</span>
        </h2>
        <p className="text-sm text-secondary-600 mt-1">
          Configure detection parameters for optimal tracking results
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Object Class Selection */}
        <div>
          <label className="block text-sm font-medium text-secondary-700 mb-2 flex items-center space-x-2">
            <Target className="h-4 w-4" />
            <span>Object Class</span>
          </label>
          <select
            value={config.objectClass}
            onChange={(e) => updateConfig('objectClass', parseInt(e.target.value))}
            className="input-field"
            disabled={disabled}
          >
            {OBJECT_CLASSES.map(cls => (
              <option key={cls.id} value={cls.id}>
                {cls.name} - {cls.description}
              </option>
            ))}
          </select>
        </div>

        {/* Confidence Threshold */}
        <div>
          <label className="block text-sm font-medium text-secondary-700 mb-2">
            Confidence Threshold
          </label>
          <div className="flex items-center space-x-4">
            <input
              type="range"
              min="0.1"
              max="1.0"
              step="0.05"
              value={config.confidence}
              onChange={(e) => updateConfig('confidence', parseFloat(e.target.value))}
              className="flex-1"
              disabled={disabled}
            />
            <span className="text-sm font-medium text-secondary-900 w-12">
              {config.confidence.toFixed(2)}
            </span>
          </div>
          <p className="text-xs text-secondary-500 mt-1">
            Lower values detect more objects but may include false positives
          </p>
        </div>

        {/* Input Size */}
        <div>
          <label className="block text-sm font-medium text-secondary-700 mb-2">
            Input Size (pixels)
          </label>
          <select
            value={config.inputSize}
            onChange={(e) => updateConfig('inputSize', parseInt(e.target.value))}
            className="input-field"
            disabled={disabled}
          >
            <option value={640}>640px - Fast</option>
            <option value={736}>736px - Balanced</option>
            <option value={960}>960px - Accurate (Recommended)</option>
            <option value={1280}>1280px - High Quality</option>
          </select>
          <p className="text-xs text-secondary-500 mt-1">
            Larger sizes improve accuracy but slow down processing
          </p>
        </div>

        {/* IoU Threshold */}
        <div>
          <label className="block text-sm font-medium text-secondary-700 mb-2">
            IoU Threshold
          </label>
          <div className="flex items-center space-x-4">
            <input
              type="range"
              min="0.1"
              max="1.0"
              step="0.1"
              value={config.iouThreshold}
              onChange={(e) => updateConfig('iouThreshold', parseFloat(e.target.value))}
              className="flex-1"
              disabled={disabled}
            />
            <span className="text-sm font-medium text-secondary-900 w-12">
              {config.iouThreshold.toFixed(1)}
            </span>
          </div>
          <p className="text-xs text-secondary-500 mt-1">
            Controls overlap detection for non-maximum suppression
          </p>
        </div>

        {/* Optional: Real-world Scaling */}
        <div className="border-t border-secondary-200 pt-4">
          <h3 className="text-sm font-medium text-secondary-700 mb-3 flex items-center space-x-2">
            <Ruler className="h-4 w-4" />
            <span>Real-world Scaling (Optional)</span>
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-secondary-700 mb-2">
                Pixels per Meter
              </label>
              <input
                type="number"
                placeholder="e.g., 100"
                value={config.pixelsPerMeter || ''}
                onChange={(e) => updateConfig('pixelsPerMeter', e.target.value ? parseFloat(e.target.value) : undefined)}
                className="input-field"
                disabled={disabled}
              />
              <p className="text-xs text-secondary-500 mt-1">
                For real-world measurements
              </p>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-secondary-700 mb-2 flex items-center space-x-1">
                <Weight className="h-4 w-4" />
                <span>Object Mass (kg)</span>
              </label>
              <input
                type="number"
                step="0.1"
                placeholder="e.g., 0.45"
                value={config.objectMass || ''}
                onChange={(e) => updateConfig('objectMass', e.target.value ? parseFloat(e.target.value) : undefined)}
                className="input-field"
                disabled={disabled}
              />
              <p className="text-xs text-secondary-500 mt-1">
                For force calculations
              </p>
            </div>
          </div>
        </div>

        {/* Start Analysis Button */}
        <button
          type="submit"
          disabled={disabled}
          className="w-full btn-primary flex items-center justify-center space-x-2 py-3"
        >
          <Play className="h-5 w-5" />
          <span>{disabled ? 'Processing...' : 'Start Analysis'}</span>
        </button>
      </form>
    </div>
  );
};
