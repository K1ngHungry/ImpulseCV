export interface AnalysisData {
  frames: number;
  duration: number;
  fps: number;
  trajectory: TrajectoryPoint[];
  statistics: AnalysisStatistics;
  trackIds: number[];
  confidence: ConfidenceStats;
  videoInfo?: VideoInfo;
}

export interface VideoInfo {
  width: number;
  height: number;
  fps: number;
  frameCount: number;
}

export interface TrajectoryPoint {
  frame: number;
  time: number;
  x: number;
  y: number;
  vx?: number;
  vy?: number;
  velocity?: number;
  confidence: number;
  trackId: number;
}

export interface AnalysisStatistics {
  totalDistance: number;
  maxVelocity: number;
  avgVelocity: number;
  maxAcceleration: number;
  avgAcceleration: number;
  xRange: [number, number];
  yRange: [number, number];
}

export interface ConfidenceStats {
  min: number;
  max: number;
  average: number;
}

export type AnalysisStatus = 'idle' | 'processing' | 'completed' | 'error';

export interface AnalysisConfig {
  confidence: number;
  objectClass: number;
  pixelsPerMeter?: number;
  objectMass?: number;
  inputSize: number;
  iouThreshold: number;
}
