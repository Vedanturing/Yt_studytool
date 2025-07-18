export interface Comment {
  text: string;
  author: string;
  likes: number;
}

export interface Video {
  title: string;
  video_url: string;
  views: number;
  likes: number;
  description: string;
  comment_count: number;
  top_comments: Comment[];
  thumbnail_url: string;
  published_date?: string;
  duration?: number; // Duration in seconds
}

export interface VideoResponse {
  videos: Video[];
  total_count: number;
  source: string;
  keyword: string;
}

export interface VideoRequest {
  keyword: string;
}

export interface TranscribeResponse {
  transcription: string;
  video_url: string;
  video_title: string;
  duration?: number;
}

export interface SummarizeResponse {
  summary: string;
  original_length: number;
  summary_length: number;
}

export interface TranscriptionState {
  transcription: string;
  summary: string;
  video_title: string;
  video_url: string;
  isTranscribing: boolean;
  isSummarizing: boolean;
  transcriptionError: string | null;
  summarizationError: string | null;
}

export interface Flashcard {
  question: string;
  answer: string;
  type: 'mcq' | 'fact';
}

export interface LearningModeResponse {
  video_id: string;
  video_title: string;
  flashcards: Flashcard[];
  total_cards: number;
}

export interface LearningModeState {
  flashcards: Flashcard[];
  currentCardIndex: number;
  showAnswer: boolean;
  cardProgress: { [cardIndex: number]: 'known' | 'difficult' | 'unanswered' };
  isGenerating: boolean;
  error: string | null;
  video_title: string;
  video_id: string;
}

// Syllabus-related interfaces
export interface SyllabusTopic {
  unit: string;
  topic: string;
  description?: string;
}

export interface SyllabusVideoMapping {
  topic: string;
  unit: string;
  videos: Video[];
}

export interface SyllabusVideosResponse {
  syllabus_mapping: SyllabusVideoMapping[];
  total_topics: number;
  total_videos: number;
}

export interface QuizQuestion {
  question: string;
  options: string[];
  answer: string;
  explanation?: string;
  topic: string;
  difficulty?: string; // "easy", "medium", "hard"
  type?: string; // "mcq", "true_false", "fill_blank", "code_output"
}

export interface QuizResponse {
  questions: QuizQuestion[];
  total_questions: number;
  topics_covered: string[];
}

export interface QuizAttempt {
  question: string;
  selected_answer: string;
  correct_answer: string;
  is_correct: boolean;
  topic: string;
}

export interface ReportResponse {
  overall_score: number;
  topic_scores: { [topic: string]: number };
  weak_areas: string[];
  recommendations: string[];
  common_mistakes: string[];
  unwatched_topics: string[];
  report_data: any;
}

export interface SyllabusState {
  topics: SyllabusTopic[];
  syllabusVideos: SyllabusVideoMapping[];
  isUploading: boolean;
  isProcessing: boolean;
  error: string | null;
  totalTopics: number;
  totalVideos: number;
}

export interface QuizState {
  questions: QuizQuestion[];
  currentQuestionIndex: number;
  userAnswers: { [questionIndex: number]: string };
  isGenerating: boolean;
  isCompleted: boolean;
  score: number;
  error: string | null;
  totalQuestions: number;
  topicsCovered: string[];
  source?: string; // "api", "offline", "fallback"
  difficulty?: string; // "easy", "medium", "hard"
  questionTypes?: string[]; // ["mcq", "true_false", etc.]
  subject?: string; // Subject name for organization
}

export interface ReportState {
  report: ReportResponse | null;
  isGenerating: boolean;
  error: string | null;
}

// Study module interfaces
export interface Subject {
  code: string;
  name: string;
  units: string[];
}

export interface Unit {
  unit: string;
  topics: string[];
}

