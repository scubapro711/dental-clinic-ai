/**
 * Tooth Chart Component
 * 
 * Interactive dental chart showing all 32 adult teeth with:
 * - FDI/ISO 3950 notation (international standard)
 * - Universal numbering system (US standard)
 * - Visual status indicators (healthy, cavity, filling, crown, missing, etc.)
 * - Click to view tooth details
 * - Treatment history per tooth
 * - Sarah AI proactive analysis
 * 
 * Tooth Numbering:
 * - FDI: 11-18 (upper right), 21-28 (upper left), 31-38 (lower left), 41-48 (lower right)
 * - Universal: 1-16 (upper), 17-32 (lower), clockwise from upper right
 */

import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardContent } from '../ui/card';
import { Alert, AlertDescription } from '../ui/alert';
import { Badge } from '../ui/badge';
import { Button } from '../ui/button';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '../ui/tooltip';

// Tooth status types
const ToothStatus = {
  HEALTHY: 'healthy',
  CAVITY: 'cavity',
  FILLING: 'filling',
  CROWN: 'crown',
  ROOT_CANAL: 'root_canal',
  EXTRACTION: 'extraction',
  MISSING: 'missing',
  IMPLANT: 'implant',
  BRIDGE: 'bridge',
  NEEDS_ATTENTION: 'needs_attention',
};

// Status colors
const STATUS_COLORS = {
  [ToothStatus.HEALTHY]: 'bg-green-100 border-green-300 hover:bg-green-200',
  [ToothStatus.CAVITY]: 'bg-red-100 border-red-300 hover:bg-red-200',
  [ToothStatus.FILLING]: 'bg-blue-100 border-blue-300 hover:bg-blue-200',
  [ToothStatus.CROWN]: 'bg-purple-100 border-purple-300 hover:bg-purple-200',
  [ToothStatus.ROOT_CANAL]: 'bg-orange-100 border-orange-300 hover:bg-orange-200',
  [ToothStatus.EXTRACTION]: 'bg-gray-100 border-gray-300 hover:bg-gray-200',
  [ToothStatus.MISSING]: 'bg-gray-50 border-gray-200',
  [ToothStatus.IMPLANT]: 'bg-indigo-100 border-indigo-300 hover:bg-indigo-200',
  [ToothStatus.BRIDGE]: 'bg-teal-100 border-teal-300 hover:bg-teal-200',
  [ToothStatus.NEEDS_ATTENTION]: 'bg-yellow-100 border-yellow-300 hover:bg-yellow-200 animate-pulse',
};

// Tooth names (FDI notation)
const TOOTH_NAMES = {
  // Upper right (quadrant 1)
  11: 'Central Incisor', 12: 'Lateral Incisor', 13: 'Canine', 14: 'First Premolar',
  15: 'Second Premolar', 16: 'First Molar', 17: 'Second Molar', 18: 'Third Molar',
  // Upper left (quadrant 2)
  21: 'Central Incisor', 22: 'Lateral Incisor', 23: 'Canine', 24: 'First Premolar',
  25: 'Second Premolar', 26: 'First Molar', 27: 'Second Molar', 28: 'Third Molar',
  // Lower left (quadrant 3)
  31: 'Central Incisor', 32: 'Lateral Incisor', 33: 'Canine', 34: 'First Premolar',
  35: 'Second Premolar', 36: 'First Molar', 37: 'Second Molar', 38: 'Third Molar',
  // Lower right (quadrant 4)
  41: 'Central Incisor', 42: 'Lateral Incisor', 43: 'Canine', 44: 'First Premolar',
  45: 'Second Premolar', 46: 'First Molar', 47: 'Second Molar', 48: 'Third Molar',
};

// FDI to Universal conversion
const FDI_TO_UNIVERSAL = {
  18: 1, 17: 2, 16: 3, 15: 4, 14: 5, 13: 6, 12: 7, 11: 8,
  21: 9, 22: 10, 23: 11, 24: 12, 25: 13, 26: 14, 27: 15, 28: 16,
  38: 17, 37: 18, 36: 19, 35: 20, 34: 21, 33: 22, 32: 23, 31: 24,
  48: 25, 47: 26, 46: 27, 45: 28, 44: 29, 43: 30, 42: 31, 41: 32,
};

