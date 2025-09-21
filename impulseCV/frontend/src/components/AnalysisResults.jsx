import React from 'react'

const AnalysisResults = ({ status, apiBaseUrl }) => {
  const { trajectory_analysis, physics_insights, csv_file } = status

  const downloadCSV = () => {
    if (csv_file) {
      window.open(`${apiBaseUrl}/download/${csv_file}`, '_blank')
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-xl font-semibold text-gray-900">Analysis Results</h3>
        {csv_file && (
          <button
            onClick={downloadCSV}
            className="btn-primary text-sm"
          >
            <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            Download CSV
          </button>
        )}
      </div>

      {/* Trajectory Analysis */}
      {trajectory_analysis && Object.keys(trajectory_analysis).length > 0 && (
        <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg p-6">
          <h4 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <svg className="w-5 h-5 mr-2 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            Trajectory Analysis
          </h4>
          
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {Object.entries(trajectory_analysis).map(([key, value]) => (
              <div key={key} className="bg-white rounded-lg p-4 shadow-sm">
                <div className="text-sm font-medium text-gray-500 mb-1">
                  {key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                </div>
                <div className="text-lg font-semibold text-gray-900">
                  {typeof value === 'number' ? value.toFixed(3) : value}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Physics Insights */}
      {physics_insights && Object.keys(physics_insights).length > 0 && (
        <div className="bg-gradient-to-r from-green-50 to-teal-50 rounded-lg p-6">
          <h4 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <svg className="w-5 h-5 mr-2 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
            Physics Insights
          </h4>
          
          <div className="space-y-4">
            {Object.entries(physics_insights).map(([key, value]) => (
              <div key={key} className="bg-white rounded-lg p-4 shadow-sm">
                <div className="text-sm font-medium text-gray-500 mb-2">
                  {key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                </div>
                <div className="text-gray-900">
                  {typeof value === 'string' ? value : JSON.stringify(value)}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Summary Stats */}
      <div className="bg-gray-50 rounded-lg p-6">
        <h4 className="text-lg font-semibold text-gray-900 mb-4">Analysis Summary</h4>
        
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">
              {status.data_points || 0}
            </div>
            <div className="text-sm text-gray-600">Data Points</div>
          </div>
          
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">
              {trajectory_analysis?.max_speed ? trajectory_analysis.max_speed.toFixed(2) : '0.00'}
            </div>
            <div className="text-sm text-gray-600">Max Speed (m/s)</div>
          </div>
          
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-600">
              {trajectory_analysis?.max_acceleration ? trajectory_analysis.max_acceleration.toFixed(2) : '0.00'}
            </div>
            <div className="text-sm text-gray-600">Max Acceleration (m/s²)</div>
          </div>
          
          <div className="text-center">
            <div className="text-2xl font-bold text-orange-600">
              {trajectory_analysis?.total_distance ? trajectory_analysis.total_distance.toFixed(2) : '0.00'}
            </div>
            <div className="text-sm text-gray-600">Distance (m)</div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default AnalysisResults
