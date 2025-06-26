import React, { useEffect } from 'react';
import { useVideoStore } from '../store/useVideoStore';
import { Video } from '../types';

interface TranscriptionModalProps {
  isOpen: boolean;
  onClose: () => void;
  video: Video;
}

export const TranscriptionModal: React.FC<TranscriptionModalProps> = ({
  isOpen,
  onClose,
  video
}) => {
  const {
    transcriptionState,
    transcribeVideo,
    summarizeTranscription,
    clearTranscription,
    exportTranscript
  } = useVideoStore();

  const {
    transcription,
    summary,
    video_title,
    isTranscribing,
    isSummarizing,
    transcriptionError,
    summarizationError
  } = transcriptionState;

  useEffect(() => {
    if (isOpen && video.video_url && !transcription && !isTranscribing) {
      transcribeVideo(video.video_url);
    }
  }, [isOpen, video.video_url, transcription, isTranscribing, transcribeVideo]);

  const handleClose = () => {
    clearTranscription();
    onClose();
  };

  const handleSummarize = () => {
    if (transcription && !isSummarizing) {
      summarizeTranscription(transcription);
    }
  };

  const copyToClipboard = (text: string, type: string) => {
    navigator.clipboard.writeText(text).then(() => {
      alert(`${type} copied to clipboard!`);
    }).catch(() => {
      alert('Failed to copy to clipboard');
    });
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
            Video Transcription
          </h2>
          <button
            onClick={handleClose}
            className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[calc(90vh-120px)]">
          {/* Video Info */}
          <div className="mb-6 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
            <h3 className="font-medium text-gray-900 dark:text-white mb-2">Video Information</h3>
            <p className="text-sm text-gray-600 dark:text-gray-300 mb-1">
              <strong>Title:</strong> {video.title}
            </p>
            <p className="text-sm text-gray-600 dark:text-gray-300">
              <strong>URL:</strong> 
              <a href={video.video_url} target="_blank" rel="noopener noreferrer" className="text-blue-600 dark:text-blue-400 hover:underline ml-1">
                {video.video_url}
              </a>
            </p>
          </div>

          {/* Transcription Section */}
          <div className="mb-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-medium text-gray-900 dark:text-white">Transcription</h3>
              {transcription && (
                <div className="flex gap-2">
                  <button
                    onClick={() => copyToClipboard(transcription, 'Transcription')}
                    className="px-3 py-1 text-sm bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
                  >
                    Copy
                  </button>
                </div>
              )}
            </div>

            {isTranscribing && (
              <div className="flex items-center space-x-3 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
                <div>
                  <p className="font-medium text-blue-900 dark:text-blue-100">Transcribing video...</p>
                  <p className="text-sm text-blue-600 dark:text-blue-300">This may take a few minutes depending on video length</p>
                </div>
              </div>
            )}

            {transcriptionError && (
              <div className="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
                <p className="text-red-600 dark:text-red-400 font-medium">Transcription Error</p>
                <p className="text-red-500 dark:text-red-300 text-sm mt-1">{transcriptionError}</p>
                <button
                  onClick={() => transcribeVideo(video.video_url)}
                  className="mt-2 px-3 py-1 bg-red-500 text-white text-sm rounded hover:bg-red-600 transition-colors"
                >
                  Retry
                </button>
              </div>
            )}

            {transcription && (
              <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4 max-h-64 overflow-y-auto">
                <p className="text-gray-800 dark:text-gray-200 whitespace-pre-wrap">{transcription}</p>
              </div>
            )}
          </div>

          {/* Summary Section */}
          {transcription && (
            <div className="mb-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium text-gray-900 dark:text-white">Summary</h3>
                <div className="flex gap-2">
                  {!summary && !isSummarizing && (
                    <button
                      onClick={handleSummarize}
                      className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600 transition-colors"
                    >
                      Generate Summary
                    </button>
                  )}
                  {summary && (
                    <button
                      onClick={() => copyToClipboard(summary, 'Summary')}
                      className="px-3 py-1 text-sm bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
                    >
                      Copy
                    </button>
                  )}
                </div>
              </div>

              {isSummarizing && (
                <div className="flex items-center space-x-3 p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
                  <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-green-600"></div>
                  <div>
                    <p className="font-medium text-green-900 dark:text-green-100">Generating summary...</p>
                    <p className="text-sm text-green-600 dark:text-green-300">Processing transcription text</p>
                  </div>
                </div>
              )}

              {summarizationError && (
                <div className="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
                  <p className="text-red-600 dark:text-red-400 font-medium">Summarization Error</p>
                  <p className="text-red-500 dark:text-red-300 text-sm mt-1">{summarizationError}</p>
                  <button
                    onClick={handleSummarize}
                    className="mt-2 px-3 py-1 bg-red-500 text-white text-sm rounded hover:bg-red-600 transition-colors"
                  >
                    Retry
                  </button>
                </div>
              )}

              {summary && (
                <div className="bg-green-50 dark:bg-green-900/20 rounded-lg p-4">
                  <p className="text-gray-800 dark:text-gray-200 whitespace-pre-wrap">{summary}</p>
                </div>
              )}
            </div>
          )}

          {/* Export Section */}
          {transcription && (
            <div className="border-t border-gray-200 dark:border-gray-700 pt-6">
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Export</h3>
              <div className="flex gap-2">
                <button
                  onClick={() => exportTranscript('txt')}
                  className="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600 transition-colors"
                >
                  Export as TXT
                </button>
                <button
                  onClick={() => exportTranscript('pdf')}
                  className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600 transition-colors"
                >
                  Export as PDF
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}; 