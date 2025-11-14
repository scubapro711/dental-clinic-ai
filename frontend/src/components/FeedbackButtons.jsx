import React, { useState } from 'react';
import { ThumbsUp, ThumbsDown, Star } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import API_CONFIG from '@/config/api';

/**
 * Feedback Buttons Component
 * 
 * Allows users to rate agent responses with thumbs up/down or star rating.
 * Feedback is used to build training dataset for fine-tuning.
 */
export default function FeedbackButtons({
  conversationId,
  messageId,
  userMessage,
  agentResponse,
  agentName,
  onFeedbackSubmitted
}) {
  const [feedback, setFeedback] = useState(null); // 'up', 'down', or rating number
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showRating, setShowRating] = useState(false);

  const submitFeedback = async (type, value) => {
    setIsSubmitting(true);
    
    try {
      const response = await fetch(API_CONFIG.endpoint('ai/feedback/submit'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token') || 'demo_token'}`
        },
        body: JSON.stringify({
          conversation_id: conversationId,
          message_id: messageId,
          user_message: userMessage,
          agent_response: agentResponse,
          agent_name: agentName,
          feedback_type: type,
          feedback_value: value
        })
      });

      if (response.ok) {
        setFeedback(type === 'thumbs_up' ? 'up' : type === 'thumbs_down' ? 'down' : value);
        if (onFeedbackSubmitted) {
          onFeedbackSubmitted({ type, value });
        }
      }
    } catch (error) {
      console.error('Error submitting feedback:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleThumbsUp = () => {
    if (feedback === 'up') return;
    setShowRating(true);
  };

  const handleThumbsDown = () => {
    if (feedback === 'down') return;
    submitFeedback('thumbs_down', false);
  };

  const handleRating = (rating) => {
    submitFeedback('rating', rating);
    setShowRating(false);
  };

  return (
    <div className="flex items-center gap-2 mt-2">
      {!showRating && !feedback && (
        <>
          <Button
            variant="ghost"
            size="sm"
            onClick={handleThumbsUp}
            disabled={isSubmitting || feedback === 'up'}
            className={cn(
              "h-7 px-2 text-xs hover:bg-green-50 hover:text-green-600 transition-colors",
              feedback === 'up' && "bg-green-100 text-green-700"
            )}
          >
            <ThumbsUp className={cn(
              "w-3.5 h-3.5",
              feedback === 'up' && "fill-current"
            )} />
          </Button>

          <Button
            variant="ghost"
            size="sm"
            onClick={handleThumbsDown}
            disabled={isSubmitting || feedback === 'down'}
            className={cn(
              "h-7 px-2 text-xs hover:bg-red-50 hover:text-red-600 transition-colors",
              feedback === 'down' && "bg-red-100 text-red-700"
            )}
          >
            <ThumbsDown className={cn(
              "w-3.5 h-3.5",
              feedback === 'down' && "fill-current"
            )} />
          </Button>
        </>
      )}

      {showRating && !feedback && (
        <div className="flex items-center gap-1 animate-in fade-in slide-in-from-left-2 duration-200">
          <span className="text-xs text-gray-600 mr-1">דרג:</span>
          {[1, 2, 3, 4, 5].map((rating) => (
            <Button
              key={rating}
              variant="ghost"
              size="sm"
              onClick={() => handleRating(rating)}
              disabled={isSubmitting}
              className="h-7 w-7 p-0 hover:bg-yellow-50 transition-colors"
            >
              <Star className="w-3.5 h-3.5 text-yellow-500 hover:fill-yellow-500" />
            </Button>
          ))}
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setShowRating(false)}
            className="h-7 px-2 text-xs text-gray-500"
          >
            ביטול
          </Button>
        </div>
      )}

      {feedback && typeof feedback === 'number' && (
        <div className="flex items-center gap-1">
          {[...Array(feedback)].map((_, i) => (
            <Star key={i} className="w-3 h-3 text-yellow-500 fill-yellow-500" />
          ))}
          <span className="text-xs text-gray-500 mr-1">תודה על הדירוג!</span>
        </div>
      )}

      {feedback === 'up' && (
        <span className="text-xs text-green-600 flex items-center gap-1">
          <ThumbsUp className="w-3 h-3 fill-current" />
          תודה!
        </span>
      )}

      {feedback === 'down' && (
        <span className="text-xs text-red-600 flex items-center gap-1">
          <ThumbsDown className="w-3 h-3 fill-current" />
          נשתפר!
        </span>
      )}
    </div>
  );
}
