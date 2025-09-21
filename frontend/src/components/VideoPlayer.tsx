import React, { useRef, useEffect, useState } from 'react';
import { Play, Pause, RotateCcw, Volume2, VolumeX, Maximize } from 'lucide-react';

interface VideoPlayerProps {
  videoFile: File | null;
  analysisData: any;
  isPlaying: boolean;
  onPlayPause: () => void;
  onSeek: (time: number) => void;
}

export const VideoPlayer: React.FC<VideoPlayerProps> = ({
  videoFile,
  analysisData,
  isPlaying,
  onPlayPause,
  onSeek
}) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(1);
  const [isMuted, setIsMuted] = useState(false);
  const [showTracking, setShowTracking] = useState(false); // Start with tracking disabled to test video playback
  const [isLoading, setIsLoading] = useState(true);
  const [hasError, setHasError] = useState(false);
  const [isVideoPlaying, setIsVideoPlaying] = useState(false);

  // Create video URL from file
  const videoUrl = videoFile ? URL.createObjectURL(videoFile) : null;
  
  // Debug logging
  console.log('VideoPlayer: videoFile =', videoFile?.name);
  console.log('VideoPlayer: videoUrl =', videoUrl);
  console.log('VideoPlayer: analysisData =', analysisData);

  // Cleanup video URL on unmount
  useEffect(() => {
    return () => {
      if (videoUrl) {
        URL.revokeObjectURL(videoUrl);
      }
    };
  }, [videoUrl]);

  // Handle video events
  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;

    const handleTimeUpdate = () => {
      setCurrentTime(video.currentTime);
      onSeek(video.currentTime);
      
      // Debug: Log when we're near the end of analysis data
      if (analysisData && analysisData.trajectory.length > 0) {
        const lastAnalysisTime = Math.max(...analysisData.trajectory.map((p: any) => p.time));
        if (video.currentTime > lastAnalysisTime - 0.1) {
          console.log(`Video time: ${video.currentTime.toFixed(2)}s, Last analysis time: ${lastAnalysisTime.toFixed(2)}s`);
        }
      }
    };

    const handleLoadedMetadata = () => {
      setDuration(video.duration);
      setIsLoading(false);
      setHasError(false);
      
      // Debug: Compare video duration with analysis duration
      console.log(`Video duration: ${video.duration.toFixed(2)}s`);
      if (analysisData) {
        console.log(`Analysis duration: ${analysisData.duration.toFixed(2)}s`);
        console.log(`Video FPS: ${analysisData.videoInfo?.fps?.toFixed(2)}`);
        console.log(`Analysis FPS: ${analysisData.fps.toFixed(2)}`);
      }
    };

    const handleCanPlay = () => {
      setIsLoading(false);
      setHasError(false);
    };

    const handleError = () => {
      setIsLoading(false);
      setHasError(true);
      console.error('Video failed to load');
    };

    const handlePlay = () => {
      setIsVideoPlaying(true);
    };

    const handlePause = () => {
      setIsVideoPlaying(false);
      console.log('Video paused at:', video.currentTime.toFixed(2), 'seconds');
    };

    const handleEnded = () => {
      setIsVideoPlaying(false);
      console.log('Video ended at:', video.currentTime.toFixed(2), 'seconds');
      console.log('Video duration:', video.duration.toFixed(2), 'seconds');
    };

    video.addEventListener('timeupdate', handleTimeUpdate);
    video.addEventListener('loadedmetadata', handleLoadedMetadata);
    video.addEventListener('canplay', handleCanPlay);
    video.addEventListener('error', handleError);
    video.addEventListener('play', handlePlay);
    video.addEventListener('pause', handlePause);
    video.addEventListener('ended', handleEnded);

    return () => {
      video.removeEventListener('timeupdate', handleTimeUpdate);
      video.removeEventListener('loadedmetadata', handleLoadedMetadata);
      video.removeEventListener('canplay', handleCanPlay);
      video.removeEventListener('error', handleError);
      video.removeEventListener('play', handlePlay);
      video.removeEventListener('pause', handlePause);
      video.removeEventListener('ended', handleEnded);
    };
  }, [onSeek]);

  // Draw tracking overlay
  useEffect(() => {
    const video = videoRef.current;
    const canvas = canvasRef.current;
    if (!video || !canvas || !analysisData || !showTracking) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Set canvas size to match video
    const updateCanvasSize = () => {
      const rect = video.getBoundingClientRect();
      canvas.width = rect.width;
      canvas.height = rect.height;
    };

    updateCanvasSize();
    window.addEventListener('resize', updateCanvasSize);

    const drawTracking = () => {
      // Clear canvas
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // Only draw tracking if we have analysis data for current time
      if (analysisData.trajectory && analysisData.trajectory.length > 0) {
        // Find current frame data with more flexible matching
        let currentFrameData = analysisData.trajectory.find(
          (point: any) => Math.abs(point.time - currentTime) < 0.1
        );
        
        // If no exact match, find the closest frame
        if (!currentFrameData) {
          currentFrameData = analysisData.trajectory.reduce((closest: any, point: any) => {
            const closestDiff = Math.abs(closest.time - currentTime);
            const pointDiff = Math.abs(point.time - currentTime);
            return pointDiff < closestDiff ? point : closest;
          });
        }

        if (currentFrameData) {
          // Scale coordinates to canvas size using actual video dimensions
          const videoWidth = analysisData.videoInfo?.width || 1920;
          const videoHeight = analysisData.videoInfo?.height || 1080;
          const scaleX = canvas.width / videoWidth;
          const scaleY = canvas.height / videoHeight;
          
          const x = currentFrameData.x * scaleX;
          const y = currentFrameData.y * scaleY;

          // Draw bounding box
          const boxWidth = 50 * scaleX;
          const boxHeight = 50 * scaleY;
          
          ctx.strokeStyle = '#3b82f6';
          ctx.lineWidth = 3;
          ctx.strokeRect(x - boxWidth/2, y - boxHeight/2, boxWidth, boxHeight);

          // Draw center point
          ctx.fillStyle = '#ef4444';
          ctx.beginPath();
          ctx.arc(x, y, 5, 0, 2 * Math.PI);
          ctx.fill();

          // Draw track ID
          ctx.fillStyle = '#ffffff';
          ctx.font = '16px Arial';
          ctx.fillText(`Track ${currentFrameData.trackId}`, x + 10, y - 10);

          // Draw confidence
          ctx.fillStyle = '#10b981';
          ctx.font = '14px Arial';
          ctx.fillText(`Conf: ${(currentFrameData.confidence * 100).toFixed(1)}%`, x + 10, y + 10);

          // Draw velocity vector if available
          if (currentFrameData.vx !== undefined && currentFrameData.vy !== undefined) {
            const vx = currentFrameData.vx * scaleX * 5; // Scale for visibility
            const vy = currentFrameData.vy * scaleY * 5;
            
            ctx.strokeStyle = '#f59e0b';
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.moveTo(x, y);
            ctx.lineTo(x + vx, y + vy);
            ctx.stroke();

            // Draw velocity arrowhead
            const angle = Math.atan2(vy, vx);
            const arrowLength = 10;
            ctx.beginPath();
            ctx.moveTo(x + vx, y + vy);
            ctx.lineTo(
              x + vx - arrowLength * Math.cos(angle - Math.PI / 6),
              y + vy - arrowLength * Math.sin(angle - Math.PI / 6)
            );
            ctx.moveTo(x + vx, y + vy);
            ctx.lineTo(
              x + vx - arrowLength * Math.cos(angle + Math.PI / 6),
              y + vy - arrowLength * Math.sin(angle + Math.PI / 6)
            );
            ctx.stroke();
          }
        }
      }
    };

    // Draw tracking overlay
    drawTracking();

    // Redraw on time change - but don't interfere with video playback
    const interval = setInterval(drawTracking, 200); // Reduced frequency

    return () => {
      window.removeEventListener('resize', updateCanvasSize);
      clearInterval(interval);
    };
  }, [currentTime, analysisData, showTracking]);

  // Handle play/pause
  const handlePlayPause = () => {
    const video = videoRef.current;
    if (!video) {
      console.log('No video element found');
      return;
    }

    console.log('Current video state:', {
      paused: video.paused,
      readyState: video.readyState,
      currentTime: video.currentTime,
      duration: video.duration
    });

    if (video.paused) {
      video.play()
        .then(() => {
          console.log('Video started playing successfully');
        })
        .catch((error) => {
          console.error('Failed to play video:', error);
        });
    } else {
      video.pause();
      console.log('Video paused');
    }
  };

  // Handle seek
  const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
    const video = videoRef.current;
    if (!video) return;

    const time = parseFloat(e.target.value);
    video.currentTime = time;
    setCurrentTime(time);
  };

  // Handle volume
  const handleVolumeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const video = videoRef.current;
    if (!video) return;

    const newVolume = parseFloat(e.target.value);
    setVolume(newVolume);
    video.volume = newVolume;
    setIsMuted(newVolume === 0);
  };

  // Toggle mute
  const toggleMute = () => {
    const video = videoRef.current;
    if (!video) return;

    if (isMuted) {
      video.volume = volume;
      setIsMuted(false);
    } else {
      video.volume = 0;
      setIsMuted(true);
    }
  };

  // Format time
  const formatTime = (time: number) => {
    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60);
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  };

  // Fullscreen
  const toggleFullscreen = () => {
    const video = videoRef.current;
    if (!video) return;

    if (document.fullscreenElement) {
      document.exitFullscreen();
    } else {
      video.requestFullscreen();
    }
  };

  if (!videoUrl) {
    return (
      <div className="bg-secondary-100 rounded-lg p-8 text-center">
        <p className="text-secondary-600">No video loaded</p>
      </div>
    );
  }

  if (hasError) {
    return (
      <div className="bg-red-100 rounded-lg p-8 text-center">
        <p className="text-red-600">Failed to load video</p>
        <p className="text-red-500 text-sm mt-2">Please try uploading a different video file</p>
      </div>
    );
  }

  return (
    <div className="bg-black rounded-lg overflow-hidden relative">
      {/* Video Container */}
      <div className="relative">
        <video
          ref={videoRef}
          src={videoUrl}
          className="w-full h-auto cursor-pointer"
          preload="auto"
          crossOrigin="anonymous"
          controls={false}
          playsInline
          muted={false}
          onClick={handlePlayPause}
        />
        
        {/* Loading Overlay */}
        {isLoading && (
          <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center">
            <div className="text-white text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white mx-auto mb-2"></div>
              <p>Loading video...</p>
            </div>
          </div>
        )}
        
        {/* Play Button Overlay */}
        {!isLoading && !isVideoPlaying && (
          <div className="absolute inset-0 bg-black bg-opacity-30 flex items-center justify-center">
            <button
              onClick={handlePlayPause}
              className="bg-white bg-opacity-90 hover:bg-opacity-100 rounded-full p-4 transition-all"
            >
              <Play className="h-12 w-12 text-black" />
            </button>
          </div>
        )}
        
        {/* Tracking Overlay Canvas */}
        <canvas
          ref={canvasRef}
          className="absolute top-0 left-0 w-full h-full pointer-events-none"
          style={{ zIndex: 10 }}
        />
        
        {/* Tracking Toggle */}
        <button
          onClick={() => setShowTracking(!showTracking)}
          className={`absolute top-4 right-4 px-3 py-1 rounded text-sm font-medium transition-colors ${
            showTracking 
              ? 'bg-green-600 text-white' 
              : 'bg-secondary-600 text-white'
          }`}
        >
          {showTracking ? 'Hide Tracking' : 'Show Tracking'}
        </button>
      </div>

      {/* Controls */}
      <div className="bg-secondary-900 p-4 space-y-4">
        {/* Progress Bar */}
        <div className="flex items-center space-x-2">
          <span className="text-white text-sm w-12">{formatTime(currentTime)}</span>
          <input
            type="range"
            min="0"
            max={duration || 0}
            value={currentTime}
            onChange={handleSeek}
            className="flex-1 h-1 bg-secondary-700 rounded-lg appearance-none cursor-pointer"
          />
          <span className="text-white text-sm w-12">{formatTime(duration)}</span>
        </div>

        {/* Control Buttons */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <button
              onClick={handlePlayPause}
              className="bg-primary-600 hover:bg-primary-700 text-white p-2 rounded-lg transition-colors"
            >
              {isVideoPlaying ? <Pause className="h-5 w-5" /> : <Play className="h-5 w-5" />}
            </button>
            
            <button
              onClick={() => {
                const video = videoRef.current;
                if (video) {
                  video.currentTime = 0;
                  setCurrentTime(0);
                }
              }}
              className="text-white hover:text-primary-400 transition-colors"
            >
              <RotateCcw className="h-5 w-5" />
            </button>

            <button
              onClick={toggleMute}
              className="text-white hover:text-primary-400 transition-colors"
            >
              {isMuted ? <VolumeX className="h-5 w-5" /> : <Volume2 className="h-5 w-5" />}
            </button>

            <input
              type="range"
              min="0"
              max="1"
              step="0.1"
              value={isMuted ? 0 : volume}
              onChange={handleVolumeChange}
              className="w-20 h-1 bg-secondary-700 rounded-lg appearance-none cursor-pointer"
            />
          </div>

          <div className="flex items-center space-x-4">
            <button
              onClick={toggleFullscreen}
              className="text-white hover:text-primary-400 transition-colors"
            >
              <Maximize className="h-5 w-5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
