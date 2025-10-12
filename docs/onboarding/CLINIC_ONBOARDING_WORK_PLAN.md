# 🏥 תוכנית עבודה: תהליך הרשמת מרפאות (Clinic Onboarding)

**תאריך:** 8 באוקטובר 2025  
**סטטוס:** 🔴 טרם הושלם  
**עדיפות:** 🔴 קריטי למערכת SaaS

---

## 📊 סטטוס נוכחי

### ✅ מה שקיים

| רכיב | סטטוס | הערות |
|------|--------|-------|
| **User Registration** | ✅ חלקי | קיים endpoint `/auth/register` אבל בסיסי מאוד |
| **Organization Model** | ✅ קיים | טבלת organizations עם subscription tiers |
| **Organization Memberships** | ✅ קיים | קישור בין users ל-organizations |
| **Clinic Settings** | ✅ קיים | הגדרות מרפאה (שעות, מחירים) |
| **Treatment Prices** | ✅ קיים | מחירון טיפולים |

### ❌ מה שחסר

| רכיב | סטטוס | השפעה |
|------|--------|--------|
| **תהליך הרשמה מלא** | ❌ חסר | אי אפשר להירשם כמרפאה חדשה |
| **BAA Electronic Signature** | ❌ חסר | דרישה משפטית של HIPAA |
| **Organization Creation Flow** | ❌ חסר | אין API ליצירת מרפאה |
| **Initial Setup Wizard** | ❌ חסר | אין הדרכה למשתמש חדש |
| **Email Verification** | ❌ חסר | אין אימות אימייל |
| **Invitation System** | ❌ חסר | אין אפשרות להזמין צוות |
| **Onboarding Dashboard** | ❌ חסר | אין ממשק הרשמה |

---

## 🎯 מטרות

1. **ליצור תהליך הרשמה מלא** למרפאות חדשות
2. **לוודא תאימות HIPAA** עם חתימה על BAA
3. **להקל על המשתמש** עם wizard מונחה
4. **לאפשר הזמנת צוות** למרפאה
5. **לאמת זהות** דרך אימייל

---

## 📋 תוכנית עבודה - 5 קומפוננטות

### 📦 קומפוננטה 1: Organization Registration API

**זמן:** 2 ימים  
**עדיפות:** 🔴 קריטי

#### משימות:

**1.1. יצירת API Endpoint להרשמת מרפאה**

```python
# backend/app/api/v1/endpoints/organizations.py

@router.post("/organizations/register", response_model=OrganizationResponse)
async def register_organization(
    org_data: OrganizationRegisterRequest,
    db: Session = Depends(get_db)
):
    """
    Register a new dental clinic organization.
    
    Steps:
    1. Create organization
    2. Create owner user
    3. Create membership (owner role)
    4. Create default clinic settings
    5. Seed default treatment prices
    6. Send verification email
    7. Return organization + temporary access token
    """
    
    # 1. Validate email not already registered
    existing_user = db.query(User).filter(User.email == org_data.owner_email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # 2. Validate organization slug is unique
    slug = generate_slug(org_data.clinic_name)
    existing_org = db.query(Organization).filter(Organization.slug == slug).first()
    if existing_org:
        slug = f"{slug}-{uuid4().hex[:6]}"
    
    # 3. Create organization
    organization = Organization(
        name=org_data.clinic_name,
        slug=slug,
        email=org_data.clinic_email,
        phone=org_data.clinic_phone,
        address=org_data.clinic_address,
        subscription_tier=SubscriptionTier.BASIC,  # Start with free tier
        subscription_status="trial",  # 30-day trial
        subscription_start_date=datetime.utcnow(),
        subscription_end_date=datetime.utcnow() + timedelta(days=30)
    )
    db.add(organization)
    db.flush()
    
    # 4. Create owner user
    hashed_password = get_password_hash(org_data.owner_password)
    owner = User(
        email=org_data.owner_email,
        hashed_password=hashed_password,
        full_name=org_data.owner_name,
        phone=org_data.owner_phone,
        role=UserRole.OWNER,
        organization_id=organization.id,  # Legacy field
        is_active=False,  # Will be activated after email verification
        email_verified=False
    )
    db.add(owner)
    db.flush()
    
    # 5. Create membership
    membership = OrganizationMembership(
        user_id=owner.id,
        organization_id=organization.id,
        organization_role="owner",
        functional_role="administrator",
        is_active=True
    )
    db.add(membership)
    
    # 6. Create default clinic settings
    settings = ClinicSettings(
        organization_id=organization.id,
        **DEFAULT_ISRAELI_CLINIC_SETTINGS
    )
    db.add(settings)
    
    # 7. Seed default treatment prices
    for treatment in DEFAULT_ISRAELI_TREATMENT_PRICES:
        price = TreatmentPrice(
            organization_id=organization.id,
            treatment_code=treatment["code"],
            treatment_name=treatment["name"],
            category=treatment["category"],
            price=treatment["price"],
            duration_minutes=treatment["duration"]
        )
        db.add(price)
    
    db.commit()
    db.refresh(organization)
    
    # 8. Send verification email
    verification_token = generate_verification_token(owner.email)
    send_verification_email(owner.email, owner.full_name, verification_token)
    
    # 9. Return response
    return {
        "organization": organization,
        "owner": owner,
        "message": "Organization registered successfully. Please check your email to verify your account."
    }
```

