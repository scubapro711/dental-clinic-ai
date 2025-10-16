import { Mail, Phone, MapPin, Facebook, Twitter, Linkedin, Instagram } from 'lucide-react';

/**
 * Footer Component
 * 
 * Professional footer with:
 * - Company info and logo
 * - Navigation links
 * - Social media links
 * - Contact information
 * - Legal links (Privacy, Terms, HIPAA)
 */
export default function Footer() {
  const currentYear = new Date().getFullYear();

  const footerSections = [
    {
      title: 'מוצר',
      links: [
        { label: 'תכונות', href: '#features' },
        { label: 'תמחור', href: '#pricing' },
        { label: 'דמו', href: '#demo' },
        { label: 'סוכני AI', href: '#agents' },
        { label: 'ציות HIPAA', href: '#hipaa' }
      ]
    },
    {
      title: 'חברה',
      links: [
        { label: 'אודות', href: '/about' },
        { label: 'בלוג', href: '/blog' },
        { label: 'קריירה', href: '/careers' },
        { label: 'צור קשר', href: '/contact' },
        { label: 'עזרה', href: '/help' }
      ]
    },
    {
      title: 'משאבים',
      links: [
        { label: 'מדריך משתמש', href: '/docs/user-guide' },
        { label: 'תיעוד API', href: '/docs/api' },
        { label: 'וידאו הדרכה', href: '/tutorials' },
        { label: 'מרכז עזרה', href: '/help-center' },
        { label: 'מצב המערכת', href: '/status' }
      ]
    },
    {
      title: 'משפטי',
      links: [
        { label: 'תנאי שימוש', href: '/terms' },
        { label: 'מדיניות פרטיות', href: '/privacy' },
        { label: 'הסכם BAA', href: '/baa' },
        { label: 'ציות HIPAA', href: '/hipaa-compliance' },
        { label: 'אבטחת מידע', href: '/security' }
      ]
    }
  ];

  const socialLinks = [
    { icon: Facebook, href: 'https://facebook.com/dentaflow', label: 'Facebook' },
    { icon: Twitter, href: 'https://twitter.com/dentaflow', label: 'Twitter' },
    { icon: Linkedin, href: 'https://linkedin.com/company/dentaflow', label: 'LinkedIn' },
    { icon: Instagram, href: 'https://instagram.com/dentaflow', label: 'Instagram' }
  ];

  return (
    <footer className="bg-gray-900 text-gray-300" dir="rtl">
      {/* Main Footer Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid md:grid-cols-2 lg:grid-cols-6 gap-8">
          {/* Company Info */}
          <div className="lg:col-span-2">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-xl">D</span>
              </div>
              <span className="text-2xl font-bold text-white">DentaFlow</span>
            </div>
            <p className="text-gray-400 mb-6 leading-relaxed">
              הפלטפורמה הדנטלית היחידה עם 4 סוכני AI מתמחים. 
              ציות HIPAA מלא, פלטפורמה משולבת, תמיכה 24/7.
            </p>

            {/* Contact Info */}
            <div className="space-y-3">
              <div className="flex items-center gap-2 text-sm">
                <Mail className="h-4 w-4 text-blue-400" />
                <a href="mailto:info@dentaflow.ai" className="hover:text-white transition-colors">
                  info@dentaflow.ai
                </a>
              </div>
              <div className="flex items-center gap-2 text-sm">
                <Phone className="h-4 w-4 text-blue-400" />
                <a href="tel:+972-3-1234567" className="hover:text-white transition-colors">
                  03-1234567
                </a>
              </div>
              <div className="flex items-center gap-2 text-sm">
                <MapPin className="h-4 w-4 text-blue-400" />
                <span>תל אביב, ישראל</span>
              </div>
            </div>

            {/* Social Links */}
            <div className="flex gap-3 mt-6">
              {socialLinks.map((social) => (
                <a
                  key={social.label}
                  href={social.href}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="w-10 h-10 bg-gray-800 hover:bg-gray-700 rounded-lg flex items-center justify-center transition-colors"
                  aria-label={social.label}
                >
                  <social.icon className="h-5 w-5" />
                </a>
              ))}
            </div>
          </div>

          {/* Footer Links */}
          {footerSections.map((section) => (
            <div key={section.title}>
              <h3 className="text-white font-bold mb-4">{section.title}</h3>
              <ul className="space-y-2">
                {section.links.map((link) => (
                  <li key={link.label}>
                    <a
                      href={link.href}
                      className="text-sm hover:text-white transition-colors"
                    >
                      {link.label}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>

      {/* Bottom Bar */}
      <div className="border-t border-gray-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            {/* Copyright */}
            <div className="text-sm text-gray-400">
              © {currentYear} DentaFlow. כל הזכויות שמורות.
            </div>

            {/* Trust Badges */}
            <div className="flex flex-wrap gap-4 items-center">
              <div className="flex items-center gap-2 bg-gray-800 px-3 py-1 rounded-full">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span className="text-xs text-gray-300">תואם HIPAA</span>
              </div>
              <div className="flex items-center gap-2 bg-gray-800 px-3 py-1 rounded-full">
                <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                <span className="text-xs text-gray-300">הצפנת AES-256</span>
              </div>
              <div className="flex items-center gap-2 bg-gray-800 px-3 py-1 rounded-full">
                <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
                <span className="text-xs text-gray-300">SOC 2 Type II (בתהליך)</span>
              </div>
            </div>

            {/* Language Selector (Future) */}
            <div className="text-sm text-gray-400">
              🇮🇱 עברית
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}

