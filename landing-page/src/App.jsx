import { useEffect } from 'react';
import { HelmetProvider } from 'react-helmet-async';
import './App.css';
import HeroSection from './components/HeroSection';
import CompetitiveAdvantages from './components/CompetitiveAdvantages';
import AITeamSection from './components/AITeamSection';
import HIPAASection from './components/HIPAASection';
import PricingSection from './components/PricingSection';
import InteractiveDemo from './components/InteractiveDemo';
import FAQSection from './components/FAQSection';
import Footer from './components/Footer';
import CookieConsent from './components/CookieConsent';
import SEO from './components/SEO';
import GoogleAnalytics, { initGoogleAnalytics } from './components/GoogleAnalytics';

/**
 * DentaFlow Landing Page
 * 
 * Main application component that assembles all sections:
 * 1. Hero Section - Main value proposition with 4 AI agents
 * 2. Competitive Advantages - Comparison with competitors
 * 3. AI Team Section - Detailed showcase of all 4 agents
 * 4. HIPAA Compliance - Built-in compliance as competitive advantage
 * 5. Pricing - Transparent pricing with early adopter discount
 * 6. Interactive Demo - Try Alex AI live
 * 7. FAQ - Common questions
 * 8. Footer - Company info and links
 * 
 * SEO & Analytics:
 * - Comprehensive meta tags (Open Graph, Twitter Cards)
 * - Google Analytics tracking
 * - Structured data (JSON-LD)
 * - Sitemap & robots.txt
 */
function App() {
  // Initialize Google Analytics on mount
  useEffect(() => {
    const GA_ID = import.meta.env.VITE_GA_MEASUREMENT_ID || 'G-XXXXXXXXXX';
    initGoogleAnalytics(GA_ID);
  }, []);

  return (
    <HelmetProvider>
      <div className="min-h-screen bg-white">
        {/* SEO Meta Tags */}
        <SEO />

        {/* Google Analytics */}
        <GoogleAnalytics />

        {/* Hero Section */}
        <HeroSection />

        {/* Competitive Advantages */}
        <CompetitiveAdvantages />

        {/* AI Team Section */}
        <AITeamSection />

        {/* HIPAA Compliance */}
        <HIPAASection />

        {/* Pricing */}
        <PricingSection />

        {/* Interactive Demo */}
        <InteractiveDemo />

        {/* FAQ */}
        <FAQSection />

        {/* Footer */}
        <Footer />

        {/* Cookie Consent Banner */}
        <CookieConsent />
      </div>
    </HelmetProvider>
  );
}

export default App;

