import React, { useState, useCallback } from 'react'

const VideoUpload = ({ onUpload, isProcessing }) => {
  const [dragActive, setDragActive] = useState(false)
  const [uploadedFiles, setUploadedFiles] = useState([])

  const handleDrag = useCallback((e) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true)
    } else if (e.type === "dragleave") {
      setDragActive(false)
    }
  }, [])

  const handleDrop = useCallback((e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0]
      if (file.type.startsWith('video/')) {
        setUploadedFiles([file])
        onUpload(file)
      }
    }
  }, [onUpload])

  const handleChange = useCallback((e) => {
    e.preventDefault()
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0]
      if (file.type.startsWith('video/')) {
        setUploadedFiles([file])
        onUpload(file)
      }
    }
  }, [onUpload])

  const handleFileClick = (fileName) => {
    onUpload({ name: fileName })
  }

  const availableVideos = [
    'ball-in.mp4',
    'teddy.mp4'
  ]

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">
          Upload Your Video
        </h2>
        <p className="text-gray-600">
          Upload a video or select from our sample videos to analyze object motion
        </p>
      </div>

      {/* Drag & Drop Upload */}
      <div
        className={`relative border-2 border-dashed rounded-xl p-8 text-center transition-colors ${
          dragActive
            ? 'border-primary-500 bg-primary-50'
            : 'border-gray-300 hover:border-gray-400'
        } ${isProcessing ? 'opacity-50 pointer-events-none' : ''}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <input
          type="file"
          accept="video/*"
          onChange={handleChange}
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
          disabled={isProcessing}
        />
        
        <div className="space-y-4">
          <div className="mx-auto w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center">
            <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
            </svg>
          </div>
          
          <div>
            <p className="text-lg font-medium text-gray-900">
              {dragActive ? 'Drop your video here' : 'Drag & drop your video here'}
            </p>
            <p className="text-gray-500">
              or click to browse files
            </p>
          </div>
          
          <p className="text-sm text-gray-400">
            Supports MP4, AVI, MOV, and other video formats
          </p>
        </div>
      </div>

      {/* Sample Videos */}
      <div className="border-t border-gray-200 pt-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Or try our sample videos:
        </h3>
        
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {availableVideos.map((video) => (
            <button
              key={video}
              onClick={() => handleFileClick(video)}
              disabled={isProcessing}
              className={`p-4 border rounded-lg text-left transition-all ${
                isProcessing
                  ? 'opacity-50 cursor-not-allowed'
                  : 'hover:border-primary-500 hover:bg-primary-50 cursor-pointer'
              }`}
            >
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center">
                  <svg className="w-5 h-5 text-red-600" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M8 5v14l11-7z"/>
                  </svg>
                </div>
                <div>
                  <p className="font-medium text-gray-900">{video}</p>
                  <p className="text-sm text-gray-500">Sample video</p>
                </div>
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Uploaded Files */}
      {uploadedFiles.length > 0 && (
        <div className="border-t border-gray-200 pt-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Uploaded Files:
          </h3>
          {uploadedFiles.map((file, index) => (
            <div key={index} className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
              <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
                <svg className="w-4 h-4 text-blue-600" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M8 5v14l11-7z"/>
                </svg>
              </div>
              <div className="flex-1">
                <p className="font-medium text-gray-900">{file.name}</p>
                <p className="text-sm text-gray-500">
                  {(file.size / (1024 * 1024)).toFixed(2)} MB
                </p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default VideoUpload