export interface StudyMaterial {
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

export interface StudyQuizQuestion {
  id: number;
  question: string;
  options: string[];
  correct_answer: string;
  concept: string;
  question_type: string;
  difficulty: string;
}

export interface StudyMistake {
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

export interface StudyState {
  subjects: Subject[];
  selectedSubject: string;
  selectedUnits: string[];
  units: Unit[];
  studyMaterials: Record<string, StudyMaterial>;
  quizQuestions: StudyQuizQuestion[];
  currentQuestionIndex: number;
  userAnswers: Record<number, string>;
  quizCompleted: boolean;
  evaluationResult: any;
  reportGenerated: boolean;
  loadingSubjects: boolean;
  loadingUnits: boolean;
  loadingMaterials: boolean;
  loadingQuiz: boolean;
  loadingEvaluation: boolean;
  loadingReport: boolean;
  activeStep: number;
  activeTab: 'materials' | 'quiz' | 'report';
}

export type SortOption = 'relevance' | 'views' | 'likes' | 'date' | 'duration';

export type DurationFilter = 'all' | 'short' | 'medium' | 'long'; // <4min, 4-20min, >20min

export type ContentTypeFilter = 'all' | 'videos' | 'shorts'; // Removed 'playlists'

export interface FilterState {
  sortBy: SortOption;
  durationFilter: DurationFilter;
  contentTypeFilter: ContentTypeFilter;
  currentPage: number;
  itemsPerPage: number;
}

export type Theme = 'light' | 'dark' | 'system';

export type TabType = 'overview' | 'transcription' | 'summary' | 'comments' | 'learning' | 'syllabus' | 'quiz' | 'report' | 'offline' | 'study';

export interface VideoStore {
  keyword: string;
  loading: boolean;
  videos: Video[];
  filteredVideos: Video[];
  paginatedVideos: Video[];
  error: string | null;
  totalCount: number;
  source: string;
  filterState: FilterState;
  transcriptionState: TranscriptionState;
  learningModeState: LearningModeState;
  syllabusState: SyllabusState;
  quizState: QuizState;
  reportState: ReportState;
  theme: Theme;
  activeTab: TabType;
  setKeyword: (keyword: string) => void;
  setLoading: (loading: boolean) => void;
  setResults: (response: VideoResponse) => void;
  setError: (error: string) => void;
  clearError: () => void;
  setSortBy: (sortBy: SortOption) => void;
  setDurationFilter: (filter: DurationFilter) => void;
  setContentTypeFilter: (filter: ContentTypeFilter) => void;
  setCurrentPage: (page: number) => void;
  setTheme: (theme: Theme) => void;
  setActiveTab: (tab: TabType) => void;
  fetchVideos: (keyword: string) => Promise<void>;
  exportToExcel: (videos: Video[]) => Promise<void>;
  exportToPdf: (videos: Video[]) => Promise<void>;
  transcribeVideo: (videoUrl: string) => Promise<void>;
  summarizeTranscription: (transcription: string) => Promise<void>;
  clearTranscription: () => void;
  exportTranscript: (format: 'pdf' | 'txt') => Promise<void>;
  generateLearningMode: (videoUrl: string) => Promise<void>;
  setCurrentCard: (index: number) => void;
  toggleAnswer: () => void;
  rateCard: (rating: 'known' | 'difficult') => void;
  resetLearningMode: () => void;
  // Syllabus methods
  uploadSyllabus: (file?: File, textContent?: string) => Promise<void>;
  getVideosBySyllabus: (topics: SyllabusTopic[]) => Promise<void>;
  generateQuiz: (topics: string[], numQuestions?: number, difficulty?: string, questionTypes?: string[], subject?: string) => Promise<void>;
  submitQuizAnswer: (questionIndex: number, answer: string) => void;
  nextQuestion: () => void;
  previousQuestion: () => void;
  completeQuiz: () => void;
  generateReport: (quizAttempts: QuizAttempt[], watchedVideos: string[], syllabusTopics: SyllabusTopic[]) => Promise<void>;
  resetSyllabus: () => void;
  resetQuiz: () => void;
  resetReport: () => void;
  // Study module methods
  loadSubjects: () => Promise<void>;
  loadUnits: (subjectCode: string) => Promise<void>;
  selectSubject: (subjectCode: string) => void;
  selectUnits: (units: string[]) => void;
  generateStudyMaterials: () => Promise<void>;
  generateStudyQuiz: () => Promise<void>;
  submitStudyQuiz: () => Promise<void>;
  generateStudyReport: () => Promise<void>;
  resetStudy: () => void;
} 