import React from 'react';
import { Target, Zap } from 'lucide-react';

export const Header: React.FC = () => {
  return (
    <header className="bg-white shadow-sm border-b border-secondary-200">
      <div className="container mx-auto px-4 py-6">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-3">
            <div className="bg-primary-600 p-2 rounded-lg">
              <Target className="h-6 w-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-secondary-900">ImpulseCV</h1>
              <p className="text-sm text-secondary-600">Physics Learning Tool for Object Tracking</p>
            </div>
          </div>
          
          <div className="hidden md:flex items-center space-x-6 ml-auto">
            <div className="flex items-center space-x-2 text-secondary-600">
              <Zap className="h-4 w-4" />
              <span className="text-sm">Real-time Analysis</span>
            </div>
            <div className="flex items-center space-x-2 text-secondary-600">
              <Target className="h-4 w-4" />
              <span className="text-sm">YOLOv8 + ByteTrack</span>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};
