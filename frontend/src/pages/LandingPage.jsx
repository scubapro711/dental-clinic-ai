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
                  <span>{t("landing.whyNotBot.singleAI")}</span>
                </li>
                <li className="comparison-item bad">
                  <span className="item-icon">✗</span>
                  <span>{t("landing.whyNotBot.failsComplex")}</span>
                </li>
                <li className="comparison-item bad">
                  <span className="item-icon">✗</span>
                  <span>{t("landing.whyNotBot.genericResponses")}</span>
                </li>
                <li className="comparison-item bad">
                  <span className="item-icon">✗</span>
                  <span>{t("landing.whyNotBot.noUnderstanding")}</span>
                </li>
                <li className="comparison-item bad">
                  <span className="item-icon">✗</span>
                  <span>{t("landing.whyNotBot.noHandoffs")}</span>
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
                  <span>{t("landing.whyNotBot.specializedAgents")}</span>
                </li>
                <li className="comparison-item good">
                  <span className="item-icon">✓</span>
                  <span>{t("landing.whyNotBot.deepContext")}</span>
                </li>
                <li className="comparison-item good">
                  <span className="item-icon">✓</span>
                  <span>{t("landing.whyNotBot.personalizedResponses")}</span>
                </li>
                <li className="comparison-item good">
                  <span className="item-icon">✓</span>
                  <span>{t("landing.whyNotBot.realOdoo")}</span>
                </li>
                <li className="comparison-item good">
                  <span className="item-icon">✓</span>
                  <span>{t("landing.whyNotBot.seamlessCollaboration")}</span>
                </li>
              </ul>
            </div>
          </div>

          <div className="research-note">
            <span className="research-icon">📚</span>
            <span>
              {t("landing.whyNotBot.researchNote")}
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
                <h3>Alex</h3>
                <p className="agent-card-role">{t("landing.agentsSection.alex.role")}</p>
              </div>
              <ul className="agent-card-features">
                <li>{t("landing.agentsSection.alex.feature1")}</li>
                <li>{t("landing.agentsSection.alex.feature2")}</li>
                <li>{t("landing.agentsSection.alex.feature3")}</li>
                <li>{t("landing.agentsSection.alex.feature4")}</li>
              </ul>
              <div className="agent-card-stat">
                <span className="stat-value">3x</span>
                <span className="stat-label">{t("landing.agentsSection.alex.statLabel")}</span>
              </div>
            </div>

            <div className="agent-card">
              <div className="agent-card-header">
                <span className="agent-card-avatar">👩‍⚕️</span>
                <h3>Sarah</h3>
                <p className="agent-card-role">{t("landing.agentsSection.sarah.role")}</p>
              </div>
              <ul className="agent-card-features">
                <li>{t("landing.agentsSection.sarah.feature1")}</li>
                <li>{t("landing.agentsSection.sarah.feature2")}</li>
                <li>{t("landing.agentsSection.sarah.feature3")}</li>
                <li>{t("landing.agentsSection.sarah.feature4")}</li>
              </ul>
              <div className="agent-card-stat">
                <span className="stat-value">85%</span>
                <span className="stat-label">{t("landing.agentsSection.sarah.statLabel")}</span>
              </div>
            </div>

            <div className="agent-card">
              <div className="agent-card-header">
                <span className="agent-card-avatar">👨‍💼</span>
                <h3>Marcus</h3>
                <p className="agent-card-role">{t("landing.agentsSection.marcus.role")}</p>
              </div>
              <ul className="agent-card-features">
                <li>{t("landing.agentsSection.marcus.feature1")}</li>
                <li>{t("landing.agentsSection.marcus.feature2")}</li>
                <li>{t("landing.agentsSection.marcus.feature3")}</li>
                <li>{t("landing.agentsSection.marcus.feature4")}</li>
              </ul>
              <div className="agent-card-stat">
                <span className="stat-value">₪15K+</span>
                <span className="stat-label">{t("landing.agentsSection.marcus.statLabel")}</span>
              </div>
            </div>

            <div className="agent-card">
              <div className="agent-card-header">
                <span className="agent-card-avatar">👩‍💼</span>
                <h3>Sophia</h3>
                <p className="agent-card-role">{t("landing.agentsSection.sophia.role")}</p>
              </div>
              <ul className="agent-card-features">
                <li>{t("landing.agentsSection.sophia.feature1")}</li>
                <li>{t("landing.agentsSection.sophia.feature2")}</li>
                <li>{t("landing.agentsSection.sophia.feature3")}</li>
                <li>{t("landing.agentsSection.sophia.feature4")}</li>
              </ul>
              <div className="agent-card-stat">
                <span className="stat-value">10h+</span>
                <span className="stat-label">{t("landing.agentsSection.sophia.statLabel")}</span>
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
              <h3>Analytics Dashboard</h3>
              <p>Real-time insights into revenue, patients, and operations</p>
            </div>
            <div className="feature-card">
              <span className="feature-icon">🔗</span>
              <h3>Odoo Integration</h3>
              <p>Seamless connection with your existing Odoo ERP system</p>
            </div>
            <div className="feature-card">
              <span className="feature-icon">🔒</span>
              <h3>HIPAA Compliant</h3>
              <p>Enterprise-grade security with full HIPAA and GDPR compliance</p>
            </div>
          </div>
        </div>
      </section>

      {/* Pricing Section - Research-Based */}
      <section id="pricing" className="pricing-section">
        <div className="section-container">
          <div className="section-header">
            <h2>Simple, Transparent Pricing</h2>
            <p className="section-subtitle">
              Choose the plan that fits your clinic. No hidden fees.
            </p>
          </div>

          <div className="pricing-grid">
            <div className={`pricing-card ${selectedPlan === 'starter' ? 'selected' : ''}`}>
              <div className="pricing-header">
                <h3>Starter</h3>
                <div className="pricing-price">
                  <span className="price-currency">₪</span>
                  <span className="price-amount">499</span>
                  <span className="price-period">/month</span>
                </div>
                <p className="pricing-description">Perfect for small clinics</p>
              </div>
              <ul className="pricing-features">
                <li>✓ Up to 100 patients</li>
                <li>✓ 2 AI agents (Alex + Sarah)</li>
                <li>✓ Web Chat + SMS</li>
                <li>✓ Basic analytics</li>
                <li>✓ Email support</li>
              </ul>
              <button 
                className="pricing-cta"
                onClick={() => navigate('/register?plan=starter')}
              >
                Start Free Trial
              </button>
            </div>

            <div className={`pricing-card popular ${selectedPlan === 'professional' ? 'selected' : ''}`}>
              <div className="popular-badge">Most Popular</div>
              <div className="pricing-header">
                <h3>Professional</h3>
                <div className="pricing-price">
                  <span className="price-currency">₪</span>
                  <span className="price-amount">799</span>
                  <span className="price-period">/month</span>
                </div>
                <p className="pricing-description">For growing practices</p>
              </div>
              <ul className="pricing-features">
                <li>✓ Up to 500 patients</li>
                <li>✓ All 4 AI agents</li>
                <li>✓ All channels (incl. WhatsApp)</li>
                <li>✓ Advanced analytics</li>
                <li>✓ Priority support</li>
                <li>✓ Odoo integration</li>
              </ul>
              <button 
                className="pricing-cta primary"
                onClick={() => navigate('/register?plan=professional')}
              >
                Start Free Trial
              </button>
            </div>

            <div className={`pricing-card ${selectedPlan === 'enterprise' ? 'selected' : ''}`}>
              <div className="pricing-header">
                <h3>Enterprise</h3>
                <div className="pricing-price">
                  <span className="price-currency">₪</span>
                  <span className="price-amount">1,499</span>
                  <span className="price-period">/month</span>
                </div>
                <p className="pricing-description">For large clinics</p>
              </div>
              <ul className="pricing-features">
                <li>✓ Unlimited patients</li>
                <li>✓ All 4 AI agents</li>
                <li>✓ All channels</li>
                <li>✓ Custom analytics</li>
                <li>✓ Dedicated support</li>
                <li>✓ Custom integrations</li>
                <li>✓ SLA guarantee</li>
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
              🎁 <strong>30-day free trial</strong> on all plans. {t("landing.hero.noCredit")} required.
              Cancel anytime.
            </p>
          </div>
        </div>
      </section>

      {/* Pilot Program Section - Research-Based */}
      <section id="pilot" className="pilot-section">
        <div className="section-container">
          <div className="pilot-card">
            <div className="pilot-badge">🌟 Limited Opportunity</div>
            <h2>Join Our Pilot Program</h2>
            <p className="pilot-subtitle">
              Be one of 10 pioneering clinics to shape the future of dental AI
            </p>

            <div className="pilot-benefits">
              <div className="pilot-benefit">
                <span className="pilot-icon">🎁</span>
                <div>
                  <h4>6 Months Completely Free</h4>
                  <p>Full access to all features, zero cost</p>
                </div>
              </div>
              <div className="pilot-benefit">
                <span className="pilot-icon">💎</span>
                <div>
                  <h4>20% Lifetime Discount</h4>
                  <p>After pilot ends, pay 20% less forever</p>
                </div>
              </div>
              <div className="pilot-benefit">
                <span className="pilot-icon">🤝</span>
                <div>
                  <h4>Dedicated Support</h4>
                  <p>Direct line to our team, priority assistance</p>
                </div>
              </div>
              <div className="pilot-benefit">
                <span className="pilot-icon">🎯</span>
                <div>
                  <h4>Shape the Product</h4>
                  <p>Your feedback directly influences development</p>
                </div>
              </div>
            </div>

            <div className="pilot-cta-container">
              <button 
                className="pilot-cta"
                onClick={() => navigate('/register?pilot=true')}
              >
                Apply for Pilot Program
              </button>
              <p className="pilot-spots">⚠️ Only <strong>3 spots remaining</strong> out of 10</p>
            </div>
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section className="faq-section">
        <div className="section-container">
          <div className="section-header">
            <h2>Frequently Asked Questions</h2>
          </div>

          <div className="faq-grid">
            <div className="faq-item">
              <h4>How is this different from a chatbot?</h4>
              <p>
                DentaFlow uses a Multi-Agent AI system with 4 specialized agents, not a single chatbot.
                Each agent is an expert in their domain (patient relations, clinical ops, finance, management)
                and they collaborate seamlessly. Research shows this approach delivers 40% higher quality
                than traditional chatbots.
              </p>
            </div>

            <div className="faq-item">
              <h4>Do I need to change my current system?</h4>
              <p>
                No! DentaFlow integrates seamlessly with Odoo ERP. Your existing data, workflows,
                and processes remain unchanged. We add an AI layer on top.
              </p>
            </div>

            <div className="faq-item">
              <h4>Is my patient data secure?</h4>
              <p>
                Absolutely. We're fully HIPAA compliant and GDPR ready. All data is encrypted in transit
                and at rest. We have a 99.9% uptime SLA and enterprise-grade security.
              </p>
            </div>

            <div className="faq-item">
              <h4>How long does implementation take?</h4>
              <p>
                Most clinics are up and running in 2-3 days. We handle the Odoo integration,
                data migration, and team training. You'll have dedicated support throughout.
              </p>
            </div>

            <div className="faq-item">
              <h4>Can I try before I buy?</h4>
              <p>
                Yes! You can try our Interactive Demo (no signup), start a 30-day free trial
                (no credit card), or apply for our Pilot Program ({t("landing.hero.monthsFree")}). Three ways to
                experience DentaFlow risk-free.
              </p>
            </div>

            <div className="faq-item">
              <h4>What if I need help?</h4>
              <p>
                We offer email support on Starter, priority support on Professional, and dedicated
                support on Enterprise. Pilot program members get direct access to our team.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Final CTA Section */}
      <section className="final-cta-section">
        <div className="section-container">
          <h2>Ready to Transform Your Dental Practice?</h2>
          <p>Join forward-thinking clinics using AI to save time and increase revenue</p>
          <div className="final-ctas">
            <button className="cta-large primary" onClick={() => navigate('/demo')}>
              {t("landing.hero.tryDemo")}
            </button>
            <button className="cta-large secondary" onClick={() => navigate('/register')}>
              Start Free Trial
            </button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="landing-footer">
        <div className="footer-container">
          <div className="footer-grid">
            <div className="footer-col">
              <h4>Product</h4>
              <a href="#features">{t("landing.nav.features")}</a>
              <a href="#agents">AI Agents</a>
              <a href="#pricing">{t("landing.nav.pricing")}</a>
              <a href="/demo">Interactive Demo</a>
            </div>
            <div className="footer-col">
              <h4>Company</h4>
              <a href="#pilot">{t("landing.nav.pilot")}</a>
              <a href="/register">Start Trial</a>
              <a href="mailto:support@dentaflow.ai">Contact</a>
            </div>
            <div className="footer-col">
              <h4>Legal</h4>
              <a href="/legal/terms">Terms of Service</a>
              <a href="/legal/privacy">Privacy Policy</a>
              <a href="/legal/baa">BAA (HIPAA)</a>
              <a href="/legal/dpa">DPA (GDPR)</a>
              <a href="/legal/sla">SLA</a>
            </div>
            <div className="footer-col">
              <h4>Resources</h4>
              <a href="/legal/acceptable-use">Acceptable Use</a>
              <a href="/legal/cookies">Cookie Policy</a>
              <a href="mailto:support@dentaflow.ai">Support</a>
            </div>
          </div>
          <div className="footer-bottom">
            <p>&copy; 2025 DentaFlow. All rights reserved.</p>
            <div className="footer-trust">
              <span>🔒 HIPAA Compliant</span>
              <span>🛡️ GDPR Ready</span>
              <span>✓ 99.9% Uptime</span>
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

