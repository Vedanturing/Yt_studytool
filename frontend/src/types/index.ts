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

export type SortOption = 'relevance' | 'views' | 'likes' | 'date';

export interface FilterState {
  sortBy: SortOption;
}

export interface VideoStore {
  keyword: string;
  loading: boolean;
  videos: Video[];
  filteredVideos: Video[];
  error: string | null;
  totalCount: number;
  source: string;
  filterState: FilterState;
  transcriptionState: TranscriptionState;
  setKeyword: (keyword: string) => void;
  setLoading: (loading: boolean) => void;
  setResults: (response: VideoResponse) => void;
  setError: (error: string) => void;
  clearError: () => void;
  setSortBy: (sortBy: SortOption) => void;
  fetchVideos: (keyword: string) => Promise<void>;
  exportToExcel: (videos: Video[]) => Promise<void>;
  exportToPdf: (videos: Video[]) => Promise<void>;
  transcribeVideo: (videoUrl: string) => Promise<void>;
  summarizeTranscription: (transcription: string) => Promise<void>;
  clearTranscription: () => void;
  exportTranscript: (format: 'pdf' | 'txt') => Promise<void>;
} 