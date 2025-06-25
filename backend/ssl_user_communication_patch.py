"""
Patch to enhance SSL error communication with user guidance
"""
import logging

logger = logging.getLogger(__name__)


def enhance_ssl_communication(main_module):
    """Add better SSL error communication to main.py"""
    
    # Store original notify_clients
    original_notify_clients = main_module.notify_clients
    
    async def enhanced_ssl_notification(project_id: str, message: dict):
        """Enhanced notification for SSL issues"""
        
        # Check if this is an SSL-related notification
        if message.get("status") == "ssl_fixed":
            # Instead of just status, provide more detail
            enhanced_message = {
                "type": "status",
                "message": "🔒 Setting up secure connection to external APIs...",
                "status": "processing"
            }
            await original_notify_clients(project_id, enhanced_message)
            
            # Follow up with details
            detail_message = {
                "type": "chat_response",
                "message": """I've detected that your app uses external APIs. I'm automatically adding the necessary security permissions.

**What I'm doing:**
- Adding network permissions to Info.plist
- Configuring SSL certificate handling
- Setting up API transport security

This will allow your app to connect to external services securely."""
            }
            await original_notify_clients(project_id, detail_message)
            
        elif "ssl" in str(message.get("message", "")).lower() or "certificate" in str(message.get("message", "")).lower():
            # For SSL errors, provide actionable guidance
            if main_module.user_comm_service:
                error_msg = message.get("message", "SSL error detected")
                await main_module.user_comm_service.notify_error(
                    project_id,
                    error_msg,
                    {"original_message": message}
                )
            else:
                await original_notify_clients(project_id, message)
        else:
            # For non-SSL messages, use original
            await original_notify_clients(project_id, message)
    
    # Replace the function
    main_module.notify_clients = enhanced_ssl_notification
    
    return main_module


def add_ssl_manual_action_detection():
    """Add detection for when manual SSL configuration might be needed"""
    
    async def check_ssl_manual_action(project_id: str, error: str, domain: str, user_comm_service):
        """Check if manual action is needed for SSL issues"""
        
        error_lower = error.lower()
        
        # Cases where manual action might be needed
        if "localhost" in domain or "127.0.0.1" in domain or "192.168" in domain:
            await user_comm_service.notify_manual_action_needed(
                project_id,
                "Local Development Server Detected",
                "Your app is trying to connect to a local development server",
                """To fix this:
1. **Option A**: Use a public API instead (recommended)
   - Try: api.quotable.io, jsonplaceholder.typicode.com, etc.
   
2. **Option B**: Deploy your local server to the internet
   - Use services like ngrok, localtunnel, or Heroku
   
3. **Option C**: Ask me to add special development permissions
   - Say: "Add development server support for localhost:3000"
   
The iOS Simulator cannot connect to 'localhost' on your Mac directly."""
            )
            
        elif "self-signed" in error_lower or "certificate verify failed" in error_lower:
            await user_comm_service.notify_manual_action_needed(
                project_id,
                "Invalid SSL Certificate",
                f"The server at {domain} has an invalid or self-signed certificate",
                """To fix this:
1. **For production**: Use a server with a valid SSL certificate
   
2. **For development**: Ask me to add an exception
   - Say: "Add certificate exception for {domain}"
   
3. **Check the server**: Ensure the API is accessible via HTTPS
   - Try visiting https://{domain} in your browser"""
            )
            
        elif "cleartext" in error_lower or "http:" in domain:
            await user_comm_service.notify_manual_action_needed(
                project_id,
                "Insecure HTTP Connection",
                f"iOS blocks insecure HTTP connections to {domain}",
                """iOS requires HTTPS for all connections. To fix this:
1. **Best solution**: Use HTTPS instead of HTTP
   - Change http:// to https:// in your API URL
   
2. **If HTTPS not available**: I can add an exception
   - Say: "Allow HTTP connection to {domain}"
   - Note: This reduces security and Apple may reject the app
   
3. **For testing only**: Use a different API that supports HTTPS"""
            )
    
    return check_ssl_manual_action