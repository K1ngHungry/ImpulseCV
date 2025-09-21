import React, { useState } from 'react';
import { VideoUpload } from './components/VideoUpload';
import { AnalysisConfig } from './components/AnalysisConfig';
import { AnalysisResults } from './components/AnalysisResults';
import { Header } from './components/Header';
import { AnalysisData, AnalysisStatus } from './types';

function App() {
  const [analysisData, setAnalysisData] = useState<AnalysisData | null>(null);
  const [analysisStatus, setAnalysisStatus] = useState<AnalysisStatus>('idle');
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);

  const handleFileUpload = (file: File) => {
    setUploadedFile(file);
    setAnalysisData(null);
    setAnalysisStatus('idle');
  };

  const handleAnalysisStart = async (config: any) => {
    if (!uploadedFile) return;
    
    setAnalysisStatus('processing');
    
    try {
      // Create FormData for the API call
      const formData = new FormData();
      formData.append('video', uploadedFile);
      formData.append('config', JSON.stringify(config));
      
      console.log('Sending request to /api/analyze with:', {
        file: uploadedFile.name,
        config: config
      });
      
      const response = await fetch('http://localhost:5001/api/analyze', {
        method: 'POST',
        body: formData,
      });
      
      console.log('Response status:', response.status);
      console.log('Response headers:', Object.fromEntries(response.headers.entries()));
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('Error response:', errorText);
        throw new Error(`Analysis failed: ${response.status} ${response.statusText}`);
      }
      
      const data = await response.json();
      console.log('Analysis data received:', data);
      setAnalysisData(data);
      setAnalysisStatus('completed');
    } catch (error) {
      console.error('Analysis error:', error);
      setAnalysisStatus('error');
    }
  };

  const handleReset = () => {
    setUploadedFile(null);
    setAnalysisData(null);
    setAnalysisStatus('idle');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-secondary-50">
      <Header />
      
      <main className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Left Column - Upload and Configuration */}
          <div className="space-y-6">
            <VideoUpload 
              onFileUpload={handleFileUpload}
              uploadedFile={uploadedFile}
              disabled={analysisStatus === 'processing'}
            />
            
            {uploadedFile && (
              <AnalysisConfig 
                onStartAnalysis={handleAnalysisStart}
                disabled={analysisStatus === 'processing'}
              />
            )}
          </div>
          
          {/* Right Column - Results */}
          <div>
            <AnalysisResults 
              analysisData={analysisData}
              analysisStatus={analysisStatus}
              uploadedFile={uploadedFile}
              onReset={handleReset}
            />
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
