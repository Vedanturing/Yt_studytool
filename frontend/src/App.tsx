import React from 'react';
import { motion } from 'framer-motion';
import { ThemeProvider, useTheme } from './contexts/ThemeContext';
import SearchBar from './components/SearchBar';
import VideoList from './components/VideoList';
import FilterControls from './components/FilterControls';
import { useVideoStore } from './store/useVideoStore';

const AppContent: React.FC = () => {
  const { theme, toggleTheme } = useTheme();
  const { videos, totalCount, source } = useVideoStore();

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50 dark:from-gray-900 dark:to-blue-900 transition-all duration-300">
      {/* Header */}
      <motion.header
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-lg border-b border-gray-200 dark:border-gray-700 sticky top-0 z-50"
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            {/* Logo/Title */}
            <motion.div
              whileHover={{ scale: 1.05 }}
              className="flex items-center gap-3"
            >
              <div className="w-10 h-10 bg-gradient-to-br from-red-500 to-red-600 rounded-xl flex items-center justify-center shadow-lg">
                <span className="text-white text-xl font-bold">▶️</span>
              </div>
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-red-600 to-blue-600 bg-clip-text text-transparent">
                  YouTube Explorer
                </h1>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Discover and analyze YouTube content
                </p>
              </div>
            </motion.div>

            {/* Theme Toggle */}
            <motion.button
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              onClick={toggleTheme}
              className="p-3 rounded-xl bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
            >
              {theme === 'light' ? (
                <svg className="w-5 h-5 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
                </svg>
              ) : (
                <svg className="w-5 h-5 text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
                </svg>
              )}
            </motion.button>
          </div>
        </div>
      </motion.header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="space-y-8">
          {/* Search Section */}
          <motion.section
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center space-y-6"
          >
            <div className="space-y-2">
              <h2 className="text-4xl font-bold text-gray-900 dark:text-white">
                Explore YouTube Content
              </h2>
              <p className="text-lg text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
                Search, analyze, and transcribe YouTube videos with AI-powered insights
              </p>
            </div>
            <SearchBar />
          </motion.section>

          {/* Results Section */}
          {videos.length > 0 && (
            <motion.section
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="space-y-6"
            >
              {/* Results Header */}
              <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-lg rounded-2xl shadow-lg p-6 border border-gray-200 dark:border-gray-700">
                <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                  <div>
                    <h3 className="text-2xl font-bold text-gray-900 dark:text-white">
                      Found {totalCount} videos
                    </h3>
                    <p className="text-gray-600 dark:text-gray-400 flex items-center gap-2">
                      <span className={source === 'api' ? 'text-green-600 dark:text-green-400' : 'text-orange-600 dark:text-orange-400'}>
                        {source === 'api' ? '🟢' : '🟡'}
                      </span>
                      Data source: {source === 'api' ? 'YouTube Data API' : 'yt-dlp fallback'}
                    </p>
                  </div>
                  {source === 'yt-dlp' && (
                    <motion.div
                      initial={{ opacity: 0, scale: 0.9 }}
                      animate={{ opacity: 1, scale: 1 }}
                      className="bg-orange-50 dark:bg-orange-900/20 border border-orange-200 dark:border-orange-800 rounded-xl px-4 py-2"
                    >
                      <div className="flex items-center text-sm text-orange-800 dark:text-orange-200">
                        <svg className="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                        </svg>
                        Using fallback method (limited data)
                      </div>
                    </motion.div>
                  )}
                </div>
              </div>

              {/* Filter Controls */}
              <FilterControls />

              {/* Video Grid */}
              <VideoList />
            </motion.section>
          )}

          {/* Welcome Section (when no videos) */}
          {videos.length === 0 && (
            <motion.section
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="text-center py-16"
            >
              <div className="space-y-6">
                <div className="text-8xl">🎬</div>
                <div className="space-y-2">
                  <h3 className="text-2xl font-bold text-gray-900 dark:text-white">
                    Welcome to YouTube Explorer
                  </h3>
                  <p className="text-gray-600 dark:text-gray-400 max-w-lg mx-auto">
                    Start by searching for any topic to discover the most popular YouTube videos 
                    with detailed analytics and AI-powered transcription capabilities.
                  </p>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto mt-12">
                  {[
                    { icon: '🔍', title: 'Smart Search', desc: 'Find top videos by popularity and relevance' },
                    { icon: '📊', title: 'Rich Analytics', desc: 'View detailed stats, comments, and insights' },
                    { icon: '🎯', title: 'AI Transcription', desc: 'Generate transcripts and summaries automatically' }
                  ].map((feature, i) => (
                    <motion.div
                      key={feature.title}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.6 + i * 0.1 }}
                      className="bg-white/50 dark:bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 border border-gray-200 dark:border-gray-700"
                    >
                      <div className="text-3xl mb-3">{feature.icon}</div>
                      <h4 className="font-semibold text-gray-900 dark:text-white mb-2">
                        {feature.title}
                      </h4>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        {feature.desc}
                      </p>
                    </motion.div>
                  ))}
                </div>
              </div>
            </motion.section>
          )}
        </div>
      </main>

      {/* Footer */}
      <motion.footer
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1 }}
        className="mt-16 bg-white/50 dark:bg-gray-800/50 backdrop-blur-sm border-t border-gray-200 dark:border-gray-700"
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center text-gray-600 dark:text-gray-400">
            <p>Built with React, TypeScript, TailwindCSS, and Framer Motion</p>
            <p className="text-sm mt-2">Powered by YouTube Data API and AI transcription</p>
          </div>
        </div>
      </motion.footer>
    </div>
  );
};

const App: React.FC = () => {
  return (
    <ThemeProvider>
      <AppContent />
    </ThemeProvider>
  );
};

export default App; 