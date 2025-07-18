import { create } from 'zustand';
import axios from 'axios';
import { VideoStore, VideoResponse, SortOption, DurationFilter, ContentTypeFilter, Theme, TabType, TranscribeResponse, SummarizeResponse, LearningModeState, LearningModeResponse, SyllabusTopic, QuizQuestion, QuizAttempt } from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Helper function to get duration category
const getDurationCategory = (duration?: number): string => {
  if (!duration) return 'unknown';
  if (duration < 240) return 'short'; // <4 minutes
  if (duration < 1200) return 'medium'; // 4-20 minutes
  return 'long'; // >20 minutes
};

// Helper function to determine content type based on duration and title
const getContentType = (video: any): string => {
  const title = video.title?.toLowerCase() || '';
  const duration = video.duration || 0;
  
  if (duration < 60 || title.includes('#shorts') || title.includes('short')) return 'shorts';
  return 'videos';
};

// Enhanced filtering function
const filterVideos = (videos: any[], filters: any): any[] => {
  return videos.filter(video => {
    // Duration filter
    if (filters.durationFilter !== 'all') {
      const category = getDurationCategory(video.duration);
      if (category !== filters.durationFilter) return false;
    }
    
    // Content type filter
    if (filters.contentTypeFilter !== 'all') {
      const type = getContentType(video);
      if (type !== filters.contentTypeFilter) return false;
    }
    
    return true;
  });
};

// Memoized sorting function with better performance
const sortVideos = (videos: any[], sortBy: SortOption): any[] => {
  if (!videos || videos.length === 0) return [];
  
  // Clone the array to avoid mutating the original
  const sortedVideos = [...videos];
  
  switch (sortBy) {
    case 'views':
      return sortedVideos.sort((a, b) => {
        const viewsA = typeof a.views === 'number' ? a.views : 0;
        const viewsB = typeof b.views === 'number' ? b.views : 0;
        return viewsB - viewsA;
      });
    case 'likes':
      return sortedVideos.sort((a, b) => {
        const likesA = typeof a.likes === 'number' ? a.likes : 0;
        const likesB = typeof b.likes === 'number' ? b.likes : 0;
        return likesB - likesA;
      });
    case 'date':
      return sortedVideos.sort((a, b) => {
        if (a.published_date && b.published_date) {
          const dateA = new Date(a.published_date).getTime();
          const dateB = new Date(b.published_date).getTime();
          return dateB - dateA; // Newest first
        }
        return 0;
      });
    case 'duration':
      return sortedVideos.sort((a, b) => {
        const durationA = typeof a.duration === 'number' ? a.duration : 0;
        const durationB = typeof b.duration === 'number' ? b.duration : 0;
        return durationB - durationA; // Longest first
      });
    case 'relevance':
    default:
      // Keep original order (relevance as returned by API)
      return sortedVideos;
  }
};

// Pagination function
const paginateVideos = (videos: any[], currentPage: number, itemsPerPage: number): any[] => {
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  return videos.slice(startIndex, endIndex);
};

