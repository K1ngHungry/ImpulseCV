import React, { useState } from 'react';
import { BarChart3, Download, RotateCcw, AlertCircle, CheckCircle, Loader, Video } from 'lucide-react';
import { AnalysisData, AnalysisStatus } from '../types';
import { TrajectoryChart } from './TrajectoryChart';
import { StatisticsPanel } from './StatisticsPanel';
import { VideoPlayer } from './VideoPlayer';

interface AnalysisResultsProps {
  analysisData: AnalysisData | null;
  analysisStatus: AnalysisStatus;
  uploadedFile: File | null;
  onReset: () => void;
}

export const AnalysisResults: React.FC<AnalysisResultsProps> = ({
  analysisData,
  analysisStatus,
  uploadedFile,
  onReset
}) => {
  const [currentVideoTime, setCurrentVideoTime] = useState(0);
  const handleDownloadCSV = () => {
    if (!analysisData) return;
    
    // Convert analysis data to CSV format
    const csvContent = [
      'frame,time_s,track_id,class_id,class_name,conf,x1,y1,x2,y2,cx,cy,vx,vy,velocity',
      ...analysisData.trajectory.map(point => 
        `${point.frame},${point.time},${point.trackId},32,sports ball,${point.confidence},${point.x-25},${point.y-25},${point.x+25},${point.y+25},${point.x},${point.y},${point.vx || 0},${point.vy || 0},${point.velocity || 0}`
      )
    ].join('\n');
    
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'analysis_results.csv';
    a.click();
    window.URL.revokeObjectURL(url);
  };

  const renderStatusContent = () => {
    switch (analysisStatus) {
      case 'processing':
        return (
          <div className="text-center py-12">
            <div className="bg-primary-100 p-4 rounded-full w-16 h-16 mx-auto mb-4 animate-pulse-slow">
              <Loader className="h-8 w-8 text-primary-600 animate-spin" />
            </div>
            <h3 className="text-lg font-semibold text-secondary-900 mb-2">
              Analyzing Video
            </h3>
            <p className="text-secondary-600">
              Processing frames and tracking objects...
            </p>
            <div className="mt-4 bg-secondary-100 rounded-full h-2">
              <div className="bg-primary-600 h-2 rounded-full animate-pulse" style={{ width: '60%' }}></div>
            </div>
          </div>
        );
        
      case 'error':
        return (
          <div className="text-center py-12">
            <div className="bg-red-100 p-4 rounded-full w-16 h-16 mx-auto mb-4">
              <AlertCircle className="h-8 w-8 text-red-600" />
            </div>
            <h3 className="text-lg font-semibold text-secondary-900 mb-2">
              Analysis Failed
            </h3>
            <p className="text-secondary-600 mb-4">
              There was an error processing your video. Please try again.
            </p>
            <button onClick={onReset} className="btn-secondary">
              Try Again
            </button>
          </div>
        );
        
      case 'completed':
        return (
          <div className="space-y-6">
            {/* Success Header */}
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className="bg-green-100 p-2 rounded-lg">
                  <CheckCircle className="h-6 w-6 text-green-600" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-secondary-900">
                    Analysis Complete
                  </h3>
                  <p className="text-sm text-secondary-600">
                    {analysisData?.frames} frames processed
                  </p>
                </div>
              </div>
              
              <div className="flex space-x-2">
                <button
                  onClick={handleDownloadCSV}
                  className="btn-secondary flex items-center space-x-2"
                >
                  <Download className="h-4 w-4" />
                  <span>CSV</span>
                </button>
                <button onClick={onReset} className="btn-secondary flex items-center space-x-2">
                  <RotateCcw className="h-4 w-4" />
                  <span>Reset</span>
                </button>
              </div>
            </div>

            {/* Video Player with Tracking */}
            {uploadedFile && (
              <div>
                <h4 className="text-md font-medium text-secondary-900 mb-3 flex items-center space-x-2">
                  <Video className="h-4 w-4 text-primary-600" />
                  <span>Video with Tracking Overlay</span>
                </h4>
                <VideoPlayer
                  videoFile={uploadedFile}
                  analysisData={analysisData}
                  isPlaying={false}
                  onPlayPause={() => {}}
                  onSeek={setCurrentVideoTime}
                />
              </div>
            )}

            {/* Trajectory Visualization */}
            <div>
              <h4 className="text-md font-medium text-secondary-900 mb-3 flex items-center space-x-2">
                <BarChart3 className="h-4 w-4 text-primary-600" />
                <span>Trajectory Visualization</span>
              </h4>
              <TrajectoryChart data={analysisData} />
            </div>

            {/* Statistics */}
            <StatisticsPanel data={analysisData} />
          </div>
        );
        
      default:
        return (
          <div className="text-center py-12">
            <div className="bg-secondary-100 p-4 rounded-full w-16 h-16 mx-auto mb-4">
              <BarChart3 className="h-8 w-8 text-secondary-600" />
            </div>
            <h3 className="text-lg font-semibold text-secondary-900 mb-2">
              Ready for Analysis
            </h3>
            <p className="text-secondary-600">
              Upload a video and configure settings to begin tracking analysis
            </p>
          </div>
        );
    }
  };

  return (
    <div className="card">
      <div className="card-header">
        <h2 className="text-xl font-semibold text-secondary-900">
          Analysis Results
        </h2>
        <p className="text-sm text-secondary-600 mt-1">
          View trajectory visualization and physics statistics
        </p>
      </div>

      <div className="min-h-[600px]">
        {renderStatusContent()}
      </div>
    </div>
  );
};
