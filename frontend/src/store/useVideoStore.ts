import { create } from 'zustand';
import axios from 'axios';
import { VideoStore, VideoResponse, SortOption, TranscribeResponse, SummarizeResponse } from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Memoized sorting function
const sortVideos = (videos: any[], sortBy: SortOption): any[] => {
  const sortedVideos = [...videos]; // Clone the array
  
  switch (sortBy) {
    case 'views':
      return sortedVideos.sort((a, b) => b.views - a.views);
    case 'likes':
      return sortedVideos.sort((a, b) => b.likes - a.likes);
    case 'date':
      // Sort by published date if available, otherwise keep original order
      return sortedVideos.sort((a, b) => {
        if (a.published_date && b.published_date) {
          return new Date(b.published_date).getTime() - new Date(a.published_date).getTime();
        }
        return 0;
      });
    case 'relevance':
    default:
      // Keep original order (relevance as returned by API)
      return sortedVideos;
  }
};

export const useVideoStore = create<VideoStore>((set, get) => ({
  keyword: '',
  loading: false,
  videos: [],
  filteredVideos: [],
  error: null,
  totalCount: 0,
  source: '',
  filterState: {
    sortBy: 'relevance'
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

  setKeyword: (keyword: string) => {
    set({ keyword });
  },

  setLoading: (loading: boolean) => {
    set({ loading });
  },

  setResults: (response: VideoResponse) => {
    const { filterState } = get();
    const sortedVideos = sortVideos(response.videos, filterState.sortBy);
    
    set({
      videos: response.videos,
      filteredVideos: sortedVideos,
      totalCount: response.total_count,
      source: response.source,
      error: null,
    });
  },

  setError: (error: string) => {
    set({ error, videos: [], filteredVideos: [], totalCount: 0, source: '' });
  },

  clearError: () => {
    set({ error: null });
  },

  setSortBy: (sortBy: SortOption) => {
    const { videos } = get();
    const sortedVideos = sortVideos(videos, sortBy);
    
    set({
      filterState: { sortBy },
      filteredVideos: sortedVideos
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
    try {
      const response = await axios.post(
        `${API_BASE_URL}/export/excel`,
        { videos },
        {
          responseType: 'blob',
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', response.headers['content-disposition']?.split('filename=')[1] || 'yt_results.xlsx');
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
    try {
      const response = await axios.post(
        `${API_BASE_URL}/export/pdf`,
        { videos },
        {
          responseType: 'blob',
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', response.headers['content-disposition']?.split('filename=')[1] || 'yt_results.pdf');
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

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      const extension = format === 'pdf' ? 'pdf' : 'txt';
      link.setAttribute('download', response.headers['content-disposition']?.split('filename=')[1] || `transcript.${extension}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error exporting transcript:', error);
      alert(`Failed to export transcript as ${format.toUpperCase()}. Please try again.`);
    }
  },
})); 