**1.2. Schema להרשמה**

```python
# backend/app/schemas/organization.py

class OrganizationRegisterRequest(BaseModel):
    # Clinic info
    clinic_name: str = Field(..., min_length=2, max_length=255)
    clinic_email: EmailStr
    clinic_phone: str = Field(..., regex=r"^05\d{8}$")  # Israeli mobile
    clinic_address: str = Field(..., min_length=10)
    
    # Owner info
    owner_name: str = Field(..., min_length=2, max_length=255)
    owner_email: EmailStr
    owner_phone: str = Field(..., regex=r"^05\d{8}$")
    owner_password: str = Field(..., min_length=8)
    
    # Terms acceptance
    terms_accepted: bool = Field(..., description="Must be true")
    privacy_accepted: bool = Field(..., description="Must be true")
    
    @validator('terms_accepted', 'privacy_accepted')
    def must_be_true(cls, v):
        if not v:
            raise ValueError('Must accept terms and privacy policy')
        return v
```

**קבצים ליצור/עדכן:**
- ✅ `backend/app/api/v1/endpoints/organizations.py`
- ✅ `backend/app/schemas/organization.py`
- ✅ `backend/app/services/organization_service.py`
- ✅ `backend/tests/test_organization_registration.py`

---

### 📦 קומפוננטה 2: Email Verification System

**זמן:** 1 יום  
**עדיפות:** 🔴 קריטי

#### משימות:

**2.1. טבלת Verification Tokens**

```python
# alembic/versions/XXXXX_add_email_verification_tokens.py

def upgrade():
    op.create_table(
        'email_verification_tokens',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('token', sa.String(255), nullable=False, unique=True),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('verified_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_index('ix_verification_token', 'email_verification_tokens', ['token'])
```

**2.2. API Endpoints**

```python
# backend/app/api/v1/endpoints/verification.py

@router.get("/verify-email")
async def verify_email(token: str, db: Session = Depends(get_db)):
    """
    Verify user email address.
    
    - **token**: Verification token from email
    """
    # Find token
    verification = db.query(EmailVerificationToken).filter(
        EmailVerificationToken.token == token,
        EmailVerificationToken.verified_at.is_(None),
        EmailVerificationToken.expires_at > datetime.utcnow()
    ).first()
    
    if not verification:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    
    # Mark as verified
    verification.verified_at = datetime.utcnow()
    
    # Activate user
    user = db.query(User).filter(User.id == verification.user_id).first()
    user.is_active = True
    user.email_verified = True
    
    db.commit()
    
    return {"message": "Email verified successfully. You can now log in."}


@router.post("/resend-verification")
async def resend_verification(email: EmailStr, db: Session = Depends(get_db)):
    """Resend verification email."""
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        # Don't reveal if email exists
        return {"message": "If email exists, verification email was sent"}
    
    if user.email_verified:
        raise HTTPException(status_code=400, detail="Email already verified")
    
    # Generate new token
    token = generate_verification_token(user.email)
    send_verification_email(user.email, user.full_name, token)
    
    return {"message": "Verification email sent"}
```

