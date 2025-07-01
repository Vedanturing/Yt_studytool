import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useVideoStore } from '../store/useVideoStore';

const LearningMode: React.FC = () => {
  const {
    learningModeState,
    setCurrentCard,
    toggleAnswer,
    rateCard,
    resetLearningMode
  } = useVideoStore();

  const {
    flashcards,
    currentCardIndex,
    showAnswer,
    cardProgress,
    isGenerating,
    error,
    video_title
  } = learningModeState;

  if (isGenerating) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-8 border border-gray-200 dark:border-gray-700">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
            Generating Learning Cards...
          </h2>
          <p className="text-gray-600 dark:text-gray-400">
            AI is analyzing the video content and creating personalized flashcards for you.
          </p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-8 border border-gray-200 dark:border-gray-700">
        <div className="text-center">
          <div className="text-red-500 text-4xl mb-4">❌</div>
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
            Failed to Generate Learning Mode
          </h2>
          <p className="text-gray-600 dark:text-gray-400 mb-4">{error}</p>
          <button
            onClick={resetLearningMode}
            className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg font-medium transition-colors"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  if (flashcards.length === 0) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-8 border border-gray-200 dark:border-gray-700">
        <div className="text-center">
          <div className="text-gray-400 text-4xl mb-4">🧠</div>
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
            Learning Mode
          </h2>
          <p className="text-gray-600 dark:text-gray-400">
            Click the "🧠 Learn" button on any video card to generate AI-powered flashcards and start learning!
          </p>
        </div>
      </div>
    );
  }

  const currentCard = flashcards[currentCardIndex];
  const totalCards = flashcards.length;
  const completedCards = Object.keys(cardProgress).length;
  const knownCards = Object.values(cardProgress).filter(rating => rating === 'known').length;
  const difficultCards = Object.values(cardProgress).filter(rating => rating === 'difficult').length;

  const nextCard = () => {
    if (currentCardIndex < totalCards - 1) {
      setCurrentCard(currentCardIndex + 1);
    }
  };

  const prevCard = () => {
    if (currentCardIndex > 0) {
      setCurrentCard(currentCardIndex - 1);
    }
  };

  const isLastCard = currentCardIndex === totalCards - 1;
  const isFirstCard = currentCardIndex === 0;

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-500 to-purple-600 text-white p-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold">🧠 Learning Mode</h2>
            <p className="text-blue-100 mt-1">{video_title}</p>
          </div>
          <button
            onClick={resetLearningMode}
            className="bg-white/20 hover:bg-white/30 text-white px-4 py-2 rounded-lg font-medium transition-colors"
          >
            Exit
          </button>
        </div>
        
        {/* Progress Bar */}
        <div className="mt-4">
          <div className="flex justify-between text-sm text-blue-100 mb-2">
            <span>Progress: {completedCards}/{totalCards}</span>
            <span>Card {currentCardIndex + 1} of {totalCards}</span>
          </div>
          <div className="w-full bg-white/20 rounded-full h-2">
            <div 
              className="bg-white rounded-full h-2 transition-all duration-300"
              style={{ width: `${(completedCards / totalCards) * 100}%` }}
            />
          </div>
        </div>
      </div>

      {/* Card Content */}
      <div className="p-8">
        <AnimatePresence mode="wait">
          <motion.div
            key={currentCardIndex}
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -50 }}
            transition={{ duration: 0.3 }}
            className="min-h-[300px] flex flex-col justify-center"
          >
            {/* Card Type Badge */}
            <div className="flex justify-center mb-4">
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                currentCard.type === 'mcq' 
                  ? 'bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-300'
                  : 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300'
              }`}>
                {currentCard.type === 'mcq' ? '🎯 Multiple Choice' : '💡 Fact'}
              </span>
            </div>

            {/* Question */}
            <div className="text-center mb-8">
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
                {currentCard.question}
              </h3>
            </div>

            {/* Answer Section */}
            <AnimatePresence>
              {showAnswer ? (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-6 mb-6"
                >
                  <h4 className="text-lg font-medium text-green-800 dark:text-green-300 mb-2">
                    ✅ Answer:
                  </h4>
                  <p className="text-green-700 dark:text-green-200">
                    {currentCard.answer}
                  </p>
                </motion.div>
              ) : (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="text-center mb-6"
                >
                  <button
                    onClick={toggleAnswer}
                    className="bg-blue-500 hover:bg-blue-600 text-white px-8 py-3 rounded-lg font-medium transition-colors text-lg"
                  >
                    Show Answer
                  </button>
                </motion.div>
              )}
            </AnimatePresence>

            {/* Rating Buttons (only show when answer is visible) */}
            {showAnswer && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex justify-center gap-4 mb-6"
              >
                <button
                  onClick={() => rateCard('known')}
                  className="bg-green-500 hover:bg-green-600 text-white px-6 py-3 rounded-lg font-medium transition-colors flex items-center gap-2"
                >
                  ✅ I Know This
                </button>
                <button
                  onClick={() => rateCard('difficult')}
                  className="bg-orange-500 hover:bg-orange-600 text-white px-6 py-3 rounded-lg font-medium transition-colors flex items-center gap-2"
                >
                  🤔 Need Review
                </button>
              </motion.div>
            )}

            {/* Current card progress indicator */}
            {cardProgress[currentCardIndex] && (
              <div className="text-center">
                <span className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-sm font-medium ${
                  cardProgress[currentCardIndex] === 'known'
                    ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300'
                    : 'bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-300'
                }`}>
                  {cardProgress[currentCardIndex] === 'known' ? '✅ Known' : '🤔 Needs Review'}
                </span>
              </div>
            )}
          </motion.div>
        </AnimatePresence>
      </div>

      {/* Navigation */}
      <div className="bg-gray-50 dark:bg-gray-700 px-8 py-4">
        <div className="flex justify-between items-center">
          <button
            onClick={prevCard}
            disabled={isFirstCard}
            className="flex items-center gap-2 px-4 py-2 text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            ← Previous
          </button>

          <div className="flex gap-2">
            {flashcards.map((_, index) => (
              <button
                key={index}
                onClick={() => setCurrentCard(index)}
                className={`w-3 h-3 rounded-full transition-colors ${
                  index === currentCardIndex
                    ? 'bg-blue-500'
                    : cardProgress[index]
                    ? cardProgress[index] === 'known'
                      ? 'bg-green-400'
                      : 'bg-orange-400'
                    : 'bg-gray-300 dark:bg-gray-600'
                }`}
              />
            ))}
          </div>

          <button
            onClick={nextCard}
            disabled={isLastCard}
            className="flex items-center gap-2 px-4 py-2 text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            Next →
          </button>
        </div>
      </div>

      {/* Summary (show when all cards are completed) */}
      {completedCards === totalCards && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-gradient-to-r from-green-500 to-blue-500 text-white p-6 m-6 rounded-lg"
        >
          <div className="text-center">
            <h3 className="text-xl font-bold mb-2">🎉 Learning Session Complete!</h3>
            <div className="flex justify-center gap-6 text-sm">
              <div>
                <span className="font-semibold">{knownCards}</span> concepts mastered
              </div>
              <div>
                <span className="font-semibold">{difficultCards}</span> need review
              </div>
            </div>
            <button
              onClick={resetLearningMode}
              className="mt-4 bg-white text-gray-800 px-6 py-2 rounded-lg font-medium hover:bg-gray-100 transition-colors"
            >
              Start New Session
            </button>
          </div>
        </motion.div>
      )}
    </div>
  );
};

export default LearningMode; 