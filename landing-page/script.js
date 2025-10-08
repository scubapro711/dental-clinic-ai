// Scenarios Data
const scenarios = {
    1: {
        title: "ביטול תור",
        bot: [
            { type: 'user', text: 'שלום, אני צריך לבטל את התור שלי מחר' },
            { type: 'bot', text: 'אוקיי, תודה על העדכון. האם אתה רוצה לקבוע תור חדש?' },
            { type: 'user', text: 'לא, תודה' },
            { type: 'bot', text: 'בסדר גמור. יום טוב!' }
        ],
        agent: [
            { type: 'user', text: 'שלום, אני צריך לבטל את התור שלי מחר' },
            { 
                type: 'agent', 
                text: 'הבנתי, דוד. אני מטפל בזה עכשיו:',
                actions: [
                    '✅ התור בוטל במערכת Odoo',
                    '✅ 3 מטופלים מרשימת ההמתנה קיבלו SMS',
                    '✅ התור התמלא תוך 4 דקות',
                    '💰 חסכת למרפאה ₪450'
                ]
            },
            { type: 'agent', text: 'התור בוטל בהצלחה. אם תרצה לקבוע תור חדש, אני כאן 😊' }
        ],
        botResult: 'התור בוטל, אבל נשאר ריק. המרפאה הפסידה ₪450.',
        agentResult: 'התור בוטל ומולא אוטומטית מרשימת המתנה. אפס הפסד, שקיפות מלאה.'
    },
    2: {
        title: "שאלה על מחיר",
        bot: [
            { type: 'user', text: 'כמה עולה טיפול שורש?' },
            { type: 'bot', text: 'טיפול שורש עולה בין ₪2,000 ל-₪3,000 תלוי בשן' },
            { type: 'user', text: 'תודה' },
            { type: 'bot', text: 'בשמחה! 😊' }
        ],
        agent: [
            { type: 'user', text: 'כמה עולה טיפול שורש?' },
            { 
                type: 'agent', 
                text: 'טיפול שורש במרפאה שלנו:',
                actions: [
                    '💰 שן קדמית: ₪2,200',
                    '💰 שן אחורית: ₪2,800',
                    '📊 תוכנית תשלומים: 4 תשלומים ללא ריבית',
                    '🎁 הנחה 10% אם משלמים מראש',
                    '📱 שלחתי לך הצעה מפורטת ל-WhatsApp'
                ]
            },
            { type: 'agent', text: 'רוצה לקבוע תור לייעוץ חינם?' }
        ],
        botResult: 'המטופל קיבל מידע בסיסי, אבל לא הומר ללקוח.',
        agentResult: 'המטופל קיבל הצעה מפורטת, תוכנית תשלומים, והצעה לתור. סיכוי גבוה להמרה.'
    },
    3: {
        title: "לקוח חדש",
        bot: [
            { type: 'user', text: 'שלום, אני רוצה לקבוע תור' },
            { type: 'bot', text: 'בטח! מתי נוח לך?' },
            { type: 'user', text: 'מחר אחר הצהריים' },
            { type: 'bot', text: 'יש לנו תור ב-15:00' },
            { type: 'user', text: 'מעולה' },
            { type: 'bot', text: 'נרשמת לתור מחר ב-15:00. נתראה!' }
        ],
        agent: [
            { type: 'user', text: 'שלום, אני רוצה לקבוע תור' },
            { type: 'agent', text: 'שמח לעזור! אני רואה שאתה לקוח חדש. מה הסיבה לביקור?' },
            { type: 'user', text: 'כאב בשן' },
            { 
                type: 'agent', 
                text: 'מבין, זה דחוף. אני מטפל:',
                actions: [
                    '✅ קבעתי תור דחוף למחר 15:00',
                    '✅ שלחתי SMS עם הוראות הגעה',
                    '✅ הוספתי "כאב חריף" לתיק הרפואי',
                    '✅ שלחתי שאלון רפואי למילוי מראש',
                    '✅ עדכנתי את ד"ר כהן על המקרה',
                    '💡 יש לנו תור מוקדם יותר ב-10:00 אם דחוף'
                ]
            }
        ],
        botResult: 'תור נקבע, אבל אין הכנה מוקדמת. הרופא לא יודע על הכאב.',
        agentResult: 'תור נקבע, המטופל הכין שאלון, והרופא יודע מראש על הכאב. חוויה מעולה.'
    },
    4: {
        title: "תזרים נמוך",
        bot: [
            { type: 'user', text: 'תן לי דוח על התזרים החודש' },
            { type: 'bot', text: 'אני לא יכול לעזור בזה. תצטרך לדבר עם המנהלת' },
            { type: 'user', text: 'אוקיי...' }
        ],
        agent: [
            { type: 'user', text: 'תן לי דוח על התזרים החודש' },
            { 
                type: 'agent', 
                text: 'כמובן! אני מנתח עכשיו:',
                actions: [
                    '📊 תזרים החודש: ₪85,000 (-15% מהחודש שעבר)',
                    '⚠️ זיהיתי: 12 חשבוניות שלא שולמו (₪18,000)',
                    '💡 המלצה: הצע מבצע "הבאת חבר" ל-3 השבועות הבאים',
                    '📈 תחזית: עם המבצע, תזרים צפוי לעלות ל-₪95,000',
                    '📄 שלחתי דוח מפורט למייל שלך',
                    '📅 קבעתי פגישה איתך מחר ב-9:00 לדון באסטרטגיה'
                ]
            }
        ],
        botResult: 'הרופא לא קיבל מידע ונאלץ לחפש בעצמו.',
        agentResult: 'הרופא קיבל ניתוח מלא, המלצות, ופגישה נקבעה. פרואקטיבי לחלוטין.'
    },
    5: {
        title: "מלאי נגמר",
        bot: [
            { type: 'user', text: 'נגמר לי חומר איטום' },
            { type: 'bot', text: 'תזמין מהספק' },
            { type: 'user', text: 'אוקיי' }
        ],
        agent: [
            { type: 'user', text: 'נגמר לי חומר איטום' },
            { 
                type: 'agent', 
                text: 'אני מטפלת בזה:',
                actions: [
                    '🔍 בדקתי מלאי: נשארו 2 יחידות (מתחת לסף)',
                    '💰 מצאתי ספק חדש זול ב-25%: ₪320 חיסכון',
                    '📊 השוויתי 3 ספקים לפי מחיר ואיכות',
                    '✅ הזמנתי 10 יחידות (מספיק ל-2 חודשים)',
                    '🚚 זמן אספקה: 24 שעות',
                    '📝 עדכנתי במערכת Odoo'
                ]
            }
        ],
        botResult: 'הרופא צריך לעצור עבודה, לחפש ספק, ולהזמין בעצמו.',
        agentResult: 'הסוכן זיהה את הבעיה, מצא פתרון זול יותר, והזמין אוטומטית. אפס עבודה לרופא.'
    }
};

