import React, { useState, useRef } from 'react';
import { motion } from 'framer-motion';
import { useVideoStore } from '../store/useVideoStore';
import { SyllabusTopic } from '../types';
import toast from 'react-hot-toast';

const Syllabus: React.FC = () => {
  const {
    syllabusState,
    uploadSyllabus,
    getVideosBySyllabus,
    resetSyllabus,
    generateQuiz,
    setActiveTab,
  } = useVideoStore();

  const [textContent, setTextContent] = useState('');
  const [showTextInput, setShowTextInput] = useState(false);
  const [showQuizOptions, setShowQuizOptions] = useState(false);
  const [numQuestions, setNumQuestions] = useState<number>(10);
  const [difficulty, setDifficulty] = useState<string>('medium');
  const [questionTypes, setQuestionTypes] = useState<string[]>(['mcq', 'true_false']);
  const [subject, setSubject] = useState<string>('General');
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Validate file type
    const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
    if (!allowedTypes.includes(file.type)) {
      toast.error('Please upload a PDF or DOCX file.');
      return;
    }

    // Validate file size (10MB limit)
    if (file.size > 10 * 1024 * 1024) {
      toast.error('File size must be less than 10MB.');
      return;
    }

    try {
      await uploadSyllabus(file);
      toast.success('Syllabus uploaded successfully!');
    } catch (error) {
      toast.error('Failed to upload syllabus.');
    }
  };

  const handleTextUpload = async () => {
    if (!textContent.trim()) {
      toast.error('Please enter syllabus content.');
      return;
    }

    try {
      await uploadSyllabus(undefined, textContent);
      toast.success('Syllabus uploaded successfully!');
      setTextContent('');
      setShowTextInput(false);
    } catch (error) {
      toast.error('Failed to upload syllabus.');
    }
  };

  const handleGetVideos = async () => {
    if (syllabusState.topics.length === 0) {
      toast.error('Please upload a syllabus first.');
      return;
    }

    try {
      await getVideosBySyllabus(syllabusState.topics);
      toast.success(`Found ${syllabusState.totalVideos} videos for ${syllabusState.totalTopics} topics!`);
    } catch (error) {
      toast.error('Failed to get videos for syllabus.');
    }
  };

  const handleReset = () => {
    resetSyllabus();
    setTextContent('');
    setShowTextInput(false);
    setShowQuizOptions(false);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
    toast.success('Syllabus reset successfully.');
  };

  const handleGenerateQuiz = async () => {
    if (syllabusState.topics.length === 0) {
      toast.error('Please upload a syllabus first to generate a quiz.');
      return;
    }

    const topics = syllabusState.topics.map(topic => topic.topic);
    try {
      await generateQuiz(topics, numQuestions, difficulty, questionTypes, subject);
      setActiveTab('quiz');
      toast.success('Quiz generated successfully! Navigate to Quiz tab to start.');
    } catch (error) {
      toast.error('Failed to generate quiz.');
    }
  };

  const handleQuizTypeToggle = (type: string) => {
    setQuestionTypes(prev => 
      prev.includes(type) 
        ? prev.filter(t => t !== type)
        : [...prev, type]
    );
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
          📚 Syllabus-Based Learning
        </h2>
        <p className="text-gray-600 dark:text-gray-400">
          Upload your course syllabus to automatically find relevant YouTube videos and generate quizzes.
        </p>
      </div>

      {/* Upload Section */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Upload Syllabus
        </h3>

        <div className="space-y-4">
          {/* File Upload */}
          <div className="space-y-2">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
              Upload File (PDF or DOCX)
            </label>
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,.docx,.doc"
              onChange={handleFileUpload}
              className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 dark:file:bg-blue-900 dark:file:text-blue-300"
              disabled={syllabusState.isUploading}
            />
          </div>

          {/* Or Divider */}
          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-300 dark:border-gray-600" />
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-2 bg-white dark:bg-gray-800 text-gray-500">or</span>
            </div>
          </div>

          {/* Text Input */}
          <div className="space-y-2">
            <button
              onClick={() => setShowTextInput(!showTextInput)}
              className="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 text-sm font-medium"
            >
              {showTextInput ? 'Hide' : 'Paste'} syllabus text
            </button>
            
            {showTextInput && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="space-y-2"
              >
                <textarea
                  value={textContent}
                  onChange={(e) => setTextContent(e.target.value)}
                  placeholder="Paste your syllabus content here...&#10;&#10;Example:&#10;Unit 1: Introduction to AI&#10;1. What is Artificial Intelligence&#10;2. History of AI&#10;3. Types of AI"
                  className="w-full h-32 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white resize-none"
                  disabled={syllabusState.isUploading}
                />
                <button
                  onClick={handleTextUpload}
                  disabled={syllabusState.isUploading || !textContent.trim()}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed text-sm font-medium"
                >
                  {syllabusState.isUploading ? 'Uploading...' : 'Upload Text'}
                </button>
              </motion.div>
            )}
          </div>
        </div>

        {/* Error Display */}
        {syllabusState.error && (
          <div className="mt-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
            <p className="text-red-600 dark:text-red-400 text-sm">{syllabusState.error}</p>
          </div>
        )}
      </div>

      {/* Topics Display */}
      {syllabusState.topics.length > 0 && (
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              Parsed Topics ({syllabusState.totalTopics})
            </h3>
            <button
              onClick={handleReset}
              className="px-3 py-1 text-sm text-red-600 dark:text-red-400 hover:text-red-800 dark:hover:text-red-300 font-medium"
            >
              Reset
            </button>
          </div>

          <div className="space-y-3">
            {syllabusState.topics.map((topic: SyllabusTopic, index: number) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="p-3 bg-gray-50 dark:bg-gray-700 rounded-lg border border-gray-200 dark:border-gray-600"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-900 dark:text-white">
                      {topic.topic}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      {topic.unit}
                    </p>
                    {topic.description && (
                      <p className="text-xs text-gray-600 dark:text-gray-300 mt-1">
                        {topic.description}
                      </p>
                    )}
                  </div>
                </div>
              </motion.div>
            ))}
          </div>

          {/* Action Buttons */}
          <div className="mt-6 flex gap-3">
            <button
              onClick={handleGetVideos}
              disabled={syllabusState.isProcessing}
              className="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
            >
              {syllabusState.isProcessing ? (
                <span className="flex items-center justify-center">
                  <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Finding Videos...
                </span>
              ) : (
                'Find Videos for Topics'
              )}
            </button>
          </div>
        </div>
      )}

      {/* Videos Display */}
      {syllabusState.syllabusVideos.length > 0 && (
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Videos by Topic ({syllabusState.totalVideos} total)
          </h3>

          <div className="space-y-6">
            {syllabusState.syllabusVideos.map((mapping, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="border border-gray-200 dark:border-gray-600 rounded-lg overflow-hidden"
              >
                <div className="bg-gray-50 dark:bg-gray-700 px-4 py-3 border-b border-gray-200 dark:border-gray-600">
                  <h4 className="font-semibold text-gray-900 dark:text-white">
                    {mapping.topic}
                  </h4>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    {mapping.unit} • {mapping.videos.length} videos
                  </p>
                </div>
                
                <div className="p-4 space-y-3">
                  {mapping.videos.map((video, videoIndex) => (
                    <div
                      key={videoIndex}
                      className="flex items-start space-x-3 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors"
                    >
                      {video.thumbnail_url && (
                        <img
                          src={video.thumbnail_url}
                          alt={video.title}
                          className="w-20 h-15 object-cover rounded"
                        />
                      )}
                      <div className="flex-1 min-w-0">
                        <h5 className="font-medium text-gray-900 dark:text-white text-sm line-clamp-2">
                          {video.title}
                        </h5>
                        <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                          {video.views.toLocaleString()} views • {video.likes.toLocaleString()} likes
                        </p>
                        <a
                          href={video.video_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-xs text-blue-600 dark:text-blue-400 hover:underline mt-1 inline-block"
                        >
                          Watch Video →
                        </a>
                      </div>
                    </div>
                  ))}
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default Syllabus; 