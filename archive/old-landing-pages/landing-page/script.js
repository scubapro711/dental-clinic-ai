// Smooth scroll functions
function scrollToNotify() {
    document.getElementById('notify').scrollIntoView({ behavior: 'smooth' });
}

function scrollToFeatures() {
    document.getElementById('features').scrollIntoView({ behavior: 'smooth' });
}

// Form submission
document.getElementById('notifyForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const email = this.querySelector('input[type="email"]').value;
    const button = this.querySelector('button');
    const originalText = button.innerHTML;
    
    // Show loading state
    button.innerHTML = '<span>שולח...</span>';
    button.disabled = true;
    
    try {
        // TODO: Replace with actual API endpoint
        // For now, just simulate success
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // Show success message
        button.innerHTML = '<span>✓ נרשמת בהצלחה!</span>';
        button.style.background = '#10b981';
        
        // Clear form
        this.querySelector('input[type="email"]').value = '';
        
        // Reset button after 3 seconds
        setTimeout(() => {
            button.innerHTML = originalText;
            button.disabled = false;
            button.style.background = '';
        }, 3000);
        
    } catch (error) {
        // Show error message
        button.innerHTML = '<span>שגיאה, נסה שוב</span>';
        button.style.background = '#ef4444';
        
        // Reset button after 3 seconds
        setTimeout(() => {
            button.innerHTML = originalText;
            button.disabled = false;
            button.style.background = '';
        }, 3000);
    }
});

// Add parallax effect to hero
window.addEventListener('scroll', function() {
    const scrolled = window.pageYOffset;
    const hero = document.querySelector('.hero');
    if (hero) {
        hero.style.transform = `translateY(${scrolled * 0.5}px)`;
    }
});

// Animate elements on scroll
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -100px 0px'
};

const observer = new IntersectionObserver(function(entries) {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, observerOptions);

// Observe all sections
document.addEventListener('DOMContentLoaded', function() {
    const sections = document.querySelectorAll('.why-different, .agents, .tech-stack, .notify');
    sections.forEach(section => {
        section.style.opacity = '0';
        section.style.transform = 'translateY(30px)';
        section.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(section);
    });
});
