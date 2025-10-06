import React, { useState, useEffect } from 'react';
import ToothChart from './ToothChart';
import ToothDetails from './ToothDetails';
import { Button } from '@/components/ui/button';
import { AlertCircle, Save, RefreshCw, Printer } from 'lucide-react';

/**
 * Odontogram Component
 * 
 * Main container for the dental chart
 * Manages state for all 32 teeth and handles interactions
 */
export default function Odontogram({ patientId, readonly = false }) {
  const [odontogram, setOdontogram] = useState(null);
  const [selectedTeeth, setSelectedTeeth] = useState([]);
  const [detailsOpen, setDetailsOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState(null);
  const [hasChanges, setHasChanges] = useState(false);

  // Initialize with 32 teeth
  const initializeTeeth = () => {
    const teeth = [];
    
    // Generate all 32 teeth with FDI notation
    for (let quadrant = 1; quadrant <= 4; quadrant++) {
      for (let position = 1; position <= 8; position++) {
        const toothId = quadrant * 10 + position;
        teeth.push({
          id: toothId,
          quadrant,
          position,
          type: getToothType(position),
          status: {
            code: 'healthy',
            label: 'בריא',
            color: 'green',
            updatedAt: new Date().toISOString(),
            updatedBy: 'system'
          },
          conditions: [],
          treatments: [],
          notes: ''
        });
      }
    }
    
    return teeth;
  };

  const getToothType = (position) => {
    if (position <= 2) return 'incisor';
    if (position === 3) return 'canine';
    if (position <= 5) return 'premolar';
    return 'molar';
  };

  // Load odontogram from API
  useEffect(() => {
    if (patientId) {
      loadOdontogram();
    } else {
      // Demo mode - initialize with default teeth
      setOdontogram({
        id: 'demo',
        patientId: 'demo',
        teeth: initializeTeeth(),
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      });
      setIsLoading(false);
    }
  }, [patientId]);

  const loadOdontogram = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch(
        `http://localhost:8000/api/v1/patients/${patientId}/odontogram`,
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token') || 'demo_token'}`
          }
        }
      );
      
      if (response.ok) {
        const data = await response.json();
        setOdontogram(data);
      } else if (response.status === 404) {
        // No odontogram exists, create new one
        const newOdontogram = {
          patientId,
          teeth: initializeTeeth(),
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString()
        };
        setOdontogram(newOdontogram);
      } else {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
    } catch (err) {
      console.error('Error loading odontogram:', err);
      setError(err.message);
      // Fallback to demo data
      setOdontogram({
        id: 'demo',
        patientId: patientId || 'demo',
        teeth: initializeTeeth(),
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      });
    } finally {
      setIsLoading(false);
    }
  };

  const saveOdontogram = async () => {
    if (!odontogram || readonly) return;
    
    setIsSaving(true);
    setError(null);
    
    try {
      const url = odontogram.id && odontogram.id !== 'demo'
        ? `http://localhost:8000/api/v1/patients/${patientId}/odontogram/${odontogram.id}`
        : `http://localhost:8000/api/v1/patients/${patientId}/odontogram`;
      
      const method = odontogram.id && odontogram.id !== 'demo' ? 'PUT' : 'POST';
      
      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token') || 'demo_token'}`
        },
        body: JSON.stringify({
          ...odontogram,
          updatedAt: new Date().toISOString()
        })
      });
      
      if (response.ok) {
        const saved = await response.json();
        setOdontogram(saved);
        setHasChanges(false);
        alert('מפת השיניים נשמרה בהצלחה!');
      } else {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
    } catch (err) {
      console.error('Error saving odontogram:', err);
      setError('שגיאה בשמירת מפת השיניים');
      alert('שגיאה בשמירה. אנא נסה שוב.');
    } finally {
      setIsSaving(false);
    }
  };

  const handleToothSelect = (tooth, multiSelect) => {
    if (readonly) return;
    
    setSelectedTeeth(prev => {
      if (multiSelect) {
        // Multi-select with Ctrl/Cmd
        const isAlreadySelected = prev.some(t => t.id === tooth.id);
        if (isAlreadySelected) {
          return prev.filter(t => t.id !== tooth.id);
        } else {
          return [...prev, tooth];
        }
      } else {
        // Single select
        const isAlreadySelected = prev.length === 1 && prev[0].id === tooth.id;
        return isAlreadySelected ? [] : [tooth];
      }
    });
  };

  const handleToothDoubleClick = (tooth) => {
    setSelectedTeeth([tooth]);
    setDetailsOpen(true);
  };

  const handleToothUpdate = (updatedTooth) => {
    setOdontogram(prev => ({
      ...prev,
      teeth: prev.teeth.map(t => 
        t.id === updatedTooth.id ? updatedTooth : t
      ),
      updatedAt: new Date().toISOString()
    }));
    setHasChanges(true);
    
    // Update selected teeth
    setSelectedTeeth(prev => 
      prev.map(t => t.id === updatedTooth.id ? updatedTooth : t)
    );
  };

  const handlePrint = () => {
    window.print();
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <RefreshCw className="w-12 h-12 animate-spin text-blue-500 mx-auto mb-4" />
          <p className="text-gray-600">טוען מפת שיניים...</p>
        </div>
      </div>
    );
  }

  if (error && !odontogram) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <p className="text-red-600 mb-4">{error}</p>
          <Button onClick={loadOdontogram}>נסה שוב</Button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header Actions */}
      {!readonly && (
        <div className="flex justify-between items-center">
          <div>
            {hasChanges && (
              <span className="text-sm text-orange-600 font-semibold">
                ⚠️ יש שינויים שלא נשמרו
              </span>
            )}
          </div>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={handlePrint}
            >
              <Printer className="w-4 h-4 mr-2" />
              הדפס
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={loadOdontogram}
              disabled={isLoading}
            >
              <RefreshCw className="w-4 h-4 mr-2" />
              רענן
            </Button>
            <Button
              size="sm"
              onClick={saveOdontogram}
              disabled={isSaving || !hasChanges}
            >
              <Save className="w-4 h-4 mr-2" />
              {isSaving ? 'שומר...' : 'שמור'}
            </Button>
          </div>
        </div>
      )}

      {/* Tooth Chart */}
      <ToothChart
        teeth={odontogram?.teeth || []}
        selectedTeeth={selectedTeeth}
        onToothSelect={handleToothSelect}
        onToothDoubleClick={handleToothDoubleClick}
      />

      {/* Tooth Details Panel */}
      {detailsOpen && selectedTeeth.length === 1 && (
        <ToothDetails
          tooth={selectedTeeth[0]}
          onClose={() => setDetailsOpen(false)}
          onUpdate={handleToothUpdate}
          readonly={readonly}
        />
      )}

      {/* Error Message */}
      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex items-center gap-2 text-red-800">
            <AlertCircle className="w-5 h-5" />
            <span>{error}</span>
          </div>
        </div>
      )}
    </div>
  );
}
