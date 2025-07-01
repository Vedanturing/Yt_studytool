import React from 'react';
import { ThemeProvider } from './contexts/ThemeContext';
import { SearchBar } from './components/SearchBar';
import FilterControls from './components/FilterControls';
import TabNavigation from './components/TabNavigation';
import VideoList from './components/VideoList';
import ThemeToggle from './components/ThemeToggle';
import LearningMode from './components/LearningMode';
import { useVideoStore } from './store/useVideoStore';
import './index.css';

function AppContent() {
  const { activeTab } = useVideoStore();

  const renderTabContent = () => {
    switch (activeTab) {
      case 'overview':
        return <VideoList />;
      case 'transcription':
        return (
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
              Video Transcription
            </h2>
            <p className="text-gray-600 dark:text-gray-400">
              Select a video from the overview tab and click the transcribe button to view transcriptions here.
            </p>
          </div>
        );
      case 'summary':
        return (
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
              AI Summary
            </h2>
            <p className="text-gray-600 dark:text-gray-400">
              Transcribe a video first to generate AI-powered summaries.
            </p>
          </div>
        );
      case 'learning':
        return <LearningMode />;
      case 'comments':
        return (
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
              Video Comments
            </h2>
            <p className="text-gray-600 dark:text-gray-400">
              View and analyze comments from the selected videos.
            </p>
          </div>
        );
      default:
        return <VideoList />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors duration-200">
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-7xl mx-auto">
          {/* Header with Theme Toggle */}
          <div className="flex items-center justify-between mb-8">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
                YouTube Video Search
              </h1>
              <p className="text-gray-600 dark:text-gray-400">
                Search, filter, and analyze YouTube videos with AI-powered transcription and summarization
              </p>
            </div>
            <ThemeToggle />
          </div>

          {/* Search Bar */}
      <SearchBar />

          {/* Filter Controls */}
          <FilterControls />

          {/* Tab Navigation */}
          <TabNavigation />

          {/* Tab Content */}
          {renderTabContent()}
        </div>
      </div>
    </div>
  );
}

function App() {
  return (
    <ThemeProvider>
      <AppContent />
    </ThemeProvider>
  );
}

export default App; 