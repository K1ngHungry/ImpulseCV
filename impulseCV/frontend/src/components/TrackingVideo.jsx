import React, { useState } from 'react'

const TrackingVideo = ({ videoPath, title }) => {
  const [isPlaying, setIsPlaying] = useState(false)

  if (!videoPath) {
    return (
      <div className="text-center py-12">
        <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
          </svg>
        </div>
        <h3 className="text-lg font-semibold text-gray-900 mb-2">No Tracking Video</h3>
        <p className="text-gray-600">Process a video to see AI object tracking visualization</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-xl font-semibold text-gray-900">{title}</h3>
        <div className="flex items-center space-x-2 text-sm text-gray-600">
          <div className="w-2 h-2 bg-green-500 rounded-full"></div>
          <span>AI Tracking Active</span>
        </div>
      </div>

      <div className="relative bg-black rounded-lg overflow-hidden shadow-lg">
        <video
          className="w-full h-auto"
          controls
          preload="metadata"
          onPlay={() => setIsPlaying(true)}
          onPause={() => setIsPlaying(false)}
          onEnded={() => setIsPlaying(false)}
        >
          <source src={`http://localhost:8000/${videoPath}`} type="video/mp4" />
          Your browser does not support the video tag.
        </video>

        {/* Overlay Info */}
        <div className="absolute top-4 left-4 bg-black bg-opacity-75 text-white px-3 py-1 rounded-lg text-sm">
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
            <span>Live Tracking</span>
          </div>
        </div>

        {/* Play Button Overlay */}
        {!isPlaying && (
          <div className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-20">
            <div className="w-16 h-16 bg-white bg-opacity-90 rounded-full flex items-center justify-center cursor-pointer hover:bg-opacity-100 transition-all">
              <svg className="w-6 h-6 text-gray-900 ml-1" fill="currentColor" viewBox="0 0 24 24">
                <path d="M8 5v14l11-7z"/>
              </svg>
            </div>
          </div>
        )}
      </div>

      <div className="bg-blue-50 rounded-lg p-4">
        <div className="flex items-start space-x-3">
          <div className="w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
            <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div>
            <h4 className="font-semibold text-blue-900 mb-1">AI Object Tracking Features</h4>
            <ul className="text-sm text-blue-800 space-y-1">
              <li>• Real-time bounding box detection</li>
              <li>• Trajectory path visualization</li>
              <li>• Track ID consistency across frames</li>
              <li>• Confidence score display</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}

export default TrackingVideo
