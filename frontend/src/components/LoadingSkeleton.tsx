import React from 'react';
import { motion } from 'framer-motion';

interface LoadingSkeletonProps {
  count?: number;
}

const SkeletonCard: React.FC = () => (
  <motion.div
    initial={{ opacity: 0 }}
    animate={{ opacity: 1 }}
    className="bg-white dark:bg-gray-800 rounded-xl shadow-md p-6 space-y-4"
  >
    {/* Thumbnail skeleton */}
    <div className="relative">
      <motion.div
        animate={{
          backgroundPosition: ['200% 0', '-200% 0'],
        }}
        transition={{
          duration: 1.5,
          repeat: Infinity,
          ease: 'linear',
        }}
        className="w-full h-48 bg-gradient-to-r from-gray-200 via-gray-300 to-gray-200 dark:from-gray-700 dark:via-gray-600 dark:to-gray-700 rounded-lg"
        style={{
          backgroundSize: '400% 100%',
        }}
      />
    </div>

    {/* Title skeleton */}
    <div className="space-y-2">
      <motion.div
        animate={{
          backgroundPosition: ['200% 0', '-200% 0'],
        }}
        transition={{
          duration: 1.5,
          repeat: Infinity,
          ease: 'linear',
          delay: 0.1,
        }}
        className="h-4 bg-gradient-to-r from-gray-200 via-gray-300 to-gray-200 dark:from-gray-700 dark:via-gray-600 dark:to-gray-700 rounded w-3/4"
        style={{
          backgroundSize: '400% 100%',
        }}
      />
      <motion.div
        animate={{
          backgroundPosition: ['200% 0', '-200% 0'],
        }}
        transition={{
          duration: 1.5,
          repeat: Infinity,
          ease: 'linear',
          delay: 0.2,
        }}
        className="h-4 bg-gradient-to-r from-gray-200 via-gray-300 to-gray-200 dark:from-gray-700 dark:via-gray-600 dark:to-gray-700 rounded w-1/2"
        style={{
          backgroundSize: '400% 100%',
        }}
      />
    </div>

    {/* Stats skeleton */}
    <div className="flex space-x-4">
      {[1, 2, 3].map((i) => (
        <motion.div
          key={i}
          animate={{
            backgroundPosition: ['200% 0', '-200% 0'],
          }}
          transition={{
            duration: 1.5,
            repeat: Infinity,
            ease: 'linear',
            delay: 0.1 * i,
          }}
          className="h-3 bg-gradient-to-r from-gray-200 via-gray-300 to-gray-200 dark:from-gray-700 dark:via-gray-600 dark:to-gray-700 rounded w-16"
          style={{
            backgroundSize: '400% 100%',
          }}
        />
      ))}
    </div>

    {/* Description skeleton */}
    <div className="space-y-2">
      {[1, 2, 3].map((i) => (
        <motion.div
          key={i}
          animate={{
            backgroundPosition: ['200% 0', '-200% 0'],
          }}
          transition={{
            duration: 1.5,
            repeat: Infinity,
            ease: 'linear',
            delay: 0.05 * i,
          }}
          className="h-3 bg-gradient-to-r from-gray-200 via-gray-300 to-gray-200 dark:from-gray-700 dark:via-gray-600 dark:to-gray-700 rounded"
          style={{
            backgroundSize: '400% 100%',
            width: i === 3 ? '60%' : '100%',
          }}
        />
      ))}
    </div>
  </motion.div>
);

export const LoadingSkeleton: React.FC<LoadingSkeletonProps> = ({ count = 6 }) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {Array.from({ length: count }, (_, i) => (
        <SkeletonCard key={i} />
      ))}
    </div>
  );
}; 