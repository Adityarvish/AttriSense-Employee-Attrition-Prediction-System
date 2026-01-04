document.addEventListener("DOMContentLoaded", function () {
    // Add ripple effect to buttons
    document.addEventListener('click', function(e) {
        if (e.target.closest('.btn')) {
            const btn = e.target.closest('.btn');
            const ripple = document.createElement('span');
            ripple.classList.add('btn-ripple');
            
            // Get click position relative to button
            const rect = btn.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size/2;
            const y = e.clientY - rect.top - size/2;
            
            // Position the ripple
            ripple.style.width = ripple.style.height = size + 'px';
            ripple.style.left = x + 'px';
            ripple.style.top = y + 'px';
            
            btn.appendChild(ripple);
            
            // Remove ripple after animation
            setTimeout(() => {
                ripple.remove();
            }, 600);
        }
    });

    // Form submission with enhanced loading state
    const predictionForm = document.getElementById('predictionForm');
    if (predictionForm) {
        predictionForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const submitBtn = document.getElementById('predictBtn');
            
            if (submitBtn) {
                // Save original content
                const originalContent = submitBtn.innerHTML;
                const originalWidth = submitBtn.offsetWidth;
                
                // Set fixed width to prevent button resizing
                submitBtn.style.width = `${originalWidth}px`;
                
                // Create loading state
                submitBtn.innerHTML = `
                    <span class="loader"></span>
                    Analyzing...
                `;
                submitBtn.disabled = true;
                
                // Add loader styling
                const style = document.createElement('style');
                style.innerHTML = `
                    .loader {
                        display: inline-block;
                        width: 1.2rem;
                        height: 1.2rem;
                        border: 3px solid rgba(255,255,255,0.3);
                        border-radius: 50%;
                        border-top-color: white;
                        animation: spin 1s ease-in-out infinite;
                        margin-right: 0.8rem;
                        vertical-align: middle;
                    }
                    
                    @keyframes spin {
                        to { transform: rotate(360deg); }
                    }
                `;
                document.head.appendChild(style);
                
                // Submit after delay for animation
                setTimeout(() => {
                    predictionForm.submit();
                    
                    // Restore original state after submission
                    setTimeout(() => {
                        submitBtn.innerHTML = originalContent;
                        submitBtn.disabled = false;
                        submitBtn.style.width = '';
                        document.head.removeChild(style);
                    }, 1000);
                }, 1500);
            }
        });
    }
    
    // Animate cards on load
    const cards = document.querySelectorAll('.glass-card, .prediction-card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(30px)';
        card.style.transition = 'all 0.6s cubic-bezier(0.16, 1, 0.3, 1)';
        
        setTimeout(() => {
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, 100 + (index * 150));
    });
    
    // Floating label enhancement
    const floatLabels = document.querySelectorAll('.floating-label-group input');
    floatLabels.forEach(input => {
        input.addEventListener('focus', () => {
            const label = input.nextElementSibling;
            label.style.color = 'var(--primary)';
        });
        
        input.addEventListener('blur', () => {
            if (!input.value) {
                const label = input.nextElementSibling;
                label.style.color = 'var(--gray)';
            }
        });
    });
    
    // Hover effects for cards
    const hoverCards = document.querySelectorAll('.factors-card, .suggestions-card');
    hoverCards.forEach(card => {
        card.addEventListener('mouseenter', () => {
            card.style.transform = 'translateY(-5px)';
            card.style.boxShadow = '0 15px 30px rgba(0, 0, 0, 0.1)';
        });
        
        card.addEventListener('mouseleave', () => {
            card.style.transform = '';
            card.style.boxShadow = '';
        });
    });
});