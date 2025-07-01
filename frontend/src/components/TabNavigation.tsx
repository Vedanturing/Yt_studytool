import React from 'react';
import { motion } from 'framer-motion';
import { useVideoStore } from '../store/useVideoStore';
import { TabType } from '../types';

const TabNavigation: React.FC = () => {
  const { activeTab, setActiveTab, filteredVideos } = useVideoStore();

  const tabs: { id: TabType; label: string; icon: string; count?: number }[] = [
    { 
      id: 'overview', 
      label: 'Overview', 
      icon: '📊', 
      count: filteredVideos.length 
    },
    { 
      id: 'transcription', 
      label: 'Transcription', 
      icon: '📝' 
    },
    { 
      id: 'summary', 
      label: 'Summary', 
      icon: '📋' 
    },
    { 
      id: 'learning', 
      label: 'Learning', 
      icon: '🧠' 
    },
    { 
      id: 'comments', 
      label: 'Comments', 
      icon: '💬' 
    },
  ];

  // Don't render if no videos
  if (filteredVideos.length === 0) {
    return null;
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 mb-6">
      <div className="flex overflow-x-auto scrollbar-hide">
        {tabs.map((tab) => (
          <motion.button
            key={tab.id}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => setActiveTab(tab.id)}
            className={`
              flex items-center gap-2 px-6 py-4 text-sm font-medium transition-all duration-200
              border-b-2 whitespace-nowrap
              ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/20'
                  : 'border-transparent text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700/50'
              }
            `}
          >
            <span>{tab.icon}</span>
            <span>{tab.label}</span>
            {tab.count !== undefined && (
              <span className={`
                px-2 py-1 rounded-full text-xs font-medium
                ${
                  activeTab === tab.id
                    ? 'bg-blue-100 dark:bg-blue-800 text-blue-700 dark:text-blue-300'
                    : 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400'
                }
              `}>
                {tab.count}
              </span>
            )}
          </motion.button>
        ))}
      </div>
    </div>
  );
};

export default TabNavigation;