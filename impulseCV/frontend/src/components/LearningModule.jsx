import React, { useState, useEffect } from 'react';

const LearningModule = ({ analysis, explanations, quiz }) => {
  const [currentSection, setCurrentSection] = useState('overview');
  const [quizAnswers, setQuizAnswers] = useState({});
  const [quizScore, setQuizScore] = useState(null);
  const [showExplanations, setShowExplanations] = useState(false);

  const handleQuizSubmit = () => {
    let correct = 0;
    const total = quiz.questions.length;
    
    quiz.questions.forEach((question, index) => {
      if (quizAnswers[index] === question.correct) {
        correct++;
      }
    });
    
    setQuizScore({
      correct,
      total,
      percentage: Math.round((correct / total) * 100)
    });
    setShowExplanations(true);
  };

  const getScoreColor = (percentage) => {
    if (percentage >= 80) return 'text-green-600';
    if (percentage >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreMessage = (percentage) => {
    if (percentage >= 80) return 'Excellent! You have a strong understanding of these physics concepts.';
    if (percentage >= 60) return 'Good job! Review the explanations to strengthen your understanding.';
    return 'Keep studying! Physics takes practice - review the concepts and try again.';
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-800 flex items-center">
          🎓 Physics Learning Center
        </h2>
        <div className="flex space-x-2">
          <button
            onClick={() => setCurrentSection('overview')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              currentSection === 'overview'
                ? 'bg-blue-500 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            Overview
          </button>
          <button
            onClick={() => setCurrentSection('concepts')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              currentSection === 'concepts'
                ? 'bg-blue-500 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            Concepts
          </button>
          <button
            onClick={() => setCurrentSection('quiz')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              currentSection === 'quiz'
                ? 'bg-blue-500 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            Quiz
          </button>
        </div>
      </div>

      {currentSection === 'overview' && (
        <div className="space-y-6">
          <div className="bg-blue-50 border-l-4 border-blue-400 p-4">
            <h3 className="text-lg font-semibold text-blue-800 mb-2">📚 What You're Learning</h3>
            <p className="text-blue-700">{explanations?.overview || 'Analyzing the physics concepts in your video...'}</p>
          </div>

          {explanations?.step_by_step && (
            <div className="bg-green-50 border-l-4 border-green-400 p-4">
              <h3 className="text-lg font-semibold text-green-800 mb-3">🔬 Step-by-Step Analysis</h3>
              <ol className="space-y-2">
                {explanations.step_by_step.map((step, index) => (
                  <li key={index} className="text-green-700 flex items-start">
                    <span className="bg-green-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm font-bold mr-3 mt-0.5">
                      {index + 1}
                    </span>
                    {step}
                  </li>
                ))}
              </ol>
            </div>
          )}

          {explanations?.formulas_used && (
            <div className="bg-purple-50 border-l-4 border-purple-400 p-4">
              <h3 className="text-lg font-semibold text-purple-800 mb-3">📐 Key Formulas</h3>
              <div className="space-y-2">
                {explanations.formulas_used.map((formula, index) => (
                  <div key={index} className="bg-white p-3 rounded border font-mono text-purple-700">
                    {formula}
                  </div>
                ))}
              </div>
            </div>
          )}

          {explanations?.concept_connections && (
            <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4">
              <h3 className="text-lg font-semibold text-yellow-800 mb-3">🔗 Concept Connections</h3>
              <ul className="space-y-1">
                {explanations.concept_connections.map((connection, index) => (
                  <li key={index} className="text-yellow-700">• {connection}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {currentSection === 'concepts' && (
        <div className="space-y-6">
          <div className="bg-gray-50 p-4 rounded-lg">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">🧠 Physics Concepts Identified</h3>
            {analysis?.key_concepts && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {analysis.key_concepts.map((concept, index) => (
                  <div key={index} className="bg-white p-4 rounded border">
                    <h4 className="font-semibold text-gray-800 capitalize mb-2">
                      {concept.replace('_', ' ')}
                    </h4>
                    <p className="text-gray-600 text-sm">
                      {concept === 'projectile_motion' && 'The object follows a parabolic path under gravity.'}
                      {concept === 'acceleration' && 'The object\'s velocity is changing over time.'}
                      {concept === 'high_speed_motion' && 'The object is moving at high speeds with significant kinetic energy.'}
                      {concept === 'energy_transformation' && 'Energy is being converted between different forms.'}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </div>

          {analysis?.learning_points && (
            <div className="bg-blue-50 p-4 rounded-lg">
              <h3 className="text-lg font-semibold text-blue-800 mb-3">💡 Key Learning Points</h3>
              <ul className="space-y-2">
                {analysis.learning_points.map((point, index) => (
                  <li key={index} className="text-blue-700 flex items-start">
                    <span className="text-blue-500 mr-2">•</span>
                    {point}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {analysis?.real_world_connections && (
            <div className="bg-green-50 p-4 rounded-lg">
              <h3 className="text-lg font-semibold text-green-800 mb-3">🌍 Real-World Applications</h3>
              <ul className="space-y-2">
                {analysis.real_world_connections.map((connection, index) => (
                  <li key={index} className="text-green-700 flex items-start">
                    <span className="text-green-500 mr-2">•</span>
                    {connection}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {currentSection === 'quiz' && (
        <div className="space-y-6">
          {!quizScore ? (
            <div>
              <h3 className="text-lg font-semibold text-gray-800 mb-4">📝 Test Your Understanding</h3>
              {quiz?.questions && quiz.questions.map((question, index) => (
                <div key={index} className="bg-gray-50 p-4 rounded-lg mb-4">
                  <h4 className="font-semibold text-gray-800 mb-3">
                    {index + 1}. {question.question}
                  </h4>
                  <div className="space-y-2">
                    {question.options.map((option, optionIndex) => (
                      <label key={optionIndex} className="flex items-center space-x-3 cursor-pointer">
                        <input
                          type="radio"
                          name={`question-${index}`}
                          value={optionIndex}
                          checked={quizAnswers[index] === optionIndex}
                          onChange={(e) => setQuizAnswers({
                            ...quizAnswers,
                            [index]: parseInt(e.target.value)
                          })}
                          className="text-blue-500"
                        />
                        <span className="text-gray-700">{option}</span>
                      </label>
                    ))}
                  </div>
                </div>
              ))}
              <button
                onClick={handleQuizSubmit}
                className="bg-blue-500 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-600 transition-colors"
              >
                Submit Quiz
              </button>
            </div>
          ) : (
            <div className="text-center">
              <div className={`text-4xl font-bold mb-4 ${getScoreColor(quizScore.percentage)}`}>
                {quizScore.percentage}%
              </div>
              <h3 className="text-xl font-semibold text-gray-800 mb-2">Quiz Results</h3>
              <p className="text-gray-600 mb-4">
                You got {quizScore.correct} out of {quizScore.total} questions correct.
              </p>
              <p className="text-gray-700 mb-6">{getScoreMessage(quizScore.percentage)}</p>
              
              {showExplanations && (
                <div className="bg-gray-50 p-4 rounded-lg text-left">
                  <h4 className="font-semibold text-gray-800 mb-3">📖 Explanations</h4>
                  {quiz.questions.map((question, index) => (
                    <div key={index} className="mb-4">
                      <p className="font-medium text-gray-800 mb-1">
                        {index + 1}. {question.question}
                      </p>
                      <p className="text-sm text-gray-600">
                        <span className="font-medium">Correct Answer: </span>
                        {question.options[question.correct]}
                      </p>
                      <p className="text-sm text-gray-600 mt-1">
                        <span className="font-medium">Explanation: </span>
                        {question.explanation}
                      </p>
                    </div>
                  ))}
                </div>
              )}
              
              <button
                onClick={() => {
                  setQuizScore(null);
                  setQuizAnswers({});
                  setShowExplanations(false);
                }}
                className="bg-gray-500 text-white px-6 py-3 rounded-lg font-semibold hover:bg-gray-600 transition-colors mt-4"
              >
                Retake Quiz
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default LearningModule;