// Current scenario
let currentScenario = 1;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    // Load first scenario
    loadScenario(1);

    // Scenario tabs
    document.querySelectorAll('.scenario-tab').forEach(tab => {
        tab.addEventListener('click', () => {
            const scenarioId = parseInt(tab.dataset.scenario);
            currentScenario = scenarioId;
            
            // Update active tab
            document.querySelectorAll('.scenario-tab').forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            
            // Load scenario
            loadScenario(scenarioId);
        });
    });

    // ROI Calculator
    setupROICalculator();

    // Form submission
    document.getElementById('notify-form').addEventListener('submit', handleFormSubmit);
});

// Load scenario
function loadScenario(id) {
    const scenario = scenarios[id];
    
    // Clear chats
    const botChat = document.getElementById('bot-chat');
    const agentChat = document.getElementById('agent-chat');
    botChat.innerHTML = '';
    agentChat.innerHTML = '';
    
    // Animate bot messages
    let botDelay = 0;
    scenario.bot.forEach((msg, index) => {
        setTimeout(() => {
            addMessage(botChat, msg);
        }, botDelay);
        botDelay += 1500;
    });
    
    // Animate agent messages
    let agentDelay = 0;
    scenario.agent.forEach((msg, index) => {
        setTimeout(() => {
            addMessage(agentChat, msg);
        }, agentDelay);
        agentDelay += 1500;
    });
    
    // Update results
    document.getElementById('bot-result-text').textContent = scenario.botResult;
    document.getElementById('agent-result-text').textContent = scenario.agentResult;
}

