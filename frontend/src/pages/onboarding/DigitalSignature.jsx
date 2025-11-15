import { useState, useRef } from 'react';
import { FileText, Download, Check } from 'lucide-react';
import SignatureCanvas from 'react-signature-canvas';
import API_CONFIG from '@/config/api';

/**
 * Digital Signature Component
 * 
 * Allows users to digitally sign legal documents (BAA, DPA)
 * Features:
 * - Document preview
 * - Signature pad
 * - Full name + title input
 * - Timestamp
 * - IP address logging (for legal validity)
 */
export default function DigitalSignature({ documentType, documentTitle, documentUrl, onSign }) {
  const [fullName, setFullName] = useState('');
  const [title, setTitle] = useState('');
  const [agreedToDocument, setAgreedToDocument] = useState(false);
  const [isSigning, setIsSigning] = useState(false);
  const signatureRef = useRef(null);

  const handleClear = () => {
    signatureRef.current?.clear();
  };

  const handleSign = async () => {
    // Validation
    if (!fullName.trim()) {
      alert('נא להזין שם מלא');
      return;
    }

    if (!title.trim()) {
      alert('נא להזין תפקיד');
      return;
    }

    if (!agreedToDocument) {
      alert('נא לאשר שקראת והבנת את המסמך');
      return;
    }

    if (signatureRef.current?.isEmpty()) {
      alert('נא לחתום על המסמך');
      return;
    }

    setIsSigning(true);

    try {
      // Get signature as base64 image
      const signatureImage = signatureRef.current?.toDataURL();

      // Create signature data object
      const signatureData = {
        documentType,
        fullName,
        title,
        signatureImage,
        timestamp: new Date().toISOString(),
        ipAddress: await getIPAddress(), // For legal validity
        userAgent: navigator.userAgent
      };

      // In production, send to backend API
      // await fetch(API_CONFIG.endpoint('signatures'), { method: 'POST', body: JSON.stringify(signatureData) });

      // Call parent callback
      onSign(signatureData);
    } catch (error) {
      console.error('Signature error:', error);
      alert('שגיאה בחתימה. נא לנסות שוב.');
    } finally {
      setIsSigning(false);
    }
  };

  const getIPAddress = async () => {
    try {
      const response = await fetch('https://api.ipify.org?format=json');
      const data = await response.json();
      return data.ip;
    } catch {
      return 'unknown';
    }
  };

  return (
    <div className="space-y-6">
      {/* Document Preview */}
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <FileText className="h-6 w-6 text-blue-600" />
            <div>
              <h3 className="font-bold text-gray-900">{documentTitle}</h3>
              <p className="text-sm text-gray-500">מסמך משפטי מחייב</p>
            </div>
          </div>
          <a
            href={documentUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 text-blue-600 hover:text-blue-700 text-sm font-medium"
          >
            <Download className="h-4 w-4" />
            <span>הורד PDF</span>
          </a>
        </div>

        <div className="bg-white border border-gray-200 rounded p-4 max-h-64 overflow-y-auto text-sm text-gray-700">
          <p className="mb-3">
            <strong>חשוב:</strong> נא לקרוא בעיון את המסמך המלא לפני החתימה.
          </p>
          <p className="mb-3">
            מסמך זה מהווה הסכם משפטי מחייב בין המרפאה שלך לבין DentaFlow Ltd.
          </p>
          <p className="text-blue-600 font-medium">
            👉 <a href={documentUrl} target="_blank" rel="noopener noreferrer" className="underline">
              לחץ כאן לקריאת המסמך המלא
            </a>
          </p>
        </div>
      </div>

      {/* Signer Information */}
      <div className="space-y-4">
        <h3 className="font-bold text-gray-900">פרטי החותם</h3>
        
        <div>
          <label htmlFor="fullName" className="block text-sm font-medium text-gray-700 mb-1">
            שם מלא *
          </label>
          <input
            type="text"
            id="fullName"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            placeholder="ד״ר יוסי כהן"
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            required
          />
        </div>

        <div>
          <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-1">
            תפקיד במרפאה *
          </label>
          <input
            type="text"
            id="title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="רופא שיניים / מנהל מרפאה"
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            required
          />
        </div>
      </div>

      {/* Signature Pad */}
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <label className="block text-sm font-medium text-gray-700">
            חתימה דיגיטלית *
          </label>
          <button
            type="button"
            onClick={handleClear}
            className="text-sm text-gray-600 hover:text-gray-900"
          >
            נקה חתימה
          </button>
        </div>
        <div className="border-2 border-gray-300 rounded-lg bg-white">
          <SignatureCanvas
            ref={signatureRef}
            canvasProps={{
              className: 'w-full h-40',
              style: { touchAction: 'none' }
            }}
            backgroundColor="white"
          />
        </div>
        <p className="text-xs text-gray-500">
          חתום בעזרת העכבר או המסך המגע
        </p>
      </div>

      {/* Agreement Checkbox */}
      <div className="flex items-start gap-3 bg-blue-50 border border-blue-200 rounded-lg p-4">
        <input
          type="checkbox"
          id="agreement"
          checked={agreedToDocument}
          onChange={(e) => setAgreedToDocument(e.target.checked)}
          className="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
        />
        <label htmlFor="agreement" className="text-sm text-gray-700 leading-relaxed">
          אני מאשר/ת שקראתי והבנתי את <strong>{documentTitle}</strong> במלואו, 
          ואני מסכים/ה לכל התנאים המפורטים בו. חתימתי הדיגיטלית מהווה הסכמה משפטית מחייבת.
        </label>
      </div>

      {/* Legal Notice */}
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 text-xs text-gray-600">
        <p className="mb-2">
          <strong>הודעה משפטית:</strong>
        </p>
        <ul className="space-y-1 list-disc list-inside">
          <li>חתימה דיגיטלית זו תועד עם חותמת זמן, כתובת IP, ופרטי הדפדפן</li>
          <li>המסמך החתום יישמר במערכת שלנו למשך 7 שנים לפחות</li>
          <li>תוכל לבקש עותק של המסמך החתום בכל עת</li>
          <li>חתימה זו תקפה משפטית על פי חוק החתימה האלקטרונית, התשס"א-2001</li>
        </ul>
      </div>

      {/* Sign Button */}
      <button
        onClick={handleSign}
        disabled={isSigning}
        className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-medium py-3 px-6 rounded-lg transition-colors flex items-center justify-center gap-2"
      >
        {isSigning ? (
          <>
            <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
            <span>חותם...</span>
          </>
        ) : (
          <>
            <Check className="h-5 w-5" />
            <span>חתום על המסמך</span>
          </>
        )}
      </button>
    </div>
  );
}

