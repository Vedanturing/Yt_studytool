import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Video } from '../types';
import { TranscriptionModal } from './TranscriptionModal';

interface VideoCardProps {
  video: Video;
  index: number;
}

const VideoCard: React.FC<VideoCardProps> = ({ video, index }) => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [imageError, setImageError] = useState(false);

  const formatNumber = (num: number): string => {
    if (num >= 1000000) {
      return (num / 1000000).toFixed(1) + 'M';
    }
    if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
  };

  const formatDate = (dateString?: string): string => {
    if (!dateString) return 'Unknown date';
    try {
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      });
    } catch {
      return 'Unknown date';
    }
  };

  const truncateText = (text: string, maxLength: number): string => {
    if (text.length <= maxLength) return text;
    return text.slice(0, maxLength) + '...';
  };

  const handleImageError = () => {
    setImageError(true);
  };

  return (
    <>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ 
          duration: 0.5, 
          delay: index * 0.1,
          ease: "easeOut"
        }}
        whileHover={{ 
          y: -8,
          transition: { duration: 0.2 }
        }}
        className="bg-white dark:bg-gray-800 rounded-xl shadow-lg hover:shadow-2xl transition-all duration-300 overflow-hidden border border-gray-200 dark:border-gray-700 group"
      >
        {/* Thumbnail Section */}
        <div className="relative overflow-hidden">
          {!imageError ? (
            <motion.img
              whileHover={{ scale: 1.05 }}
              transition={{ duration: 0.3 }}
              src={video.thumbnail_url}
              alt={video.title}
              onError={handleImageError}
              className="w-full h-48 object-cover transition-transform duration-300"
            />
          ) : (
            <div className="w-full h-48 bg-gradient-to-br from-gray-200 to-gray-300 dark:from-gray-700 dark:to-gray-600 flex items-center justify-center">
              <div className="text-center text-gray-500 dark:text-gray-400">
                <svg className="w-12 h-12 mx-auto mb-2" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4l4-8 3 6 2-4 3 6z" clipRule="evenodd" />
                </svg>
                <p className="text-sm">No thumbnail</p>
              </div>
            </div>
          )}
          
          {/* Overlay with quick actions */}
          <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-20 transition-all duration-300 flex items-center justify-center opacity-0 group-hover:opacity-100">
            <motion.a
              initial={{ scale: 0 }}
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.95 }}
              animate={{ scale: 1 }}
              href={video.video_url}
              target="_blank"
              rel="noopener noreferrer"
              className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg font-medium flex items-center gap-2 shadow-lg"
            >
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clipRule="evenodd" />
              </svg>
              Watch
            </motion.a>
          </div>
        </div>

        {/* Content Section */}
        <div className="p-6 space-y-4">
          {/* Title */}
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white leading-tight group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors duration-200">
            {truncateText(video.title, 80)}
          </h3>

          {/* Stats */}
          <div className="flex flex-wrap gap-4 text-sm">
            <motion.div 
              whileHover={{ scale: 1.05 }}
              className="flex items-center gap-1 bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 px-3 py-1 rounded-full"
            >
              <span>👁️</span>
              <span className="font-medium">{formatNumber(video.views)}</span>
            </motion.div>
            <motion.div 
              whileHover={{ scale: 1.05 }}
              className="flex items-center gap-1 bg-red-50 dark:bg-red-900/30 text-red-700 dark:text-red-300 px-3 py-1 rounded-full"
            >
              <span>❤️</span>
              <span className="font-medium">{formatNumber(video.likes)}</span>
            </motion.div>
            <motion.div 
              whileHover={{ scale: 1.05 }}
              className="flex items-center gap-1 bg-green-50 dark:bg-green-900/30 text-green-700 dark:text-green-300 px-3 py-1 rounded-full"
            >
              <span>💬</span>
              <span className="font-medium">{formatNumber(video.comment_count)}</span>
            </motion.div>
          </div>

          {/* Publish Date */}
          {video.published_date && (
            <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
              <span>📅</span>
              <span>{formatDate(video.published_date)}</span>
            </div>
          )}

          {/* Description */}
          <p className="text-gray-600 dark:text-gray-300 text-sm leading-relaxed">
            {truncateText(video.description, 120)}
          </p>

          {/* Top Comments Preview */}
          {video.top_comments && video.top_comments.length > 0 && (
            <div className="border-t border-gray-200 dark:border-gray-700 pt-4">
              <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 flex items-center gap-2">
                <span>💭</span>
                Top Comment
              </h4>
              <div className="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-3">
                <p className="text-sm text-gray-600 dark:text-gray-300 italic">
                  "{truncateText(video.top_comments[0].text, 100)}"
                </p>
                <div className="flex items-center justify-between mt-2 text-xs text-gray-500 dark:text-gray-400">
                  <span>— {video.top_comments[0].author}</span>
                  <span className="flex items-center gap-1">
                    <span>👍</span>
                    {video.top_comments[0].likes}
                  </span>
                </div>
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex gap-2 pt-2">
            <motion.a
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              href={video.video_url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex-1 bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 text-center"
            >
              🎬 Watch Video
            </motion.a>
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => setIsModalOpen(true)}
              className="bg-gradient-to-r from-purple-500 to-purple-600 hover:from-purple-600 hover:to-purple-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200"
            >
              🎯 Transcribe
            </motion.button>
          </div>
        </div>
      </motion.div>

      {/* Transcription Modal */}
      <TranscriptionModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        video={video}
      />
    </>
  );
};

export default VideoCard; 