**2.3. Email Templates**

```python
# backend/app/services/email_service.py

def send_verification_email(email: str, name: str, token: str):
    """Send email verification link."""
    verification_url = f"{settings.FRONTEND_URL}/verify-email?token={token}"
    
    html_content = f"""
    <!DOCTYPE html>
    <html dir="rtl" lang="he">
    <head>
        <meta charset="UTF-8">
        <title>אימות כתובת אימייל - DentaFlow</title>
    </head>
    <body style="font-family: Arial, sans-serif; direction: rtl; text-align: right;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <h1 style="color: #2563eb;">ברוך הבא ל-DentaFlow! 🦷</h1>
            
            <p>שלום {name},</p>
            
            <p>תודה שנרשמת ל-DentaFlow. כדי להשלים את ההרשמה, אנא אמת את כתובת האימייל שלך:</p>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{verification_url}" 
                   style="background-color: #2563eb; color: white; padding: 12px 30px; 
                          text-decoration: none; border-radius: 5px; display: inline-block;">
                    אמת אימייל
                </a>
            </div>
            
            <p>או העתק את הקישור הבא לדפדפן:</p>
            <p style="background-color: #f3f4f6; padding: 10px; word-break: break-all;">
                {verification_url}
            </p>
            
            <p style="color: #6b7280; font-size: 14px;">
                הקישור תקף ל-24 שעות.
            </p>
            
            <hr style="margin: 30px 0; border: none; border-top: 1px solid #e5e7eb;">
            
            <p style="color: #6b7280; font-size: 12px;">
                אם לא ביקשת להירשם ל-DentaFlow, אנא התעלם ממייל זה.
            </p>
        </div>
    </body>
    </html>
    """
    
    send_email(
        to=email,
        subject="אימות כתובת אימייל - DentaFlow",
        html_content=html_content
    )
```

**קבצים ליצור/עדכן:**
- ✅ `alembic/versions/XXXXX_add_email_verification_tokens.py`
- ✅ `backend/app/models/email_verification_token.py`
- ✅ `backend/app/api/v1/endpoints/verification.py`
- ✅ `backend/app/services/email_service.py`
- ✅ `backend/tests/test_email_verification.py`

---

### 📦 קומפוננטה 3: BAA Electronic Signature System

**זמן:** 2 ימים  
**עדיפות:** 🔴 קריטי (HIPAA)

#### משימות:

**3.1. טבלת BAA Signatures**

```python
# alembic/versions/XXXXX_add_baa_signatures_table.py

def upgrade():
    op.create_table(
        'baa_signatures',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('organization_id', sa.UUID(), nullable=False, unique=True),
        
        # Signatory details
        sa.Column('signatory_name', sa.String(255), nullable=False),
        sa.Column('signatory_email', sa.String(255), nullable=False),
        sa.Column('signatory_title', sa.String(100), nullable=False),
        
        # Agreement details
        sa.Column('baa_version', sa.String(20), nullable=False),
        sa.Column('baa_text_hash', sa.String(64), nullable=False),
        
        # Signature metadata
        sa.Column('ip_address', sa.String(45), nullable=False),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('signed_at', sa.DateTime(), nullable=False),
        
        # Legal compliance
        sa.Column('consent_checkbox', sa.Boolean(), nullable=False),
        sa.Column('electronic_signature_consent', sa.Boolean(), nullable=False),
        
        # Audit
        sa.Column('created_at', sa.DateTime(), nullable=False),
        
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
```

**3.2. API Endpoints**

