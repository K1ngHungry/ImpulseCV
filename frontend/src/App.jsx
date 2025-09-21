import React, { useState, useEffect } from 'react';
import LearningModule from './components/LearningModule';
import PhysicsConceptLibrary from './components/PhysicsConceptLibrary';
import StudentProgress from './components/StudentProgress';

function App() {
  const [status, setStatus] = useState({ status: 'idle', progress: 0, message: 'Ready to upload video.' });
  const [videoFile, setVideoFile] = useState(null);
  const [processingIntervalId, setProcessingIntervalId] = useState(null);
  const [currentTab, setCurrentTab] = useState('analyze');
  const [educationalData, setEducationalData] = useState(null);

  const API_BASE_URL = 'http://localhost:8000';

  const fetchStatus = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/status`);
      const data = await response.json();
      setStatus(data);
      
      // Fetch educational data when analysis is complete
      if (data.status === 'completed' && !educationalData) {
        try {
          const eduResponse = await fetch(`${API_BASE_URL}/educational_analysis`);
          if (eduResponse.ok) {
            const eduData = await eduResponse.json();
            setEducationalData(eduData);
          }
        } catch (error) {
          console.log('Educational analysis not available yet');
        }
      }
      
      if (data.status === 'completed' || data.status === 'error') {
        clearInterval(processingIntervalId);
        setProcessingIntervalId(null);
      }
    } catch (error) {
      console.error('Error fetching status:', error);
      clearInterval(processingIntervalId);
      setProcessingIntervalId(null);
      setStatus(prev => ({ ...prev, status: 'error', message: 'Failed to connect to backend.' }));
    }
  };

  useEffect(() => {
    fetchStatus();
  }, []);

  const handleVideoUpload = async (file) => {
    setVideoFile(file);
    setStatus({ status: 'uploading', progress: 0, message: 'Uploading video...' });

    const formData = new FormData();
    formData.append('file', file);

    try {
      const uploadResponse = await fetch(`${API_BASE_URL}/upload`, {
        method: 'POST',
        body: formData,
      });

      if (!uploadResponse.ok) {
        throw new Error(`Upload failed with status: ${uploadResponse.status}`);
      }

      const uploadData = await uploadResponse.json();
      setStatus(prev => ({ ...prev, status: 'uploaded', message: uploadData.message }));

      const interval = setInterval(fetchStatus, 2000);
      setProcessingIntervalId(interval);

    } catch (error) {
      console.error('Error uploading video:', error);
      setStatus({ status: 'error', progress: 0, message: `Upload failed: ${error.message}` });
    }
  };

  const handleProcessAsset = async (assetName) => {
    setStatus({ status: 'processing', progress: 0, message: `Processing ${assetName}...` });
    try {
      const response = await fetch(`${API_BASE_URL}/process_asset/${assetName}`);
      if (!response.ok) {
        throw new Error(`Processing failed with status: ${response.status}`);
      }
      const data = await response.json();
      setStatus(prev => ({ ...prev, message: data.message }));

      const interval = setInterval(fetchStatus, 2000);
      setProcessingIntervalId(interval);

    } catch (error) {
      console.error('Error processing asset:', error);
      setStatus({ status: 'error', progress: 0, message: `Processing failed: ${error.message}` });
    }
  };

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#f3f4f6', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <header style={{ backgroundColor: '#2563eb', color: 'white', padding: '1rem', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 'bold', margin: 0 }}>
            🚀 ImpulseCV - Physics Learning Platform
          </h1>
          <nav>
            <ul style={{ display: 'flex', listStyle: 'none', gap: '1rem', margin: 0, padding: 0 }}>
              <li>
                <button
                  onClick={() => setCurrentTab('analyze')}
                  style={{
                    color: currentTab === 'analyze' ? '#fbbf24' : 'white',
                    textDecoration: 'none',
                    background: 'none',
                    border: 'none',
                    cursor: 'pointer',
                    fontSize: '1rem',
                    fontWeight: currentTab === 'analyze' ? 'bold' : 'normal'
                  }}
                >
                  📹 Analyze
                </button>
              </li>
              <li>
                <button
                  onClick={() => setCurrentTab('learn')}
                  style={{
                    color: currentTab === 'learn' ? '#fbbf24' : 'white',
                    textDecoration: 'none',
                    background: 'none',
                    border: 'none',
                    cursor: 'pointer',
                    fontSize: '1rem',
                    fontWeight: currentTab === 'learn' ? 'bold' : 'normal'
                  }}
                >
                  📚 Learn
                </button>
              </li>
              <li>
                <button
                  onClick={() => setCurrentTab('progress')}
                  style={{
                    color: currentTab === 'progress' ? '#fbbf24' : 'white',
                    textDecoration: 'none',
                    background: 'none',
                    border: 'none',
                    cursor: 'pointer',
                    fontSize: '1rem',
                    fontWeight: currentTab === 'progress' ? 'bold' : 'normal'
                  }}
                >
                  📊 Progress
                </button>
              </li>
            </ul>
          </nav>
        </div>
      </header>

      <main style={{ flex: 1, maxWidth: '1200px', margin: '0 auto', padding: '2rem', width: '100%' }}>
        {currentTab === 'analyze' && (
          <>
            {/* Hero Section */}
            <div style={{ textAlign: 'center', marginBottom: '3rem' }}>
              <h2 style={{ fontSize: '2.5rem', fontWeight: 'bold', color: '#1f2937', marginBottom: '1rem' }}>
                AI-Powered Physics Analysis
              </h2>
              <p style={{ fontSize: '1.125rem', color: '#6b7280', marginBottom: '2rem' }}>
                Upload a video and watch AI analyze object motion with advanced physics calculations
              </p>
            </div>
          </>
        )}

        {currentTab === 'learn' && (
          <>
            <div style={{ textAlign: 'center', marginBottom: '3rem' }}>
              <h2 style={{ fontSize: '2.5rem', fontWeight: 'bold', color: '#1f2937', marginBottom: '1rem' }}>
                Physics Learning Center
              </h2>
              <p style={{ fontSize: '1.125rem', color: '#6b7280', marginBottom: '2rem' }}>
                Explore physics concepts, take quizzes, and enhance your understanding
              </p>
            </div>
          </>
        )}

        {currentTab === 'progress' && (
          <>
            <div style={{ textAlign: 'center', marginBottom: '3rem' }}>
              <h2 style={{ fontSize: '2.5rem', fontWeight: 'bold', color: '#1f2937', marginBottom: '1rem' }}>
                Your Learning Journey
              </h2>
              <p style={{ fontSize: '1.125rem', color: '#6b7280', marginBottom: '2rem' }}>
                Track your progress, unlock achievements, and see how much you've learned
              </p>
            </div>
          </>
        )}

        {/* Tab Content */}
        {currentTab === 'analyze' && (
          <>
            {/* Upload Section */}
            <div style={{ backgroundColor: 'white', borderRadius: '0.5rem', padding: '2rem', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', marginBottom: '2rem' }}>
          <h3 style={{ fontSize: '1.5rem', fontWeight: 'semibold', color: '#1f2937', marginBottom: '1rem' }}>
            Upload Your Video
          </h3>
          
          <div
            style={{
              border: '2px dashed #d1d5db',
              borderRadius: '0.5rem',
              padding: '3rem',
              textAlign: 'center',
              cursor: 'pointer',
              transition: 'border-color 0.2s'
            }}
            onDragOver={(e) => e.preventDefault()}
            onDrop={(e) => {
              e.preventDefault();
              const files = e.dataTransfer.files;
              if (files && files.length > 0) {
                handleVideoUpload(files[0]);
              }
            }}
            onClick={() => document.getElementById('fileInput').click()}
          >
            <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>📁</div>
            <h4 style={{ fontSize: '1.25rem', fontWeight: 'semibold', color: '#374151', marginBottom: '0.5rem' }}>
              Drop your video here or click to browse
            </h4>
            <p style={{ color: '#6b7280' }}>Supports MP4, MOV, AVI, and MKV files up to 100MB</p>
            <input
              id="fileInput"
              type="file"
              accept="video/*"
              style={{ display: 'none' }}
              onChange={(e) => {
                if (e.target.files && e.target.files.length > 0) {
                  handleVideoUpload(e.target.files[0]);
                }
              }}
            />
          </div>

          <div style={{ marginTop: '2rem' }}>
            <h4 style={{ fontSize: '1.125rem', fontWeight: 'semibold', color: '#374151', marginBottom: '1rem' }}>
              Or try our sample videos:
            </h4>
            <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
              <button
                onClick={() => handleProcessAsset('ball-in.mp4')}
                style={{
                  backgroundColor: '#e5e7eb',
                  color: '#374151',
                  fontWeight: 'semibold',
                  padding: '0.75rem 1rem',
                  borderRadius: '0.5rem',
                  border: 'none',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem'
                }}
              >
                🎥 ball-in.mp4
              </button>
              <button
                onClick={() => handleProcessAsset('teddy.mp4')}
                style={{
                  backgroundColor: '#e5e7eb',
                  color: '#374151',
                  fontWeight: 'semibold',
                  padding: '0.75rem 1rem',
                  borderRadius: '0.5rem',
                  border: 'none',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem'
                }}
              >
                🎥 teddy.mp4
              </button>
            </div>
          </div>
        </div>

        {/* Processing Status */}
        {status.status !== 'idle' && status.status !== 'completed' && status.status !== 'error' && (
          <div style={{ backgroundColor: 'white', borderRadius: '0.5rem', padding: '1.5rem', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', marginBottom: '2rem' }}>
            <h5 style={{ fontSize: '1.25rem', fontWeight: 'semibold', color: '#1f2937', marginBottom: '1rem' }}>
              Processing Video...
            </h5>
            <div style={{ width: '100%', backgroundColor: '#e5e7eb', borderRadius: '9999px', height: '1rem', marginBottom: '1rem' }}>
              <div
                style={{
                  backgroundColor: '#2563eb',
                  height: '1rem',
                  borderRadius: '9999px',
                  width: `${status.progress}%`,
                  transition: 'width 0.5s ease'
                }}
              />
            </div>
            <p style={{ color: '#374151', fontSize: '1.125rem' }}>{status.message}</p>
          </div>
        )}

        {/* Results */}
        {status.status === 'completed' && (
          <div style={{ backgroundColor: 'white', borderRadius: '0.5rem', padding: '1.5rem', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', marginBottom: '2rem' }}>
            <h3 style={{ fontSize: '1.5rem', fontWeight: 'semibold', color: '#1f2937', marginBottom: '1rem' }}>
              🎉 Analysis Complete!
            </h3>
            
            {/* Tracking Video Display */}
            {status.tracking_video && (
              <div style={{ marginBottom: '2rem' }}>
                <h4 style={{ fontSize: '1.25rem', fontWeight: 'semibold', color: '#1f2937', marginBottom: '1rem' }}>
                  🎥 AI Object Tracking Video
                </h4>
                <div style={{ borderRadius: '0.5rem', overflow: 'hidden', boxShadow: '0 4px 6px rgba(0,0,0,0.1)' }}>
                  <video
                    controls
                    autoPlay
                    loop
                    muted
                    playsInline
                    preload="metadata"
                    style={{ width: '100%', height: 'auto' }}
                    src={`${API_BASE_URL}/${status.tracking_video}`}
                    onError={(e) => {
                      console.error('Video playback error:', e);
                      e.target.style.display = 'none';
                      e.target.nextSibling.style.display = 'block';
                    }}
                  >
                    Your browser does not support the video tag.
                  </video>
                  <div style={{ display: 'none', padding: '2rem', textAlign: 'center', backgroundColor: '#f3f4f6', borderRadius: '0.5rem' }}>
                    <p>Video playback not supported. You can download the video file directly.</p>
                    <a 
                      href={`${API_BASE_URL}/${status.tracking_video}`} 
                      download
                      style={{ 
                        display: 'inline-block', 
                        padding: '0.5rem 1rem', 
                        backgroundColor: '#2563eb', 
                        color: 'white', 
                        textDecoration: 'none', 
                        borderRadius: '0.25rem' 
                      }}
                    >
                      Download Video
                    </a>
                  </div>
                </div>
                <p style={{ color: '#6b7280', fontSize: '0.875rem', marginTop: '0.5rem' }}>
                  Watch the AI track objects in real-time with bounding boxes and trajectory trails
                </p>
              </div>
            )}
            
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '2rem' }}>
              <div style={{ backgroundColor: '#f9fafb', padding: '1rem', borderRadius: '0.5rem' }}>
                <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#2563eb' }}>
                  {status.data_points || 0}
                </div>
                <div style={{ fontSize: '0.875rem', color: '#6b7280' }}>Data Points</div>
              </div>
              
              <div style={{ backgroundColor: '#f9fafb', padding: '1rem', borderRadius: '0.5rem' }}>
                <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#059669' }}>
                  {status.duration ? `${status.duration.toFixed(2)}s` : '-'}
                </div>
                <div style={{ fontSize: '0.875rem', color: '#6b7280' }}>Duration</div>
              </div>
              
              <div style={{ backgroundColor: '#f9fafb', padding: '1rem', borderRadius: '0.5rem' }}>
                <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#7c3aed' }}>
                  {status.objects_tracked || 0}
                </div>
                <div style={{ fontSize: '0.875rem', color: '#6b7280' }}>Objects Tracked</div>
              </div>
            </div>

            {status.csv_file && (
              <a
                href={`${API_BASE_URL}/download/${status.csv_file}`}
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                  backgroundColor: '#2563eb',
                  color: 'white',
                  padding: '0.75rem 1rem',
                  borderRadius: '0.5rem',
                  textDecoration: 'none',
                  fontWeight: 'semibold'
                }}
              >
                📥 Download CSV Data
              </a>
            )}
          </div>
        )}

            {/* Error State */}
            {status.status === 'error' && (
              <div style={{ backgroundColor: '#fef2f2', border: '1px solid #fecaca', borderRadius: '0.5rem', padding: '1.5rem', marginBottom: '2rem' }}>
                <h3 style={{ fontSize: '1.25rem', fontWeight: 'semibold', color: '#dc2626', marginBottom: '0.5rem' }}>
                  ❌ Error
                </h3>
                <p style={{ color: '#dc2626' }}>{status.message}</p>
              </div>
            )}
          </>
        )}

        {currentTab === 'learn' && (
          <>
            {/* Learning Module */}
            {educationalData && (
              <LearningModule 
                analysis={educationalData.analysis}
                explanations={educationalData.explanations}
                quiz={educationalData.quiz}
              />
            )}
            
            {/* Physics Concept Library */}
            <PhysicsConceptLibrary />
          </>
        )}

        {currentTab === 'progress' && (
          <>
            {/* Student Progress */}
            <StudentProgress />
          </>
        )}
      </main>

      <footer style={{ backgroundColor: '#1f2937', color: 'white', textAlign: 'center', padding: '1rem', marginTop: '2rem' }}>
        <p style={{ margin: 0 }}>&copy; 2024 ImpulseCV. Built for hackathon excellence.</p>
      </footer>
    </div>
  );
}

export default App;