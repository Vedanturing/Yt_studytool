import React from 'react';
import { motion } from 'framer-motion';
import FeatureCard from './FeatureCard';

const FeaturesSection: React.FC = () => {
  const features = [
    {
      icon: '🎓',
      title: 'Diploma Study Module',
      description: 'Complete study flow for Diploma Computer Engineering 5th Sem with auto-generated materials, quizzes, and detailed reports.',
      route: '/study',
      tags: ['Diploma Focused', 'Auto-Generated', 'Comprehensive'],
      gradient: 'from-emerald-500 to-teal-600'
    },
    {
      icon: '📚',
      title: 'Syllabus Upload & Topic Extraction',
      description: 'Upload your course syllabus and let AI automatically extract topics, learning objectives, and create a structured learning path.',
      route: '/syllabus',
      tags: ['AI-Powered', 'PDF Support', 'Auto-Extraction'],
      gradient: 'from-blue-500 to-indigo-600'
    },
    {
      icon: '🎥',
      title: 'YouTube Video Curation',
      description: 'AI finds and ranks the best YouTube videos for each topic, ensuring high-quality, relevant content for your learning journey.',
      route: '/app',
      tags: ['AI-Curated', 'Quality Ranked', 'Personalized'],
      gradient: 'from-indigo-500 to-purple-600'
    },
    {
      icon: '🧠',
      title: 'Learning Mode with Flashcards',
      description: 'Generate interactive flashcards from video content and test your knowledge with spaced repetition learning techniques.',
      route: '/learning',
      tags: ['Interactive', 'Spaced Repetition', 'AI-Generated'],
      gradient: 'from-purple-500 to-pink-600'
    },
    {
      icon: '📝',
      title: 'Quiz Generator',
      description: 'Create custom quizzes with multiple question types, difficulty levels, and offline access for continuous learning.',
      route: '/quiz',
      tags: ['Offline Available', 'Multiple Types', 'Difficulty Levels'],
      gradient: 'from-pink-500 to-red-600'
    },
    {
      icon: '📊',
      title: 'Performance Reports',
      description: 'Track your learning progress with detailed analytics, identify weak areas, and get personalized recommendations.',
      route: '/app?tab=report',
      tags: ['Analytics', 'Progress Tracking', 'Recommendations'],
      gradient: 'from-red-500 to-orange-600'
    },
    {
      icon: '🗂️',
      title: 'Study Playlist Creator',
      description: 'Organize your learning materials into custom playlists and share them with classmates or study groups.',
      route: '/app?tab=overview',
      tags: ['Customizable', 'Shareable', 'Organized'],
      gradient: 'from-orange-500 to-yellow-600'
    },
    {
      icon: '📥',
      title: 'Material Downloader',
      description: 'Download videos, notes, and study materials for offline access. Never lose your learning progress.',
      route: '/app?tab=offline',
      tags: ['Offline Access', 'Multiple Formats', 'Sync'],
      gradient: 'from-yellow-500 to-green-600'
    },
    {
      icon: '⚙️',
      title: 'Settings & Customization',
      description: 'Customize your learning experience with dark mode, notification preferences, and personalized settings.',
      route: '/app',
      tags: ['Dark Mode', 'Customizable', 'User Preferences'],
      gradient: 'from-green-500 to-teal-600'
    }
  ];

  return (
    <section id="features" className="py-20 bg-gray-50 dark:bg-gray-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <h2 className="text-3xl md:text-5xl font-bold text-gray-900 dark:text-white mb-6">
            Powerful Features for Modern Learning
          </h2>
          <p className="text-xl text-gray-600 dark:text-gray-300 max-w-3xl mx-auto">
            Everything you need to transform your learning experience, from AI-powered content curation to offline study tools.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 lg:gap-8">
          {features.map((feature, index) => (
            <FeatureCard
              key={index}
              icon={feature.icon}
              title={feature.title}
              description={feature.description}
              route={feature.route}
              tags={feature.tags}
              gradient={feature.gradient}
              delay={index * 0.1}
            />
          ))}
        </div>

        {/* Bottom CTA */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.8 }}
          viewport={{ once: true }}
          className="text-center mt-16"
        >
          <div className="bg-gradient-to-r from-indigo-600 to-purple-600 rounded-2xl p-8 text-white">
            <h3 className="text-2xl font-bold mb-4">
              Ready to Experience the Future of Learning?
            </h3>
            <p className="text-indigo-100 mb-6 max-w-2xl mx-auto">
              Join thousands of students who are already using our platform to accelerate their learning journey.
            </p>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="bg-white text-indigo-600 px-8 py-3 rounded-xl font-semibold hover:bg-gray-100 transition-colors duration-200 shadow-lg"
            >
              Start Learning Now
            </motion.button>
          </div>
        </motion.div>
      </div>
    </section>
  );
};

export default FeaturesSection; 