```python
# backend/app/api/v1/endpoints/baa.py

@router.get("/baa/text")
async def get_baa_text():
    """Get current BAA text for display."""
    with open("backend/docs/legal/BUSINESS_ASSOCIATE_AGREEMENT.md", "r") as f:
        baa_text = f.read()
    
    return {
        "version": "1.0",
        "text": baa_text,
        "hash": hashlib.sha256(baa_text.encode()).hexdigest()
    }


@router.post("/organizations/{org_id}/sign-baa")
async def sign_baa(
    org_id: UUID,
    signature_data: BAASignatureCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Sign the Business Associate Agreement.
    
    Requirements:
    - User must be organization owner
    - Organization must not have existing signature
    - All consent checkboxes must be checked
    """
    # 1. Verify user is owner
    membership = db.query(OrganizationMembership).filter(
        OrganizationMembership.organization_id == org_id,
        OrganizationMembership.user_id == current_user.id,
        OrganizationMembership.organization_role == "owner"
    ).first()
    
    if not membership:
        raise HTTPException(status_code=403, detail="Only organization owner can sign BAA")
    
    # 2. Check if already signed
    existing = db.query(BAASignature).filter(
        BAASignature.organization_id == org_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="BAA already signed")
    
    # 3. Get current BAA text
    with open("backend/docs/legal/BUSINESS_ASSOCIATE_AGREEMENT.md", "r") as f:
        baa_text = f.read()
    baa_hash = hashlib.sha256(baa_text.encode()).hexdigest()
    
    # 4. Create signature record
    signature = BAASignature(
        organization_id=org_id,
        signatory_name=signature_data.name,
        signatory_email=signature_data.email,
        signatory_title=signature_data.title,
        baa_version="1.0",
        baa_text_hash=baa_hash,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent"),
        signed_at=datetime.utcnow(),
        consent_checkbox=True,
        electronic_signature_consent=True
    )
    
    db.add(signature)
    db.commit()
    db.refresh(signature)
    
    # 5. Generate signed PDF
    pdf_path = generate_signed_baa_pdf(signature, baa_text)
    
    # 6. Send confirmation email
    send_baa_confirmation_email(
        email=signature.signatory_email,
        name=signature.signatory_name,
        pdf_path=pdf_path
    )
    
    return {
        "message": "BAA signed successfully",
        "signature_id": signature.id,
        "signed_at": signature.signed_at
    }


@router.get("/organizations/{org_id}/baa-status")
async def get_baa_status(
    org_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Check if organization has signed BAA."""
    signature = db.query(BAASignature).filter(
        BAASignature.organization_id == org_id
    ).first()
    
    if not signature:
        return {"signed": False}
    
    return {
        "signed": True,
        "signed_at": signature.signed_at,
        "signatory_name": signature.signatory_name,
        "version": signature.baa_version
    }
```

**3.3. PDF Generation**

```python
# backend/app/services/pdf_service.py

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

def generate_signed_baa_pdf(signature: BAASignature, baa_text: str) -> str:
    """Generate signed BAA PDF."""
    filename = f"BAA_{signature.organization_id}_{signature.signed_at.strftime('%Y%m%d')}.pdf"
    filepath = f"/tmp/{filename}"
    
    doc = SimpleDocTemplate(filepath, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
    # Title
    story.append(Paragraph("Business Associate Agreement", styles['Title']))
    story.append(Spacer(1, 12))
    
    # BAA text
    for paragraph in baa_text.split('\n\n'):
        story.append(Paragraph(paragraph, styles['Normal']))
        story.append(Spacer(1, 6))
    
    # Signature block
    story.append(Spacer(1, 24))
    story.append(Paragraph("<b>ELECTRONICALLY SIGNED</b>", styles['Heading2']))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"Signatory: {signature.signatory_name}", styles['Normal']))
    story.append(Paragraph(f"Title: {signature.signatory_title}", styles['Normal']))
    story.append(Paragraph(f"Email: {signature.signatory_email}", styles['Normal']))
    story.append(Paragraph(f"Date: {signature.signed_at.strftime('%B %d, %Y at %H:%M UTC')}", styles['Normal']))
    story.append(Paragraph(f"IP Address: {signature.ip_address}", styles['Normal']))
    
    doc.build(story)
    
    return filepath
```

**קבצים ליצור/עדכן:**
- ✅ `alembic/versions/XXXXX_add_baa_signatures_table.py`
- ✅ `backend/app/models/baa_signature.py`
- ✅ `backend/app/api/v1/endpoints/baa.py`
- ✅ `backend/app/services/pdf_service.py`
- ✅ `backend/tests/test_baa_signature.py`

---

### 📦 קומפוננטה 4: Team Invitation System

**זמן:** 2 ימים  
**עדיפות:** 🟡 גבוה