// Add message to chat
function addMessage(chatElement, message) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `chat-message ${message.type}`;
    msgDiv.textContent = message.text;
    
    if (message.actions) {
        const actionsDiv = document.createElement('div');
        actionsDiv.className = 'chat-actions';
        message.actions.forEach(action => {
            const actionDiv = document.createElement('div');
            actionDiv.textContent = action;
            actionsDiv.appendChild(actionDiv);
        });
        msgDiv.appendChild(actionsDiv);
    }
    
    chatElement.appendChild(msgDiv);
    chatElement.scrollTop = chatElement.scrollHeight;
}

// Setup ROI Calculator
function setupROICalculator() {
    const appointmentsInput = document.getElementById('appointments-week');
    const avgPriceInput = document.getElementById('avg-price');
    const adminHoursInput = document.getElementById('admin-hours');
    
    function calculate() {
        const appointmentsWeek = parseInt(appointmentsInput.value) || 100;
        const avgPrice = parseInt(avgPriceInput.value) || 450;
        const adminHours = parseInt(adminHoursInput.value) || 10;
        
        // Calculations
        const appointmentsYear = appointmentsWeek * 52;
        
        // Cancellation savings (30% → 10% = 20% saved)
        const cancellationSavings = Math.round(appointmentsYear * 0.20 * avgPrice);
        
        // Time savings (₪200/hour)
        const timeSavings = Math.round(adminHours * 52 * 200);
        
        // Cashflow improvement (15% faster payments)
        const yearlyRevenue = appointmentsYear * avgPrice;
        const cashflowSavings = Math.round(yearlyRevenue * 0.15);
        
        // Total
        const totalSavings = cancellationSavings + timeSavings + cashflowSavings;
        
        // Update UI
        document.getElementById('cancellation-savings').textContent = `₪${cancellationSavings.toLocaleString()}`;
        document.getElementById('time-savings').textContent = `₪${timeSavings.toLocaleString()}`;
        document.getElementById('cashflow-savings').textContent = `₪${cashflowSavings.toLocaleString()}`;
        document.getElementById('total-savings').textContent = `₪${totalSavings.toLocaleString()}`;
    }
    
    // Initial calculation
    calculate();
    
    // Update on input
    appointmentsInput.addEventListener('input', calculate);
    avgPriceInput.addEventListener('input', calculate);
    adminHoursInput.addEventListener('input', calculate);
}

// Handle form submission
function handleFormSubmit(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const data = Object.fromEntries(formData);
    
    // Here you would send to your backend
    console.log('Form submitted:', data);
    
    // Show success message
    alert('תודה על ההרשמה! נחזור אליך בקרוב 🎉');
    e.target.reset();
}

// Scroll to notify section
function scrollToNotify() {
    document.getElementById('notify').scrollIntoView({ behavior: 'smooth' });
}

// Intersection Observer for animations
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -100px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, observerOptions);

// Observe all sections
document.querySelectorAll('section').forEach(section => {
    section.style.opacity = '0';
    section.style.transform = 'translateY(30px)';
    section.style.transition = 'opacity 0.8s ease-out, transform 0.8s ease-out';
    observer.observe(section);
});
