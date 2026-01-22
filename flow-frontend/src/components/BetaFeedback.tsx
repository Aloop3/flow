import React, { useState } from 'react';
import { post } from 'aws-amplify/api';
import { fetchAuthSession } from 'aws-amplify/auth';
import { toast } from 'react-toastify';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';

interface FeedbackData {
  category: 'bug' | 'suggestion' | 'question' | 'feature-request';
  message: string;
  pageUrl?: string;
}

// Helper to get auth headers
const getAuthHeaders = async () => {
  try {
    const { tokens } = await fetchAuthSession();
    return {
      Authorization: `Bearer ${tokens?.idToken?.toString()}`,
    };
  } catch (error) {
    console.error('Error getting auth session:', error);
    throw new Error('Authentication required');
  }
};

const BetaFeedback: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formData, setFormData] = useState<FeedbackData>({
    category: 'bug',
    message: '',
    pageUrl: window.location.href
  });

  const categoryOptions = [
    { value: 'bug', label: '🐛 Bug Report', description: 'Something is broken or not working' },
    { value: 'suggestion', label: '💡 Suggestion', description: 'Idea for improvement' },
    { value: 'question', label: '❓ Question', description: 'Need help or clarification' },
    { value: 'feature-request', label: '✨ Feature Request', description: 'New feature idea' }
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.message.trim()) {
      toast.error('Please enter your feedback message');
      return;
    }

    setIsSubmitting(true);

    try {
      const headers = await getAuthHeaders();
      
      await post({
        apiName: 'flow-api',
        path: '/feedback',
        options: {
          body: JSON.stringify({
            category: formData.category,
            message: formData.message.trim(),
            pageUrl: formData.pageUrl
          }),
          headers: {
            ...headers,
            'Content-Type': 'application/json'
          }
        }
      });

      toast.success('Thank you! Your feedback has been submitted.');
      
      // Reset form and close widget
      setFormData({
        category: 'bug',
        message: '',
        pageUrl: window.location.href
      });
      setIsOpen(false);

    } catch (error: any) {
      console.error('Error submitting feedback:', error);
      toast.error('Failed to submit feedback. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleClose = () => {
    setIsOpen(false);
    // Reset form when closing
    setFormData({
      category: 'bug',
      message: '',
      pageUrl: window.location.href
    });
  };

  return (
    <div className="fixed bottom-4 right-4 z-50">
      {/* Collapsed State - Feedback Button */}
      {!isOpen && (
        <Button
          onClick={() => setIsOpen(true)}
          className="rounded-full p-3 shadow-lg transform transition-all duration-200 hover:scale-105"
          title="Send Beta Feedback"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 8h10m0 0V6a2 2 0 00-2-2H9a2 2 0 00-2 2v2m0 0v8a2 2 0 002 2h6a2 2 0 002-2V8M9 12h6" />
          </svg>
          <span className="hidden sm:inline text-sm font-medium ml-2">Beta Feedback</span>
        </Button>
      )}

      {/* Expanded State - Feedback Form */}
      {isOpen && (
        <div className="bg-white rounded-lg shadow-xl border border-gray-200 w-80 sm:w-96">
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b border-gray-200 bg-blue-50 rounded-t-lg">
            <div className="flex items-center gap-2">
              <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 8h10m0 0V6a2 2 0 00-2-2H9a2 2 0 00-2 2v2m0 0v8a2 2 0 002 2h6a2 2 0 002-2V8M9 12h6" />
              </svg>
              <h3 className="font-semibold text-gray-900">Beta Feedback</h3>
              <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded-full">BETA</span>
            </div>
            <button
              onClick={handleClose}
              className="text-gray-400 hover:text-gray-600 transition-colors"
              title="Close"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="p-4 space-y-4">
            {/* Category Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Feedback Type
              </label>
              <div className="space-y-2">
                {categoryOptions.map((option) => (
                  <label key={option.value} className="flex items-start gap-2 cursor-pointer">
                    <input
                      type="radio"
                      name="category"
                      value={option.value}
                      checked={formData.category === option.value}
                      onChange={(e) => setFormData(prev => ({ 
                        ...prev, 
                        category: e.target.value as FeedbackData['category']
                      }))}
                      className="mt-1 text-blue-600 focus:ring-blue-500"
                    />
                    <div>
                      <div className="text-sm font-medium text-gray-900">{option.label}</div>
                      <div className="text-xs text-gray-500">{option.description}</div>
                    </div>
                  </label>
                ))}
              </div>
            </div>

            {/* Message */}
            <div>
              <label htmlFor="feedback-message" className="block text-sm font-medium text-gray-700 mb-1">
                Message
              </label>
              <Textarea
                id="feedback-message"
                rows={4}
                value={formData.message}
                onChange={(e) => setFormData(prev => ({ ...prev, message: e.target.value }))}
                placeholder="Describe your feedback in detail..."
                className="resize-none"
                disabled={isSubmitting}
              />
            </div>

            {/* Current Page Info */}
            <div className="text-xs text-gray-500 bg-gray-50 p-2 rounded">
              <strong>Current page:</strong> {formData.pageUrl}
            </div>

            {/* Actions */}
            <div className="flex gap-2 pt-2">
              <Button
                type="submit"
                disabled={isSubmitting || !formData.message.trim()}
                className="flex-1"
              >
                {isSubmitting ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                    Sending...
                  </>
                ) : (
                  <>
                    <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                    </svg>
                    Send Feedback
                  </>
                )}
              </Button>
              <Button
                type="button"
                variant="ghost"
                onClick={handleClose}
                disabled={isSubmitting}
              >
                Cancel
              </Button>
            </div>
          </form>

          {/* Footer */}
          <div className="px-4 pb-3 text-xs text-gray-500 text-center">
            Help us improve Flow during beta testing
          </div>
        </div>
      )}
    </div>
  );
};

export default BetaFeedback;