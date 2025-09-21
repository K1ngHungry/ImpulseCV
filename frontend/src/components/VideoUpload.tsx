import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, Video, FileVideo, X } from 'lucide-react';

interface VideoUploadProps {
  onFileUpload: (file: File) => void;
  uploadedFile: File | null;
  disabled?: boolean;
}

export const VideoUpload: React.FC<VideoUploadProps> = ({
  onFileUpload,
  uploadedFile,
  disabled = false
}) => {
  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      onFileUpload(acceptedFiles[0]);
    }
  }, [onFileUpload]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'video/*': ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv']
    },
    multiple: false,
    disabled
  });

  const handleRemoveFile = () => {
    onFileUpload(null as any);
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="card">
      <div className="card-header">
        <h2 className="text-xl font-semibold text-secondary-900 flex items-center space-x-2">
          <Video className="h-5 w-5 text-primary-600" />
          <span>Video Upload</span>
        </h2>
        <p className="text-sm text-secondary-600 mt-1">
          Upload a video file to analyze ball motion and physics
        </p>
      </div>

      {!uploadedFile ? (
        <div
          {...getRootProps()}
          className={`
            border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors duration-200
            ${isDragActive 
              ? 'border-primary-400 bg-primary-50' 
              : 'border-secondary-300 hover:border-primary-400 hover:bg-primary-50'
            }
            ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
          `}
        >
          <input {...getInputProps()} />
          <div className="flex flex-col items-center space-y-4">
            <div className="bg-primary-100 p-4 rounded-full">
              <Upload className="h-8 w-8 text-primary-600" />
            </div>
            <div>
              <p className="text-lg font-medium text-secondary-900">
                {isDragActive ? 'Drop your video here' : 'Upload Video File'}
              </p>
              <p className="text-sm text-secondary-600 mt-1">
                Drag and drop or click to select
              </p>
            </div>
            <div className="text-xs text-secondary-500">
              Supports MP4, AVI, MOV, MKV, WMV, FLV
            </div>
          </div>
        </div>
      ) : (
        <div className="bg-secondary-50 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="bg-primary-100 p-2 rounded-lg">
                <FileVideo className="h-5 w-5 text-primary-600" />
              </div>
              <div>
                <p className="font-medium text-secondary-900">{uploadedFile.name}</p>
                <p className="text-sm text-secondary-600">
                  {formatFileSize(uploadedFile.size)} • {uploadedFile.type}
                </p>
              </div>
            </div>
            {!disabled && (
              <button
                onClick={handleRemoveFile}
                className="text-secondary-400 hover:text-red-500 transition-colors duration-200"
              >
                <X className="h-5 w-5" />
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
