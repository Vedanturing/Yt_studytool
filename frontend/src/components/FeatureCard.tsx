import React from 'react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';

interface FeatureCardProps {
  icon: string;
  title: string;
  description: string;
  route: string;
  tags?: string[];
  gradient: string;
  delay?: number;
}

const FeatureCard: React.FC<FeatureCardProps> = ({
  icon,
  title,
  description,
  route,
  tags = [],
  gradient,
  delay = 0
}) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      whileInView={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, delay }}
      viewport={{ once: true }}
      whileHover={{ y: -8 }}
      className="group"
    >
      <Link to={route} className="block">
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6 border border-gray-200 dark:border-gray-700 hover:shadow-2xl transition-all duration-300 h-full">
          {/* Icon */}
          <motion.div
            whileHover={{ scale: 1.1, rotate: 5 }}
            className={`w-14 h-14 bg-gradient-to-r ${gradient} rounded-xl flex items-center justify-center text-2xl mb-4 group-hover:shadow-lg transition-shadow duration-300`}
          >
            {icon}
          </motion.div>

          {/* Title */}
          <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-3 group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors duration-200">
            {title}
          </h3>

          {/* Description */}
          <p className="text-gray-600 dark:text-gray-300 mb-4 leading-relaxed">
            {description}
          </p>

          {/* Tags */}
          {tags.length > 0 && (
            <div className="flex flex-wrap gap-2 mb-4">
              {tags.map((tag, index) => (
                <span
                  key={index}
                  className="px-2 py-1 bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 text-xs rounded-full font-medium"
                >
                  {tag}
                </span>
              ))}
            </div>
          )}

          {/* Arrow indicator */}
          <div className="flex items-center justify-between">
            <span className="text-indigo-600 dark:text-indigo-400 font-medium text-sm group-hover:translate-x-1 transition-transform duration-200">
              Get Started
            </span>
            <motion.svg
              className="w-5 h-5 text-indigo-600 dark:text-indigo-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              initial={{ x: 0 }}
              whileHover={{ x: 4 }}
              transition={{ duration: 0.2 }}
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 5l7 7-7 7"
              />
            </motion.svg>
          </div>
        </div>
      </Link>
    </motion.div>
  );
};

export default FeatureCard; 