const ToothChart = ({ patientId, onToothClick, showSarahAnalysis = true }) => {
  const [toothData, setToothData] = useState({});
  const [selectedTooth, setSelectedTooth] = useState(null);
  const [loading, setLoading] = useState(true);
  const [sarahSuggestions, setSarahSuggestions] = useState([]);
  const [notationSystem, setNotationSystem] = useState('fdi'); // 'fdi' or 'universal'

  // Fetch tooth data from backend
  useEffect(() => {
    if (patientId) {
      fetchToothData();
      if (showSarahAnalysis) {
        fetchSarahAnalysis();
      }
    }
  }, [patientId]);

  const fetchToothData = async () => {
    try {
      setLoading(true);
      // TODO: Replace with actual API call
      // const response = await fetch(`/api/v1/patients/${patientId}/tooth-chart`);
      // const data = await response.json();
      
      // Mock data for now
      const mockData = {
        16: { status: ToothStatus.FILLING, lastTreatment: '2024-08-15', notes: 'Composite filling' },
        26: { status: ToothStatus.CROWN, lastTreatment: '2024-06-20', notes: 'Porcelain crown' },
        36: { status: ToothStatus.NEEDS_ATTENTION, lastTreatment: '2024-09-01', notes: 'Follow-up needed' },
        46: { status: ToothStatus.ROOT_CANAL, lastTreatment: '2024-07-10', notes: 'Root canal completed' },
        18: { status: ToothStatus.EXTRACTION, lastTreatment: '2023-12-05', notes: 'Wisdom tooth extracted' },
        28: { status: ToothStatus.MISSING, lastTreatment: null, notes: 'Congenitally missing' },
      };
      
      setToothData(mockData);
    } catch (error) {
      console.error('Error fetching tooth data:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchSarahAnalysis = async () => {
    try {
      // TODO: Replace with actual API call to Sarah agent
      // const response = await fetch(`/api/v1/decision-queue?agent_name=sarah&patient_id=${patientId}`);
      // const suggestions = await response.json();
      
      // Mock Sarah suggestions
      const mockSuggestions = [
        {
          id: '1',
          title: 'Tooth #36 Follow-up Required',
          message: 'Patient should return for follow-up examination of tooth #36 within 2 weeks.',
          priority: 'high',
          confidence: 87,
        },
        {
          id: '2',
          title: 'Routine Cleaning Overdue',
          message: 'Patient is 2 months overdue for routine cleaning. Schedule appointment.',
          priority: 'medium',
          confidence: 92,
        },
      ];
      
      setSarahSuggestions(mockSuggestions);
    } catch (error) {
      console.error('Error fetching Sarah analysis:', error);
    }
  };

  const handleToothClick = (toothNumber) => {
    setSelectedTooth(toothNumber);
    if (onToothClick) {
      onToothClick(toothNumber, toothData[toothNumber]);
    }
  };

  const getToothStatus = (toothNumber) => {
    return toothData[toothNumber]?.status || ToothStatus.HEALTHY;
  };

  const getToothColor = (toothNumber) => {
    const status = getToothStatus(toothNumber);
    return STATUS_COLORS[status];
  };

  const renderTooth = (toothNumber) => {
    const status = getToothStatus(toothNumber);
    const data = toothData[toothNumber];
    const universalNumber = FDI_TO_UNIVERSAL[toothNumber];
    const displayNumber = notationSystem === 'fdi' ? toothNumber : universalNumber;

    return (
      <TooltipProvider key={toothNumber}>
        <Tooltip>
          <TooltipTrigger asChild>
            <button
              onClick={() => handleToothClick(toothNumber)}
              className={`
                relative w-12 h-16 rounded-lg border-2 transition-all
                ${getToothColor(toothNumber)}
                ${selectedTooth === toothNumber ? 'ring-2 ring-blue-500 scale-110' : ''}
                ${status === ToothStatus.MISSING ? 'opacity-30 cursor-not-allowed' : 'cursor-pointer'}
              `}
              disabled={status === ToothStatus.MISSING}
            >
              <div className="text-xs font-bold">{displayNumber}</div>
              {data && (
                <div className="absolute -top-1 -right-1 w-3 h-3 bg-blue-500 rounded-full" />
              )}
            </button>
          </TooltipTrigger>
          <TooltipContent>
            <div className="text-sm">
              <div className="font-bold">
                Tooth #{toothNumber} ({TOOTH_NAMES[toothNumber]})
              </div>
              <div>Universal: #{universalNumber}</div>
              <div className="mt-1">Status: {status.replace('_', ' ')}</div>
              {data?.lastTreatment && (
                <div>Last treatment: {data.lastTreatment}</div>
              )}
              {data?.notes && (
                <div className="text-gray-600">{data.notes}</div>
              )}
            </div>
          </TooltipContent>
        </Tooltip>
      </TooltipProvider>
    );
  };

  const renderQuadrant = (quadrant, teeth) => {
    return (
      <div className="flex gap-1">
        {teeth.map(tooth => renderTooth(tooth))}
      </div>
    );
  };

  if (loading) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="text-center text-gray-500">Loading tooth chart...</div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <Card>
        <CardHeader>
          <div className="flex justify-between items-center">
            <h3 className="text-lg font-bold">Tooth Chart</h3>
            <div className="flex gap-2">
              <Button
                variant={notationSystem === 'fdi' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setNotationSystem('fdi')}
              >
                FDI/ISO
              </Button>
              <Button
                variant={notationSystem === 'universal' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setNotationSystem('universal')}
              >
                Universal
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {/* Upper teeth */}
          <div className="mb-8">
            <div className="text-xs text-gray-500 mb-2 text-center">Upper Jaw</div>
            <div className="flex justify-center gap-8">
              {/* Upper right (quadrant 1) */}
              <div>
                <div className="text-xs text-gray-500 mb-1">Right</div>
                {renderQuadrant(1, [18, 17, 16, 15, 14, 13, 12, 11])}
              </div>
              {/* Upper left (quadrant 2) */}
              <div>
                <div className="text-xs text-gray-500 mb-1">Left</div>
                {renderQuadrant(2, [21, 22, 23, 24, 25, 26, 27, 28])}
              </div>
            </div>
          </div>

          {/* Lower teeth */}
          <div>
            <div className="text-xs text-gray-500 mb-2 text-center">Lower Jaw</div>
            <div className="flex justify-center gap-8">
              {/* Lower right (quadrant 4) */}
              <div>
                <div className="text-xs text-gray-500 mb-1">Right</div>
                {renderQuadrant(4, [48, 47, 46, 45, 44, 43, 42, 41])}
              </div>
              {/* Lower left (quadrant 3) */}
              <div>
                <div className="text-xs text-gray-500 mb-1">Left</div>
                {renderQuadrant(3, [31, 32, 33, 34, 35, 36, 37, 38])}
              </div>
            </div>
          </div>

          {/* Legend */}
          <div className="mt-6 pt-4 border-t">
            <div className="text-xs font-semibold mb-2">Legend:</div>
            <div className="grid grid-cols-2 md:grid-cols-5 gap-2 text-xs">
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 rounded bg-green-100 border border-green-300" />
                <span>Healthy</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 rounded bg-red-100 border border-red-300" />
                <span>Cavity</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 rounded bg-blue-100 border border-blue-300" />
                <span>Filling</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 rounded bg-purple-100 border border-purple-300" />
                <span>Crown</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 rounded bg-orange-100 border border-orange-300" />
                <span>Root Canal</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 rounded bg-gray-100 border border-gray-300" />
                <span>Extraction</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 rounded bg-gray-50 border border-gray-200" />
                <span>Missing</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 rounded bg-indigo-100 border border-indigo-300" />
                <span>Implant</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 rounded bg-teal-100 border border-teal-300" />
                <span>Bridge</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 rounded bg-yellow-100 border border-yellow-300 animate-pulse" />
                <span>Needs Attention</span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Sarah AI Analysis */}
      {showSarahAnalysis && sarahSuggestions.length > 0 && (
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <span className="text-lg font-bold">🤖 Sarah's Analysis</span>
              <Badge variant="secondary">AI-Powered</Badge>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {sarahSuggestions.map((suggestion) => (
                <Alert key={suggestion.id} className={
                  suggestion.priority === 'high' ? 'border-red-300 bg-red-50' :
                  suggestion.priority === 'medium' ? 'border-yellow-300 bg-yellow-50' :
                  'border-blue-300 bg-blue-50'
                }>
                  <AlertDescription>
                    <div className="flex justify-between items-start">
                      <div>
                        <div className="font-semibold">{suggestion.title}</div>
                        <div className="text-sm text-gray-600 mt-1">{suggestion.message}</div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge variant="outline">{suggestion.confidence}% confident</Badge>
                        <Button size="sm" variant="outline">Review</Button>
                      </div>
                    </div>
                  </AlertDescription>
                </Alert>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default ToothChart;

