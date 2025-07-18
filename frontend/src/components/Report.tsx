import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useVideoStore } from '../store/useVideoStore';
import { QuizAttempt } from '../types';
import toast from 'react-hot-toast';

const Report: React.FC = () => {
  const {
    reportState,
    quizState,
    syllabusState,
    generateReport,
    resetReport,
  } = useVideoStore();

  const [watchedVideos, setWatchedVideos] = useState<string[]>([]);

  const handleGenerateReport = async () => {
    if (quizState.questions.length === 0 || !quizState.isCompleted) {
      toast.error('Please complete a quiz first to generate a report.');
      return;
    }

    if (syllabusState.topics.length === 0) {
      toast.error('No syllabus topics available for report generation.');
      return;
    }

    try {
      // Convert quiz state to quiz attempts
      const quizAttempts: QuizAttempt[] = quizState.questions.map((question, index) => {
        const userAnswer = quizState.userAnswers[index];
        return {
          question: question.question,
          selected_answer: userAnswer || '',
          correct_answer: question.answer,
          is_correct: userAnswer === question.answer,
          topic: question.topic,
        };
      });

      await generateReport(quizAttempts, watchedVideos, syllabusState.topics);
      toast.success('Learning report generated successfully!');
    } catch (error) {
      toast.error('Failed to generate report.');
    }
  };

  const handleReset = () => {
    resetReport();
    setWatchedVideos([]);
    toast.success('Report reset successfully.');
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600 dark:text-green-400';
    if (score >= 60) return 'text-yellow-600 dark:text-yellow-400';
    return 'text-red-600 dark:text-red-400';
  };

  const getScoreBgColor = (score: number) => {
    if (score >= 80) return 'bg-green-100 dark:bg-green-900/20';
    if (score >= 60) return 'bg-yellow-100 dark:bg-yellow-900/20';
    return 'bg-red-100 dark:bg-red-900/20';
  };

  if (!reportState.report) {
    return (
      <div className="space-y-6">
        {/* Header */}
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
            📊 Learning Report
          </h2>
          <p className="text-gray-600 dark:text-gray-400">
            Generate comprehensive learning reports with performance analytics and personalized recommendations.
          </p>
        </div>

        {/* Generate Report Section */}
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Generate Learning Report
          </h3>

          {quizState.questions.length === 0 || !quizState.isCompleted ? (
            <div className="text-center py-8">
              <p className="text-gray-600 dark:text-gray-400 mb-4">
                No completed quiz available. Please complete a quiz first.
              </p>
              <button
                onClick={() => window.location.href = '#quiz'}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium"
              >
                Go to Quiz
              </button>
            </div>
          ) : (
            <div className="space-y-6">
              {/* Quiz Summary */}
              <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                <h4 className="font-semibold text-gray-900 dark:text-white mb-2">
                  Quiz Summary
                </h4>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-gray-600 dark:text-gray-400">Score:</span>
                    <span className={`ml-2 font-semibold ${getScoreColor(quizState.score)}`}>
                      {quizState.score.toFixed(1)}%
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-600 dark:text-gray-400">Questions:</span>
                    <span className="ml-2 font-semibold text-gray-900 dark:text-white">
                      {quizState.questions.length}
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-600 dark:text-gray-400">Topics Covered:</span>
                    <span className="ml-2 font-semibold text-gray-900 dark:text-white">
                      {quizState.topicsCovered.length}
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-600 dark:text-gray-400">Correct Answers:</span>
                    <span className="ml-2 font-semibold text-gray-900 dark:text-white">
                      {Math.round((quizState.score / 100) * quizState.questions.length)}
                    </span>
                  </div>
                </div>
              </div>

              {/* Watched Videos Input */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Watched Videos (Optional)
                </label>
                <textarea
                  value={watchedVideos.join('\n')}
                  onChange={(e) => setWatchedVideos(e.target.value.split('\n').filter(v => v.trim()))}
                  placeholder="Enter video URLs you've watched (one per line)&#10;Example:&#10;https://www.youtube.com/watch?v=example1&#10;https://www.youtube.com/watch?v=example2"
                  className="w-full h-24 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white resize-none"
                />
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  This helps provide more personalized recommendations.
                </p>
              </div>

              {/* Generate Button */}
              <button
                onClick={handleGenerateReport}
                disabled={reportState.isGenerating}
                className="w-full px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
              >
                {reportState.isGenerating ? (
                  <span className="flex items-center justify-center">
                    <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Generating Report...
                  </span>
                ) : (
                  'Generate Learning Report'
                )}
              </button>
            </div>
          )}

          {/* Error Display */}
          {reportState.error && (
            <div className="mt-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
              <p className="text-red-600 dark:text-red-400 text-sm">{reportState.error}</p>
            </div>
          )}
        </div>
      </div>
    );
  }

  const report = reportState.report;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
            📊 Learning Report
          </h2>
          <button
            onClick={handleReset}
            className="px-3 py-1 text-sm text-red-600 dark:text-red-400 hover:text-red-800 dark:hover:text-red-300 font-medium"
          >
            Reset Report
          </button>
        </div>
        <p className="text-gray-600 dark:text-gray-400">
          Comprehensive analysis of your learning progress and personalized recommendations.
        </p>
      </div>

      {/* Overall Score */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700"
      >
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Overall Performance
        </h3>
        <div className="text-center">
          <div className={`text-5xl font-bold mb-2 ${getScoreColor(report.overall_score)}`}>
            {report.overall_score.toFixed(1)}%
          </div>
          <p className="text-gray-600 dark:text-gray-400">
            Overall accuracy across all topics
          </p>
        </div>
      </motion.div>

      {/* Topic Breakdown */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700"
      >
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Topic Performance
        </h3>
        <div className="space-y-3">
          {Object.entries(report.topic_scores).map(([topic, score], index) => (
            <motion.div
              key={topic}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg"
            >
              <span className="font-medium text-gray-900 dark:text-white">{topic}</span>
              <div className="flex items-center space-x-3">
                <div className="w-24 bg-gray-200 dark:bg-gray-600 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full ${getScoreBgColor(score)}`}
                    style={{ width: `${score}%` }}
                  />
                </div>
                <span className={`font-semibold ${getScoreColor(score)}`}>
                  {score.toFixed(1)}%
                </span>
              </div>
            </motion.div>
          ))}
        </div>
      </motion.div>

      {/* Weak Areas */}
      {report.weak_areas.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700"
        >
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            ⚠️ Areas for Improvement
          </h3>
          <div className="space-y-2">
            {report.weak_areas.map((area, index) => (
              <div
                key={index}
                className="flex items-center space-x-2 text-red-600 dark:text-red-400"
              >
                <span>•</span>
                <span>{area}</span>
              </div>
            ))}
          </div>
        </motion.div>
      )}

      {/* Recommendations */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700"
      >
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          💡 Recommendations
        </h3>
        <div className="space-y-3">
          {report.recommendations.map((recommendation, index) => (
            <div
              key={index}
              className="flex items-start space-x-3 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg"
            >
              <span className="text-blue-600 dark:text-blue-400 mt-1">💡</span>
              <span className="text-blue-800 dark:text-blue-300">{recommendation}</span>
            </div>
          ))}
        </div>
      </motion.div>

      {/* Common Mistakes */}
      {report.common_mistakes.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700"
        >
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            🔍 Common Mistakes
          </h3>
          <div className="space-y-2">
            {report.common_mistakes.map((mistake, index) => (
              <div
                key={index}
                className="flex items-start space-x-2 text-orange-600 dark:text-orange-400"
              >
                <span>•</span>
                <span>{mistake}</span>
              </div>
            ))}
          </div>
        </motion.div>
      )}

      {/* Unwatched Topics */}
      {report.unwatched_topics.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700"
        >
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            📚 Topics to Explore
          </h3>
          <div className="space-y-2">
            {report.unwatched_topics.map((topic, index) => (
              <div
                key={index}
                className="flex items-center space-x-2 text-gray-600 dark:text-gray-400"
              >
                <span>•</span>
                <span>{topic}</span>
              </div>
            ))}
          </div>
        </motion.div>
      )}

      {/* Detailed Report Data */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
        className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700"
      >
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          📈 Detailed Analytics
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
          <div className="p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
            <span className="text-gray-600 dark:text-gray-400">Strongest Topic:</span>
            <span className="ml-2 font-semibold text-gray-900 dark:text-white">
              {report.report_data.performance_analysis.strongest_topic}
            </span>
          </div>
          <div className="p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
            <span className="text-gray-600 dark:text-gray-400">Weakest Topic:</span>
            <span className="ml-2 font-semibold text-gray-900 dark:text-white">
              {report.report_data.performance_analysis.weakest_topic}
            </span>
          </div>
          <div className="p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
            <span className="text-gray-600 dark:text-gray-400">Topics Covered:</span>
            <span className="ml-2 font-semibold text-gray-900 dark:text-white">
              {report.report_data.performance_analysis.topics_covered}
            </span>
          </div>
          <div className="p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
            <span className="text-gray-600 dark:text-gray-400">Topics Missed:</span>
            <span className="ml-2 font-semibold text-gray-900 dark:text-white">
              {report.report_data.performance_analysis.topics_missed}
            </span>
          </div>
        </div>
      </motion.div>
    </div>
  );
};

export default Report; 