import React from 'react';
import { AnalysisData } from '../types';

interface StatisticsPanelProps {
  data: AnalysisData | null;
}

export const StatisticsPanel: React.FC<StatisticsPanelProps> = ({ data }) => {
  if (!data) {
    return (
      <div className="bg-secondary-100 rounded-lg p-8 text-center">
        <p className="text-secondary-600">No statistics available</p>
      </div>
    );
  }

  return (
    <div className="bg-secondary-100 rounded-lg p-6">
      <h3 className="text-lg font-semibold text-secondary-900 mb-4">Analysis Statistics</h3>
      
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-white rounded-lg p-4">
          <h4 className="font-medium text-secondary-900">Total Frames</h4>
          <p className="text-2xl font-bold text-primary-600">{data.frames}</p>
        </div>
        
        <div className="bg-white rounded-lg p-4">
          <h4 className="font-medium text-secondary-900">Duration</h4>
          <p className="text-2xl font-bold text-primary-600">{data.duration.toFixed(1)}s</p>
        </div>
        
        <div className="bg-white rounded-lg p-4">
          <h4 className="font-medium text-secondary-900">FPS</h4>
          <p className="text-2xl font-bold text-primary-600">{data.fps.toFixed(1)}</p>
        </div>
        
        <div className="bg-white rounded-lg p-4">
          <h4 className="font-medium text-secondary-900">Tracks</h4>
          <p className="text-2xl font-bold text-primary-600">{data.trackIds.length}</p>
        </div>
      </div>
    </div>
  );
};