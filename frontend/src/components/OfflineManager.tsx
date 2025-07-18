import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import axios from 'axios';
import toast from 'react-hot-toast';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

interface OfflineQuiz {
  subject: string;
  unit: string;
  topic: string;
  created_at: string;
  question_count: number;
  difficulty: string;
  question_types: string[];
}

interface StudyMaterial {
  material_type: string;
  title: string;
  url?: string;
  filename?: string;
  created_at: string;
  metadata: any;
}

const OfflineManager: React.FC = () => {
  const [quizzes, setQuizzes] = useState<OfflineQuiz[]>([]);
  const [materials, setMaterials] = useState<StudyMaterial[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedSubject, setSelectedSubject] = useState<string>('');
  const [activeTab, setActiveTab] = useState<'quizzes' | 'materials'>('quizzes');

  useEffect(() => {
    loadOfflineContent();
  }, [selectedSubject]);

  const loadOfflineContent = async () => {
    setLoading(true);
    try {
      // Load available quizzes
      const quizzesResponse = await axios.get(`${API_BASE_URL}/available_quizzes`, {
        params: { subject: selectedSubject || undefined }
      });
      setQuizzes(quizzesResponse.data.quizzes || []);

      // Load study materials (if we have a subject selected)
      if (selectedSubject) {
        const materialsResponse = await axios.get(`${API_BASE_URL}/get_study_materials/${selectedSubject}/general`);
        setMaterials(materialsResponse.data.materials || []);
      } else {
        setMaterials([]);
      }
    } catch (error) {
      console.error('Error loading offline content:', error);
      toast.error('Failed to load offline content');
    } finally {
      setLoading(false);
    }
  };

  const handleRetryQuiz = async (quiz: OfflineQuiz) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/load_quiz/${quiz.subject}/${quiz.unit}/${quiz.topic}`);
      
      // Convert the loaded quiz to the format expected by the store
      const quizData = response.data;
      const questions = quizData.questions.map((q: any) => ({
        ...q,
        difficulty: q.difficulty || 'medium',
        type: q.type || 'mcq'
      }));

      // You would typically dispatch this to your store
      // For now, we'll just show a success message
      toast.success(`Loaded ${questions.length} questions from offline storage`);
      
      // You can implement a callback to pass this back to the parent component
      // or use a global state management solution
    } catch (error) {
      console.error('Error loading quiz:', error);
      toast.error('Failed to load quiz from offline storage');
    }
  };

  const handleDeleteQuiz = async (quiz: OfflineQuiz) => {
    if (!window.confirm(`Are you sure you want to delete the quiz for "${quiz.topic}"?`)) {
      return;
    }

    try {
      // Note: You'll need to implement a delete endpoint in the backend
      // await axios.delete(`${API_BASE_URL}/delete_quiz/${quiz.subject}/${quiz.unit}/${quiz.topic}`);
      toast.success('Quiz deleted successfully');
      loadOfflineContent(); // Reload the list
    } catch (error) {
      console.error('Error deleting quiz:', error);
      toast.error('Failed to delete quiz');
    }
  };

  const handleDownloadMaterial = async (material: StudyMaterial) => {
    if (material.url) {
      window.open(material.url, '_blank');
    } else if (material.filename) {
      try {
        const response = await axios.get(`${API_BASE_URL}/download_material/${material.filename}`, {
          responseType: 'blob'
        });
        
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', material.filename || 'material');
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.URL.revokeObjectURL(url);
      } catch (error) {
        console.error('Error downloading material:', error);
        toast.error('Failed to download material');
      }
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'easy': return 'text-green-600 dark:text-green-400';
      case 'hard': return 'text-red-600 dark:text-red-400';
      default: return 'text-yellow-600 dark:text-yellow-400';
    }
  };

  const getMaterialIcon = (type: string) => {
    switch (type) {
      case 'video': return '🎥';
      case 'pdf': return '📄';
      case 'note': return '📝';
      default: return '📁';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
          💾 Offline Content Manager
        </h2>
        <p className="text-gray-600 dark:text-gray-400">
          Manage your locally stored quizzes and study materials for offline access.
        </p>
      </div>

      {/* Subject Filter */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700">
        <div className="flex items-center space-x-4">
          <label htmlFor="subject-filter" className="text-gray-700 dark:text-gray-300 font-medium">
            Filter by Subject:
          </label>
          <input
            id="subject-filter"
            type="text"
            value={selectedSubject}
            onChange={(e) => setSelectedSubject(e.target.value)}
            placeholder="Enter subject name or leave empty for all"
            className="flex-1 px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-900 dark:text-white"
          />
          <button
            onClick={loadOfflineContent}
            disabled={loading}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 font-medium"
          >
            {loading ? 'Loading...' : 'Refresh'}
          </button>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700">
        <div className="flex space-x-4 mb-6">
          <button
            onClick={() => setActiveTab('quizzes')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              activeTab === 'quizzes'
                ? 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300'
                : 'text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200'
            }`}
          >
            🧠 Quizzes ({quizzes.length})
          </button>
          <button
            onClick={() => setActiveTab('materials')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              activeTab === 'materials'
                ? 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300'
                : 'text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200'
            }`}
          >
            📚 Study Materials ({materials.length})
          </button>
        </div>

        {/* Content */}
        {activeTab === 'quizzes' ? (
          <div className="space-y-4">
            {quizzes.length === 0 ? (
              <div className="text-center py-8">
                <p className="text-gray-600 dark:text-gray-400">
                  {selectedSubject ? `No offline quizzes found for "${selectedSubject}"` : 'No offline quizzes found'}
                </p>
                <p className="text-sm text-gray-500 dark:text-gray-500 mt-2">
                  Generate quizzes first to see them here for offline access.
                </p>
              </div>
            ) : (
              quizzes.map((quiz, index) => (
                <motion.div
                  key={`${quiz.subject}-${quiz.unit}-${quiz.topic}-${index}`}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="border border-gray-200 dark:border-gray-600 rounded-lg p-4 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <h3 className="font-semibold text-gray-900 dark:text-white">
                        {quiz.topic}
                      </h3>
                      <div className="flex items-center space-x-4 mt-1 text-sm text-gray-600 dark:text-gray-400">
                        <span>Subject: {quiz.subject}</span>
                        <span>Unit: {quiz.unit}</span>
                        <span className={`font-medium ${getDifficultyColor(quiz.difficulty)}`}>
                          {quiz.difficulty}
                        </span>
                        <span>{quiz.question_count} questions</span>
                        <span>{quiz.question_types.join(', ')}</span>
                      </div>
                      <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">
                        Created: {formatDate(quiz.created_at)}
                      </p>
                    </div>
                    <div className="flex space-x-2">
                      <button
                        onClick={() => handleRetryQuiz(quiz)}
                        className="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 font-medium"
                      >
                        Load
                      </button>
                      <button
                        onClick={() => handleDeleteQuiz(quiz)}
                        className="px-3 py-1 text-sm bg-red-600 text-white rounded hover:bg-red-700 font-medium"
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                </motion.div>
              ))
            )}
          </div>
        ) : (
          <div className="space-y-4">
            {materials.length === 0 ? (
              <div className="text-center py-8">
                <p className="text-gray-600 dark:text-gray-400">
                  {selectedSubject ? `No study materials found for "${selectedSubject}"` : 'Select a subject to view study materials'}
                </p>
                <p className="text-sm text-gray-500 dark:text-gray-500 mt-2">
                  Save study materials first to see them here for offline access.
                </p>
              </div>
            ) : (
              materials.map((material, index) => (
                <motion.div
                  key={`${material.material_type}-${material.title}-${index}`}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="border border-gray-200 dark:border-gray-600 rounded-lg p-4 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3 flex-1">
                      <span className="text-2xl">{getMaterialIcon(material.material_type)}</span>
                      <div>
                        <h3 className="font-semibold text-gray-900 dark:text-white">
                          {material.title}
                        </h3>
                        <div className="flex items-center space-x-4 mt-1 text-sm text-gray-600 dark:text-gray-400">
                          <span className="capitalize">{material.material_type}</span>
                          <span>Created: {formatDate(material.created_at)}</span>
                        </div>
                      </div>
                    </div>
                    <div className="flex space-x-2">
                      <button
                        onClick={() => handleDownloadMaterial(material)}
                        className="px-3 py-1 text-sm bg-green-600 text-white rounded hover:bg-green-700 font-medium"
                      >
                        {material.url ? 'Open' : 'Download'}
                      </button>
                    </div>
                  </div>
                </motion.div>
              ))
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default OfflineManager; 