#### משימות:

**4.1. טבלת Invitations**

```python
# alembic/versions/XXXXX_add_invitations_table.py

def upgrade():
    op.create_table(
        'invitations',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('organization_id', sa.UUID(), nullable=False),
        sa.Column('invited_by_user_id', sa.UUID(), nullable=False),
        
        # Invitee details
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('organization_role', sa.String(50), nullable=False),
        sa.Column('functional_role', sa.String(50), nullable=True),
        
        # Token
        sa.Column('token', sa.String(255), nullable=False, unique=True),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        
        # Status
        sa.Column('status', sa.String(20), nullable=False, default='pending'),  # pending, accepted, expired
        sa.Column('accepted_at', sa.DateTime(), nullable=True),
        sa.Column('accepted_by_user_id', sa.UUID(), nullable=True),
        
        # Timestamps
        sa.Column('created_at', sa.DateTime(), nullable=False),
        
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['invited_by_user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['accepted_by_user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
```

**4.2. API Endpoints**

```python
# backend/app/api/v1/endpoints/invitations.py

@router.post("/organizations/{org_id}/invitations")
async def invite_team_member(
    org_id: UUID,
    invitation_data: InvitationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Invite a team member to join the organization.
    
    Roles:
    - owner: Full access
    - manager: Manage staff and patients
    - staff: Limited access (dentist, hygienist, receptionist)
    """
    # 1. Verify user has permission to invite
    membership = db.query(OrganizationMembership).filter(
        OrganizationMembership.organization_id == org_id,
        OrganizationMembership.user_id == current_user.id,
        OrganizationMembership.organization_role.in_(["owner", "manager"])
    ).first()
    
    if not membership:
        raise HTTPException(status_code=403, detail="Only owners and managers can invite")
    
    # 2. Check if user already exists in organization
    existing_user = db.query(User).filter(User.email == invitation_data.email).first()
    if existing_user:
        existing_membership = db.query(OrganizationMembership).filter(
            OrganizationMembership.user_id == existing_user.id,
            OrganizationMembership.organization_id == org_id
        ).first()
        
        if existing_membership:
            raise HTTPException(status_code=400, detail="User already member of organization")
    
    # 3. Check for pending invitation
    pending = db.query(Invitation).filter(
        Invitation.email == invitation_data.email,
        Invitation.organization_id == org_id,
        Invitation.status == "pending",
        Invitation.expires_at > datetime.utcnow()
    ).first()
    
    if pending:
        raise HTTPException(status_code=400, detail="Invitation already sent")
    
    # 4. Create invitation
    token = secrets.token_urlsafe(32)
    invitation = Invitation(
        organization_id=org_id,
        invited_by_user_id=current_user.id,
        email=invitation_data.email,
        organization_role=invitation_data.role,
        functional_role=invitation_data.functional_role,
        token=token,
        expires_at=datetime.utcnow() + timedelta(days=7),
        status="pending"
    )
    
    db.add(invitation)
    db.commit()
    db.refresh(invitation)
    
    # 5. Send invitation email
    organization = db.query(Organization).filter(Organization.id == org_id).first()
    send_invitation_email(
        email=invitation_data.email,
        organization_name=organization.name,
        invited_by=current_user.full_name,
        token=token
    )
    
    return invitation


@router.post("/invitations/{token}/accept")
async def accept_invitation(
    token: str,
    user_data: InvitationAcceptRequest,
    db: Session = Depends(get_db)
):
    """Accept an invitation and join the organization."""
    # 1. Find invitation
    invitation = db.query(Invitation).filter(
        Invitation.token == token,
        Invitation.status == "pending",
        Invitation.expires_at > datetime.utcnow()
    ).first()
    
    if not invitation:
        raise HTTPException(status_code=400, detail="Invalid or expired invitation")
    
    # 2. Check if user exists
    user = db.query(User).filter(User.email == invitation.email).first()
    
    if not user:
        # Create new user
        hashed_password = get_password_hash(user_data.password)
        user = User(
            email=invitation.email,
            hashed_password=hashed_password,
            full_name=user_data.full_name,
            phone=user_data.phone,
            role=UserRole.STAFF,
            organization_id=invitation.organization_id,
            is_active=True,
            email_verified=True  # Email verified through invitation
        )
        db.add(user)
        db.flush()
    
    # 3. Create membership
    membership = OrganizationMembership(
        user_id=user.id,
        organization_id=invitation.organization_id,
        organization_role=invitation.organization_role,
        functional_role=invitation.functional_role,
        is_active=True
    )
    db.add(membership)
    
    # 4. Mark invitation as accepted
    invitation.status = "accepted"
    invitation.accepted_at = datetime.utcnow()
    invitation.accepted_by_user_id = user.id
    
    db.commit()
    
    return {"message": "Invitation accepted successfully"}
```

