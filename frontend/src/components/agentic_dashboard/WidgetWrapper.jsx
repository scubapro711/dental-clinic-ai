/**
 * WidgetWrapper Component
 * 
 * Wraps dashboard widgets with consistent styling and close button.
 */
import React from 'react';
import PropTypes from 'prop-types';
import { X } from 'lucide-react';

export const WidgetWrapper = ({ children, title, onClose, isWide = false }) => {
  return (
    <div className={`flex flex-col bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden relative group transition-all hover:shadow-md h-full dark:bg-slate-800 dark:border-slate-700 ${isWide ? 'md:col-span-2 xl:col-span-2' : 'col-span-1'}`}>
      <div className="absolute top-2 right-2 z-20 opacity-0 group-hover:opacity-100 transition-opacity flex gap-1">
        {onClose && (
          <button 
            onClick={onClose} 
            title="הסר" 
            className="p-1 text-slate-400 hover:text-red-500 hover:bg-red-50 rounded dark:hover:bg-red-900/30"
          >
            <X size={14}/>
          </button>
        )}
      </div>
      <div className="h-full w-full">{children}</div>
    </div>
  );
};

WidgetWrapper.propTypes = {
  children: PropTypes.node.isRequired,
  title: PropTypes.string,
  onClose: PropTypes.func,
  isWide: PropTypes.bool
};
