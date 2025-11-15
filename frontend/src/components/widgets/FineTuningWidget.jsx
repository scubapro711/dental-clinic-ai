import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import API_CONFIG from '@/config/api';
import {
  Brain, 
  TrendingUp, 
  Database, 
  Download, 
  Upload,
  CheckCircle,
  XCircle,
  Clock,
  Zap
} from 'lucide-react';

/**
 * Fine-Tuning Widget Component
 * 
 * Displays training data collection, model performance, and feedback analytics
 */
export default function FineTuningWidget({ onChatWithAgent }) {
  const [trainingData, setTrainingData] = useState({
    total_examples: 0,
    good_examples: 0,
    bad_examples: 0,
    pending_review: 0,
    last_training: null
  });

  const [modelPerformance, setModelPerformance] = useState({
    base_model_accuracy: 0.75,
    finetuned_model_accuracy: 0.89,
    improvement: 0.14
  });

  const [isLoading, setIsLoading] = useState(false);

  // Fetch training data stats
  useEffect(() => {
    fetchTrainingStats();
    // Refresh every 30 seconds
    const interval = setInterval(fetchTrainingStats, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchTrainingStats = async () => {
    try {
      const response = await fetch(API_CONFIG.endpoint('ai/feedback/stats'), {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token') || 'demo_token'}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        if (data.success && data.stats) {
          setTrainingData({
            total_examples: data.stats.total_feedback || 0,
            good_examples: data.stats.good_examples || 0,
            bad_examples: data.stats.thumbs_down || 0,
            pending_review: 0,
            last_training: null
          });
        }
      }
    } catch (error) {
      console.error('Error fetching training stats:', error);
    }
  };

  const handleExportData = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(API_CONFIG.endpoint('ai/feedback/export'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token') || 'demo_token'}`
        },
        body: JSON.stringify({
          min_score: 4,
          include_system_prompt: true
        })
      });
      
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `training_data_${new Date().toISOString()}.jsonl`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      }
    } catch (error) {
      console.error('Error exporting data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleStartTraining = () => {
    if (onChatWithAgent) {
      onChatWithAgent('אני רוצה להתחיל אימון של המודל עם הדוגמאות שאספנו');
    }
  };

  return (
    <Card className="border-purple-200 shadow-lg hover:shadow-xl transition-shadow">
      <CardHeader className="bg-gradient-to-r from-purple-50 to-pink-50 border-b">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
              <Brain className="w-5 h-5 text-white" />
            </div>
            <CardTitle className="text-lg">🧠 Fine-Tuning</CardTitle>
          </div>
          <Badge variant="outline" className="bg-purple-100 text-purple-700 border-purple-300">
            AI Training
          </Badge>
        </div>
      </CardHeader>

      <CardContent className="p-4 space-y-4">
        {/* Training Data Stats */}
        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-600 flex items-center gap-2">
              <Database className="w-4 h-4" />
              סה"כ דוגמאות
            </span>
            <span className="font-bold text-lg">{trainingData.total_examples}</span>
          </div>

          <div className="grid grid-cols-2 gap-2">
            <div className="bg-green-50 rounded-lg p-2 border border-green-200">
              <div className="flex items-center gap-1 text-green-700">
                <CheckCircle className="w-3 h-3" />
                <span className="text-xs">טובות</span>
              </div>
              <div className="text-lg font-bold text-green-800">
                {trainingData.good_examples}
              </div>
            </div>

            <div className="bg-red-50 rounded-lg p-2 border border-red-200">
              <div className="flex items-center gap-1 text-red-700">
                <XCircle className="w-3 h-3" />
                <span className="text-xs">רעות</span>
              </div>
              <div className="text-lg font-bold text-red-800">
                {trainingData.bad_examples}
              </div>
            </div>
          </div>

          <div className="bg-yellow-50 rounded-lg p-2 border border-yellow-200">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-1 text-yellow-700">
                <Clock className="w-3 h-3" />
                <span className="text-xs">ממתינות לסקירה</span>
              </div>
              <span className="text-sm font-bold text-yellow-800">
                {trainingData.pending_review}
              </span>
            </div>
          </div>
        </div>

        {/* Model Performance */}
        <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-3 border border-purple-200">
          <div className="flex items-center gap-2 mb-2">
            <TrendingUp className="w-4 h-4 text-purple-600" />
            <span className="text-sm font-semibold text-purple-900">ביצועי המודל</span>
          </div>

          <div className="space-y-2">
            <div className="flex items-center justify-between text-xs">
              <span className="text-gray-600">Base Model</span>
              <span className="font-bold">{(modelPerformance.base_model_accuracy * 100).toFixed(1)}%</span>
            </div>

            <div className="flex items-center justify-between text-xs">
              <span className="text-gray-600">Fine-tuned Model</span>
              <span className="font-bold text-green-600">
                {(modelPerformance.finetuned_model_accuracy * 100).toFixed(1)}%
              </span>
            </div>

            <div className="flex items-center justify-between text-xs pt-2 border-t border-purple-200">
              <span className="text-purple-700 font-semibold">שיפור</span>
              <span className="font-bold text-purple-700 flex items-center gap-1">
                <TrendingUp className="w-3 h-3" />
                +{(modelPerformance.improvement * 100).toFixed(1)}%
              </span>
            </div>
          </div>
        </div>

        {/* Last Training */}
        {trainingData.last_training && (
          <div className="text-xs text-gray-500 flex items-center gap-1">
            <Clock className="w-3 h-3" />
            <span>אימון אחרון: {new Date(trainingData.last_training).toLocaleDateString('he-IL')}</span>
          </div>
        )}

        {/* Actions */}
        <div className="grid grid-cols-2 gap-2 pt-2">
          <Button
            variant="outline"
            size="sm"
            onClick={handleExportData}
            disabled={isLoading || trainingData.total_examples === 0}
            className="flex items-center gap-2"
          >
            <Download className="w-4 h-4" />
            ייצוא
          </Button>

          <Button
            size="sm"
            onClick={handleStartTraining}
            disabled={trainingData.good_examples < 10}
            className="flex items-center gap-2 bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600"
          >
            <Zap className="w-4 h-4" />
            אמן מודל
          </Button>
        </div>

        {trainingData.good_examples < 10 && (
          <div className="text-xs text-amber-600 bg-amber-50 border border-amber-200 rounded p-2">
            💡 צריך לפחות 10 דוגמאות טובות כדי להתחיל אימון
          </div>
        )}
      </CardContent>
    </Card>
  );
}
