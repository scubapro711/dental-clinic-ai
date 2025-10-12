import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Textarea } from '@/components/ui/textarea';
import { 
  Brain, ThumbsUp, ThumbsDown, Star, TrendingUp, 
  CheckCircle2, XCircle, Clock, Sparkles, Download, Upload 
} from 'lucide-react';
import { cn } from '@/lib/utils';

/**
 * Enhanced Fine-Tuning Widget
 * 
 * Features:
 * - Feedback collection for AI responses
 * - Rating system (1-5 stars)
 * - Good/Bad example categorization
 * - Training data management
 * - Model performance tracking
 * - Export training data
 * - Integration with Decision Queue
 */
export default function EnhancedFineTuningWidget({ onChatWithAgent }) {
  const [trainingData, setTrainingData] = useState({
    good: 0,
    bad: 0,
    pending: 0,
  });
  
  const [modelPerformance, setModelPerformance] = useState({
    baseModel: 75.0,
    fineTunedModel: 89.0,
    improvement: 14.0,
  });
  
  const [recentFeedback, setRecentFeedback] = useState([]);
  const [showFeedbackForm, setShowFeedbackForm] = useState(false);
  const [selectedResponse, setSelectedResponse] = useState(null);
  
  // Load training data
  useEffect(() => {
    loadTrainingData();
  }, []);
  
  const loadTrainingData = async () => {
    try {
      // TODO: Replace with actual API call
      // const response = await fetch('/api/v1/fine-tuning/stats');
      // const data = await response.json();
      
      // Mock data for now
      setTrainingData({
        good: 45,
        bad: 12,
        pending: 8,
      });
      
      setRecentFeedback([
        {
          id: 1,
          agent: 'marcus',
          query: 'What is our revenue this month?',
          response: 'Revenue is ₪45,000, up 15% from last month.',
          rating: 5,
          category: 'good',
          feedback: 'Accurate and concise',
          timestamp: Date.now() - 3600000,
        },
        {
          id: 2,
          agent: 'sarah',
          query: 'Analyze tooth #14 for patient John',
          response: 'Tooth #14 shows signs of decay...',
          rating: 4,
          category: 'good',
          feedback: 'Good analysis but could be more detailed',
          timestamp: Date.now() - 7200000,
        },
        {
          id: 3,
          agent: 'alex',
          query: 'Schedule appointment for Sarah',
          response: 'I cannot schedule appointments yet.',
          rating: 2,
          category: 'bad',
          feedback: 'Should provide alternative or ask for details',
          timestamp: Date.now() - 10800000,
        },
      ]);
    } catch (error) {
      console.error('Error loading training data:', error);
    }
  };
  
  const handleProvideFeedback = () => {
    setShowFeedbackForm(true);
  };
  
  const handleExportData = () => {
    // TODO: Implement export functionality
    console.log('Exporting training data...');
  };
  
  const handleTrainModel = () => {
    if (onChatWithAgent) {
      onChatWithAgent('Start fine-tuning the model with the collected feedback data');
    }
  };
  
  const totalExamples = trainingData.good + trainingData.bad;
  const canTrain = trainingData.good >= 10;
  
  return (
    <Card className="h-full flex flex-col">
      <CardHeader className="border-b flex-shrink-0">
        <div className="flex items-center justify-between">
          <CardTitle className="text-sm flex items-center gap-2">
            <Brain className="w-4 h-4 text-purple-600" />
            AI Fine-Tuning
          </CardTitle>
          <Badge variant="secondary" className="text-xs">
            <Sparkles className="w-3 h-3 mr-1" />
            Active
          </Badge>
        </div>
      </CardHeader>
      
      <CardContent className="flex-1 overflow-y-auto p-4 space-y-4">
        {/* Training Data Stats */}
        <div className="space-y-2">
          <div className="text-xs font-semibold text-gray-600">Training Data</div>
          
          <div className="grid grid-cols-3 gap-2">
            <StatCard
              icon={<ThumbsUp className="w-4 h-4 text-green-600" />}
              label="Good"
              value={trainingData.good}
              color="bg-green-50 border-green-200"
            />
            <StatCard
              icon={<ThumbsDown className="w-4 h-4 text-red-600" />}
              label="Bad"
              value={trainingData.bad}
              color="bg-red-50 border-red-200"
            />
            <StatCard
              icon={<Clock className="w-4 h-4 text-yellow-600" />}
              label="Pending"
              value={trainingData.pending}
              color="bg-yellow-50 border-yellow-200"
            />
          </div>
          
          <div className="text-xs text-gray-600">
            Total: {totalExamples} examples
          </div>
        </div>
        
        {/* Model Performance */}
        <div className="space-y-2">
          <div className="text-xs font-semibold text-gray-600">Model Performance</div>
          
          <div className="bg-gradient-to-br from-purple-50 to-blue-50 rounded-lg p-3 border-2 border-purple-200">
            <div className="space-y-2">
              <div className="flex items-center justify-between text-xs">
                <span className="text-gray-600">Base Model</span>
                <span className="font-semibold">{modelPerformance.baseModel}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-gray-400 h-2 rounded-full"
                  style={{ width: `${modelPerformance.baseModel}%` }}
                />
              </div>
              
              <div className="flex items-center justify-between text-xs">
                <span className="text-gray-600">Fine-tuned Model</span>
                <span className="font-semibold text-purple-600">
                  {modelPerformance.fineTunedModel}%
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-gradient-to-r from-purple-500 to-blue-500 h-2 rounded-full"
                  style={{ width: `${modelPerformance.fineTunedModel}%` }}
                />
              </div>
              
              <div className="flex items-center justify-center gap-1 text-xs text-green-600 font-semibold pt-1">
                <TrendingUp className="w-3 h-3" />
                <span>+{modelPerformance.improvement}% improvement</span>
              </div>
            </div>
          </div>
        </div>
        
        {/* Recent Feedback */}
        <div className="space-y-2">
          <div className="text-xs font-semibold text-gray-600">Recent Feedback</div>
          
          <div className="space-y-2">
            {recentFeedback.slice(0, 3).map((feedback) => (
              <FeedbackItem key={feedback.id} feedback={feedback} />
            ))}
          </div>
        </div>
        
        {/* Training Status */}
        {!canTrain && (
          <div className="bg-yellow-50 border-2 border-yellow-200 rounded-lg p-3">
            <div className="flex items-start gap-2">
              <Clock className="w-4 h-4 text-yellow-600 flex-shrink-0 mt-0.5" />
              <div className="text-xs">
                <p className="font-semibold text-yellow-900 mb-1">
                  Need more training data
                </p>
                <p className="text-yellow-800">
                  Collect at least 10 good examples to start training.
                  Current: {trainingData.good}/10
                </p>
              </div>
            </div>
          </div>
        )}
        
        {/* Actions */}
        <div className="space-y-2">
          <Button
            onClick={handleProvideFeedback}
            className="w-full text-xs"
            variant="outline"
          >
            <Star className="w-3 h-3 mr-2" />
            Provide Feedback
          </Button>
          
          <div className="grid grid-cols-2 gap-2">
            <Button
              onClick={handleExportData}
              className="text-xs"
              variant="outline"
              size="sm"
              aria-label="Export training data as JSON"
            >
              <Download className="w-3 h-3 mr-1" aria-hidden="true" />
              Export
            </Button>
            
            <Button
              onClick={handleTrainModel}
              className="text-xs"
              variant="outline"
              size="sm"
              disabled={!canTrain}
              aria-label={canTrain ? "Start training model" : "Need at least 10 good examples to train"}
              aria-disabled={!canTrain}
            >
              <Upload className="w-3 h-3 mr-1" aria-hidden="true" />
              Train
            </Button>
          </div>
        </div>
      </CardContent>
      
      {/* Feedback Form Modal */}
      {showFeedbackForm && (
        <FeedbackFormModal
          onClose={() => setShowFeedbackForm(false)}
          onSubmit={(feedback) => {
            console.log('Feedback submitted:', feedback);
            setShowFeedbackForm(false);
            loadTrainingData();
          }}
        />
      )}
    </Card>
  );
}

