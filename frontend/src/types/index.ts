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

export type TabType = 'overview' | 'transcription' | 'summary' | 'comments' | 'learning';

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
} 