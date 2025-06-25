// Frontend enhancement for better error communication
// Add this to app.js in the handleWebSocketMessage switch statement

// Add these cases after the existing cases:

case 'manual_action':
    // Handle cases where user needs to take action
    this.hideProgress();
    this.isProcessing = false;
    
    // Create a special message with action items
    const actionMessage = `
${message.message}

**Action Required:** ${message.action_required}

**How to fix:**
${message.how_to_fix}
    `.trim();
    
    this.addMessage('assistant', actionMessage, false);
    this.updateStatus('warning', 'Action needed');
    
    // Re-enable input for user to respond
    const actionInput = document.getElementById('chatInput');
    const actionSendBtn = document.getElementById('sendButton') || document.querySelector('button[type="submit"]');
    if (actionInput) actionInput.disabled = false;
    if (actionSendBtn) actionSendBtn.disabled = false;
    break;

// Enhanced error case with suggestions
case 'error':
    // Handle build/generation errors with suggestions
    this.hideProgress();
    this.isProcessing = false;
    
    let errorMessage = message.message || '❌ An error occurred';
    
    // Add suggestion if available
    if (message.suggestion) {
        errorMessage += `\n\n💡 **Suggestion:** ${message.suggestion}`;
    }
    
    // Add technical details if in debug mode
    if (this.debugMode && message.technical_details) {
        errorMessage += `\n\n🔧 **Technical details:** ${message.technical_details}`;
    }
    
    if (message.errors && message.errors.length > 0) {
        this.buildLogs = message.errors;
        this.addMessage('assistant', errorMessage, false, message.errors);
    } else {
        this.addMessage('assistant', errorMessage);
    }
    
    // Update status based on error type
    const statusText = message.status === 'needs_action' ? 'Action needed' : 'Error occurred';
    this.updateStatus('error', statusText);
    
    // Re-enable input
    const errorInput = document.getElementById('chatInput');
    const errorSendBtn = document.getElementById('sendButton') || document.querySelector('button[type="submit"]');
    if (errorInput) errorInput.disabled = false;
    if (errorSendBtn) errorSendBtn.disabled = false;
    break;

// Add to the existing status case to show more helpful status messages:
case 'status':
    // Enhanced status handling
    if (message.status === 'error' && message.suggestion) {
        // Show error with suggestion in status bar
        this.updateStatus('error', message.message);
        // Also add to chat for visibility
        this.addMessage('assistant', `${message.message}\n\n💡 ${message.suggestion}`);
    } else if (message.message.includes('SSL') || message.message.includes('API')) {
        // Special handling for API/SSL status
        this.updateStatus('processing', message.message);
        // Add informative message to chat
        if (message.message.includes('Setting up')) {
            this.addMessage('assistant', `🔧 ${message.message}\n\nThis may take a moment while I configure the security settings.`);
        }
    } else {
        this.updateStatus(message.status || 'processing', message.message);
    }
    break;