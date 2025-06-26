import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useVideoStore } from '../store/useVideoStore';

const SearchBar: React.FC = () => {
  const { keyword, setKeyword, fetchVideos, loading } = useVideoStore();
  const [inputValue, setInputValue] = useState(keyword);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (inputValue.trim()) {
      setKeyword(inputValue.trim());
      fetchVideos(inputValue.trim());
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setInputValue(e.target.value);
  };

  const clearSearch = () => {
    setInputValue('');
    setKeyword('');
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      className="w-full max-w-4xl mx-auto"
    >
      <form onSubmit={handleSubmit} className="relative">
        <div className="relative flex items-center">
          {/* Search Icon */}
          <div className="absolute left-4 z-10">
            <svg
              className="w-5 h-5 text-gray-400 dark:text-gray-500"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
              />
            </svg>
          </div>

          {/* Input Field */}
          <motion.input
            whileFocus={{ scale: 1.02 }}
            type="text"
            value={inputValue}
            onChange={handleInputChange}
            placeholder="Search for YouTube videos..."
            disabled={loading}
            className={`
              w-full pl-12 pr-24 py-4 text-lg
              bg-white dark:bg-gray-800 
              border-2 border-gray-200 dark:border-gray-700
              rounded-2xl shadow-lg
              focus:outline-none focus:border-blue-500 dark:focus:border-blue-400
              focus:ring-4 focus:ring-blue-500/20 dark:focus:ring-blue-400/20
              text-gray-900 dark:text-white
              placeholder-gray-500 dark:placeholder-gray-400
              transition-all duration-200
              ${loading ? 'opacity-50 cursor-not-allowed' : ''}
            `}
          />

          {/* Clear Button */}
          {inputValue && (
            <motion.button
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.8 }}
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              type="button"
              onClick={clearSearch}
              className="absolute right-16 p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </motion.button>
          )}

          {/* Search Button */}
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            type="submit"
            disabled={loading || !inputValue.trim()}
            className={`
              absolute right-2 px-6 py-2 rounded-xl font-medium
              transition-all duration-200
              ${
                loading || !inputValue.trim()
                  ? 'bg-gray-200 dark:bg-gray-700 text-gray-400 dark:text-gray-500 cursor-not-allowed'
                  : 'bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white shadow-lg hover:shadow-xl'
              }
            `}
          >
            {loading ? (
              <div className="flex items-center gap-2">
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                  className="w-4 h-4 border-2 border-current border-t-transparent rounded-full"
                />
                <span className="hidden sm:inline">Searching...</span>
              </div>
            ) : (
              <div className="flex items-center gap-2">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
                <span className="hidden sm:inline">Search</span>
              </div>
            )}
          </motion.button>
        </div>

        {/* Search Suggestions */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="mt-4 flex flex-wrap gap-2 justify-center"
        >
          {['React tutorials', 'JavaScript ES6', 'Web development', 'Python programming', 'CSS animations'].map((suggestion) => (
            <motion.button
              key={suggestion}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              type="button"
              onClick={() => {
                setInputValue(suggestion);
                setKeyword(suggestion);
                fetchVideos(suggestion);
              }}
              className="px-3 py-1 text-sm bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-full hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
            >
              {suggestion}
            </motion.button>
          ))}
        </motion.div>
      </form>
    </motion.div>
  );
};

export default SearchBar; 