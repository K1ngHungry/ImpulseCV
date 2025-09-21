import React from 'react'

const ProcessingStatus = ({ status }) => {
  const isProcessing = status.status === 'processing'
  const isCompleted = status.status === 'completed'
  const hasError = status.status === 'error'

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-xl font-semibold text-gray-900">
          Processing Status
        </h3>
        <div className={`px-3 py-1 rounded-full text-sm font-medium ${
          isProcessing 
            ? 'bg-yellow-100 text-yellow-800' 
            : isCompleted 
            ? 'bg-green-100 text-green-800'
            : hasError
            ? 'bg-red-100 text-red-800'
            : 'bg-gray-100 text-gray-800'
        }`}>
          {isProcessing && 'Processing'}
          {isCompleted && 'Completed'}
          {hasError && 'Error'}
          {status.status === 'idle' && 'Ready'}
        </div>
      </div>

      <p className="text-gray-600">{status.message}</p>

      {isProcessing && (
        <div className="space-y-3">
          <div className="flex justify-between text-sm text-gray-600">
            <span>Progress</span>
            <span>{status.progress || 0}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-gradient-to-r from-blue-500 to-purple-600 h-2 rounded-full transition-all duration-300 ease-out"
              style={{ width: `${status.progress || 0}%` }}
            />
          </div>
        </div>
      )}

      {isCompleted && (
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mt-6">
          <div className="bg-blue-50 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-blue-600">
              {status.data_points || 0}
            </div>
            <div className="text-sm text-blue-600">Data Points</div>
          </div>
          
          <div className="bg-green-50 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-green-600">
              {status.plots ? Object.keys(status.plots).length : 0}
            </div>
            <div className="text-sm text-green-600">Charts Generated</div>
          </div>
          
          <div className="bg-purple-50 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-purple-600">
              {status.tracking_video ? '1' : '0'}
            </div>
            <div className="text-sm text-purple-600">Tracking Videos</div>
          </div>
        </div>
      )}

      {hasError && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center space-x-2">
            <svg className="w-5 h-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span className="text-red-800 font-medium">Processing Error</span>
          </div>
          <p className="text-red-700 mt-1">{status.message}</p>
        </div>
      )}
    </div>
  )
}

export default ProcessingStatus
