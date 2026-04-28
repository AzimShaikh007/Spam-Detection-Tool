// Debounce helper
function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

async function checkEmails() {
  // Find email rows in Gmail
  const emailRows = document.querySelectorAll('tr.zA');
  
  for (const row of emailRows) {
    // Prevent duplicate processing
    if (row.dataset.spamChecked === 'true') continue;
    row.dataset.spamChecked = 'true';
    
    // Find message ID using standard Gmail attributes
    const msgId = row.getAttribute('data-legacy-message-id') || row.querySelector('[data-legacy-message-id]')?.getAttribute('data-legacy-message-id');
    
    if (!msgId) continue;
    
    try {
      const response = await fetch(`http://localhost:8000/reason/${msgId}`);
      if (response.ok) {
        const data = await response.json();
        
        if (data.reasons && data.reasons.length > 0) {
          injectBadge(row, data.reasons);
        }
      }
    } catch (e) {
      console.error('Error fetching spam status:', e);
    }
  }
}

function injectBadge(row, reasons) {
  // Find subject element
  const subjectEl = row.querySelector('.bog');
  if (!subjectEl) return;
  
  // Prevent duplicate badges
  if (row.querySelector('.spam-badge')) return;
  
  const badge = document.createElement('span');
  badge.className = 'spam-badge';
  badge.textContent = '⚠ Spam';
  
  const tooltip = document.createElement('div');
  tooltip.className = 'spam-tooltip';
  tooltip.innerHTML = reasons.join('<br>');
  
  badge.appendChild(tooltip);
  subjectEl.parentElement.appendChild(badge);
}

const observer = new MutationObserver(debounce(checkEmails, 1000));

observer.observe(document.body, {
  childList: true,
  subtree: true
});

// Initial check
setTimeout(checkEmails, 2000);