**קבצים ליצור/עדכן:**
- ✅ `alembic/versions/XXXXX_add_invitations_table.py`
- ✅ `backend/app/models/invitation.py`
- ✅ `backend/app/api/v1/endpoints/invitations.py`
- ✅ `backend/tests/test_invitations.py`

---

### 📦 קומפוננטה 5: Onboarding Frontend (React)

**זמן:** 3 ימים  
**עדיפות:** 🟡 גבוה

#### משימות:

**5.1. Registration Wizard**

```typescript
// frontend/src/pages/Onboarding/RegistrationWizard.tsx

const RegistrationWizard = () => {
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({
    // Clinic info
    clinicName: '',
    clinicEmail: '',
    clinicPhone: '',
    clinicAddress: '',
    
    // Owner info
    ownerName: '',
    ownerEmail: '',
    ownerPhone: '',
    ownerPassword: '',
    
    // Terms
    termsAccepted: false,
    privacyAccepted: false,
  });
  
  const steps = [
    { id: 1, title: 'פרטי המרפאה', component: ClinicInfoStep },
    { id: 2, title: 'פרטי בעל המרפאה', component: OwnerInfoStep },
    { id: 3, title: 'תנאי שימוש', component: TermsStep },
    { id: 4, title: 'אישור', component: ConfirmationStep },
  ];
  
  const handleNext = () => setStep(step + 1);
  const handleBack = () => setStep(step - 1);
  
  const handleSubmit = async () => {
    try {
      const response = await api.post('/organizations/register', formData);
      
      // Show success message
      message.success('הרשמה הצליחה! אנא בדוק את האימייל שלך לאימות.');
      
      // Redirect to email verification page
      navigate('/verify-email-sent');
    } catch (error) {
      message.error('שגיאה בהרשמה: ' + error.response.data.detail);
    }
  };
  
  const CurrentStepComponent = steps[step - 1].component;
  
  return (
    <div className="registration-wizard">
      <Steps current={step - 1} direction="horizontal">
        {steps.map(s => (
          <Step key={s.id} title={s.title} />
        ))}
      </Steps>
      
      <div className="step-content">
        <CurrentStepComponent 
          data={formData}
          onChange={setFormData}
        />
      </div>
      
      <div className="step-actions">
        {step > 1 && (
          <Button onClick={handleBack}>חזור</Button>
        )}
        
        {step < steps.length && (
          <Button type="primary" onClick={handleNext}>הבא</Button>
        )}
        
        {step === steps.length && (
          <Button type="primary" onClick={handleSubmit}>הירשם</Button>
        )}
      </div>
    </div>
  );
};
```

**5.2. BAA Signature Modal**