/**
 * Stat Card Component
 */
function StatCard({ icon, label, value, color }) {
  return (
    <div className={cn('rounded-lg border-2 p-2 text-center', color)}>
      <div className="flex justify-center mb-1">{icon}</div>
      <div className="text-lg font-bold">{value}</div>
      <div className="text-xs text-gray-600">{label}</div>
    </div>
  );
}

/**
 * Feedback Item Component
 */
function FeedbackItem({ feedback }) {
  const agentConfig = {
    alex: { name: 'Alex', icon: '👨‍⚕️', color: 'blue' },
    marcus: { name: 'Marcus', icon: '💼', color: 'green' },
    sarah: { name: 'Sarah', icon: '🩺', color: 'purple' },
    sophia: { name: 'Sophia', icon: '📋', color: 'pink' },
  };
  
  const config = agentConfig[feedback.agent] || agentConfig.alex;
  
  const timeAgo = getTimeAgo(feedback.timestamp);
  
  return (
    <div className="bg-white rounded-lg border-2 border-gray-200 p-2 hover:border-gray-300 transition-colors">
      <div className="flex items-start gap-2">
        <span className="text-lg flex-shrink-0">{config.icon}</span>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-semibold">{config.name}</span>
            <Badge 
              variant={feedback.category === 'good' ? 'success' : 'destructive'}
              className="text-xs"
            >
              {feedback.category === 'good' ? (
                <CheckCircle2 className="w-3 h-3 mr-1" />
              ) : (
                <XCircle className="w-3 h-3 mr-1" />
              )}
              {feedback.category}
            </Badge>
            <div className="flex items-center gap-0.5">
              {[...Array(5)].map((_, i) => (
                <Star
                  key={i}
                  className={cn(
                    'w-3 h-3',
                    i < feedback.rating ? 'fill-yellow-400 text-yellow-400' : 'text-gray-300'
                  )}
                />
              ))}
            </div>
          </div>
          <p className="text-xs text-gray-600 line-clamp-1 mb-1">
            {feedback.query}
          </p>
          <p className="text-xs text-gray-500 italic line-clamp-1">
            "{feedback.feedback}"
          </p>
          <div className="text-xs text-gray-400 mt-1">{timeAgo}</div>
        </div>
      </div>
    </div>
  );
}

