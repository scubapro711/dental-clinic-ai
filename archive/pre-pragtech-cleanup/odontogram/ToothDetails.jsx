import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  X, Plus, Edit2, Trash2, Calendar, User, 
  AlertCircle, CheckCircle, Clock 
} from 'lucide-react';
import { cn } from '@/lib/utils';

/**
 * ToothDetails Component
 * 
 * Displays detailed information about a selected tooth
 * Shows conditions, treatments, and allows editing
 */
export default function ToothDetails({ tooth, onClose, onUpdate, readonly = false }) {
  const [editMode, setEditMode] = useState(false);
  const [editedTooth, setEditedTooth] = useState(tooth);

  const statusOptions = [
    { code: 'healthy', label: 'בריא', color: 'green' },
    { code: 'watch', label: 'מעקב', color: 'yellow' },
    { code: 'needs_treatment', label: 'דרוש טיפול', color: 'orange' },
    { code: 'urgent', label: 'דחוף', color: 'red' },
    { code: 'missing', label: 'חסר', color: 'gray' },
    { code: 'treated', label: 'טופל', color: 'blue' },
  ];

  const conditionTypes = [
    { value: 'cavity', label: 'עששת' },
    { value: 'fracture', label: 'שבר' },
    { value: 'wear', label: 'שחיקה' },
    { value: 'sensitivity', label: 'רגישות' },
    { value: 'other', label: 'אחר' },
  ];

  const treatmentTypes = [
    { value: 'filling', label: 'סתימה' },
    { value: 'crown', label: 'כתר' },
    { value: 'root_canal', label: 'טיפול שורש' },
    { value: 'extraction', label: 'עקירה' },
    { value: 'cleaning', label: 'ניקוי' },
    { value: 'other', label: 'אחר' },
  ];

  const handleStatusChange = (newStatus) => {
    const updatedTooth = {
      ...editedTooth,
      status: {
        ...statusOptions.find(s => s.code === newStatus),
        updatedAt: new Date().toISOString(),
        updatedBy: 'current_user' // TODO: Get from auth
      }
    };
    setEditedTooth(updatedTooth);
  };

  const handleSave = () => {
    onUpdate(editedTooth);
    setEditMode(false);
  };

  const handleCancel = () => {
    setEditedTooth(tooth);
    setEditMode(false);
  };

  const handleAddCondition = () => {
    const newCondition = {
      id: `cond_${Date.now()}`,
      type: 'cavity',
      severity: 'mild',
      description: '',
      diagnosedAt: new Date().toISOString(),
      diagnosedBy: 'current_user'
    };
    setEditedTooth({
      ...editedTooth,
      conditions: [...(editedTooth.conditions || []), newCondition]
    });
    setEditMode(true);
  };

  const handleAddTreatment = () => {
    const newTreatment = {
      id: `treat_${Date.now()}`,
      type: 'filling',
      status: 'planned',
      date: new Date().toISOString().split('T')[0],
      dentist: 'current_user',
      cost: 0,
      notes: ''
    };
    setEditedTooth({
      ...editedTooth,
      treatments: [...(editedTooth.treatments || []), newTreatment]
    });
    setEditMode(true);
  };

  const handleRemoveCondition = (conditionId) => {
    setEditedTooth({
      ...editedTooth,
      conditions: editedTooth.conditions.filter(c => c.id !== conditionId)
    });
  };

  const handleRemoveTreatment = (treatmentId) => {
    setEditedTooth({
      ...editedTooth,
      treatments: editedTooth.treatments.filter(t => t.id !== treatmentId)
    });
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('he-IL');
  };

  const getTreatmentStatusBadge = (status) => {
    const variants = {
      planned: { variant: 'secondary', label: 'מתוכנן', icon: Clock },
      in_progress: { variant: 'default', label: 'בביצוע', icon: AlertCircle },
      completed: { variant: 'default', label: 'הושלם', icon: CheckCircle },
      cancelled: { variant: 'destructive', label: 'בוטל', icon: X },
    };
    const config = variants[status] || variants.planned;
    const Icon = config.icon;
    
    return (
      <Badge variant={config.variant} className="flex items-center gap-1">
        <Icon className="w-3 h-3" />
        {config.label}
      </Badge>
    );
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-3xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="p-6 border-b border-gray-200 flex justify-between items-center">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">
              שן מספר {tooth.id}
            </h2>
            <p className="text-sm text-gray-600 mt-1">
              {tooth.type === 'incisor' && 'חותכת'}
              {tooth.type === 'canine' && 'ניב'}
              {tooth.type === 'premolar' && 'טוחנת קדמית'}
              {tooth.type === 'molar' && 'טוחנת'}
              {' | '}
              רביע {tooth.quadrant}
            </p>
          </div>
          <Button variant="ghost" size="sm" onClick={onClose}>
            <X className="w-5 h-5" />
          </Button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {/* Status Section */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-3">סטטוס</h3>
            {editMode ? (
              <div className="flex flex-wrap gap-2">
                {statusOptions.map(status => (
                  <button
                    key={status.code}
                    onClick={() => handleStatusChange(status.code)}
                    className={cn(
                      "px-4 py-2 rounded-lg border-2 transition-all",
                      editedTooth.status.code === status.code
                        ? `border-${status.color}-500 bg-${status.color}-50`
                        : "border-gray-200 hover:border-gray-300"
                    )}
                  >
                    {status.label}
                  </button>
                ))}
              </div>
            ) : (
              <div className={cn(
                "inline-flex items-center gap-2 px-4 py-2 rounded-lg border-2",
                `border-${tooth.status.color}-500 bg-${tooth.status.color}-50`
              )}>
                <span className="font-semibold">{tooth.status.label}</span>
                <span className="text-xs text-gray-600">
                  ({formatDate(tooth.status.updatedAt)})
                </span>
              </div>
            )}
          </div>

          {/* Conditions Section */}
          <div>
            <div className="flex justify-between items-center mb-3">
              <h3 className="text-lg font-semibold text-gray-900">
                מצבים ({editedTooth.conditions?.length || 0})
              </h3>
              {!readonly && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleAddCondition}
                >
                  <Plus className="w-4 h-4 mr-2" />
                  הוסף מצב
                </Button>
              )}
            </div>
            
            {editedTooth.conditions?.length > 0 ? (
              <div className="space-y-3">
                {editedTooth.conditions.map(condition => (
                  <div
                    key={condition.id}
                    className="p-4 bg-gray-50 rounded-lg border border-gray-200"
                  >
                    <div className="flex justify-between items-start mb-2">
                      <div>
                        <span className="font-semibold">
                          {conditionTypes.find(t => t.value === condition.type)?.label}
                        </span>
                        <Badge variant="secondary" className="mr-2">
                          {condition.severity === 'mild' && 'קל'}
                          {condition.severity === 'moderate' && 'בינוני'}
                          {condition.severity === 'severe' && 'חמור'}
                        </Badge>
                      </div>
                      {editMode && !readonly && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleRemoveCondition(condition.id)}
                        >
                          <Trash2 className="w-4 h-4 text-red-500" />
                        </Button>
                      )}
                    </div>
                    {condition.description && (
                      <p className="text-sm text-gray-600 mb-2">{condition.description}</p>
                    )}
                    <div className="flex items-center gap-4 text-xs text-gray-500">
                      <span className="flex items-center gap-1">
                        <Calendar className="w-3 h-3" />
                        {formatDate(condition.diagnosedAt)}
                      </span>
                      <span className="flex items-center gap-1">
                        <User className="w-3 h-3" />
                        {condition.diagnosedBy}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-gray-500">אין מצבים רשומים</p>
            )}
          </div>

          {/* Treatments Section */}
          <div>
            <div className="flex justify-between items-center mb-3">
              <h3 className="text-lg font-semibold text-gray-900">
                טיפולים ({editedTooth.treatments?.length || 0})
              </h3>
              {!readonly && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleAddTreatment}
                >
                  <Plus className="w-4 h-4 mr-2" />
                  הוסף טיפול
                </Button>
              )}
            </div>
            
            {editedTooth.treatments?.length > 0 ? (
              <div className="space-y-3">
                {editedTooth.treatments.map(treatment => (
                  <div
                    key={treatment.id}
                    className="p-4 bg-gray-50 rounded-lg border border-gray-200"
                  >
                    <div className="flex justify-between items-start mb-2">
                      <div>
                        <span className="font-semibold">
                          {treatmentTypes.find(t => t.value === treatment.type)?.label}
                        </span>
                        <span className="mr-2">
                          {getTreatmentStatusBadge(treatment.status)}
                        </span>
                      </div>
                      {editMode && !readonly && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleRemoveTreatment(treatment.id)}
                        >
                          <Trash2 className="w-4 h-4 text-red-500" />
                        </Button>
                      )}
                    </div>
                    {treatment.notes && (
                      <p className="text-sm text-gray-600 mb-2">{treatment.notes}</p>
                    )}
                    <div className="flex items-center gap-4 text-xs text-gray-500">
                      <span className="flex items-center gap-1">
                        <Calendar className="w-3 h-3" />
                        {formatDate(treatment.date)}
                      </span>
                      <span className="flex items-center gap-1">
                        <User className="w-3 h-3" />
                        {treatment.dentist}
                      </span>
                      {treatment.cost > 0 && (
                        <span className="font-semibold">
                          ₪{treatment.cost.toLocaleString()}
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-gray-500">אין טיפולים רשומים</p>
            )}
          </div>

          {/* Notes Section */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-3">הערות</h3>
            {editMode ? (
              <textarea
                className="w-full p-3 border border-gray-300 rounded-lg resize-none"
                rows="3"
                value={editedTooth.notes || ''}
                onChange={(e) => setEditedTooth({
                  ...editedTooth,
                  notes: e.target.value
                })}
                placeholder="הוסף הערות..."
              />
            ) : (
              <p className="text-sm text-gray-600">
                {tooth.notes || 'אין הערות'}
              </p>
            )}
          </div>
        </div>

        {/* Footer Actions */}
        {!readonly && (
          <div className="p-6 border-t border-gray-200 flex justify-end gap-2">
            {editMode ? (
              <>
                <Button variant="outline" onClick={handleCancel}>
                  ביטול
                </Button>
                <Button onClick={handleSave}>
                  שמור שינויים
                </Button>
              </>
            ) : (
              <Button onClick={() => setEditMode(true)}>
                <Edit2 className="w-4 h-4 mr-2" />
                ערוך
              </Button>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
