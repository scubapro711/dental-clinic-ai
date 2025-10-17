import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { LanguageSwitcher } from '../components/LanguageSwitcher';
import DemoChatButton from '../components/DemoChatButton';
import './LandingPage.css';

const LandingPage = () => {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const [selectedPlan, setSelectedPlan] = useState('professional');

  return (
    <div className="landing-page">
      {/* Navigation */}
      <nav className="landing-nav">
        <div className="nav-container">
          <div className="nav-logo">
            <span className="logo-icon">🦷</span>
            <span className="logo-text">DentaFlow</span>
          </div>
          <div className="nav-links">
            <a href="#features">{t("landing.nav.features")}</a>
            <a href="#why-not-bot">{t("landing.nav.whyNotBot")}</a>
            <a href="#pricing">{t("landing.nav.pricing")}</a>
            <a href="#pilot">{t("landing.nav.pilot")}</a>
            <LanguageSwitcher />
            <Link to="/demo" className="nav-cta-demo">{t("landing.nav.tryDemo")}</Link>
            <Link to="/register" className="nav-cta">{t("landing.nav.startTrial")}</Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="hero">
        <div className="hero-container">
          <div className="hero-content">
            <div className="hero-badge">{t("landing.hero.badge")}</div>
            <h1 className="hero-title">
              {t("landing.hero.title1")}
              <span className="hero-gradient">{t("landing.hero.title2")}</span>
            </h1>
            <p className="hero-subtitle">
              {t("landing.hero.subtitle")}
            </p>
            
            {/* 3-Level CTA Strategy */}
            <div className="hero-ctas">
              <button className="cta-primary" onClick={() => navigate('/demo')}>
                <span className="cta-icon">💬</span>
                {t("landing.hero.tryDemo")}
                <span className="cta-badge">{t("landing.hero.noSignup")}</span>
              </button>
              <button className="cta-secondary" onClick={() => navigate('/register')}>
                <span className="cta-icon">🎁</span>
                {t("landing.hero.startTrial")}
                <span className="cta-badge">{t("landing.hero.noCredit")}</span>
              </button>
              <button className="cta-tertiary" onClick={() => document.getElementById('pilot').scrollIntoView({ behavior: 'smooth' })}>
                <span className="cta-icon">🌟</span>
                {t("landing.hero.joinPilot")}
                <span className="cta-badge">{t("landing.hero.monthsFree")}</span>
              </button>
            </div>

            {/* Trust Indicators */}
            <div className="hero-trust">
              <div className="trust-item">
                <span className="trust-icon">✓</span>
                <span>{t("landing.hero.hipaa")}</span>
              </div>
              <div className="trust-item">
                <span className="trust-icon">✓</span>
                <span>{t("landing.hero.gdpr")}</span>
              </div>
              <div className="trust-item">
                <span className="trust-icon">✓</span>
                <span>{t("landing.hero.uptime")}</span>
              </div>
              <div className="trust-item">
                <span className="trust-icon">✓</span>
                <span>{t("landing.hero.odoo")}</span>
              </div>
            </div>
          </div>

          <div className="hero-visual">
            <div className="hero-card">
              <div className="card-header">
                <span className="card-badge">{t("landing.hero.liveDemo")}</span>
                <span className="card-time">{t("landing.hero.active247")}</span>
              </div>
              <div className="card-agents">
                <div className="agent-item">
                  <span className="agent-avatar">👨‍💼</span>
                  <div className="agent-info">
                    <div className="agent-name">{t("landing.agents.alex.name")}</div>
                    <div className="agent-role">{t("landing.agents.alex.role")}</div>
                  </div>
                  <span className="agent-status online">●</span>
                </div>
                <div className="agent-item">
                  <span className="agent-avatar">👩‍⚕️</span>
                  <div className="agent-info">
                    <div className="agent-name">{t("landing.agents.sarah.name")}</div>
                    <div className="agent-role">{t("landing.agents.sarah.role")}</div>
                  </div>
                  <span className="agent-status online">●</span>
                </div>
                <div className="agent-item">
                  <span className="agent-avatar">👨‍💼</span>
                  <div className="agent-info">
                    <div className="agent-name">{t("landing.agents.marcus.name")}</div>
                    <div className="agent-role">{t("landing.agents.marcus.role")}</div>
                  </div>
                  <span className="agent-status online">●</span>
                </div>
                <div className="agent-item">
                  <span className="agent-avatar">👩‍💼</span>
                  <div className="agent-info">
                    <div className="agent-name">{t("landing.agents.sophia.name")}</div>
                    <div className="agent-role">{t("landing.agents.sophia.role")}</div>
                  </div>
                  <span className="agent-status online">●</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Why Not a Bot Section - Research-Based */}
      <section id="why-not-bot" className="why-not-bot">
        <div className="section-container">
          <div className="section-header">
            <h2>{t("landing.whyNotBot.title")}</h2>
            <p className="section-subtitle">
              {t("landing.whyNotBot.subtitle")}
            </p>
          </div>

          <div className="comparison-grid">
            <div className="comparison-card bad">
              <div className="comparison-header">
                <span className="comparison-icon">🤖</span>
                <h3>{t("landing.whyNotBot.chatbot")}</h3>
              </div>
              <ul className="comparison-list">
                <li className="comparison-item bad">
                  <span className="item-icon">✗</span>
                  <span>Single AI, limited context</span>
                </li>
                <li className="comparison-item bad">
                  <span className="item-icon">✗</span>
                  <span>Fails with complex questions</span>
                </li>
                <li className="comparison-item bad">
                  <span className="item-icon">✗</span>
                  <span>Generic, scripted responses</span>
                </li>
                <li className="comparison-item bad">
                  <span className="item-icon">✗</span>
                  <span>No real understanding</span>
                </li>
                <li className="comparison-item bad">
                  <span className="item-icon">✗</span>
                  <span>Can't handle handoffs</span>
                </li>
              </ul>
            </div>

            <div className="comparison-card good">
              <div className="comparison-header">
                <span className="comparison-icon">🎯</span>
                <h3>{t("landing.whyNotBot.dentaflow")}</h3>
              </div>
              <ul className="comparison-list">
                <li className="comparison-item good">
                  <span className="item-icon">✓</span>
                  <span>4 specialized AI agents</span>
                </li>
                <li className="comparison-item good">
                  <span className="item-icon">✓</span>
                  <span>Deep context understanding</span>
                </li>
                <li className="comparison-item good">
                  <span className="item-icon">✓</span>
                  <span>Personalized, intelligent responses</span>
                </li>
                <li className="comparison-item good">
                  <span className="item-icon">✓</span>
                  <span>Real Odoo integration</span>
                </li>
                <li className="comparison-item good">
                  <span className="item-icon">✓</span>
                  <span>Seamless agent collaboration</span>
                </li>
              </ul>
            </div>
          </div>

          <div className="research-note">
            <span className="research-icon">📚</span>
            <span>
              {t("landing.whyNotBot.research")}
            </span>
          </div>
        </div>
      </section>

      {/* The 4 AI Agents Section */}
      <section id="agents" className="agents-section">
        <div className="section-container">
          <div className="section-header">
            <h2>{t("landing.agentsSection.title")}</h2>
            <p className="section-subtitle">
              {t("landing.agentsSection.subtitle")}
            </p>
          </div>

          <div className="agents-grid">
            <div className="agent-card">
              <div className="agent-card-header">
                <span className="agent-card-avatar">👨‍💼</span>
                <h3>{t("landing.agents.alex.name")}</h3>
                <p className="agent-card-role">{t("landing.agents.alex.role")}</p>
              </div>
              <ul className="agent-card-features">
                <li>{t("landing.agents.alex.feature1")}</li>
                <li>{t("landing.agents.alex.feature2")}</li>
                <li>{t("landing.agents.alex.feature3")}</li>
                <li>{t("landing.agents.alex.feature4")}</li>
              </ul>
              <div className="agent-card-stat">
                <span className="stat-value">3x</span>
                <span className="stat-label">{t("landing.agents.alex.stat")}</span>
              </div>
            </div>

            <div className="agent-card">
              <div className="agent-card-header">
                <span className="agent-card-avatar">👩‍⚕️</span>
                <h3>{t("landing.agents.sarah.name")}</h3>
                <p className="agent-card-role">{t("landing.agents.sarah.role")}</p>
              </div>
              <ul className="agent-card-features">
                <li>{t("landing.agents.sarah.feature1")}</li>
                <li>{t("landing.agents.sarah.feature2")}</li>
                <li>{t("landing.agents.sarah.feature3")}</li>
                <li>{t("landing.agents.sarah.feature4")}</li>
              </ul>
              <div className="agent-card-stat">
                <span className="stat-value">85%</span>
                <span className="stat-label">{t("landing.agents.sarah.stat")}</span>
              </div>
            </div>

            <div className="agent-card">
              <div className="agent-card-header">
                <span className="agent-card-avatar">👨‍💼</span>
                <h3>{t("landing.agents.marcus.name")}</h3>
                <p className="agent-card-role">{t("landing.agents.marcus.role")}</p>
              </div>
              <ul className="agent-card-features">
                <li>{t("landing.agents.marcus.feature1")}</li>
                <li>{t("landing.agents.marcus.feature2")}</li>
                <li>{t("landing.agents.marcus.feature3")}</li>
                <li>{t("landing.agents.marcus.feature4")}</li>
              </ul>
              <div className="agent-card-stat">
                <span className="stat-value">₪15K+</span>
                <span className="stat-label">{t("landing.agents.marcus.stat")}</span>
              </div>
            </div>

            <div className="agent-card">
              <div className="agent-card-header">
                <span className="agent-card-avatar">👩‍💼</span>
                <h3>{t("landing.agents.sophia.name")}</h3>
                <p className="agent-card-role">{t("landing.agents.sophia.role")}</p>
              </div>
              <ul className="agent-card-features">
                <li>{t("landing.agents.sophia.feature1")}</li>
                <li>{t("landing.agents.sophia.feature2")}</li>
                <li>{t("landing.agents.sophia.feature3")}</li>
                <li>{t("landing.agents.sophia.feature4")}</li>
              </ul>
              <div className="agent-card-stat">
                <span className="stat-value">10h+</span>
                <span className="stat-label">{t("landing.agents.sophia.stat")}</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Multi-Channel Communication Section - Research-Based */}
      <section id="communication" className="communication-section">
        <div className="section-container">
          <div className="section-header">
            <h2>Multi-Channel Patient Communication</h2>
            <p className="section-subtitle">
              Reach patients where they are—3x higher response rates
            </p>
          </div>

          <div className="channels-timeline">
            <div className="timeline-item available">
              <div className="timeline-badge">✓ Available Now</div>
              <div className="timeline-content">
                <h3>Current Channels</h3>
                <div className="channels-grid">
                  <div className="channel-item">
                    <span className="channel-icon">💬</span>
                    <span className="channel-name">Web Chat</span>
                    <span className="channel-stat">Instant</span>
                  </div>
                  <div className="channel-item">
                    <span className="channel-icon">📱</span>
                    <span className="channel-name">SMS</span>
                    <span className="channel-stat">98% open rate</span>
                  </div>
                  <div className="channel-item">
                    <span className="channel-icon">📧</span>
                    <span className="channel-name">Email</span>
                    <span className="channel-stat">Professional</span>
                  </div>
                </div>
              </div>
            </div>

            <div className="timeline-item coming-soon">
              <div className="timeline-badge">🚀 Coming Q1 2026</div>
              <div className="timeline-content">
                <h3>Expanding Soon</h3>
                <div className="channels-grid">
                  <div className="channel-item">
                    <span className="channel-icon">📲</span>
                    <span className="channel-name">WhatsApp</span>
                    <span className="channel-stat">2B+ users</span>
                  </div>
                  <div className="channel-item">
                    <span className="channel-icon">✈️</span>
                    <span className="channel-name">Telegram</span>
                    <span className="channel-stat">700M+ users</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="communication-benefits">
            <div className="benefit-card">
              <span className="benefit-icon">📈</span>
              <h4>3x Higher Response Rate</h4>
              <p>Patients respond faster when contacted via their preferred channel</p>
            </div>
            <div className="benefit-card">
              <span className="benefit-icon">💰</span>
              <h4>Lower Cost Per Message</h4>
              <p>WhatsApp & Telegram cost 80% less than SMS</p>
            </div>
            <div className="benefit-card">
              <span className="benefit-icon">🎯</span>
              <h4>Patient Choice</h4>
              <p>Let patients choose their preferred communication method</p>
            </div>
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section id="features" className="features-section">
        <div className="section-container">
          <div className="section-header">
            <h2>Everything Your Clinic Needs</h2>
            <p className="section-subtitle">
              Comprehensive practice management powered by AI
            </p>
          </div>

          <div className="features-grid">
            <div className="feature-card">
              <span className="feature-icon">📅</span>
              <h3>Smart Scheduling</h3>
              <p>AI-powered appointment booking with automatic reminders and rescheduling</p>
            </div>
            <div className="feature-card">
              <span className="feature-icon">💬</span>
              <h3>Patient Communication</h3>
              <p>Multi-channel messaging with intelligent routing and personalization</p>
            </div>
            <div className="feature-card">
              <span className="feature-icon">💰</span>
              <h3>Billing & Payments</h3>
              <p>Automated invoicing, payment tracking, and financial analytics</p>
            </div>
            <div className="feature-card">
              <span className="feature-icon">📊</span>
              <h3>{t("landing.features.analytics.title")}</h3>
              <p>{t("landing.features.analytics.description")}</p>
            </div>
            <div className="feature-card">
              <span className="feature-icon">🔗</span>
              <h3>{t("landing.features.odoo.title")}</h3>
              <p>{t("landing.features.odoo.description")}</p>
            </div>
            <div className="feature-card">
              <span className="feature-icon">🔒</span>
              <h3>{t("landing.features.hipaa.title")}</h3>
              <p>{t("landing.features.hipaa.description")}</p>
            </div>
          </div>
        </div>
      </section>

      {/* Pricing Section - Research-Based */}
      <section id="pricing" className="pricing-section">
        <div className="section-container">
          <div className="section-header">
            <h2>{t("landing.pricingSection.title")}</h2>
            <p className="section-subtitle">
              {t("landing.pricingSection.subtitle")}
            </p>
          </div>

          <div className="pricing-grid">
            <div className={`pricing-card ${selectedPlan === 'starter' ? 'selected' : ''}`}>
              <div className="pricing-header">
                <h3>{t("landing.pricingSection.starter.name")}</h3>
                <div className="pricing-price">
                  <span className="price-currency">₪</span>
                  <span className="price-amount">499</span>
                  <span className="price-period">/month</span>
                </div>
                <p className="pricing-description">{t("landing.pricingSection.starter.description")}</p>
              </div>
              <ul className="pricing-features">
                <li>✓ {t("landing.pricingSection.starter.feature1")}</li>
                <li>✓ {t("landing.pricingSection.starter.feature2")}</li>
                <li>✓ {t("landing.pricingSection.starter.feature3")}</li>
                <li>✓ {t("landing.pricingSection.starter.feature4")}</li>
                <li>✓ {t("landing.pricingSection.starter.feature5")}</li>
              </ul>
              <button 
                className="pricing-cta"
                onClick={() => navigate('/register?plan=starter')}
              >
                {t("landing.pricingSection.cta")}
              </button>
            </div>

            <div className={`pricing-card popular ${selectedPlan === 'professional' ? 'selected' : ''}`}>
              <div className="popular-badge">{t("landing.pricingSection.professional.mostPopular")}</div>
              <div className="pricing-header">
                <h3>{t("landing.pricingSection.professional.name")}</h3>
                <div className="pricing-price">
                  <span className="price-currency">₪</span>
                  <span className="price-amount">799</span>
                  <span className="price-period">/month</span>
                </div>
                <p className="pricing-description">{t("landing.pricingSection.professional.description")}</p>
              </div>
              <ul className="pricing-features">
                <li>✓ {t("landing.pricingSection.professional.feature1")}</li>
                <li>✓ {t("landing.pricingSection.professional.feature2")}</li>
                <li>✓ {t("landing.pricingSection.professional.feature3")}</li>
                <li>✓ {t("landing.pricingSection.professional.feature4")}</li>
                <li>✓ {t("landing.pricingSection.professional.feature5")}</li>
                <li>✓ {t("landing.pricingSection.professional.feature6")}</li>
              </ul>
              <button 
                className="pricing-cta primary"
                onClick={() => navigate('/register?plan=professional')}
              >
                {t("landing.pricingSection.cta")}
              </button>
            </div>

            <div className={`pricing-card ${selectedPlan === 'enterprise' ? 'selected' : ''}`}>
              <div className="pricing-header">
                <h3>{t("landing.pricingSection.enterprise.name")}</h3>
                <div className="pricing-price">
                  <span className="price-currency">₪</span>
                  <span className="price-amount">1,499</span>
                  <span className="price-period">/month</span>
                </div>
                <p className="pricing-description">{t("landing.pricingSection.enterprise.description")}</p>
              </div>
              <ul className="pricing-features">
                <li>✓ {t("landing.pricingSection.enterprise.feature1")}</li>
                <li>✓ {t("landing.pricingSection.professional.feature2")}</li>
                <li>✓ All channels</li>
                <li>✓ {t("landing.pricingSection.enterprise.feature4")}</li>
                <li>✓ {t("landing.pricingSection.enterprise.feature5")}</li>
                <li>✓ {t("landing.pricingSection.enterprise.feature6")}</li>
                <li>✓ {t("landing.pricingSection.enterprise.feature7")}</li>
              </ul>
              <button 
                className="cta"
                onClick={() => navigate('/register?plan=enterprise')}
              >
                Contact Sales
              </button>
            </div>
          </div>

          <div className="pricing-note">
            <p>
              {t("landing.pricingSection.trialNote")}
            </p>
          </div>
        </div>
      </section>

      {/* Pilot Program Section - Research-Based */}
      <section id="pilot" className="pilot-section">
        <div className="section-container">
          <div className="pilot-card">
            <div className="pilot-badge">{t("landing.pilotSection.badge")}</div>
            <h2>{t("landing.pilotSection.title")}</h2>
            <p className="pilot-subtitle">
              {t("landing.pilotSection.subtitle")}
            </p>

            <div className="pilot-benefits">
              <div className="pilot-benefit">
                <span className="pilot-icon">🎁</span>
                <div>
                  <h4>{t("landing.pilotSection.benefit1Title")}</h4>
                  <p>{t("landing.pilotSection.benefit1Desc")}</p>
                </div>
              </div>
              <div className="pilot-benefit">
                <span className="pilot-icon">💎</span>
                <div>
                  <h4>{t("landing.pilotSection.benefit2Title")}</h4>
                  <p>{t("landing.pilotSection.benefit2Desc")}</p>
                </div>
              </div>
              <div className="pilot-benefit">
                <span className="pilot-icon">🤝</span>
                <div>
                  <h4>{t("landing.pilotSection.benefit3Title")}</h4>
                  <p>{t("landing.pilotSection.benefit3Desc")}</p>
                </div>
              </div>
              <div className="pilot-benefit">
                <span className="pilot-icon">🎯</span>
                <div>
                  <h4>{t("landing.pilotSection.benefit4Title")}</h4>
                  <p>{t("landing.pilotSection.benefit4Desc")}</p>
                </div>
              </div>
            </div>

            <div className="pilot-cta-container">
              <button 
                className="pilot-cta"
                onClick={() => navigate('/register?pilot=true')}
              >
                {t("landing.pilotSection.cta")}
              </button>
              <p className="pilot-spots">{t("landing.pilotSection.spotsRemaining")}</p>
            </div>
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section className="faq-section">
        <div className="section-container">
          <div className="section-header">
            <h2>{t("landing.faqSection.title")}</h2>
          </div>

          <div className="faq-grid">
            <div className="faq-item">
              <h4>{t("landing.faqSection.q1")}</h4>
              <p>
                {t("landing.faqSection.a1")}
              </p>
            </div>

            <div className="faq-item">
              <h4>{t("landing.faqSection.q2")}</h4>
              <p>
                {t("landing.faqSection.a2")}
              </p>
            </div>

            <div className="faq-item">
              <h4>{t("landing.faqSection.q3")}</h4>
              <p>
                {t("landing.faqSection.a3")}
              </p>
            </div>

            <div className="faq-item">
              <h4>{t("landing.faqSection.q4")}</h4>
              <p>
                {t("landing.faqSection.a4")}
              </p>
            </div>

            <div className="faq-item">
              <h4>{t("landing.faqSection.q5")}</h4>
              <p>
                {t("landing.faqSection.a5")}
              </p>
            </div>

            <div className="faq-item">
              <h4>{t("landing.faqSection.q6")}</h4>
              <p>
                {t("landing.faqSection.a6")}
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Final CTA Section */}
      <section className="final-cta-section">
        <div className="section-container">
          <h2>{t("landing.finalCta.title")}</h2>
          <p>{t("landing.finalCta.subtitle")}</p>
          <div className="final-ctas">
            <button className="cta-large primary" onClick={() => navigate('/demo')}>
              {t("landing.hero.tryDemo")}
            </button>
            <button className="cta-large secondary" onClick={() => navigate('/register')}>
              {t("landing.pricingSection.cta")}
            </button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="landing-footer">
        <div className="footer-container">
          <div className="footer-grid">
            <div className="footer-col">
              <h4>{t("landing.footerSection.product")}</h4>
              <a href="#features">{t("landing.nav.features")}</a>
              <a href="#agents">{t("landing.footerSection.agents")}</a>
              <a href="#pricing">{t("landing.nav.pricing")}</a>
              <a href="/demo">{t("landing.footerSection.demo")}</a>
            </div>
            <div className="footer-col">
              <h4>{t("landing.footerSection.company")}</h4>
              <a href="#pilot">{t("landing.nav.pilot")}</a>
              <a href="/register">{t("landing.footerSection.startTrial")}</a>
              <a href="mailto:support@dentaflow.ai">{t("landing.footerSection.contact")}</a>
            </div>
            <div className="footer-col">
              <h4>{t("landing.footerSection.legal")}</h4>
              <a href="/legal/terms">{t("landing.footerSection.terms")}</a>
              <a href="/legal/privacy">{t("landing.footerSection.privacy")}</a>
              <a href="/legal/baa">{t("landing.footerSection.baa")}</a>
              <a href="/legal/dpa">{t("landing.footerSection.dpa")}</a>
              <a href="/legal/sla">{t("landing.footerSection.sla")}</a>
            </div>
            <div className="footer-col">
              <h4>{t("landing.footerSection.resources")}</h4>
              <a href="/legal/acceptable-use">{t("landing.footerSection.acceptableUse")}</a>
              <a href="/legal/cookies">{t("landing.footerSection.cookies")}</a>
              <a href="mailto:support@dentaflow.ai">{t("landing.footerSection.support")}</a>
            </div>
          </div>
          <div className="footer-bottom">
            <p>{t("landing.footerSection.copyright")}</p>
            <div className="footer-trust">
              <span>{t("landing.footerSection.hipaaCompliant")}</span>
              <span>{t("landing.footerSection.gdprReady")}</span>
              <span>{t("landing.footerSection.uptime")}</span>
            </div>
          </div>
        </div>
      </footer>

      {/* Demo Chat Button (Floating) */}
      <DemoChatButton />
    </div>
  );
};

export default LandingPage;

