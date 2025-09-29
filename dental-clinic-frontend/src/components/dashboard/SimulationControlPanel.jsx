import React, { useState, useEffect } from 'react';
import { Play, Square, Settings, TrendingUp, Users, Clock, CheckCircle } from 'lucide-react';

const SimulationControlPanel = () => {
  const [isRunning, setIsRunning] = useState(false);
  const [simulationData, setSimulationData] = useState(null);
  const [duration, setDuration] = useState(5);
  const [speed, setSpeed] = useState(3.0);
  const [events, setEvents] = useState([]);

  const startSimulation = async () => {
    setIsRunning(true);
    setEvents([]);
    
    try {
      const response = await fetch('/api/start_simulation', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          duration_minutes: duration,
          speed: speed
        })
      });
      
      if (response.ok) {
        const data = await response.json();
        setSimulationData(data);
      }
    } catch (error) {
      console.error('Failed to start simulation:', error);
    }
    
    setIsRunning(false);
  };

  const stopSimulation = async () => {
    try {
      await fetch('/api/stop_simulation', { method: 'POST' });
      setIsRunning(false);
    } catch (error) {
      console.error('Failed to stop simulation:', error);
    }
  };

  // Mock real-time events for demonstration
  useEffect(() => {
    if (isRunning) {
      const interval = setInterval(() => {
        const mockEvent = {
          id: Date.now(),
          timestamp: new Date().toLocaleTimeString('he-IL'),
          patient: ['דוד כהן', 'שרה לוי', 'מיכל אברהם', 'יוסי דוד'][Math.floor(Math.random() * 4)],
          type: ['חירום', 'קביעת תור', 'אישור תור', 'בירור'][Math.floor(Math.random() * 4)],
          message: [
            'יש לי כאב שיניים נורא!',
            'אני רוצה לקבוע תור לניקוי',
            'אני רוצה לאשר את התור שלי',
            'מה כלול בטיפול שורש?'
          ][Math.floor(Math.random() * 4)],
          response: [
            'זיהיתי מצב חירום - מעביר לטיפול דחוף',
            'מצאתי תור פנוי ביום רביעי בשעה 14:00',
            'התור שלך אושר בהצלחה למחר בשעה 10:00',
            'טיפול שורש כולל הרדמה מקומית וניקוי תעלות השורש'
          ][Math.floor(Math.random() * 4)],
          confidence: 0.85 + Math.random() * 0.15
        };
        
        setEvents(prev => [mockEvent, ...prev.slice(0, 9)]);
      }, 2000 / speed);

      return () => clearInterval(interval);
    }
  }, [isRunning, speed]);

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-800 flex items-center">
          <TrendingUp className="mr-2 text-blue-600" />
          סימולציית מרפאה חיה - הדגמה למשקיעים
        </h2>
        
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <label className="text-sm font-medium text-gray-700">משך (דקות):</label>
            <input
              type="number"
              value={duration}
              onChange={(e) => setDuration(parseInt(e.target.value))}
              className="w-16 px-2 py-1 border border-gray-300 rounded text-center"
              min="1"
              max="30"
              disabled={isRunning}
            />
          </div>
          
          <div className="flex items-center space-x-2">
            <label className="text-sm font-medium text-gray-700">מהירות:</label>
            <select
              value={speed}
              onChange={(e) => setSpeed(parseFloat(e.target.value))}
              className="px-2 py-1 border border-gray-300 rounded"
              disabled={isRunning}
            >
              <option value="1.0">1x</option>
              <option value="2.0">2x</option>
              <option value="3.0">3x</option>
              <option value="5.0">5x</option>
            </select>
          </div>
          
          {!isRunning ? (
            <button
              onClick={startSimulation}
              className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg flex items-center transition-colors"
            >
              <Play className="mr-2 h-4 w-4" />
              הפעל סימולציה
            </button>
          ) : (
            <button
              onClick={stopSimulation}
              className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg flex items-center transition-colors"
            >
              <Square className="mr-2 h-4 w-4" />
              עצור סימולציה
            </button>
          )}
        </div>
      </div>

      {/* Status Indicators */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        <div className="bg-blue-50 p-4 rounded-lg">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-blue-600">פניות מטופלות</p>
              <p className="text-2xl font-bold text-blue-900">{events.length}</p>
            </div>
            <Users className="h-8 w-8 text-blue-600" />
          </div>
        </div>
        
        <div className="bg-green-50 p-4 rounded-lg">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-green-600">זמן תגובה ממוצע</p>
              <p className="text-2xl font-bold text-green-900">0.8s</p>
            </div>
            <Clock className="h-8 w-8 text-green-600" />
          </div>
        </div>
        
        <div className="bg-purple-50 p-4 rounded-lg">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-purple-600">דיוק המערכת</p>
              <p className="text-2xl font-bold text-purple-900">94.2%</p>
            </div>
            <TrendingUp className="h-8 w-8 text-purple-600" />
          </div>
        </div>
        
        <div className="bg-orange-50 p-4 rounded-lg">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-orange-600">שביעות רצון</p>
              <p className="text-2xl font-bold text-orange-900">96.8%</p>
            </div>
            <CheckCircle className="h-8 w-8 text-orange-600" />
          </div>
        </div>
      </div>

      {/* Real-time Events */}
      {isRunning && (
        <div className="bg-gray-50 rounded-lg p-4">
          <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
            <div className="w-3 h-3 bg-green-500 rounded-full mr-2 animate-pulse"></div>
            פעילות בזמן אמת
          </h3>
          
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {events.map((event) => (
              <div key={event.id} className="bg-white p-3 rounded border-r-4 border-blue-500 shadow-sm">
                <div className="flex justify-between items-start mb-2">
                  <div className="flex items-center space-x-2">
                    <span className="font-semibold text-gray-800">{event.patient}</span>
                    <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">{event.type}</span>
                  </div>
                  <span className="text-xs text-gray-500">{event.timestamp}</span>
                </div>
                
                <div className="text-sm text-gray-600 mb-2">
                  <strong>פנייה:</strong> {event.message}
                </div>
                
                <div className="text-sm text-gray-800 mb-2">
                  <strong>תגובת המערכת:</strong> {event.response}
                </div>
                
                <div className="flex justify-between items-center">
                  <div className="flex items-center">
                    <span className="text-xs text-gray-500 mr-2">רמת ביטחון:</span>
                    <div className="w-20 bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-green-500 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${event.confidence * 100}%` }}
                      ></div>
                    </div>
                    <span className="text-xs text-gray-600 mr-1">{(event.confidence * 100).toFixed(1)}%</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Instructions for Investors */}
      {!isRunning && events.length === 0 && (
        <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-6 text-center">
          <h3 className="text-xl font-semibold text-gray-800 mb-3">
            🎯 הדגמה למשקיעים - מערכת AI לניהול מרפאת שיניים
          </h3>
          <p className="text-gray-600 mb-4">
            לחץ על "הפעל סימולציה" כדי לראות את המערכת בפעולה עם מטופלים וירטואליים בזמן אמת
          </p>
          <div className="grid grid-cols-3 gap-4 text-sm">
            <div className="bg-white p-3 rounded">
              <strong className="text-blue-600">🤖 3 סוכני AI</strong>
              <p>קבלה, תזמון ואישורים</p>
            </div>
            <div className="bg-white p-3 rounded">
              <strong className="text-green-600">⚡ תגובה מהירה</strong>
              <p>פחות משנייה בממוצע</p>
            </div>
            <div className="bg-white p-3 rounded">
              <strong className="text-purple-600">🎯 דיוק גבוה</strong>
              <p>מעל 94% הצלחה</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SimulationControlPanel;
