import React from 'react';

const RealTimeAlerts = () => {
  // Placeholder for real-time alert logic
  const alerts = [
    { id: 1, message: 'Emergency detected in conversation #123', type: 'error' },
    { id: 2, message: 'High patient volume detected', type: 'warning' },
    { id: 3, message: 'Agent #2 is offline', type: 'info' },
  ];

  return (
    <div className="bg-white p-4 rounded-lg shadow">
      <h3 className="text-lg font-semibold mb-2">Real-time Alerts</h3>
      <ul>
        {alerts.map(alert => (
          <li key={alert.id} className={`p-2 rounded mb-2 ${
            alert.type === 'error' ? 'bg-red-100 text-red-800' :
            alert.type === 'warning' ? 'bg-yellow-100 text-yellow-800' :
            'bg-blue-100 text-blue-800'
          }`}>
            {alert.message}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default RealTimeAlerts;

