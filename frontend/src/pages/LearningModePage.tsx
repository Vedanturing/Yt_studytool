import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useVideoStore } from '../store/useVideoStore';

const LearningModePage: React.FC = () => {
  const navigate = useNavigate();
  const { setActiveTab } = useVideoStore();

  useEffect(() => {
    setActiveTab('learning');
    navigate('/app');
  }, [navigate, setActiveTab]);

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4"></div>
        <p className="text-gray-600 dark:text-gray-400">Redirecting to Learning Mode...</p>
      </div>
    </div>
  );
};

export default LearningModePage; 