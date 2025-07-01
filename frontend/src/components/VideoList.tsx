import React from 'react';
import { motion } from 'framer-motion';
import { useVideoStore } from '../store/useVideoStore';
import VideoCard from './VideoCard';
import { LoadingSkeleton } from './LoadingSkeleton';
import Pagination from './Pagination';

const VideoList: React.FC = () => {
  const { paginatedVideos, filteredVideos, loading, error } = useVideoStore();

  if (loading) {
    return <LoadingSkeleton count={12} />;
  }

  if (error) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center py-12"
      >
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl p-8 max-w-md mx-auto">
          <div className="text-red-600 dark:text-red-400 text-6xl mb-4">⚠️</div>
          <h3 className="text-lg font-semibold text-red-900 dark:text-red-200 mb-2">
            Error Loading Videos
          </h3>
          <p className="text-red-700 dark:text-red-300">{error}</p>
        </div>
      </motion.div>
    );
  }

  if (filteredVideos.length === 0) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center py-12"
      >
        <div className="text-gray-400 dark:text-gray-500 text-6xl mb-4">🔍</div>
        <h3 className="text-lg font-semibold text-gray-700 dark:text-gray-300 mb-2">
          No videos found
        </h3>
        <p className="text-gray-600 dark:text-gray-400">
          Try searching for something else or adjusting your filters.
        </p>
      </motion.div>
    );
  }

  return (
    <div>
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6"
    >
        {paginatedVideos.map((video, index) => (
          <motion.div
            key={`${video.video_url}-${index}`}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
          >
        <VideoCard
          video={video}
          index={index}
        />
          </motion.div>
      ))}
    </motion.div>
      
      <Pagination />
    </div>
  );
};

export default VideoList; 