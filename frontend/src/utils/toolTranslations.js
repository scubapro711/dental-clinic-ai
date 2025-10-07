/**
 * Tool Name Translations - Hebrew Medical Context
 * 
 * Translates technical tool names to language that dentists understand
 */

export const toolTranslations = {
  // Revenue & Financial Tools
  'get_revenue_overview_tool': {
    he: 'בודק נתוני הכנסות',
    en: 'Checking revenue data',
    description: 'מנתח את ההכנסות של המרפאה'
  },
  'get_financial_summary': {
    he: 'מכין סיכום פיננסי',
    en: 'Preparing financial summary',
    description: 'אוסף נתונים כספיים מהמערכת'
  },
  'calculate_revenue': {
    he: 'מחשב הכנסות',
    en: 'Calculating revenue',
    description: 'מבצע חישובים על נתוני הכנסות'
  },
  
  // Patient Tools
  'search_patients': {
    he: 'מחפש מטופלים',
    en: 'Searching patients',
    description: 'מחפש במאגר המטופלים'
  },
  'get_patient_info': {
    he: 'מביא פרטי מטופל',
    en: 'Fetching patient details',
    description: 'שולף מידע על מטופל ספציפי'
  },
  'update_patient_record': {
    he: 'מעדכן תיק מטופל',
    en: 'Updating patient record',
    description: 'מעדכן מידע בתיק המטופל'
  },
  
  // Appointment Tools
  'get_appointments': {
    he: 'בודק תורים',
    en: 'Checking appointments',
    description: 'מביא רשימת תורים'
  },
  'schedule_appointment': {
    he: 'קובע תור',
    en: 'Scheduling appointment',
    description: 'יוצר תור חדש במערכת'
  },
  'cancel_appointment': {
    he: 'מבטל תור',
    en: 'Canceling appointment',
    description: 'מבטל תור קיים'
  },
  'get_today_schedule': {
    he: 'מביא לוח זמנים להיום',
    en: 'Getting today schedule',
    description: 'שולף את כל התורים להיום'
  },
  
  // Staff Tools
  'get_staff_schedule': {
    he: 'בודק משמרות צוות',
    en: 'Checking staff shifts',
    description: 'מביא מידע על משמרות הצוות'
  },
  'assign_task': {
    he: 'משייך משימה',
    en: 'Assigning task',
    description: 'מקצה משימה לאחד מהצוות'
  },
  
  // Inventory Tools
  'check_inventory': {
    he: 'בודק מלאי',
    en: 'Checking inventory',
    description: 'בודק מצב מלאי של ציוד'
  },
  'order_supplies': {
    he: 'מזמין ציוד',
    en: 'Ordering supplies',
    description: 'יוצר הזמנת ציוד חדש'
  },
  
  // Analytics Tools
  'generate_report': {
    he: 'מכין דוח',
    en: 'Generating report',
    description: 'יוצר דוח מפורט'
  },
  'analyze_trends': {
    he: 'מנתח מגמות',
    en: 'Analyzing trends',
    description: 'בוחן מגמות לאורך זמן'
  }
};

/**
 * Get translated tool name
 */
export function getToolName(toolName, language = 'he') {
  const tool = toolTranslations[toolName];
  if (!tool) {
    // Fallback: convert snake_case to readable format
    return toolName
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  }
  return tool[language] || tool.en;
}

/**
 * Get tool description
 */
export function getToolDescription(toolName) {
  const tool = toolTranslations[toolName];
  return tool?.description || '';
}

/**
 * Get tool icon based on category
 */
export function getToolIcon(toolName) {
  if (toolName.includes('revenue') || toolName.includes('financial')) return '💰';
  if (toolName.includes('patient')) return '👤';
  if (toolName.includes('appointment') || toolName.includes('schedule')) return '📅';
  if (toolName.includes('search') || toolName.includes('query')) return '🔍';
  if (toolName.includes('report') || toolName.includes('analyze')) return '📊';
  if (toolName.includes('staff') || toolName.includes('assign')) return '👥';
  if (toolName.includes('inventory') || toolName.includes('supplies')) return '📦';
  if (toolName.includes('update') || toolName.includes('edit')) return '✏️';
  if (toolName.includes('cancel') || toolName.includes('delete')) return '❌';
  return '🔧';
}
