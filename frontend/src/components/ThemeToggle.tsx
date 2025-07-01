import React from 'react';
import { motion } from 'framer-motion';
import { useTheme } from '../contexts/ThemeContext';
import { Theme } from '../types';

const ThemeToggle: React.FC = () => {
  const { theme, setTheme, isDark } = useTheme();

  const themes: { value: Theme; label: string; icon: string }[] = [
    { value: 'light', label: 'Light', icon: '☀️' },
    { value: 'dark', label: 'Dark', icon: '🌙' },
    { value: 'system', label: 'System', icon: '💻' },
  ];

  return (
    <div className="flex items-center gap-1 bg-gray-100 dark:bg-gray-700 rounded-lg p-1">
      {themes.map((themeOption) => (
        <motion.button
          key={themeOption.value}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={() => setTheme(themeOption.value)}
          className={`
            px-3 py-1.5 rounded-md text-sm font-medium transition-all duration-200
            flex items-center gap-1.5
            ${
              theme === themeOption.value
                ? 'bg-white dark:bg-gray-600 text-gray-900 dark:text-gray-100 shadow-sm'
                : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
            }
          `}
          title={`Switch to ${themeOption.label} theme`}
        >
          <span className="text-xs">{themeOption.icon}</span>
          <span className="hidden sm:inline">{themeOption.label}</span>
        </motion.button>
      ))}
    </div>
  );
};

export default ThemeToggle; 