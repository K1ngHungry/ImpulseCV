import React, { useState, useEffect } from 'react';

const StudentProgress = () => {
  const [progress, setProgress] = useState({
    videosAnalyzed: 0,
    conceptsLearned: [],
    quizScores: [],
    timeSpent: 0,
    achievements: []
  });

  const [showAchievements, setShowAchievements] = useState(false);

  // Mock data - in a real app, this would come from a backend
  useEffect(() => {
    const savedProgress = localStorage.getItem('studentProgress');
    if (savedProgress) {
      setProgress(JSON.parse(savedProgress));
    }
  }, []);

  const achievements = [
    {
      id: 'first_video',
      title: 'First Steps',
      description: 'Analyzed your first video',
      icon: '🎬',
      unlocked: progress.videosAnalyzed >= 1
    },
    {
      id: 'kinematics_master',
      title: 'Kinematics Master',
      description: 'Learned 3 kinematics concepts',
      icon: '🏃‍♂️',
      unlocked: progress.conceptsLearned.filter(c => c.category === 'kinematics').length >= 3
    },
    {
      id: 'quiz_champion',
      title: 'Quiz Champion',
      description: 'Scored 100% on a quiz',
      icon: '🏆',
      unlocked: progress.quizScores.some(score => score.percentage === 100)
    },
    {
      id: 'energy_expert',
      title: 'Energy Expert',
      description: 'Mastered energy concepts',
      icon: '⚡',
      unlocked: progress.conceptsLearned.filter(c => c.category === 'energy').length >= 2
    },
    {
      id: 'dedicated_learner',
      title: 'Dedicated Learner',
      description: 'Spent 30+ minutes learning',
      icon: '📚',
      unlocked: progress.timeSpent >= 30
    }
  ];

  const getOverallProgress = () => {
    const totalConcepts = 9; // Total concepts in the library
    const learnedConcepts = progress.conceptsLearned.length;
    return Math.round((learnedConcepts / totalConcepts) * 100);
  };

  const getAverageQuizScore = () => {
    if (progress.quizScores.length === 0) return 0;
    const total = progress.quizScores.reduce((sum, score) => sum + score.percentage, 0);
    return Math.round(total / progress.quizScores.length);
  };

  const getStreakDays = () => {
    // Mock calculation - in real app, track actual daily usage
    return Math.min(progress.videosAnalyzed, 7);
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-800 flex items-center">
          📊 Your Learning Progress
        </h2>
        <button
          onClick={() => setShowAchievements(!showAchievements)}
          className="bg-purple-500 text-white px-4 py-2 rounded-lg font-medium hover:bg-purple-600 transition-colors"
        >
          {showAchievements ? 'Hide' : 'Show'} Achievements
        </button>
      </div>

      {showAchievements && (
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">🏆 Achievements</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {achievements.map((achievement) => (
              <div
                key={achievement.id}
                className={`p-4 rounded-lg border-2 transition-all ${
                  achievement.unlocked
                    ? 'bg-yellow-50 border-yellow-300'
                    : 'bg-gray-50 border-gray-200 opacity-50'
                }`}
              >
                <div className="text-3xl mb-2">{achievement.icon}</div>
                <h4 className="font-semibold text-gray-800">{achievement.title}</h4>
                <p className="text-sm text-gray-600">{achievement.description}</p>
                {achievement.unlocked && (
                  <div className="text-xs text-yellow-600 font-medium mt-2">✓ Unlocked!</div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Overall Progress */}
        <div className="bg-blue-50 p-4 rounded-lg">
          <div className="flex items-center justify-between mb-2">
            <h3 className="font-semibold text-blue-800">Overall Progress</h3>
            <span className="text-2xl">📈</span>
          </div>
          <div className="text-3xl font-bold text-blue-600 mb-2">
            {getOverallProgress()}%
          </div>
          <div className="w-full bg-blue-200 rounded-full h-2">
            <div
              className="bg-blue-500 h-2 rounded-full transition-all duration-500"
              style={{ width: `${getOverallProgress()}%` }}
            ></div>
          </div>
          <p className="text-sm text-blue-600 mt-2">
            {progress.conceptsLearned.length} of 9 concepts learned
          </p>
        </div>

        {/* Videos Analyzed */}
        <div className="bg-green-50 p-4 rounded-lg">
          <div className="flex items-center justify-between mb-2">
            <h3 className="font-semibold text-green-800">Videos Analyzed</h3>
            <span className="text-2xl">🎬</span>
          </div>
          <div className="text-3xl font-bold text-green-600 mb-2">
            {progress.videosAnalyzed}
          </div>
          <p className="text-sm text-green-600">
            Keep analyzing videos to learn more!
          </p>
        </div>

        {/* Average Quiz Score */}
        <div className="bg-purple-50 p-4 rounded-lg">
          <div className="flex items-center justify-between mb-2">
            <h3 className="font-semibold text-purple-800">Quiz Average</h3>
            <span className="text-2xl">📝</span>
          </div>
          <div className="text-3xl font-bold text-purple-600 mb-2">
            {getAverageQuizScore()}%
          </div>
          <p className="text-sm text-purple-600">
            {progress.quizScores.length} quizzes completed
          </p>
        </div>

        {/* Learning Streak */}
        <div className="bg-orange-50 p-4 rounded-lg">
          <div className="flex items-center justify-between mb-2">
            <h3 className="font-semibold text-orange-800">Learning Streak</h3>
            <span className="text-2xl">🔥</span>
          </div>
          <div className="text-3xl font-bold text-orange-600 mb-2">
            {getStreakDays()} days
          </div>
          <p className="text-sm text-orange-600">
            Keep the momentum going!
          </p>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="mt-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">Recent Activity</h3>
        <div className="bg-gray-50 p-4 rounded-lg">
          {progress.videosAnalyzed === 0 ? (
            <p className="text-gray-600 text-center py-4">
              No activity yet. Start by analyzing your first video!
            </p>
          ) : (
            <div className="space-y-3">
              {progress.conceptsLearned.slice(-3).map((concept, index) => (
                <div key={index} className="flex items-center space-x-3">
                  <span className="text-green-500">✓</span>
                  <span className="text-gray-700">
                    Learned <strong>{concept.name}</strong> from {concept.category}
                  </span>
                </div>
              ))}
              {progress.quizScores.slice(-2).map((score, index) => (
                <div key={index} className="flex items-center space-x-3">
                  <span className="text-blue-500">📝</span>
                  <span className="text-gray-700">
                    Completed quiz with {score.percentage}% score
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Learning Tips */}
      <div className="mt-6 bg-gradient-to-r from-blue-50 to-purple-50 p-4 rounded-lg">
        <h3 className="text-lg font-semibold text-gray-800 mb-3">💡 Learning Tips</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="flex items-start space-x-3">
            <span className="text-blue-500 text-xl">🎯</span>
            <div>
              <h4 className="font-medium text-gray-800">Set Goals</h4>
              <p className="text-sm text-gray-600">Try to learn one new concept each day</p>
            </div>
          </div>
          <div className="flex items-start space-x-3">
            <span className="text-green-500 text-xl">🔄</span>
            <div>
              <h4 className="font-medium text-gray-800">Practice Regularly</h4>
              <p className="text-sm text-gray-600">Analyze different types of motion to see concepts in action</p>
            </div>
          </div>
          <div className="flex items-start space-x-3">
            <span className="text-purple-500 text-xl">🤔</span>
            <div>
              <h4 className="font-medium text-gray-800">Ask Questions</h4>
              <p className="text-sm text-gray-600">Think about how physics applies to everyday situations</p>
            </div>
          </div>
          <div className="flex items-start space-x-3">
            <span className="text-orange-500 text-xl">📚</span>
            <div>
              <h4 className="font-medium text-gray-800">Review Concepts</h4>
              <p className="text-sm text-gray-600">Use the concept library to reinforce your understanding</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StudentProgress;
