import React, { useState } from 'react';
import { Save } from 'lucide-react';

const AddTreatmentModal = ({ isOpen, onClose, onAdd, doctorName }) => {
  if (!isOpen) return null;
  
  const [formData, setFormData] = useState({
    type: 'סתימה',
    tooth: '',
    desc: '',
    cost: ''
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    onAdd({
      ...formData,
      doctor: doctorName,
      date: new Date().toISOString().split('T')[0],
      status: 'completed',
      id: Date.now()
    });
    onClose();
  };

  return (
    <div className="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center z-[60] p-4 animate-in fade-in duration-200" onClick={onClose}>
      <div className="bg-white w-full max-w-md rounded-2xl shadow-2xl p-6 dark:bg-slate-800 dark:border-slate-700" onClick={e=>e.stopPropagation()}>
        <h2 className="text-xl font-bold text-slate-800 mb-4 dark:text-white">הוספת טיפול חדש</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1 dark:text-slate-300">סוג טיפול</label>
            <select 
              className="w-full p-2 border border-slate-300 rounded-lg dark:bg-slate-700 dark:border-slate-600 dark:text-white"
              value={formData.type}
              onChange={e => setFormData({...formData, type: e.target.value})}
            >
              <option>סתימה</option>
              <option>טיפול שורש</option>
              <option>עקירה</option>
              <option>כתר</option>
              <option>הסרת אבנית</option>
              <option>בדיקה</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1 dark:text-slate-300">מספר שן (אופציונלי)</label>
            <input 
              type="text" 
              className="w-full p-2 border border-slate-300 rounded-lg dark:bg-slate-700 dark:border-slate-600 dark:text-white"
              value={formData.tooth}
              onChange={e => setFormData({...formData, tooth: e.target.value})}
              placeholder="לדוגמה: 36"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1 dark:text-slate-300">תיאור הטיפול</label>
            <textarea 
              className="w-full p-2 border border-slate-300 rounded-lg dark:bg-slate-700 dark:border-slate-600 dark:text-white"
              value={formData.desc}
              onChange={e => setFormData({...formData, desc: e.target.value})}
              placeholder="פירוט מה בוצע..."
              rows={3}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1 dark:text-slate-300">עלות (₪)</label>
            <input 
              type="number" 
              className="w-full p-2 border border-slate-300 rounded-lg dark:bg-slate-700 dark:border-slate-600 dark:text-white"
              value={formData.cost}
              onChange={e => setFormData({...formData, cost: e.target.value})}
            />
          </div>
          <div className="flex gap-2 mt-6">
            <button type="button" onClick={onClose} className="flex-1 py-2 text-slate-600 hover:bg-slate-100 rounded-lg font-medium dark:text-slate-300 dark:hover:bg-slate-700">ביטול</button>
            <button type="submit" className="flex-1 py-2 bg-blue-600 text-white rounded-lg font-bold hover:bg-blue-700 shadow-sm flex justify-center items-center gap-2"><Save size={18}/> שמור טיפול</button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AddTreatmentModal;
