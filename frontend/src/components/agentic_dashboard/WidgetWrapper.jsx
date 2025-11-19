/**
 * WidgetWrapper Component
 * 
 * Wraps dashboard widgets with consistent styling.
 */

import React from 'react';
import PropTypes from 'prop-types';
import { X } from 'lucide-react';

export const WidgetWrapper = ({ children, title, onClose, isWide = false }) => {
  return (
    <div 
      className={`bg-white dark:bg-slate-800 rounded-2xl shadow-sm border border-slate-200 dark:border-slate-700 overflow-hidden flex flex-col ${
        isWide ? 'md:col-span-2' : ''
      }`}
    >
      {/* Header */}
      <div className="px-6 py-4 border-b border-slate-100 dark:border-slate-700 flex justify-between items-center shrink-0">
        <h3 className="font-bold text-slate-900 dark:text-white">{title}</h3>
        {onClose && (
          <button
            onClick={onClose}
            className="p-1 text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition"
            aria-label="Close widget"
          >
            <X size={16} />
          </button>
        )}
      </div>
      
      {/* Content */}
      <div className="flex-1 overflow-auto">
        {children}
      </div>
    </div>
  );
};

WidgetWrapper.propTypes = {
  children: PropTypes.node.isRequired,
  title: PropTypes.string.isRequired,
  onClose: PropTypes.func,
  isWide: PropTypes.bool
};
