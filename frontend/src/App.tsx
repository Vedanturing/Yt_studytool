import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider } from './contexts/ThemeContext';
import LandingPage from './pages/LandingPage';
import AppContent from './components/AppContent';
import SyllabusPage from './pages/SyllabusPage';
import QuizPage from './pages/QuizPage';
import LearningModePage from './pages/LearningModePage';
import StudyPage from './pages/StudyPage';
import { Toaster } from 'react-hot-toast';
import './index.css';

function App() {
  return (
    <ThemeProvider>
      <Router>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/app" element={<AppContent />} />
          <Route path="/app/*" element={<AppContent />} />
          <Route path="/syllabus" element={<SyllabusPage />} />
          <Route path="/quiz" element={<QuizPage />} />
          <Route path="/learning" element={<LearningModePage />} />
          <Route path="/study" element={<StudyPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Router>
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: '#363636',
            color: '#fff',
          },
          success: {
            duration: 3000,
            iconTheme: {
              primary: '#4ade80',
              secondary: '#fff',
            },
          },
          error: {
            duration: 5000,
            iconTheme: {
              primary: '#ef4444',
              secondary: '#fff',
            },
          },
        }}
      />
    </ThemeProvider>
  );
}

export default App; 