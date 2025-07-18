import React, { useState, useEffect } from 'react';
import toast from 'react-hot-toast';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

interface Subject {
  code: string;
  name: string;
  description: string;
  units: string[];
  total_topics: number;
  overview?: string;
  skills?: string;
  career?: string;
  difficulty?: string;
}

interface Unit {
  unit: string;
  topics: string[];
}

interface StudyMaterial {
  articles: Array<{
    title: string;
    url: string;
    description: string;
    source: string;
  }>;
  videos: Array<{
    title: string;
    url: string;
    description: string;
    source: string;
  }>;
  notes: Array<{
    title: string;
    url: string;
    description: string;
    source: string;
  }>;
}

interface QuizQuestion {
  id: number;
  question: string;
  options: string[];
  correct_answer: string;
  concept: string;
  question_type: string;
  difficulty: string;
}

interface Mistake {
  concept: string;
  correct_answer: string;
  user_answer: string;
  study_resources: Array<{
    title: string;
    url: string;
    type: string;
    description: string;
  }>;
}

const Study: React.FC = () => {
  
  // State management
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [selectedSubject, setSelectedSubject] = useState<string>('');
  const [selectedUnits, setSelectedUnits] = useState<string[]>([]);
  const [units, setUnits] = useState<Unit[]>([]);
  const [studyMaterials, setStudyMaterials] = useState<Record<string, StudyMaterial>>({});
  const [quizQuestions, setQuizQuestions] = useState<QuizQuestion[]>([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [userAnswers, setUserAnswers] = useState<Record<number, string>>({});
  const [quizCompleted, setQuizCompleted] = useState(false);
  const [evaluationResult, setEvaluationResult] = useState<any>(null);

  
  // Loading states
  const [loadingSubjects, setLoadingSubjects] = useState(true);
  const [loadingUnits, setLoadingUnits] = useState(false);
  const [loadingMaterials, setLoadingMaterials] = useState(false);
  const [loadingQuiz, setLoadingQuiz] = useState(false);
  const [loadingEvaluation, setLoadingEvaluation] = useState(false);
  const [loadingReport, setLoadingReport] = useState(false);
  
  // UI states
  const [activeStep, setActiveStep] = useState(1);

  // Load subjects on component mount
  useEffect(() => {
    loadSubjects();
  }, []);

  // Load units when subject changes
  useEffect(() => {
    if (selectedSubject) {
      loadUnits(selectedSubject);
    }
  }, [selectedSubject]);

  const loadSubjects = async () => {
    try {
      setLoadingSubjects(true);
      const response = await axios.get(`${API_BASE_URL}/study/subjects`);
      setSubjects(response.data.subjects);
    } catch (error) {
      console.error('Error loading subjects:', error);
      toast.error('Failed to load subjects');
    } finally {
      setLoadingSubjects(false);
    }
  };

  const loadUnits = async (subjectCode: string) => {
    try {
      setLoadingUnits(true);
      const response = await axios.get(`${API_BASE_URL}/study/subjects/${subjectCode}/units`);
      setUnits(response.data.units);
    } catch (error) {
      console.error('Error loading units:', error);
      toast.error('Failed to load units');
    } finally {
      setLoadingUnits(false);
    }
  };

  const handleSubjectChange = (subjectCode: string) => {
    setSelectedSubject(subjectCode);
    setSelectedUnits([]);
    setStudyMaterials({});
    setQuizQuestions([]);
    setUserAnswers({});
    setQuizCompleted(false);
    setEvaluationResult(null);
    setActiveStep(1);
  };

  const handleUnitToggle = (unit: string) => {
    setSelectedUnits(prev => 
      prev.includes(unit) 
        ? prev.filter(u => u !== unit)
        : [...prev, unit]
    );
  };

  const generateStudyMaterials = async () => {
    if (selectedUnits.length === 0) {
      toast.error('Please select at least one unit');
      return;
    }

    try {
      setLoadingMaterials(true);
      const response = await axios.post(`${API_BASE_URL}/study/generate_study_material`, {
        subject: selectedSubject,
        units: selectedUnits
      });
      setStudyMaterials(response.data.study_materials);
      setActiveStep(2);
      toast.success('Study materials generated successfully!');
    } catch (error) {
      console.error('Error generating study materials:', error);
      toast.error('Failed to generate study materials');
    } finally {
      setLoadingMaterials(false);
    }
  };

  const generateQuiz = async () => {
    if (selectedUnits.length === 0) {
      toast.error('Please select at least one unit');
      return;
    }

    try {
      setLoadingQuiz(true);
      const response = await axios.post(`${API_BASE_URL}/study/generate_quiz`, {
        subject: selectedSubject,
        units: selectedUnits,
        num_questions: 10,
        difficulty: 'medium',
        question_types: ['mcq', 'true_false']
      });
      setQuizQuestions(response.data.questions);
      setActiveStep(3);
      toast.success('Quiz generated successfully!');
    } catch (error) {
      console.error('Error generating quiz:', error);
      toast.error('Failed to generate quiz');
    } finally {
      setLoadingQuiz(false);
    }
  };

  const handleAnswerSelect = (questionId: number, answer: string) => {
    setUserAnswers(prev => ({
      ...prev,
      [questionId]: answer
    }));
  };

  const submitQuiz = async () => {
    if (Object.keys(userAnswers).length !== quizQuestions.length) {
      toast.error('Please answer all questions before submitting');
      return;
    }

    try {
      setLoadingEvaluation(true);
      const response = await axios.post(`${API_BASE_URL}/study/evaluate_quiz`, {
        subject: selectedSubject,
        unit: selectedUnits[0], // For now, evaluate first unit
        responses: userAnswers
      });
      setEvaluationResult(response.data);
      setQuizCompleted(true);
      setActiveStep(4);
      toast.success(`Quiz completed! Score: ${response.data.score.toFixed(1)}%`);
    } catch (error) {
      console.error('Error evaluating quiz:', error);
      toast.error('Failed to evaluate quiz');
    } finally {
      setLoadingEvaluation(false);
    }
  };

  const generateReport = async () => {
    if (!evaluationResult) {
      toast.error('No evaluation result available');
      return;
    }

    try {
      setLoadingReport(true);
      const response = await axios.post(`${API_BASE_URL}/study/generate_report`, {
        subject: selectedSubject,
        unit: selectedUnits[0],
        evaluation_result: evaluationResult
      });
      toast.success('Report generated successfully!');
      
      // Download the report
      const downloadUrl = `${API_BASE_URL}/study/download_report/${response.data.report_filename}`;
      window.open(downloadUrl, '_blank');
    } catch (error) {
      console.error('Error generating report:', error);
      toast.error('Failed to generate report');
    } finally {
      setLoadingReport(false);
    }
  };

  const resetStudy = () => {
    setSelectedSubject('');
    setSelectedUnits([]);
    setUnits([]);
    setStudyMaterials({});
    setQuizQuestions([]);
    setUserAnswers({});
          setQuizCompleted(false);
      setEvaluationResult(null);
      setActiveStep(1);
  };

  const currentQuestion = quizQuestions[currentQuestionIndex];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
          🎓 Diploma Computer Engineering 5th Sem Study Module
        </h2>
        <p className="text-gray-600 dark:text-gray-400">
          Select your subject and units to generate personalized study materials, take quizzes, and get detailed reports.
        </p>
      </div>

      {/* Progress Bar */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Progress</h3>
          <button
            onClick={resetStudy}
            className="px-3 py-1 text-sm text-red-600 dark:text-red-400 hover:text-red-800 dark:hover:text-red-300 font-medium"
          >
            Reset
          </button>
        </div>
        
        <div className="flex items-center space-x-2">
          {[1, 2, 3, 4].map((step) => (
            <div key={step} className="flex items-center">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                activeStep >= step 
                  ? 'bg-blue-600 text-white' 
                  : 'bg-gray-200 dark:bg-gray-700 text-gray-500'
              }`}>
                {step}
              </div>
              {step < 4 && (
                <div className={`w-16 h-1 mx-2 ${
                  activeStep > step ? 'bg-blue-600' : 'bg-gray-200 dark:bg-gray-700'
                }`} />
              )}
            </div>
          ))}
        </div>
        
        <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-2">
          <span>Select Subject</span>
          <span>Study Materials</span>
          <span>Take Quiz</span>
          <span>Get Report</span>
        </div>
      </div>

      {/* Step 1: Subject and Unit Selection */}
      {activeStep === 1 && (
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Step 1: Select Subject and Units
          </h3>

          {/* Subject Selection */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Select Subject
            </label>
            {loadingSubjects ? (
              <div className="animate-pulse bg-gray-200 dark:bg-gray-700 h-10 rounded"></div>
            ) : (
              <div className="space-y-3">
                {subjects.map((subject) => (
                  <div
                    key={subject.code}
                    className={`p-4 border rounded-lg cursor-pointer transition-all duration-200 ${
                      selectedSubject === subject.code
                        ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                        : 'border-gray-200 dark:border-gray-600 hover:border-gray-300 dark:hover:border-gray-500'
                    }`}
                    onClick={() => handleSubjectChange(subject.code)}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h4 className="font-semibold text-gray-900 dark:text-white">
                          {subject.code} - {subject.name}
                        </h4>
                        <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                          {subject.description}
                        </p>
                        <div className="flex items-center gap-4 mt-2 text-xs text-gray-500 dark:text-gray-400">
                          <span>{subject.units.length} units</span>
                          <span>{subject.total_topics} topics</span>
                          {subject.difficulty && (
                            <span className={`px-2 py-1 rounded ${
                              subject.difficulty === 'Advanced' ? 'bg-red-100 text-red-700 dark:bg-red-900/20 dark:text-red-300' :
                              subject.difficulty === 'Intermediate' ? 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/20 dark:text-yellow-300' :
                              'bg-green-100 text-green-700 dark:bg-green-900/20 dark:text-green-300'
                            }`}>
                              {subject.difficulty}
                            </span>
                          )}
                        </div>
                        {subject.skills && (
                          <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                            <strong>Skills:</strong> {subject.skills}
                          </p>
                        )}
                      </div>
                      <div className={`w-5 h-5 rounded-full border-2 flex items-center justify-center ${
                        selectedSubject === subject.code
                          ? 'border-blue-500 bg-blue-500'
                          : 'border-gray-300 dark:border-gray-600'
                      }`}>
                        {selectedSubject === subject.code && (
                          <div className="w-2 h-2 bg-white rounded-full"></div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Unit Selection */}
          {selectedSubject && (
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Select Units
              </label>
              {loadingUnits ? (
                <div className="animate-pulse bg-gray-200 dark:bg-gray-700 h-32 rounded"></div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                  {units.map((unit) => (
                    <label key={unit.unit} className="flex items-center p-3 border border-gray-200 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={selectedUnits.includes(unit.unit)}
                        onChange={() => handleUnitToggle(unit.unit)}
                        className="mr-3 text-blue-600 focus:ring-blue-500"
                      />
                      <div>
                        <div className="font-medium text-gray-900 dark:text-white">{unit.unit}</div>
                        <div className="text-sm text-gray-500 dark:text-gray-400">
                          {unit.topics.length} topics
                        </div>
                      </div>
                    </label>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Action Buttons */}
          {selectedUnits.length > 0 && (
            <div className="flex gap-3">
              <button
                onClick={generateStudyMaterials}
                disabled={loadingMaterials}
                className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
              >
                {loadingMaterials ? 'Generating Materials...' : 'Generate Study Materials'}
              </button>
              <button
                onClick={generateQuiz}
                disabled={loadingQuiz}
                className="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
              >
                {loadingQuiz ? 'Generating Quiz...' : 'Generate Quiz'}
              </button>
            </div>
          )}
        </div>
      )}

      {/* Step 2: Study Materials */}
      {activeStep >= 2 && Object.keys(studyMaterials).length > 0 && (
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Step 2: Study Materials
          </h3>

          <div className="space-y-4">
            {Object.entries(studyMaterials).map(([unit, materials]) => (
              <div key={unit} className="border border-gray-200 dark:border-gray-600 rounded-lg overflow-hidden">
                <div className="bg-gray-50 dark:bg-gray-700 px-4 py-3 border-b border-gray-200 dark:border-gray-600">
                  <h4 className="font-semibold text-gray-900 dark:text-white">{unit}</h4>
                </div>
                
                <div className="p-4">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {/* Articles */}
                    <div>
                      <h5 className="font-medium text-gray-900 dark:text-white mb-2">📚 Articles</h5>
                      <div className="space-y-2">
                        {materials.articles.map((article, index) => (
                          <a
                            key={index}
                            href={article.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="block p-2 bg-gray-50 dark:bg-gray-700 rounded hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors"
                          >
                            <div className="font-medium text-sm text-gray-900 dark:text-white">{article.title}</div>
                            <div className="text-xs text-gray-500 dark:text-gray-400">{article.source}</div>
                          </a>
                        ))}
                      </div>
                    </div>

                    {/* Videos */}
                    <div>
                      <h5 className="font-medium text-gray-900 dark:text-white mb-2">🎥 Videos</h5>
                      <div className="space-y-2">
                        {materials.videos.map((video, index) => (
                          <a
                            key={index}
                            href={video.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="block p-2 bg-gray-50 dark:bg-gray-700 rounded hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors"
                          >
                            <div className="font-medium text-sm text-gray-900 dark:text-white">{video.title}</div>
                            <div className="text-xs text-gray-500 dark:text-gray-400">{video.source}</div>
                          </a>
                        ))}
                      </div>
                    </div>

                    {/* Notes */}
                    <div>
                      <h5 className="font-medium text-gray-900 dark:text-white mb-2">📝 Notes</h5>
                      <div className="space-y-2">
                        {materials.notes.map((note, index) => (
                          <a
                            key={index}
                            href={note.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="block p-2 bg-gray-50 dark:bg-gray-700 rounded hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors"
                          >
                            <div className="font-medium text-sm text-gray-900 dark:text-white">{note.title}</div>
                            <div className="text-xs text-gray-500 dark:text-gray-400">{note.source}</div>
                          </a>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Step 3: Quiz */}
      {activeStep >= 3 && quizQuestions.length > 0 && (
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Step 3: Quiz ({currentQuestionIndex + 1} of {quizQuestions.length})
          </h3>

          {!quizCompleted ? (
            <div className="space-y-4">
              <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                <h4 className="font-medium text-gray-900 dark:text-white mb-3">
                  {currentQuestion?.question}
                </h4>
                
                <div className="space-y-2">
                  {currentQuestion?.options.map((option, index) => (
                    <label key={index} className="flex items-center p-3 border border-gray-200 dark:border-gray-600 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-600 cursor-pointer">
                      <input
                        type="radio"
                        name={`question-${currentQuestion.id}`}
                        value={option}
                        checked={userAnswers[currentQuestion.id] === option}
                        onChange={() => handleAnswerSelect(currentQuestion.id, option)}
                        className="mr-3 text-blue-600 focus:ring-blue-500"
                      />
                      <span className="text-gray-900 dark:text-white">{option}</span>
                    </label>
                  ))}
                </div>
              </div>

              <div className="flex justify-between">
                <button
                  onClick={() => setCurrentQuestionIndex(prev => Math.max(0, prev - 1))}
                  disabled={currentQuestionIndex === 0}
                  className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Previous
                </button>
                
                {currentQuestionIndex === quizQuestions.length - 1 ? (
                  <button
                    onClick={submitQuiz}
                    disabled={loadingEvaluation || Object.keys(userAnswers).length !== quizQuestions.length}
                    className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {loadingEvaluation ? 'Submitting...' : 'Submit Quiz'}
                  </button>
                ) : (
                  <button
                    onClick={() => setCurrentQuestionIndex(prev => Math.min(quizQuestions.length - 1, prev + 1))}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                  >
                    Next
                  </button>
                )}
              </div>
            </div>
          ) : (
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                Quiz Completed!
              </div>
              <div className="text-lg text-gray-600 dark:text-gray-400 mb-4">
                Score: {evaluationResult?.score.toFixed(1)}%
              </div>
              <button
                onClick={generateReport}
                disabled={loadingReport}
                className="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
              >
                {loadingReport ? 'Generating Report...' : 'Generate Report'}
              </button>
            </div>
          )}
        </div>
      )}

      {/* Step 4: Evaluation Results */}
      {activeStep >= 4 && evaluationResult && (
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Step 4: Evaluation Results
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Score Summary */}
            <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <h4 className="font-medium text-gray-900 dark:text-white mb-3">Performance Summary</h4>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Score:</span>
                  <span className="font-medium text-gray-900 dark:text-white">
                    {evaluationResult.score.toFixed(1)}%
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Correct Answers:</span>
                  <span className="font-medium text-gray-900 dark:text-white">
                    {evaluationResult.correct_count}/{evaluationResult.total_questions}
                  </span>
                </div>
              </div>
            </div>

            {/* Mistakes Analysis */}
            <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <h4 className="font-medium text-gray-900 dark:text-white mb-3">Areas for Improvement</h4>
              <div className="space-y-2">
                {evaluationResult.mistakes.map((mistake: Mistake, index: number) => (
                  <div key={index} className="p-2 bg-red-50 dark:bg-red-900/20 rounded">
                    <div className="font-medium text-sm text-red-800 dark:text-red-200">
                      {mistake.concept}
                    </div>
                    <div className="text-xs text-red-600 dark:text-red-300">
                      Your answer: {mistake.user_answer} | Correct: {mistake.correct_answer}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Study Resources for Mistakes */}
          {evaluationResult.mistakes.length > 0 && (
            <div className="mt-6">
              <h4 className="font-medium text-gray-900 dark:text-white mb-3">Recommended Study Resources</h4>
              <div className="space-y-4">
                {evaluationResult.mistakes.map((mistake: Mistake, index: number) => (
                  <div key={index} className="border border-gray-200 dark:border-gray-600 rounded-lg p-4">
                    <h5 className="font-medium text-gray-900 dark:text-white mb-2">
                      {mistake.concept}
                    </h5>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
                      {mistake.study_resources.map((resource, resourceIndex) => (
                        <a
                          key={resourceIndex}
                          href={resource.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="block p-2 bg-blue-50 dark:bg-blue-900/20 rounded hover:bg-blue-100 dark:hover:bg-blue-900/40 transition-colors"
                        >
                          <div className="font-medium text-sm text-blue-800 dark:text-blue-200">
                            {resource.title}
                          </div>
                          <div className="text-xs text-blue-600 dark:text-blue-300">
                            {resource.type}
                          </div>
                        </a>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default Study; 