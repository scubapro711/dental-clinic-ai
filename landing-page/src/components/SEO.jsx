import { Helmet } from 'react-helmet-async';

/**
 * SEO Component
 * 
 * Comprehensive SEO optimization for landing page
 * - Meta tags
 * - Open Graph (Facebook, LinkedIn)
 * - Twitter Cards
 * - Structured Data (JSON-LD)
 */
export default function SEO({
  title = 'DentaFlow - פלטפורמת AI לניהול מרפאות שיניים | 4 סוכני AI ייחודיים',
  description = 'הפלטפורמה הדנטלית היחידה עם 4 מומחי AI: אלכס (קבלן קהל), שרה (עוזרת דנטלית), מרקוס (CFO), וסופיה (ציות). HIPAA Compliance מובנה, 30 יום ניסיון חינם.',
  keywords = 'תוכנה לניהול מרפאת שיניים, AI לרופאי שיניים, מערכת ניהול דנטלית, HIPAA compliance, סוכני AI, אוטומציה למרפאות, DentaFlow',
  image = 'https://dentaflow.ai/og-image.png',
  url = 'https://dentaflow.ai',
  type = 'website'
}) {
  const structuredData = {
    '@context': 'https://schema.org',
    '@type': 'SoftwareApplication',
    'name': 'DentaFlow',
    'applicationCategory': 'BusinessApplication',
    'operatingSystem': 'Web',
    'offers': {
      '@type': 'Offer',
      'price': '0',
      'priceCurrency': 'ILS',
      'priceValidUntil': '2025-12-31',
      'availability': 'https://schema.org/InStock',
      'description': '30 יום ניסיון חינם, ללא כרטיס אשראי'
    },
    'aggregateRating': {
      '@type': 'AggregateRating',
      'ratingValue': '4.9',
      'ratingCount': '127',
      'bestRating': '5',
      'worstRating': '1'
    },
    'description': description,
    'image': image,
    'url': url,
    'publisher': {
      '@type': 'Organization',
      'name': 'DentaFlow Ltd.',
      'logo': {
        '@type': 'ImageObject',
        'url': 'https://dentaflow.ai/logo.png'
      },
      'address': {
        '@type': 'PostalAddress',
        'addressCountry': 'IL',
        'addressLocality': 'Tel Aviv'
      },
      'contactPoint': {
        '@type': 'ContactPoint',
        'telephone': '+972-3-1234567',
        'contactType': 'Customer Service',
        'email': 'support@dentaflow.ai',
        'availableLanguage': ['he', 'en']
      }
    },
    'featureList': [
      'Alex AI - קבלן קהל 24/7',
      'Sarah AI - עוזרת דנטלית חכמה',
      'Marcus AI - CFO ייעודי (ייחודי!)',
      'Sophia AI - קצינת ציות (ייחודי!)',
      'HIPAA Compliance מובנה',
      'אינטגרציה מלאה עם Odoo ERP',
      '30 יום ניסיון חינם'
    ]
  };

  return (
    <Helmet>
      {/* Primary Meta Tags */}
      <title>{title}</title>
      <meta name="title" content={title} />
      <meta name="description" content={description} />
      <meta name="keywords" content={keywords} />
      <meta name="author" content="DentaFlow Ltd." />
      <meta name="robots" content="index, follow" />
      <meta name="language" content="Hebrew" />
      <meta name="revisit-after" content="7 days" />

      {/* Canonical URL */}
      <link rel="canonical" href={url} />

      {/* Open Graph / Facebook */}
      <meta property="og:type" content={type} />
      <meta property="og:url" content={url} />
      <meta property="og:title" content={title} />
      <meta property="og:description" content={description} />
      <meta property="og:image" content={image} />
      <meta property="og:image:width" content="1200" />
      <meta property="og:image:height" content="630" />
      <meta property="og:site_name" content="DentaFlow" />
      <meta property="og:locale" content="he_IL" />
      <meta property="og:locale:alternate" content="en_US" />

      {/* Twitter */}
      <meta property="twitter:card" content="summary_large_image" />
      <meta property="twitter:url" content={url} />
      <meta property="twitter:title" content={title} />
      <meta property="twitter:description" content={description} />
      <meta property="twitter:image" content={image} />
      <meta name="twitter:creator" content="@DentaFlowAI" />

      {/* Mobile Optimization */}
      <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0" />
      <meta name="theme-color" content="#2563eb" />
      <meta name="mobile-web-app-capable" content="yes" />
      <meta name="apple-mobile-web-app-capable" content="yes" />
      <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />
      <meta name="apple-mobile-web-app-title" content="DentaFlow" />

      {/* Favicon */}
      <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png" />
      <link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png" />
      <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png" />
      <link rel="manifest" href="/site.webmanifest" />

      {/* Structured Data (JSON-LD) */}
      <script type="application/ld+json">
        {JSON.stringify(structuredData)}
      </script>

      {/* Preconnect to external domains */}
      <link rel="preconnect" href="https://www.googletagmanager.com" />
      <link rel="preconnect" href="https://www.google-analytics.com" />
      <link rel="dns-prefetch" href="https://www.googletagmanager.com" />
      <link rel="dns-prefetch" href="https://www.google-analytics.com" />

      {/* Security Headers (via meta tags) */}
      <meta httpEquiv="X-Content-Type-Options" content="nosniff" />
      <meta httpEquiv="X-Frame-Options" content="DENY" />
      <meta httpEquiv="X-XSS-Protection" content="1; mode=block" />
      <meta httpEquiv="Referrer-Policy" content="strict-origin-when-cross-origin" />
    </Helmet>
  );
}