```typescript
// frontend/src/components/BAA/BAASignatureModal.tsx

const BAASignatureModal = ({ organizationId, visible, onSuccess, onCancel }) => {
  const [baaText, setBaaText] = useState('');
  const [agreed, setAgreed] = useState(false);
  const [loading, setLoading] = useState(false);
  const [form] = Form.useForm();
  
  useEffect(() => {
    if (visible) {
      loadBAAText();
    }
  }, [visible]);
  
  const loadBAAText = async () => {
    const response = await api.get('/baa/text');
    setBaaText(response.data.text);
  };
  
  const handleSign = async (values) => {
    setLoading(true);
    
    try {
      await api.post(`/organizations/${organizationId}/sign-baa`, {
        name: values.name,
        title: values.title,
        email: values.email,
      });
      
      message.success('ההסכם נחתם בהצלחה!');
      onSuccess();
    } catch (error) {
      message.error('שגיאה בחתימה: ' + error.response.data.detail);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <Modal
      title="הסכם שותף עסקי (BAA)"
      visible={visible}
      onCancel={onCancel}
      width={800}
      footer={null}
    >
      <div className="baa-content">
        {/* BAA text - scrollable */}
        <div 
          className="baa-text" 
          style={{
            height: '400px',
            overflow: 'auto',
            border: '1px solid #d9d9d9',
            padding: '16px',
            marginBottom: '24px',
            backgroundColor: '#fafafa'
          }}
        >
          <ReactMarkdown>{baaText}</ReactMarkdown>
        </div>
        
        {/* Consent checkbox */}
        <Checkbox 
          checked={agreed}
          onChange={(e) => setAgreed(e.target.checked)}
          style={{ marginBottom: '24px' }}
        >
          קראתי והסכמתי לתנאי הסכם השותף העסקי
        </Checkbox>
        
        {/* Signature form */}
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSign}
        >
          <Form.Item
            name="name"
            label="שם מלא"
            rules={[{ required: true, message: 'נא להזין שם מלא' }]}
          >
            <Input placeholder="שם מלא" />
          </Form.Item>
          
          <Form.Item
            name="title"
            label="תפקיד"
            rules={[{ required: true, message: 'נא להזין תפקיד' }]}
          >
            <Input placeholder="למשל: בעל מרפאה" />
          </Form.Item>
          
          <Form.Item
            name="email"
            label="אימייל"
            rules={[
              { required: true, message: 'נא להזין אימייל' },
              { type: 'email', message: 'אימייל לא תקין' }
            ]}
          >
            <Input placeholder="email@example.com" />
          </Form.Item>
          
          <Form.Item>
            <Button 
              type="primary" 
              htmlType="submit"
              disabled={!agreed}
              loading={loading}
              block
            >
              חתום על ההסכם
            </Button>
          </Form.Item>
        </Form>
      </div>
    </Modal>
  );
};
```

**קבצים ליצור:**
- ✅ `frontend/src/pages/Onboarding/RegistrationWizard.tsx`
- ✅ `frontend/src/pages/Onboarding/ClinicInfoStep.tsx`
- ✅ `frontend/src/pages/Onboarding/OwnerInfoStep.tsx`
- ✅ `frontend/src/pages/Onboarding/TermsStep.tsx`
- ✅ `frontend/src/pages/Onboarding/ConfirmationStep.tsx`
- ✅ `frontend/src/components/BAA/BAASignatureModal.tsx`
- ✅ `frontend/src/pages/VerifyEmail.tsx`
- ✅ `frontend/src/pages/AcceptInvitation.tsx`

---

## 🎯 סדר ביצוע מומלץ

1. **קומפוננטה 1:** Organization Registration API (2 ימים)
2. **קומפוננטה 2:** Email Verification System (1 יום)
3. **קומפוננטה 3:** BAA Electronic Signature (2 ימים)
4. **קומפוננטה 4:** Team Invitation System (2 ימים)
5. **קומפוננטה 5:** Onboarding Frontend (3 ימים)

**סה"כ:** 10 ימי עבודה

---

## ✅ הצלחה מוגדרת

- [ ] מרפאה חדשה יכולה להירשם דרך הממשק
- [ ] בעל המרפאה מקבל אימייל אימות
- [ ] לאחר אימות, המערכת מציגה את ה-BAA לחתימה
- [ ] ה-BAA נחתם אלקטרונית ונשמר במסד הנתונים
- [ ] בעל המרפאה יכול להזמין צוות
- [ ] חברי צוות יכולים לקבל הזמנה ולהצטרף
- [ ] כל התהליך מתועד ב-audit log

---

## 📊 מדדי הצלחה (KPIs)

| מדד | יעד |
|-----|-----|
| **זמן הרשמה ממוצע** | < 5 דקות |
| **שיעור השלמת הרשמה** | > 80% |
| **שיעור אימות אימייל** | > 90% |
| **שיעור חתימה על BAA** | 100% |
| **שיעור קבלת הזמנות** | > 70% |

---

*נוצר על ידי: Manus AI*  
*תאריך: 8 באוקטובר 2025*
