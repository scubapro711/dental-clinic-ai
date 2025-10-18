import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import './PilotApplicationForm.css';

/**
 * Pilot Application Form
 * 
 * Controlled entry to pilot program with qualification questions
 */
const PilotApplicationForm = ({ isOpen, onClose }) => {
  const { t } = useTranslation();
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({
    // Step 1: Basic Info
    clinicName: '',
    contactName: '',
    email: '',
    phone: '',
    
    // Step 2: Clinic Details
    clinicSize: '',
    monthlyPatients: '',
    currentSoftware: '',
    teamSize: '',
    
    // Step 3: AI Readiness
    aiExperience: '',
    primaryGoal: '',
    timeline: '',
    budget: '',
    
    // Step 4: Commitment
    willingToProvideFeedback: false,
    willingToBeReferenced: false,
    agreedToTerms: false
  });
  
  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitSuccess, setSubmitSuccess] = useState(false);

  if (!isOpen) return null;

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
    // Clear error for this field
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const validateStep = (currentStep) => {
    const newErrors = {};
    
    if (currentStep === 1) {
      if (!formData.clinicName.trim()) newErrors.clinicName = t("pilot.form.errors.required");
      if (!formData.contactName.trim()) newErrors.contactName = t("pilot.form.errors.required");
      if (!formData.email.trim()) newErrors.email = t("pilot.form.errors.required");
      else if (!/\S+@\S+\.\S+/.test(formData.email)) newErrors.email = t("pilot.form.errors.invalidEmail");
      if (!formData.phone.trim()) newErrors.phone = t("pilot.form.errors.required");
    }
    
    if (currentStep === 2) {
      if (!formData.clinicSize) newErrors.clinicSize = t("pilot.form.errors.required");
      if (!formData.monthlyPatients) newErrors.monthlyPatients = t("pilot.form.errors.required");
      if (!formData.teamSize) newErrors.teamSize = t("pilot.form.errors.required");
    }
    
    if (currentStep === 3) {
      if (!formData.aiExperience) newErrors.aiExperience = t("pilot.form.errors.required");
      if (!formData.primaryGoal) newErrors.primaryGoal = t("pilot.form.errors.required");
      if (!formData.timeline) newErrors.timeline = t("pilot.form.errors.required");
    }
    
    if (currentStep === 4) {
      if (!formData.agreedToTerms) newErrors.agreedToTerms = t("pilot.form.errors.mustAgree");
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleNext = () => {
    if (validateStep(step)) {
      setStep(step + 1);
    }
  };

  const handleBack = () => {
    setStep(step - 1);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateStep(4)) return;
    
    setIsSubmitting(true);
    
    try {
      // TODO: Send to backend API
      const response = await fetch('/api/v1/pilot-applications', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });
      
      if (response.ok) {
        setSubmitSuccess(true);
        setTimeout(() => {
          onClose();
          setSubmitSuccess(false);
          setStep(1);
          setFormData({
            clinicName: '',
            contactName: '',
            email: '',
            phone: '',
            clinicSize: '',
            monthlyPatients: '',
            currentSoftware: '',
            teamSize: '',
            aiExperience: '',
            primaryGoal: '',
            timeline: '',
            budget: '',
            willingToProvideFeedback: false,
            willingToBeReferenced: false,
            agreedToTerms: false
          });
        }, 3000);
      } else {
        alert(t("pilot.form.errors.submitFailed"));
      }
    } catch (error) {
      console.error('Pilot application submission error:', error);
      alert(t("pilot.form.errors.submitFailed"));
    } finally {
      setIsSubmitting(false);
    }
  };

  const renderStepIndicator = () => (
    <div className="step-indicator">
      {[1, 2, 3, 4].map(num => (
        <div 
          key={num}
          className={`step ${step >= num ? 'active' : ''} ${step > num ? 'completed' : ''}`}
        >
          <div className="step-number">{step > num ? '✓' : num}</div>
          <div className="step-label">
            {num === 1 && t("pilot.form.steps.basicInfo")}
            {num === 2 && t("pilot.form.steps.clinicDetails")}
            {num === 3 && t("pilot.form.steps.aiReadiness")}
            {num === 4 && t("pilot.form.steps.commitment")}
          </div>
        </div>
      ))}
    </div>
  );

  if (submitSuccess) {
    return (
      <div className="pilot-form-overlay" onClick={onClose}>
        <div className="pilot-form-modal success" onClick={e => e.stopPropagation()}>
          <div className="success-icon">✓</div>
          <h2>{t("pilot.form.success.title")}</h2>
          <p>{t("pilot.form.success.message")}</p>
          <p className="success-subtitle">{t("pilot.form.success.subtitle")}</p>
          <button className="btn-primary" onClick={onClose}>
            {t("pilot.form.success.close")}
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="pilot-form-overlay" onClick={onClose}>
      <div className="pilot-form-modal" onClick={e => e.stopPropagation()}>
        <button className="close-btn" onClick={onClose}>✕</button>
        
        <div className="pilot-form-header">
          <h2>{t("pilot.form.title")}</h2>
          <p>{t("pilot.form.subtitle")}</p>
        </div>

        {renderStepIndicator()}

        <form onSubmit={handleSubmit} className="pilot-form">
          {/* Step 1: Basic Info */}
          {step === 1 && (
            <div className="form-step">
              <h3>{t("pilot.form.steps.basicInfo")}</h3>
              
              <div className="form-group">
                <label htmlFor="clinicName">{t("pilot.form.fields.clinicName")} *</label>
                <input
                  type="text"
                  id="clinicName"
                  name="clinicName"
                  value={formData.clinicName}
                  onChange={handleChange}
                  placeholder={t("pilot.form.placeholders.clinicName")}
                  className={errors.clinicName ? 'error' : ''}
                />
                {errors.clinicName && <span className="error-message">{errors.clinicName}</span>}
              </div>

              <div className="form-group">
                <label htmlFor="contactName">{t("pilot.form.fields.contactName")} *</label>
                <input
                  type="text"
                  id="contactName"
                  name="contactName"
                  value={formData.contactName}
                  onChange={handleChange}
                  placeholder={t("pilot.form.placeholders.contactName")}
                  className={errors.contactName ? 'error' : ''}
                />
                {errors.contactName && <span className="error-message">{errors.contactName}</span>}
              </div>

              <div className="form-group">
                <label htmlFor="email">{t("pilot.form.fields.email")} *</label>
                <input
                  type="email"
                  id="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  placeholder={t("pilot.form.placeholders.email")}
                  className={errors.email ? 'error' : ''}
                />
                {errors.email && <span className="error-message">{errors.email}</span>}
              </div>

              <div className="form-group">
                <label htmlFor="phone">{t("pilot.form.fields.phone")} *</label>
                <input
                  type="tel"
                  id="phone"
                  name="phone"
                  value={formData.phone}
                  onChange={handleChange}
                  placeholder={t("pilot.form.placeholders.phone")}
                  className={errors.phone ? 'error' : ''}
                />
                {errors.phone && <span className="error-message">{errors.phone}</span>}
              </div>
            </div>
          )}

          {/* Step 2: Clinic Details */}
          {step === 2 && (
            <div className="form-step">
              <h3>{t("pilot.form.steps.clinicDetails")}</h3>
              
              <div className="form-group">
                <label htmlFor="clinicSize">{t("pilot.form.fields.clinicSize")} *</label>
                <select
                  id="clinicSize"
                  name="clinicSize"
                  value={formData.clinicSize}
                  onChange={handleChange}
                  className={errors.clinicSize ? 'error' : ''}
                >
                  <option value="">{t("pilot.form.placeholders.select")}</option>
                  <option value="solo">{t("pilot.form.options.clinicSize.solo")}</option>
                  <option value="small">{t("pilot.form.options.clinicSize.small")}</option>
                  <option value="medium">{t("pilot.form.options.clinicSize.medium")}</option>
                  <option value="large">{t("pilot.form.options.clinicSize.large")}</option>
                </select>
                {errors.clinicSize && <span className="error-message">{errors.clinicSize}</span>}
              </div>

              <div className="form-group">
                <label htmlFor="monthlyPatients">{t("pilot.form.fields.monthlyPatients")} *</label>
                <select
                  id="monthlyPatients"
                  name="monthlyPatients"
                  value={formData.monthlyPatients}
                  onChange={handleChange}
                  className={errors.monthlyPatients ? 'error' : ''}
                >
                  <option value="">{t("pilot.form.placeholders.select")}</option>
                  <option value="0-50">{t("pilot.form.options.monthlyPatients.range1")}</option>
                  <option value="51-200">{t("pilot.form.options.monthlyPatients.range2")}</option>
                  <option value="201-500">{t("pilot.form.options.monthlyPatients.range3")}</option>
                  <option value="500+">{t("pilot.form.options.monthlyPatients.range4")}</option>
                </select>
                {errors.monthlyPatients && <span className="error-message">{errors.monthlyPatients}</span>}
              </div>

              <div className="form-group">
                <label htmlFor="currentSoftware">{t("pilot.form.fields.currentSoftware")}</label>
                <input
                  type="text"
                  id="currentSoftware"
                  name="currentSoftware"
                  value={formData.currentSoftware}
                  onChange={handleChange}
                  placeholder={t("pilot.form.placeholders.currentSoftware")}
                />
              </div>

              <div className="form-group">
                <label htmlFor="teamSize">{t("pilot.form.fields.teamSize")} *</label>
                <select
                  id="teamSize"
                  name="teamSize"
                  value={formData.teamSize}
                  onChange={handleChange}
                  className={errors.teamSize ? 'error' : ''}
                >
                  <option value="">{t("pilot.form.placeholders.select")}</option>
                  <option value="1-3">{t("pilot.form.options.teamSize.range1")}</option>
                  <option value="4-10">{t("pilot.form.options.teamSize.range2")}</option>
                  <option value="11-25">{t("pilot.form.options.teamSize.range3")}</option>
                  <option value="25+">{t("pilot.form.options.teamSize.range4")}</option>
                </select>
                {errors.teamSize && <span className="error-message">{errors.teamSize}</span>}
              </div>
            </div>
          )}

          {/* Step 3: AI Readiness */}
          {step === 3 && (
            <div className="form-step">
              <h3>{t("pilot.form.steps.aiReadiness")}</h3>
              
              <div className="form-group">
                <label htmlFor="aiExperience">{t("pilot.form.fields.aiExperience")} *</label>
                <select
                  id="aiExperience"
                  name="aiExperience"
                  value={formData.aiExperience}
                  onChange={handleChange}
                  className={errors.aiExperience ? 'error' : ''}
                >
                  <option value="">{t("pilot.form.placeholders.select")}</option>
                  <option value="none">{t("pilot.form.options.aiExperience.none")}</option>
                  <option value="basic">{t("pilot.form.options.aiExperience.basic")}</option>
                  <option value="intermediate">{t("pilot.form.options.aiExperience.intermediate")}</option>
                  <option value="advanced">{t("pilot.form.options.aiExperience.advanced")}</option>
                </select>
                {errors.aiExperience && <span className="error-message">{errors.aiExperience}</span>}
              </div>

              <div className="form-group">
                <label htmlFor="primaryGoal">{t("pilot.form.fields.primaryGoal")} *</label>
                <select
                  id="primaryGoal"
                  name="primaryGoal"
                  value={formData.primaryGoal}
                  onChange={handleChange}
                  className={errors.primaryGoal ? 'error' : ''}
                >
                  <option value="">{t("pilot.form.placeholders.select")}</option>
                  <option value="efficiency">{t("pilot.form.options.primaryGoal.efficiency")}</option>
                  <option value="patient-experience">{t("pilot.form.options.primaryGoal.patientExperience")}</option>
                  <option value="revenue">{t("pilot.form.options.primaryGoal.revenue")}</option>
                  <option value="automation">{t("pilot.form.options.primaryGoal.automation")}</option>
                </select>
                {errors.primaryGoal && <span className="error-message">{errors.primaryGoal}</span>}
              </div>

              <div className="form-group">
                <label htmlFor="timeline">{t("pilot.form.fields.timeline")} *</label>
                <select
                  id="timeline"
                  name="timeline"
                  value={formData.timeline}
                  onChange={handleChange}
                  className={errors.timeline ? 'error' : ''}
                >
                  <option value="">{t("pilot.form.placeholders.select")}</option>
                  <option value="immediate">{t("pilot.form.options.timeline.immediate")}</option>
                  <option value="1-3-months">{t("pilot.form.options.timeline.range1")}</option>
                  <option value="3-6-months">{t("pilot.form.options.timeline.range2")}</option>
                  <option value="6+-months">{t("pilot.form.options.timeline.range3")}</option>
                </select>
                {errors.timeline && <span className="error-message">{errors.timeline}</span>}
              </div>

              <div className="form-group">
                <label htmlFor="budget">{t("pilot.form.fields.budget")}</label>
                <select
                  id="budget"
                  name="budget"
                  value={formData.budget}
                  onChange={handleChange}
                >
                  <option value="">{t("pilot.form.placeholders.select")}</option>
                  <option value="0-500">{t("pilot.form.options.budget.range1")}</option>
                  <option value="500-1000">{t("pilot.form.options.budget.range2")}</option>
                  <option value="1000-2500">{t("pilot.form.options.budget.range3")}</option>
                  <option value="2500+">{t("pilot.form.options.budget.range4")}</option>
                </select>
              </div>
            </div>
          )}

          {/* Step 4: Commitment */}
          {step === 4 && (
            <div className="form-step">
              <h3>{t("pilot.form.steps.commitment")}</h3>
              
              <div className="commitment-info">
                <p>{t("pilot.form.commitmentInfo")}</p>
              </div>

              <div className="form-group checkbox-group">
                <label>
                  <input
                    type="checkbox"
                    name="willingToProvideFeedback"
                    checked={formData.willingToProvideFeedback}
                    onChange={handleChange}
                  />
                  <span>{t("pilot.form.fields.provideFeedback")}</span>
                </label>
              </div>

              <div className="form-group checkbox-group">
                <label>
                  <input
                    type="checkbox"
                    name="willingToBeReferenced"
                    checked={formData.willingToBeReferenced}
                    onChange={handleChange}
                  />
                  <span>{t("pilot.form.fields.beReferenced")}</span>
                </label>
              </div>

              <div className="form-group checkbox-group">
                <label>
                  <input
                    type="checkbox"
                    name="agreedToTerms"
                    checked={formData.agreedToTerms}
                    onChange={handleChange}
                    className={errors.agreedToTerms ? 'error' : ''}
                  />
                  <span>{t("pilot.form.fields.agreeToTerms")} *</span>
                </label>
                {errors.agreedToTerms && <span className="error-message">{errors.agreedToTerms}</span>}
              </div>

              <div className="pilot-benefits-summary">
                <h4>{t("pilot.form.benefitsSummary.title")}</h4>
                <ul>
                  <li>✓ {t("pilot.form.benefitsSummary.benefit1")}</li>
                  <li>✓ {t("pilot.form.benefitsSummary.benefit2")}</li>
                  <li>✓ {t("pilot.form.benefitsSummary.benefit3")}</li>
                  <li>✓ {t("pilot.form.benefitsSummary.benefit4")}</li>
                </ul>
              </div>
            </div>
          )}

          <div className="form-actions">
            {step > 1 && (
              <button type="button" className="btn-secondary" onClick={handleBack}>
                {t("pilot.form.buttons.back")}
              </button>
            )}
            {step < 4 ? (
              <button type="button" className="btn-primary" onClick={handleNext}>
                {t("pilot.form.buttons.next")}
              </button>
            ) : (
              <button 
                type="submit" 
                className="btn-primary" 
                disabled={isSubmitting}
              >
                {isSubmitting ? t("pilot.form.buttons.submitting") : t("pilot.form.buttons.submit")}
              </button>
            )}
          </div>
        </form>
      </div>
    </div>
  );
};

export default PilotApplicationForm;