/**
 * Feedback Form Modal Component
 */
function FeedbackFormModal({ onClose, onSubmit }) {
  const [rating, setRating] = useState(0);
  const [category, setCategory] = useState('good');
  const [feedback, setFeedback] = useState('');
  const [query, setQuery] = useState('');
  const [response, setResponse] = useState('');
  
  const handleSubmit = () => {
    if (!query || !response || rating === 0) {
      alert('Please fill in all required fields');
      return;
    }
    
    onSubmit({
      query,
      response,
      rating,
      category,
      feedback,
      timestamp: Date.now(),
    });
  };
  
  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <Card className="w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <CardHeader className="border-b">
          <CardTitle className="text-sm flex items-center justify-between">
            <span className="flex items-center gap-2">
              <Star className="w-4 h-4 text-yellow-600" />
              Provide Feedback
            </span>
            <Button variant="ghost" size="sm" onClick={onClose}>
              ✕
            </Button>
          </CardTitle>
        </CardHeader>
        
        <CardContent className="p-4 space-y-4">
          {/* Query */}
          <div>
            <label htmlFor="feedback-query" className="text-xs font-semibold text-gray-600 mb-1 block">
              User Query <span className="text-red-600" aria-label="required">*</span>
            </label>
            <Textarea
              id="feedback-query"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="What did the user ask?"
              className="text-sm"
              rows={2}
              required
              aria-required="true"
            />
          </div>
          
          {/* Response */}
          <div>
            <label htmlFor="feedback-response" className="text-xs font-semibold text-gray-600 mb-1 block">
              AI Response <span className="text-red-600" aria-label="required">*</span>
            </label>
            <Textarea
              id="feedback-response"
              value={response}
              onChange={(e) => setResponse(e.target.value)}
              placeholder="What did the AI respond?"
              className="text-sm"
              rows={3}
              required
              aria-required="true"
            />
          </div>
          
          {/* Rating */}
          <fieldset>
            <legend className="text-xs font-semibold text-gray-600 mb-2 block">
              Rating <span className="text-red-600" aria-label="required">*</span>
            </legend>
            <div className="flex items-center gap-2" role="radiogroup" aria-label="Rating from 1 to 5 stars">
              {[1, 2, 3, 4, 5].map((star) => (
                <button
                  key={star}
                  type="button"
                  role="radio"
                  aria-checked={star === rating}
                  aria-label={`${star} star${star > 1 ? 's' : ''}`}
                  onClick={() => setRating(star)}
                  className="transition-transform hover:scale-110"
                >
                  <Star
                    aria-hidden="true"
                    className={cn(
                      'w-8 h-8',
                      star <= rating ? 'fill-yellow-400 text-yellow-400' : 'text-gray-300'
                    )}
                  />
                </button>
              ))}
              <span className="text-sm text-gray-600 ml-2" aria-live="polite">
                {rating > 0 ? `${rating}/5` : 'Select rating'}
              </span>
            </div>
          </fieldset>
          
          {/* Category */}
          <fieldset>
            <legend className="text-xs font-semibold text-gray-600 mb-2 block">
              Category
            </legend>
            <div className="flex gap-2" role="radiogroup" aria-label="Example category">
              <Button
                type="button"
                role="radio"
                aria-checked={category === 'good'}
                variant={category === 'good' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setCategory('good')}
                className="flex-1"
              >
                <ThumbsUp className="w-4 h-4 mr-2" aria-hidden="true" />
                Good Example
              </Button>
              <Button
                type="button"
                role="radio"
                aria-checked={category === 'bad'}
                variant={category === 'bad' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setCategory('bad')}
                className="flex-1"
              >
                <ThumbsDown className="w-4 h-4 mr-2" aria-hidden="true" />
                Bad Example
              </Button>
            </div>
          </fieldset>
          
          {/* Feedback Notes */}
          <div>
            <label htmlFor="feedback-notes" className="text-xs font-semibold text-gray-600 mb-1 block">
              Feedback Notes (Optional)
            </label>
            <Textarea
              id="feedback-notes"
              value={feedback}
              onChange={(e) => setFeedback(e.target.value)}
              placeholder="Why is this a good/bad example? What could be improved?"
              className="text-sm"
              rows={3}
              aria-describedby="feedback-notes-desc"
            />
            <span id="feedback-notes-desc" className="text-xs text-gray-500 mt-1 block">
              Provide additional context to help improve the AI model
            </span>
          </div>
          
          {/* Actions */}
          <div className="flex gap-2 pt-2">
            <Button onClick={onClose} variant="outline" className="flex-1">
              Cancel
            </Button>
            <Button onClick={handleSubmit} className="flex-1">
              Submit Feedback
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

/**
 * Helper function to get time ago string
 */
function getTimeAgo(timestamp) {
  const seconds = Math.floor((Date.now() - timestamp) / 1000);
  
  if (seconds < 60) return `${seconds}s ago`;
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
  return `${Math.floor(seconds / 86400)}d ago`;
}

