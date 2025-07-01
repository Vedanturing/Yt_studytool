import React from 'react';
import { motion } from 'framer-motion';
import { useVideoStore } from '../store/useVideoStore';
import { SortOption, DurationFilter, ContentTypeFilter } from '../types';

const FilterControls: React.FC = () => {
  const { 
    filterState, 
    filteredVideos, 
    setSortBy, 
    setDurationFilter,
    setContentTypeFilter,
    exportToExcel, 
    exportToPdf, 
    keyword 
  } = useVideoStore();

  const sortOptions: { value: SortOption; label: string; icon: string; description: string }[] = [
    { value: 'relevance', label: 'Relevance', icon: '🎯', description: 'Default order from search' },
    { value: 'views', label: 'Views', icon: '👁️', description: 'Highest views first' },
    { value: 'likes', label: 'Likes', icon: '❤️', description: 'Most liked first' },
    { value: 'date', label: 'Date', icon: '📅', description: 'Newest first' },
    { value: 'duration', label: 'Duration', icon: '⏱️', description: 'Longest first' },
  ];

  const durationOptions: { value: DurationFilter; label: string; icon: string; description: string }[] = [
    { value: 'all', label: 'All', icon: '🎬', description: 'All durations' },
    { value: 'short', label: 'Short', icon: '⚡', description: 'Under 4 minutes' },
    { value: 'medium', label: 'Medium', icon: '🎞️', description: '4-20 minutes' },
    { value: 'long', label: 'Long', icon: '🎭', description: 'Over 20 minutes' },
  ];

  const contentTypeOptions: { value: ContentTypeFilter; label: string; icon: string; description: string }[] = [
    { value: 'all', label: 'All', icon: '📺', description: 'All content types' },
    { value: 'videos', label: 'Videos', icon: '🎥', description: 'Regular videos' },
    { value: 'shorts', label: 'Shorts', icon: '📱', description: 'Short-form content' },
  ];

  const handleExportExcel = () => {
    exportToExcel(filteredVideos);
  };

  const handleExportPdf = () => {
    exportToPdf(filteredVideos);
  };

  // Don't render if no videos
  if (filteredVideos.length === 0) {
    return null;
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 mb-6 border border-gray-200 dark:border-gray-700"
    >
      <div className="space-y-6">
        {/* Sort Options */}
        <div className="flex flex-col lg:flex-row lg:items-start gap-4">
          <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 whitespace-nowrap pt-2">
            Sort by:
          </h3>
          <div className="flex flex-wrap gap-2">
            {sortOptions.map((option) => (
              <motion.button
                key={option.value}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => setSortBy(option.value)}
                title={option.description}
                className={`
                  px-4 py-2 rounded-full text-sm font-medium transition-all duration-200
                  flex items-center gap-2 border-2
                  ${
                    filterState.sortBy === option.value
                      ? 'bg-blue-500 text-white border-blue-500 shadow-lg'
                      : 'bg-gray-50 dark:bg-gray-700 text-gray-700 dark:text-gray-300 border-gray-200 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-600'
                  }
                `}
              >
                <span>{option.icon}</span>
                <span>{option.label}</span>
              </motion.button>
            ))}
          </div>
        </div>

        {/* Duration Filter */}
        <div className="flex flex-col lg:flex-row lg:items-start gap-4">
          <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 whitespace-nowrap pt-2">
            Duration:
          </h3>
          <div className="flex flex-wrap gap-2">
            {durationOptions.map((option) => (
              <motion.button
                key={option.value}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => setDurationFilter(option.value)}
                title={option.description}
                className={`
                  px-4 py-2 rounded-full text-sm font-medium transition-all duration-200
                  flex items-center gap-2 border-2
                  ${
                    filterState.durationFilter === option.value
                      ? 'bg-green-500 text-white border-green-500 shadow-lg'
                      : 'bg-gray-50 dark:bg-gray-700 text-gray-700 dark:text-gray-300 border-gray-200 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-600'
                  }
                `}
              >
                <span>{option.icon}</span>
                <span>{option.label}</span>
              </motion.button>
            ))}
          </div>
        </div>

        {/* Content Type Filter */}
        <div className="flex flex-col lg:flex-row lg:items-start gap-4">
          <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 whitespace-nowrap pt-2">
            Content:
          </h3>
          <div className="flex flex-wrap gap-2">
            {contentTypeOptions.map((option) => (
              <motion.button
                key={option.value}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => setContentTypeFilter(option.value)}
                title={option.description}
                className={`
                  px-4 py-2 rounded-full text-sm font-medium transition-all duration-200
                  flex items-center gap-2 border-2
                  ${
                    filterState.contentTypeFilter === option.value
                      ? 'bg-purple-500 text-white border-purple-500 shadow-lg'
                      : 'bg-gray-50 dark:bg-gray-700 text-gray-700 dark:text-gray-300 border-gray-200 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-600'
                  }
                `}
              >
                <span>{option.icon}</span>
                <span>{option.label}</span>
              </motion.button>
            ))}
          </div>
        </div>

        {/* Export and Results Info */}
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4 pt-4 border-t border-gray-200 dark:border-gray-700">
          {/* Results Info */}
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Showing <span className="font-semibold text-blue-600 dark:text-blue-400">{filteredVideos.length}</span> results
              {keyword && (
                <span> for "<span className="font-medium">{keyword}</span>"</span>
              )}
            </p>
            <div className="flex flex-wrap gap-2 text-xs text-gray-500 dark:text-gray-500">
              {filterState.sortBy !== 'relevance' && (
                <span className="bg-blue-100 dark:bg-blue-900/30 px-2 py-1 rounded-full">
                  Sorted by {sortOptions.find(opt => opt.value === filterState.sortBy)?.label}
                </span>
              )}
              {filterState.durationFilter !== 'all' && (
                <span className="bg-green-100 dark:bg-green-900/30 px-2 py-1 rounded-full">
                  {durationOptions.find(opt => opt.value === filterState.durationFilter)?.label} duration
                </span>
              )}
              {filterState.contentTypeFilter !== 'all' && (
                <span className="bg-purple-100 dark:bg-purple-900/30 px-2 py-1 rounded-full">
                  {contentTypeOptions.find(opt => opt.value === filterState.contentTypeFilter)?.label} only
                </span>
              )}
          </div>
        </div>

        {/* Export Options */}
          <div className="flex items-center gap-4">
            <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 whitespace-nowrap">
              Export:
            </h3>
            <div className="flex gap-2">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={handleExportExcel}
                className="px-4 py-2 bg-green-500 hover:bg-green-600 text-white rounded-lg text-sm font-medium transition-colors duration-200 flex items-center gap-2 shadow-md"
                title="Export current results to Excel"
              >
                <span>📊</span>
                Excel
              </motion.button>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={handleExportPdf}
                className="px-4 py-2 bg-red-500 hover:bg-red-600 text-white rounded-lg text-sm font-medium transition-colors duration-200 flex items-center gap-2 shadow-md"
                title="Export current results to PDF"
              >
                <span>📄</span>
                PDF
              </motion.button>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default FilterControls; 