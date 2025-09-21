import React from 'react';
import { AnalysisData } from '../types';

interface TrajectoryChartProps {
  data: AnalysisData | null;
}

export const TrajectoryChart: React.FC<TrajectoryChartProps> = ({ data }) => {
  if (!data) {
    return (
      <div className="bg-secondary-100 rounded-lg p-8 text-center">
        <p className="text-secondary-600">No trajectory data available</p>
      </div>
    );
  }

  return (
    <div className="bg-secondary-100 rounded-lg p-8 text-center">
      <h3 className="text-lg font-semibold text-secondary-900 mb-4">Trajectory Chart</h3>
      <p className="text-secondary-600">
        {data.trajectory.length} trajectory points analyzed
      </p>
      <p className="text-secondary-500 text-sm mt-2">
        Chart visualization coming soon...
      </p>
    </div>
  );
};