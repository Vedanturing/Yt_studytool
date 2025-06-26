import React from 'react';
import { motion } from 'framer-motion';
import { useVideoStore } from '../store/useVideoStore';
import { SortOption } from '../types';

const FilterControls: React.FC = () => {
  const { filterState, setSortBy, videos, exportToExcel, exportToPdf } = useVideoStore();

  const sortOptions: { value: SortOption; label: string; icon: string }[] = [
    { value: 'relevance', label: 'Relevance', icon: '🎯' },
    { value: 'views', label: 'Views', icon: '👁️' },
    { value: 'likes', label: 'Likes', icon: '❤️' },
    { value: 'date', label: 'Date', icon: '📅' },
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 mb-6 border border-gray-200 dark:border-gray-700"
    >
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
        {/* Sort Options */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4">
          <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 whitespace-nowrap">
            Sort by:
          </h3>
          <div className="flex flex-wrap gap-2">
            {sortOptions.map((option) => (
              <motion.button
                key={option.value}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => setSortBy(option.value)}
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

        {/* Export Options */}
        {videos.length > 0 && (
          <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4">
            <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 whitespace-nowrap">
              Export:
            </h3>
            <div className="flex gap-2">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => exportToExcel(videos)}
                className="px-4 py-2 bg-green-500 hover:bg-green-600 text-white rounded-lg text-sm font-medium transition-colors duration-200 flex items-center gap-2"
              >
                <span>📊</span>
                Excel
              </motion.button>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => exportToPdf(videos)}
                className="px-4 py-2 bg-red-500 hover:bg-red-600 text-white rounded-lg text-sm font-medium transition-colors duration-200 flex items-center gap-2"
              >
                <span>📄</span>
                PDF
              </motion.button>
            </div>
          </div>
        )}
      </div>

      {/* Results Count */}
      {videos.length > 0 && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700"
        >
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Showing <span className="font-semibold text-blue-600 dark:text-blue-400">{videos.length}</span> results
            {filterState.sortBy !== 'relevance' && (
              <span> sorted by <span className="font-semibold">{sortOptions.find(opt => opt.value === filterState.sortBy)?.label}</span></span>
            )}
          </p>
        </motion.div>
      )}
    </motion.div>
  );
};

export default FilterControls; 