// Helper function to extract filename from content-disposition header
const getFilenameFromResponse = (response: any, defaultName: string): string => {
  const contentDisposition = response.headers['content-disposition'];
  if (contentDisposition) {
    const filenameMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
    if (filenameMatch && filenameMatch[1]) {
      return filenameMatch[1].replace(/['"]/g, '');
    }
  }
  return defaultName;
};

export const useVideoStore = create<VideoStore>((set, get) => ({
  keyword: '',
  loading: false,
  videos: [],
  filteredVideos: [],
  paginatedVideos: [],
  error: null,
  totalCount: 0,
  source: '',
  theme: 'system',
  activeTab: 'overview',
  filterState: {
    sortBy: 'relevance',
    durationFilter: 'all',
    contentTypeFilter: 'all',
    currentPage: 1,
    itemsPerPage: 12
  },
  transcriptionState: {
    transcription: '',
    summary: '',
    video_title: '',
    video_url: '',
    isTranscribing: false,
    isSummarizing: false,
    transcriptionError: null,
    summarizationError: null,
  },
  learningModeState: {
    flashcards: [],
    currentCardIndex: 0,
    showAnswer: false,
    cardProgress: {},
    isGenerating: false,
    error: null,
    video_title: '',
    video_id: '',
  },
  syllabusState: {
    topics: [],
    syllabusVideos: [],
    isUploading: false,
    isProcessing: false,
    error: null,
    totalTopics: 0,
    totalVideos: 0,
  },
  quizState: {
    questions: [],
    currentQuestionIndex: 0,
    userAnswers: {},
    isGenerating: false,
    isCompleted: false,
    score: 0,
    error: null,
    totalQuestions: 0,
    topicsCovered: [],
    source: 'api',
    difficulty: 'medium',
    questionTypes: ['mcq', 'true_false'],
    subject: 'General',
  },
  reportState: {
    report: null,
    isGenerating: false,
    error: null,
  },

  setKeyword: (keyword: string) => {
    set({ keyword });
  },

  setLoading: (loading: boolean) => {
    set({ loading });
  },

  setTheme: (theme: Theme) => {
    set({ theme });
  },

  setActiveTab: (activeTab: TabType) => {
    set({ activeTab });
  },

  setResults: (response: VideoResponse) => {
    const { filterState } = get();
    
    // Apply filters and sorting
    const filtered = filterVideos(response.videos, filterState);
    const sorted = sortVideos(filtered, filterState.sortBy);
    const paginated = paginateVideos(sorted, filterState.currentPage, filterState.itemsPerPage);
    
    set({
      videos: response.videos,
      filteredVideos: sorted,
      paginatedVideos: paginated,
      totalCount: response.total_count,
      source: response.source,
      keyword: response.keyword,
      error: null,
      filterState: { ...filterState, currentPage: 1 } // Reset to first page
    });
  },

  setError: (error: string) => {
    set({ error, videos: [], filteredVideos: [], paginatedVideos: [], totalCount: 0, source: '' });
  },

  clearError: () => {
    set({ error: null });
  },

  setSortBy: (sortBy: SortOption) => {
    const { videos, filterState } = get();
    
    // Apply filters and sorting
    const filtered = filterVideos(videos, { ...filterState, sortBy });
    const sorted = sortVideos(filtered, sortBy);
    const paginated = paginateVideos(sorted, 1, filterState.itemsPerPage);
    
    set({
      filterState: { ...filterState, sortBy, currentPage: 1 },
      filteredVideos: sorted,
      paginatedVideos: paginated
    });
  },

  setDurationFilter: (durationFilter: DurationFilter) => {
    const { videos, filterState } = get();
    
    // Apply filters and sorting
    const filtered = filterVideos(videos, { ...filterState, durationFilter });
    const sorted = sortVideos(filtered, filterState.sortBy);
    const paginated = paginateVideos(sorted, 1, filterState.itemsPerPage);
    
    set({
      filterState: { ...filterState, durationFilter, currentPage: 1 },
      filteredVideos: sorted,
      paginatedVideos: paginated
    });
  },

  setContentTypeFilter: (contentTypeFilter: ContentTypeFilter) => {
    const { videos, filterState } = get();
    
    // Apply filters and sorting
    const filtered = filterVideos(videos, { ...filterState, contentTypeFilter });
    const sorted = sortVideos(filtered, filterState.sortBy);
    const paginated = paginateVideos(sorted, 1, filterState.itemsPerPage);
    
    set({
      filterState: { ...filterState, contentTypeFilter, currentPage: 1 },
      filteredVideos: sorted,
      paginatedVideos: paginated
    });
  },

  setCurrentPage: (currentPage: number) => {
    const { filteredVideos, filterState } = get();
    const paginated = paginateVideos(filteredVideos, currentPage, filterState.itemsPerPage);
    
    set({
      filterState: { ...filterState, currentPage },
      paginatedVideos: paginated
    });
  },

  fetchVideos: async (keyword: string) => {
    const { setLoading, setResults, setError } = get();
    
    if (!keyword.trim()) {
      setError('Please enter a keyword to search');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await axios.post<VideoResponse>(
        `${API_BASE_URL}/get_videos`,
        { keyword: keyword.trim() },
        {
          headers: {
            'Content-Type': 'application/json',
          },
          timeout: 30000, // 30 second timeout
        }
      );

      setResults(response.data);
    } catch (error) {
      console.error('Error fetching videos:', error);
      
      if (axios.isAxiosError(error)) {
        if (error.response) {
          // Server responded with error status
          const errorMessage = error.response.data?.detail || error.response.data?.error || 'Server error occurred';
          setError(`Failed to fetch videos: ${errorMessage}`);
        } else if (error.request) {
          // Request was made but no response received
          setError('No response from server. Please check your connection.');
        } else {
          // Something else happened
          setError(`Request failed: ${error.message}`);
        }
      } else {
        // Non-Axios error
        setError(`Unexpected error: ${error instanceof Error ? error.message : 'Unknown error'}`);
      }
    } finally {
      setLoading(false);
    }
  },

  exportToExcel: async (videos: any[]) => {
    if (!videos || videos.length === 0) {
      alert('No videos to export');
      return;
    }

    try {
      const { keyword } = get();
      const response = await axios.post(
        `${API_BASE_URL}/export/excel`,
        { videos, keyword },
        {
          responseType: 'blob',
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );

      const filename = getFilenameFromResponse(response, 'yt_results.xlsx');
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error exporting to Excel:', error);
      alert('Failed to export to Excel. Please try again.');
    }
  },

  exportToPdf: async (videos: any[]) => {
    if (!videos || videos.length === 0) {
      alert('No videos to export');
      return;
    }

    try {
      const { keyword } = get();
      const response = await axios.post(
        `${API_BASE_URL}/export/pdf`,
        { videos, keyword },
        {
          responseType: 'blob',
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );

      const filename = getFilenameFromResponse(response, 'yt_results.pdf');
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error exporting to PDF:', error);
      alert('Failed to export to PDF. Please try again.');
    }
  },

  transcribeVideo: async (videoUrl: string) => {
    set({
      transcriptionState: {
        ...get().transcriptionState,
        isTranscribing: true,
        transcriptionError: null,
      }
    });

    try {
      const encodedUrl = encodeURIComponent(videoUrl);
      const response = await axios.post<TranscribeResponse>(
        `${API_BASE_URL}/transcribe/${encodedUrl}`,
        {},
        {
          headers: {
            'Content-Type': 'application/json',
          },
          timeout: 300000, // 5 minute timeout for transcription
        }
      );

      set({
        transcriptionState: {
          ...get().transcriptionState,
          transcription: response.data.transcription,
          video_title: response.data.video_title,
          video_url: response.data.video_url,
          isTranscribing: false,
          transcriptionError: null,
        }
      });
    } catch (error) {
      console.error('Error transcribing video:', error);
      let errorMessage = 'Failed to transcribe video. Please try again.';
      
      if (axios.isAxiosError(error)) {
        errorMessage = error.response?.data?.detail || error.message;
      }

      set({
        transcriptionState: {
          ...get().transcriptionState,
          isTranscribing: false,
          transcriptionError: errorMessage,
        }
      });
    }
  },

  summarizeTranscription: async (transcription: string) => {
    set({
      transcriptionState: {
        ...get().transcriptionState,
        isSummarizing: true,
        summarizationError: null,
      }
    });

    try {
      const response = await axios.post<SummarizeResponse>(
        `${API_BASE_URL}/summarize_transcription`,
        { transcription },
        {
          headers: {
            'Content-Type': 'application/json',
          },
          timeout: 60000, // 1 minute timeout for summarization
        }
      );

      set({
        transcriptionState: {
          ...get().transcriptionState,
          summary: response.data.summary,
          isSummarizing: false,
          summarizationError: null,
        }
      });
    } catch (error) {
      console.error('Error summarizing transcription:', error);
      let errorMessage = 'Failed to summarize transcription. Please try again.';
      
      if (axios.isAxiosError(error)) {
        errorMessage = error.response?.data?.detail || error.message;
      }

      set({
        transcriptionState: {
          ...get().transcriptionState,
          isSummarizing: false,
          summarizationError: errorMessage,
        }
      });
    }
  },

  clearTranscription: () => {
    set({
      transcriptionState: {
        transcription: '',
        summary: '',
        video_title: '',
        video_url: '',
        isTranscribing: false,
        isSummarizing: false,
        transcriptionError: null,
        summarizationError: null,
      }
    });
  },

  exportTranscript: async (format: 'pdf' | 'txt') => {
    const { transcriptionState } = get();
    
    if (!transcriptionState.transcription) {
      alert('No transcription available to export.');
      return;
    }

    try {
      const params = new URLSearchParams({
        transcription: transcriptionState.transcription,
        summary: transcriptionState.summary || 'No summary available',
        video_title: transcriptionState.video_title || 'Unknown Video',
        video_url: transcriptionState.video_url || '',
        format: format
      });

      const response = await axios.post(
        `${API_BASE_URL}/export/transcript?${params}`,
        {},
        {
          responseType: 'blob',
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );

      const filename = getFilenameFromResponse(response, `transcript.${format}`);
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error exporting transcript:', error);
      alert(`Failed to export transcript as ${format.toUpperCase()}. Please try again.`);
    }
  },

  // Learning Mode Functions
  generateLearningMode: async (videoUrl: string) => {
    set({
      learningModeState: {
        ...get().learningModeState,
        isGenerating: true,
        error: null,
      }
    });

    try {
      const encodedUrl = encodeURIComponent(videoUrl);
      const response = await axios.post<LearningModeResponse>(
        `${API_BASE_URL}/learning_mode/${encodedUrl}`,
        {},
        {
          headers: {
            'Content-Type': 'application/json',
          },
          timeout: 300000, // 5 minute timeout for learning mode generation
        }
      );

      set({
        learningModeState: {
          flashcards: response.data.flashcards,
          currentCardIndex: 0,
          showAnswer: false,
          cardProgress: {},
          isGenerating: false,
          error: null,
          video_title: response.data.video_title,
          video_id: response.data.video_id,
        }
      });
    } catch (error) {
      console.error('Error generating learning mode:', error);
      let errorMessage = 'Failed to generate learning mode. Please try again.';
      
      if (axios.isAxiosError(error)) {
        errorMessage = error.response?.data?.detail || error.message;
      }

      set({
        learningModeState: {
          ...get().learningModeState,
          isGenerating: false,
          error: errorMessage,
        }
      });
    }
  },

  setCurrentCard: (index: number) => {
    const { learningModeState } = get();
    if (index >= 0 && index < learningModeState.flashcards.length) {
      set({
        learningModeState: {
          ...learningModeState,
          currentCardIndex: index,
          showAnswer: false,
        }
      });
    }
  },

  toggleAnswer: () => {
    const { learningModeState } = get();
    set({
      learningModeState: {
        ...learningModeState,
        showAnswer: !learningModeState.showAnswer,
      }
    });
  },

  rateCard: (rating: 'known' | 'difficult') => {
    const { learningModeState } = get();
    const currentIndex = learningModeState.currentCardIndex;
    
    set({
      learningModeState: {
        ...learningModeState,
        cardProgress: {
          ...learningModeState.cardProgress,
          [currentIndex]: rating,
        }
      }
    });

    // Auto-advance to next card if not the last one
    if (currentIndex < learningModeState.flashcards.length - 1) {
      setTimeout(() => {
        get().setCurrentCard(currentIndex + 1);
      }, 500);
    }
  },

  resetLearningMode: () => {
    set({
      learningModeState: {
        flashcards: [],
        currentCardIndex: 0,
        showAnswer: false,
        cardProgress: {},
        isGenerating: false,
        error: null,
        video_title: '',
        video_id: '',
      }
    });
  },

  // Syllabus methods
  uploadSyllabus: async (file?: File, textContent?: string) => {
    set({
      syllabusState: {
        ...get().syllabusState,
        isUploading: true,
        error: null,
      }
    });

    try {
      const formData = new FormData();
      
      if (file) {
        formData.append('file', file);
      } else if (textContent) {
        formData.append('text_content', textContent);
      } else {
        throw new Error('Either file or text content must be provided');
      }

      const response = await axios.post(
        `${API_BASE_URL}/upload_syllabus`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
          timeout: 60000, // 1 minute timeout
        }
      );

      set({
        syllabusState: {
          ...get().syllabusState,
          topics: response.data.topics,
          totalTopics: response.data.total_topics,
          isUploading: false,
          error: null,
        }
      });
    } catch (error) {
      console.error('Error uploading syllabus:', error);
      let errorMessage = 'Failed to upload syllabus. Please try again.';
      
      if (axios.isAxiosError(error)) {
        errorMessage = error.response?.data?.detail || error.message;
      }

      set({
        syllabusState: {
          ...get().syllabusState,
          isUploading: false,
          error: errorMessage,
        }
      });
    }
  },

  getVideosBySyllabus: async (topics: SyllabusTopic[]) => {
    set({
      syllabusState: {
        ...get().syllabusState,
        isProcessing: true,
        error: null,
      }
    });

    try {
      const response = await axios.post(
        `${API_BASE_URL}/videos_by_syllabus`,
        { topics },
        {
          headers: {
            'Content-Type': 'application/json',
          },
          timeout: 120000, // 2 minute timeout
        }
      );

      set({
        syllabusState: {
          ...get().syllabusState,
          syllabusVideos: response.data.syllabus_mapping,
          totalVideos: response.data.total_videos,
          isProcessing: false,
          error: null,
        }
      });
    } catch (error) {
      console.error('Error getting videos by syllabus:', error);
      let errorMessage = 'Failed to get videos for syllabus. Please try again.';
      
      if (axios.isAxiosError(error)) {
        errorMessage = error.response?.data?.detail || error.message;
      }

      set({
        syllabusState: {
          ...get().syllabusState,
          isProcessing: false,
          error: errorMessage,
        }
      });
    }
  },

  generateQuiz: async (topics: string[], numQuestions: number = 10, difficulty: string = 'medium', questionTypes: string[] = ['mcq', 'true_false'], subject: string = 'General') => {
    set({
      quizState: {
        ...get().quizState,
        isGenerating: true,
        error: null,
      }
    });

    try {
      const response = await axios.post(
        `${API_BASE_URL}/generate_quiz`,
        {
          topics,
          num_questions: numQuestions,
          question_types: questionTypes,
          difficulty,
          subject
        },
        {
          headers: {
            'Content-Type': 'application/json',
          },
          timeout: 60000, // 1 minute timeout
        }
      );

      set({
        quizState: {
          questions: response.data.questions,
          currentQuestionIndex: 0,
          userAnswers: {},
          isGenerating: false,
          isCompleted: false,
          score: 0,
          error: null,
          totalQuestions: response.data.total_questions,
          topicsCovered: response.data.topics_covered,
          source: response.data.source || 'api',
          difficulty: response.data.difficulty || 'medium',
          questionTypes: response.data.question_types || questionTypes,
          subject: response.data.subject || subject,
        }
      });
    } catch (error) {
      console.error('Error generating quiz:', error);
      let errorMessage = 'Failed to generate quiz. Please try again.';
      
      if (axios.isAxiosError(error)) {
        errorMessage = error.response?.data?.detail || error.message;
      }

      set({
        quizState: {
          ...get().quizState,
          isGenerating: false,
          error: errorMessage,
        }
      });
    }
  },

  submitQuizAnswer: (questionIndex: number, answer: string) => {
    const { quizState } = get();
    set({
      quizState: {
        ...quizState,
        userAnswers: {
          ...quizState.userAnswers,
          [questionIndex]: answer,
        }
      }
    });
  },

  nextQuestion: () => {
    const { quizState } = get();
    if (quizState.currentQuestionIndex < quizState.questions.length - 1) {
      set({
        quizState: {
          ...quizState,
          currentQuestionIndex: quizState.currentQuestionIndex + 1,
        }
      });
    }
  },

  previousQuestion: () => {
    const { quizState } = get();
    if (quizState.currentQuestionIndex > 0) {
      set({
        quizState: {
          ...quizState,
          currentQuestionIndex: quizState.currentQuestionIndex - 1,
        }
      });
    }
  },

  completeQuiz: () => {
    const { quizState } = get();
    const questions = quizState.questions;
    const userAnswers = quizState.userAnswers;
    
    let correctAnswers = 0;
    const totalQuestions = questions.length;
    
    questions.forEach((question, index) => {
      const userAnswer = userAnswers[index];
      if (userAnswer && userAnswer === question.answer) {
        correctAnswers++;
      }
    });
    
    const score = totalQuestions > 0 ? (correctAnswers / totalQuestions) * 100 : 0;
    
    set({
      quizState: {
        ...quizState,
        isCompleted: true,
        score,
      }
    });
  },

  generateReport: async (quizAttempts: QuizAttempt[], watchedVideos: string[], syllabusTopics: SyllabusTopic[]) => {
    set({
      reportState: {
        ...get().reportState,
        isGenerating: true,
        error: null,
      }
    });

    try {
      const response = await axios.post(
        `${API_BASE_URL}/generate_report`,
        {
          quiz_attempts: quizAttempts,
          watched_videos: watchedVideos,
          syllabus_topics: syllabusTopics,
        },
        {
          headers: {
            'Content-Type': 'application/json',
          },
          timeout: 60000, // 1 minute timeout
        }
      );

      set({
        reportState: {
          report: response.data,
          isGenerating: false,
          error: null,
        }
      });
    } catch (error) {
      console.error('Error generating report:', error);
      let errorMessage = 'Failed to generate report. Please try again.';
      
      if (axios.isAxiosError(error)) {
        errorMessage = error.response?.data?.detail || error.message;
      }

      set({
        reportState: {
          ...get().reportState,
          isGenerating: false,
          error: errorMessage,
        }
      });
    }
  },

  resetSyllabus: () => {
    set({
      syllabusState: {
        topics: [],
        syllabusVideos: [],
        isUploading: false,
        isProcessing: false,
        error: null,
        totalTopics: 0,
        totalVideos: 0,
      }
    });
  },

  resetQuiz: () => {
    set({
      quizState: {
        questions: [],
        currentQuestionIndex: 0,
        userAnswers: {},
        isGenerating: false,
        isCompleted: false,
        score: 0,
        error: null,
        totalQuestions: 0,
        topicsCovered: [],
      }
    });
  },

  resetReport: () => {
    set({
      reportState: {
        report: null,
        isGenerating: false,
        error: null,
      }
    });
  },

  // Study module methods
  loadSubjects: async () => {
    // This method will be implemented when we add study state to the store
    console.log('loadSubjects method called');
  },

  loadUnits: async (subjectCode: string) => {
    // This method will be implemented when we add study state to the store
    console.log('loadUnits method called with:', subjectCode);
  },

  selectSubject: (subjectCode: string) => {
    // This method will be implemented when we add study state to the store
    console.log('selectSubject method called with:', subjectCode);
  },

  selectUnits: (units: string[]) => {
    // This method will be implemented when we add study state to the store
    console.log('selectUnits method called with:', units);
  },

  generateStudyMaterials: async () => {
    // This method will be implemented when we add study state to the store
    console.log('generateStudyMaterials method called');
  },

  generateStudyQuiz: async () => {
    // This method will be implemented when we add study state to the store
    console.log('generateStudyQuiz method called');
  },

  submitStudyQuiz: async () => {
    // This method will be implemented when we add study state to the store
    console.log('submitStudyQuiz method called');
  },

  generateStudyReport: async () => {
    // This method will be implemented when we add study state to the store
    console.log('generateStudyReport method called');
  },

  resetStudy: () => {
    // This method will be implemented when we add study state to the store
    console.log('resetStudy method called');
  },
})); 