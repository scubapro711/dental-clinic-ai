import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { FileText, ArrowRight, Download, Printer, AlertCircle } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

/**
 * LegalDocument Component
 * 
 * Displays legal documents in a professional, readable format
 * Supports all 7 legal documents with proper formatting
 * Loads real markdown content from backend
 */
export default function LegalDocument() {
  const { documentId } = useParams();
  const [content, setContent] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const documents = {
    terms: {
      title: 'תנאי שימוש',
      titleEn: 'Terms of Service',
      file: 'TERMS_OF_SERVICE.md',
      lastUpdated: '2025-10-16'
    },
    privacy: {
      title: 'מדיניות פרטיות',
      titleEn: 'Privacy Policy',
      file: 'PRIVACY_POLICY.md',
      lastUpdated: '2025-10-16'
    },
    cookies: {
      title: 'מדיניות עוגיות',
      titleEn: 'Cookie Policy',
      file: 'COOKIE_POLICY.md',
      lastUpdated: '2025-10-16'
    },
    hipaa: {
      title: 'הודעת פרטיות HIPAA',
      titleEn: 'HIPAA Notice of Privacy Practices',
      file: 'HIPAA_NOTICE.md',
      lastUpdated: '2025-10-16'
    },
    aup: {
      title: 'מדיניות שימוש מקובל',
      titleEn: 'Acceptable Use Policy',
      file: 'ACCEPTABLE_USE_POLICY.md',
      lastUpdated: '2025-10-16'
    },
    dpa: {
      title: 'הסכם עיבוד נתונים',
      titleEn: 'Data Processing Agreement',
      file: 'DATA_PROCESSING_AGREEMENT.md',
      lastUpdated: '2025-10-16'
    },
    sla: {
      title: 'הסכם רמת שירות',
      titleEn: 'Service Level Agreement',
      file: 'SERVICE_LEVEL_AGREEMENT.md',
      lastUpdated: '2025-10-16'
    }
  };

  const currentDoc = documents[documentId];

  useEffect(() => {
    const loadDocument = async () => {
      if (!currentDoc) {
        setError('Document not found');
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        setError(null);

        // Fetch document from backend API
        const response = await fetch(`/api/v1/legal/${documentId}`);
        
        if (!response.ok) {
          throw new Error(`Failed to load document: ${response.statusText}`);
        }

        const data = await response.json();
        setContent(data.content || '');
      } catch (err) {
        console.error('Error loading document:', err);
        setError(err.message);
        
        // Fallback: Try to load from public folder
        try {
          const publicResponse = await fetch(`/legal/${currentDoc.file}`);
          if (publicResponse.ok) {
            const text = await publicResponse.text();
            setContent(text);
            setError(null);
          }
        } catch (fallbackErr) {
          console.error('Fallback load failed:', fallbackErr);
        }
      } finally {
        setLoading(false);
      }
    };

    loadDocument();
  }, [documentId, currentDoc]);

  const handlePrint = () => {
    window.print();
  };

  const handleDownload = () => {
    // Create a blob and download
    const blob = new Blob([content], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${currentDoc?.file || 'document.md'}`;
    a.click();
    URL.revokeObjectURL(url);
  };

  if (!currentDoc) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">מסמך לא נמצא</h1>
          <p className="text-gray-600 mb-6">המסמך המבוקש אינו קיים במערכת</p>
          <Link to="/" className="text-blue-600 hover:text-blue-700 underline">
            חזרה לדף הבית
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 print:hidden">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            {/* Back Button */}
            <Link
              to="/"
              className="flex items-center gap-2 text-gray-600 hover:text-gray-900 transition-colors"
            >
              <ArrowRight className="h-5 w-5" />
              <span>חזרה</span>
            </Link>

            {/* Actions */}
            <div className="flex items-center gap-3">
              <button
                onClick={handlePrint}
                className="flex items-center gap-2 px-4 py-2 text-gray-700 hover:text-gray-900 transition-colors"
                disabled={loading}
              >
                <Print className="h-5 w-5" />
                <span className="hidden sm:inline">הדפס</span>
              </button>
              <button
                onClick={handleDownload}
                className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                disabled={loading || !content}
              >
                <Download className="h-5 w-5" />
                <span className="hidden sm:inline">הורד</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Document Content */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 md:p-12">
          {/* Document Header */}
          <div className="mb-8 pb-8 border-b border-gray-200" dir="rtl">
            <div className="flex items-center gap-3 mb-4">
              <FileText className="h-8 w-8 text-blue-600" />
              <div>
                <h1 className="text-3xl font-bold text-gray-900">{currentDoc.title}</h1>
                <p className="text-lg text-gray-600 mt-1">{currentDoc.titleEn}</p>
              </div>
            </div>
            <div className="flex items-center gap-4 text-sm text-gray-500">
              <span>עדכון אחרון: {new Date(currentDoc.lastUpdated).toLocaleDateString('he-IL')}</span>
              <span>•</span>
              <span>תקף מ: {new Date(currentDoc.lastUpdated).toLocaleDateString('he-IL')}</span>
            </div>
          </div>

          {/* Document Body */}
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
              <p className="ml-4 text-gray-600">טוען מסמך...</p>
            </div>
          ) : error && !content ? (
            <div className="bg-red-50 border-r-4 border-red-600 p-6 rounded">
              <div className="flex items-start gap-3">
                <AlertCircle className="h-6 w-6 text-red-600 flex-shrink-0 mt-1" />
                <div>
                  <p className="font-bold text-red-900 mb-2">שגיאה בטעינת המסמך</p>
                  <p className="text-sm text-red-800">{error}</p>
                  <p className="text-sm text-red-700 mt-2">
                    אנא נסה שוב מאוחר יותר או צור קשר עם התמיכה.
                  </p>
                </div>
              </div>
            </div>
          ) : (
            <div className="space-y-6">
              {/* Notice Banner */}
              <div className="bg-blue-50 border-r-4 border-blue-600 p-6 rounded" dir="rtl">
                <p className="text-sm text-blue-900">
                  <strong>הערה:</strong> זהו מסמך משפטי מחייב. אנא קרא בעיון לפני השימוש בשירות.
                  במקרה של שאלות, צור קשר עם: <a href="mailto:legal@dentaflow.ai" className="underline hover:text-blue-700">legal@dentaflow.ai</a>
                </p>
              </div>

              {/* Markdown Content */}
              <div className="prose prose-lg max-w-none prose-headings:font-bold prose-h1:text-3xl prose-h2:text-2xl prose-h3:text-xl prose-a:text-blue-600 prose-a:no-underline hover:prose-a:underline prose-strong:text-gray-900 prose-ul:list-disc prose-ol:list-decimal">
                <ReactMarkdown>{content}</ReactMarkdown>
              </div>
            </div>
          )}

          {/* Footer */}
          <div className="mt-12 pt-8 border-t border-gray-200" dir="rtl">
            <div className="bg-gray-50 rounded-lg p-6">
              <h3 className="font-bold text-gray-900 mb-3">יש לך שאלות?</h3>
              <p className="text-gray-600 mb-4">
                אם יש לך שאלות לגבי מסמך זה, אנא צור קשר איתנו:
              </p>
              <div className="space-y-2 text-sm">
                <p>📧 <a href="mailto:legal@dentaflow.ai" className="text-blue-600 hover:text-blue-700">legal@dentaflow.ai</a></p>
                <p>📞 <a href="tel:+972-3-1234567" className="text-blue-600 hover:text-blue-700">03-1234567</a></p>
                <p>📍 תל אביב, ישראל</p>
              </div>
            </div>
          </div>
        </div>

        {/* Related Documents */}
        <div className="mt-8" dir="rtl">
          <h3 className="text-lg font-bold text-gray-900 mb-4">מסמכים קשורים</h3>
          <div className="grid md:grid-cols-2 gap-4">
            {Object.entries(documents)
              .filter(([id]) => id !== documentId)
              .slice(0, 4)
              .map(([id, doc]) => (
                <Link
                  key={id}
                  to={`/legal/${id}`}
                  className="bg-white border border-gray-200 rounded-lg p-4 hover:border-blue-300 hover:shadow-md transition-all"
                >
                  <div className="flex items-center gap-3">
                    <FileText className="h-5 w-5 text-gray-400" />
                    <div>
                      <p className="font-medium text-gray-900">{doc.title}</p>
                      <p className="text-sm text-gray-500">{doc.titleEn}</p>
                    </div>
                  </div>
                </Link>
              ))}
          </div>
        </div>
      </div>
    </div>
  );
}

