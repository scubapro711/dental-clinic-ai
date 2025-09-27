import React from 'react';
import ActivityFeed from './ActivityFeed';

const ActivityFeedDemo = () => {
  const mockActivities = [
    {
      id: '1',
      title: 'תור חדש נקבע',
      description: 'תור לחולה יוסי כהן נקבע ליום ראשון בשעה 10:00',
      type: 'appointment',
      status: 'completed',
      agent: 'dental_agent_1',
      timestamp: new Date(Date.now() - 5 * 60 * 1000).toISOString(), // 5 minutes ago
      duration: '2.3s'
    },
    {
      id: '2',
      title: 'עדכון פרטי חולה',
      description: 'פרטי החולה שרה לוי עודכנו במערכת - מספר טלפון חדש',
      type: 'patient',
      status: 'in_progress',
      agent: 'dental_agent_2',
      timestamp: new Date(Date.now() - 3 * 60 * 1000).toISOString(), // 3 minutes ago
      duration: '1.5s'
    },
    {
      id: '3',
      title: 'שגיאה במערכת',
      description: 'שגיאה זמנית בחיבור למסד הנתונים - נפתרה אוטומטית',
      type: 'error',
      status: 'failed',
      agent: 'dental_agent_1',
      timestamp: new Date(Date.now() - 2 * 60 * 1000).toISOString(), // 2 minutes ago
      duration: '0.1s'
    },
    {
      id: '4',
      title: 'תזכורת נשלחה',
      description: 'תזכורת SMS נשלחה לחולה מיכל דוד לתור מחר',
      type: 'system',
      status: 'completed',
      agent: 'dental_agent_1',
      timestamp: new Date(Date.now() - 1 * 60 * 1000).toISOString(), // 1 minute ago
      duration: '0.8s'
    },
    {
      id: '5',
      title: 'ביטול תור',
      description: 'תור של חולה אבי מזרחי בוטל לבקשתו',
      type: 'appointment',
      status: 'completed',
      agent: 'dental_agent_2',
      timestamp: new Date(Date.now() - 30 * 1000).toISOString(), // 30 seconds ago
      duration: '1.2s'
    },
    {
      id: '6',
      title: 'חולה חדש נרשם',
      description: 'חולה חדש - רונית אברהם נרשמה למערכת',
      type: 'patient',
      status: 'completed',
      agent: 'dental_agent_1',
      timestamp: new Date().toISOString(), // now
      duration: '3.1s'
    }
  ];

  const handleActivityClick = (activity) => {
    console.log('Activity clicked:', activity);
    alert(`נלחץ על פעילות: ${activity.title}`);
  };

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-6xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">
            הדגמת רכיב ActivityFeed
          </h1>
          <p className="text-gray-600">
            רכיב להצגת פיד פעילות הסוכן בזמן אמת עם יכולות סינון וחיפוש
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* ActivityFeed without WebSocket */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-semibold mb-4">פיד פעילות רגיל</h2>
            <div className="h-96">
              <ActivityFeed 
                activities={mockActivities}
                onActivityClick={handleActivityClick}
                maxActivities={100}
              />
            </div>
          </div>

          {/* ActivityFeed with WebSocket simulation */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-semibold mb-4">פיד פעילות עם WebSocket</h2>
            <div className="h-96">
              <ActivityFeed 
                activities={mockActivities}
                onActivityClick={handleActivityClick}
                websocketUrl="ws://localhost:8000/ws"
                maxActivities={50}
              />
            </div>
          </div>
        </div>

        <div className="mt-8 bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-xl font-semibold mb-4">תכונות הרכיב</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 className="font-medium text-gray-900 mb-2">תכונות ויזואליות</h3>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• הצגת פעילויות עם אייקונים מותאמים</li>
                <li>• תגיות סטטוס צבעוניות</li>
                <li>• אנימציות חלקות ומעברים</li>
                <li>• עיצוב רספונסיבי</li>
                <li>• אינדיקטור חיבור WebSocket</li>
              </ul>
            </div>
            <div>
              <h3 className="font-medium text-gray-900 mb-2">תכונות אינטראקטיביות</h3>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• חיפוש בפעילויות</li>
                <li>• סינון לפי סוכן</li>
                <li>• סינון לפי סוג פעילות</li>
                <li>• לחיצה על פעילות לפרטים</li>
                <li>• עדכונים בזמן אמת</li>
              </ul>
            </div>
          </div>
        </div>

        <div className="mt-8 bg-blue-50 rounded-lg p-6">
          <h2 className="text-xl font-semibold text-blue-900 mb-4">הוראות בדיקה</h2>
          <div className="text-blue-800 space-y-2">
            <p>1. <strong>חיפוש:</strong> נסה לחפש "תור" או "חולה" בשדה החיפוש</p>
            <p>2. <strong>סינון:</strong> בחר סוכן או סוג פעילות מהתפריטים הנפתחים</p>
            <p>3. <strong>לחיצה:</strong> לחץ על כל פעילות כדי לראות הודעת התראה</p>
            <p>4. <strong>WebSocket:</strong> הרכיב הימני מדמה חיבור WebSocket</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ActivityFeedDemo;
