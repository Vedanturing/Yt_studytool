import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useVideoStore } from '../store/useVideoStore';
import { QuizQuestion } from '../types';
import toast from 'react-hot-toast';

const Quiz: React.FC = () => {
  const {
    quizState,
    syllabusState,
    generateQuiz,
    submitQuizAnswer,
    nextQuestion,
    previousQuestion,
    completeQuiz,
    resetQuiz,
  } = useVideoStore();

  const [selectedAnswer, setSelectedAnswer] = useState<string>('');
  const [showExplanation, setShowExplanation] = useState(false);
  const [numQuestions, setNumQuestions] = useState<number>(10);
  const [difficulty, setDifficulty] = useState<string>('medium');
  const [questionTypes, setQuestionTypes] = useState<string[]>(['mcq', 'true_false']);
  const [subject, setSubject] = useState<string>('General');
  
  const questionOptions = [10, 20, 30, 50];
  const difficultyOptions = [
    { value: 'easy', label: 'Easy', color: 'text-green-600' },
    { value: 'medium', label: 'Medium', color: 'text-yellow-600' },
    { value: 'hard', label: 'Hard', color: 'text-red-600' }
  ];
  const questionTypeOptions = [
    { value: 'mcq', label: 'Multiple Choice', icon: '📝' },
    { value: 'true_false', label: 'True/False', icon: '✅' },
    { value: 'fill_blank', label: 'Fill in the Blank', icon: '📝' },
    { value: 'code_output', label: 'Code Output', icon: '💻' }
  ];

  const currentQuestion = quizState.questions[quizState.currentQuestionIndex];
  const userAnswer = quizState.userAnswers[quizState.currentQuestionIndex];
  const isLastQuestion = quizState.currentQuestionIndex === quizState.questions.length - 1;
  const isFirstQuestion = quizState.currentQuestionIndex === 0;

  const handleGenerateQuiz = async () => {
    if (syllabusState.topics.length === 0) {
      toast.error('Please upload a syllabus first to generate a quiz.');
      return;
    }

    const topics = syllabusState.topics.map(topic => topic.topic);
    try {
      await generateQuiz(topics, numQuestions, difficulty, questionTypes, subject);
      
      // Show source indicator
      if (quizState.source === 'offline') {
        toast.success('Quiz loaded from offline storage!', {
          icon: '💾',
          duration: 4000
        });
      } else if (quizState.source === 'fallback') {
        toast.success('Using fallback quiz questions.', {
          icon: '⚠️',
          duration: 4000
        });
      } else {
        toast.success('Quiz generated successfully!');
      }
    } catch (error) {
      toast.error('Failed to generate quiz.');
    }
  };

  const handleAnswerSelect = (answer: string) => {
    setSelectedAnswer(answer);
    submitQuizAnswer(quizState.currentQuestionIndex, answer);
  };

  const handleNext = () => {
    if (!userAnswer) {
      toast.error('Please select an answer before continuing.');
      return;
    }

    if (isLastQuestion) {
      handleComplete();
    } else {
      nextQuestion();
      setSelectedAnswer('');
      setShowExplanation(false);
    }
  };

  const handlePrevious = () => {
    previousQuestion();
    setSelectedAnswer(quizState.userAnswers[quizState.currentQuestionIndex - 1] || '');
    setShowExplanation(false);
  };

  const handleComplete = () => {
    if (!userAnswer) {
      toast.error('Please select an answer before completing the quiz.');
      return;
    }
    completeQuiz();
    setShowExplanation(true);
    toast.success(`Quiz completed! Your score: ${quizState.score.toFixed(1)}%`);
  };

  const handleReset = () => {
    resetQuiz();
    setSelectedAnswer('');
    setShowExplanation(false);
    toast.success('Quiz reset successfully.');
  };

  const getProgressPercentage = () => {
    return ((quizState.currentQuestionIndex + 1) / quizState.questions.length) * 100;
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600 dark:text-green-400';
    if (score >= 60) return 'text-yellow-600 dark:text-yellow-400';
    return 'text-red-600 dark:text-red-400';
  };

  const getSourceIndicator = () => {
    switch (quizState.source) {
      case 'offline':
        return { text: '💾 Offline Storage', color: 'text-blue-600 dark:text-blue-400' };
      case 'fallback':
        return { text: '⚠️ Fallback Questions', color: 'text-orange-600 dark:text-orange-400' };
      default:
        return { text: '🤖 AI Generated', color: 'text-green-600 dark:text-green-400' };
    }
  };

  const getQuestionTypeIcon = (type: string) => {
    const typeOption = questionTypeOptions.find(option => option.value === type);
    return typeOption ? typeOption.icon : '📝';
  };

  const getDifficultyColor = (diff: string) => {
    const difficultyOption = difficultyOptions.find(option => option.value === diff);
    return difficultyOption ? difficultyOption.color : 'text-gray-600';
  };

  if (quizState.questions.length === 0) {
    return (
      <div className="space-y-6">
        {/* Header */}
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
            🧠 Interactive Quiz
          </h2>
          <p className="text-gray-600 dark:text-gray-400">
            Generate AI-powered quizzes based on your syllabus topics to test your knowledge.
          </p>
        </div>

        {/* Generate Quiz Section */}
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Generate Quiz
          </h3>

          {syllabusState.topics.length === 0 ? (
            <div className="text-center py-8">
              <p className="text-gray-600 dark:text-gray-400 mb-4">
                No syllabus topics available. Please upload a syllabus first.
              </p>
              <button
                onClick={() => window.location.href = '#syllabus'}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium"
              >
                Go to Syllabus
              </button>
            </div>
          ) : (
            <div className="space-y-4">
              <p className="text-gray-600 dark:text-gray-400">
                Generate a quiz with {syllabusState.topics.length} topics from your syllabus.
              </p>
              
              {/* Subject Input */}
              <div className="flex items-center space-x-2">
                <label htmlFor="subject" className="text-gray-700 dark:text-gray-300 font-medium">Subject:</label>
                <input
                  id="subject"
                  type="text"
                  value={subject}
                  onChange={e => setSubject(e.target.value)}
                  placeholder="e.g., Computer Science"
                  className="flex-1 px-3 py-1 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-900 dark:text-white"
                />
              </div>

              {/* Number of Questions Selector */}
              <div className="flex items-center space-x-2">
                <label htmlFor="num-questions" className="text-gray-700 dark:text-gray-300 font-medium">Questions:</label>
                <select
                  id="num-questions"
                  value={numQuestions}
                  onChange={e => setNumQuestions(Number(e.target.value))}
                  className="w-28 px-2 py-1 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-900 dark:text-white"
                >
                  {questionOptions.map(option => (
                    <option key={option} value={option}>{option}</option>
                  ))}
                </select>
              </div>

              {/* Difficulty Selector */}
              <div className="flex items-center space-x-2">
                <label className="text-gray-700 dark:text-gray-300 font-medium">Difficulty:</label>
                <div className="flex space-x-2">
                  {difficultyOptions.map(option => (
                    <button
                      key={option.value}
                      onClick={() => setDifficulty(option.value)}
                      className={`px-3 py-1 rounded text-sm font-medium ${
                        difficulty === option.value
                          ? 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300'
                          : 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-600'
                      }`}
                    >
                      {option.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Question Types Selector */}
              <div className="space-y-2">
                <label className="text-gray-700 dark:text-gray-300 font-medium">Question Types:</label>
                <div className="grid grid-cols-2 gap-2">
                  {questionTypeOptions.map(option => (
                    <label key={option.value} className="flex items-center space-x-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={questionTypes.includes(option.value)}
                        onChange={e => {
                          if (e.target.checked) {
                            setQuestionTypes([...questionTypes, option.value]);
                          } else {
                            setQuestionTypes(questionTypes.filter(type => type !== option.value));
                          }
                        }}
                        className="rounded focus:ring-2 focus:ring-blue-500"
                      />
                      <span className="text-sm">{option.icon} {option.label}</span>
                    </label>
                  ))}
                </div>
              </div>

              {numQuestions > 50 && (
                <p className="text-red-600 dark:text-red-400 text-sm mt-1">Maximum allowed is 50 questions.</p>
              )}
              
              <button
                onClick={handleGenerateQuiz}
                disabled={quizState.isGenerating || questionTypes.length === 0}
                className="w-full px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
              >
                {quizState.isGenerating ? (
                  <span className="flex items-center justify-center">
                    <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Generating Quiz...
                  </span>
                ) : (
                  'Generate Quiz'
                )}
              </button>
            </div>
          )}

          {/* Error Display */}
          {quizState.error && (
            <div className="mt-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
              <p className="text-red-600 dark:text-red-400 text-sm">{quizState.error}</p>
            </div>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
              🧠 Interactive Quiz
            </h2>
            <div className="flex items-center space-x-4 mt-1">
              <span className={`text-sm font-medium ${getSourceIndicator().color}`}>
                {getSourceIndicator().text}
              </span>
              <span className="text-sm text-gray-500 dark:text-gray-400">
                {quizState.difficulty} • {quizState.questionTypes?.join(', ') || 'MCQ'}
              </span>
            </div>
          </div>
          <button
            onClick={handleReset}
            className="px-3 py-1 text-sm text-red-600 dark:text-red-400 hover:text-red-800 dark:hover:text-red-300 font-medium"
          >
            Reset Quiz
          </button>
        </div>

        {/* Progress Bar */}
        <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2 mb-2">
          <motion.div
            className="bg-blue-600 h-2 rounded-full"
            initial={{ width: 0 }}
            animate={{ width: `${getProgressPercentage()}%` }}
            transition={{ duration: 0.3 }}
          />
        </div>
        <p className="text-sm text-gray-600 dark:text-gray-400">
          Question {quizState.currentQuestionIndex + 1} of {quizState.questions.length}
        </p>
      </div>

      {/* Quiz Completed View */}
      {quizState.isCompleted ? (
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700">
          <div className="text-center">
            <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
              Quiz Completed! 🎉
            </h3>
            <div className={`text-4xl font-bold mb-4 ${getScoreColor(quizState.score)}`}>
              {quizState.score.toFixed(1)}%
            </div>
            <p className="text-gray-600 dark:text-gray-400 mb-6">
              You answered {Math.round((quizState.score / 100) * quizState.questions.length)} out of {quizState.questions.length} questions correctly.
            </p>
            
            <div className="space-y-4">
              <button
                onClick={handleReset}
                className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium"
              >
                Take Quiz Again
              </button>
            </div>
          </div>
        </div>
      ) : (
        /* Question View */
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700">
          {currentQuestion && (
            <div className="space-y-6">
              {/* Question Header */}
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                    {currentQuestion.question}
                  </h3>
                  <div className="flex items-center space-x-4 text-sm text-gray-500 dark:text-gray-400">
                    <span>Topic: {currentQuestion.topic}</span>
                    <span className={`font-medium ${getDifficultyColor(currentQuestion.difficulty || 'medium')}`}>
                      {currentQuestion.difficulty || 'medium'}
                    </span>
                    <span className="flex items-center">
                      {getQuestionTypeIcon(currentQuestion.type || 'mcq')} {currentQuestion.type || 'mcq'}
                    </span>
                  </div>
                </div>
              </div>

              {/* Answer Options */}
              <div className="space-y-3">
                {currentQuestion.options.map((option, index) => (
                  <motion.button
                    key={index}
                    onClick={() => handleAnswerSelect(option)}
                    className={`w-full p-4 text-left rounded-lg border-2 transition-all duration-200 ${
                      userAnswer === option
                        ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300'
                        : 'border-gray-200 dark:border-gray-600 hover:border-gray-300 dark:hover:border-gray-500 text-gray-700 dark:text-gray-300'
                    }`}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <span className="font-medium">{String.fromCharCode(65 + index)}.</span> {option}
                  </motion.button>
                ))}
              </div>

              {/* Explanation */}
              {showExplanation && currentQuestion.explanation && (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg"
                >
                  <h4 className="font-semibold text-green-800 dark:text-green-300 mb-2">
                    Explanation:
                  </h4>
                  <p className="text-green-700 dark:text-green-400 text-sm">
                    {currentQuestion.explanation}
                  </p>
                </motion.div>
              )}

              {/* Navigation */}
              <div className="flex justify-between pt-4">
                <button
                  onClick={handlePrevious}
                  disabled={isFirstQuestion}
                  className="px-4 py-2 text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
                >
                  ← Previous
                </button>

                <button
                  onClick={handleNext}
                  disabled={!userAnswer}
                  className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
                >
                  {isLastQuestion ? 'Complete Quiz' : 'Next →'}
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Error Display */}
      {quizState.error && (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
          <p className="text-red-600 dark:text-red-400 text-sm">{quizState.error}</p>
        </div>
      )}
    </div>
  );
};

export default Quiz; 