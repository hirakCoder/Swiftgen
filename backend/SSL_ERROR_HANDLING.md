# SSL Error Handling System

## Overview

SwiftGen now includes an intelligent SSL error handling system that:
1. Automatically detects SSL/TLS errors in iOS apps
2. Provides user-friendly explanations
3. Applies appropriate fixes automatically
4. Learns from repeated issues and tries alternative approaches

## Key Components

### 1. SSL Error Handler (`ssl_error_handler.py`)
- **Purpose**: Detects and analyzes SSL-related errors
- **Features**:
  - Pattern matching for common SSL errors
  - Domain extraction from error messages
  - Info.plist status checking
  - Fix code generation
  - User-friendly explanations

### 2. iOS Specific Fixes (`ios_specific_fixes.py`)
- **Purpose**: Repository of common iOS issues and solutions
- **Categories**:
  - Security (SSL/ATS, certificates)
  - Permissions (camera, photos, location)
  - Networking (local network access)
  - Build issues (bitcode, deployment target)
  - UI issues (scene delegate)

### 3. Enhanced Modification Handler (`modification_handler.py`)
- **New Features**:
  - Issue detection and categorization
  - Repeated issue tracking
  - Alternative fix suggestions
  - Automatic SSL fix application
  - Learning from failures

## How It Works

### When a user reports an SSL error:

1. **Detection Phase**
   ```python
   # The system detects SSL-related keywords and patterns
   "App Transport Security has blocked..."
   "SSL error has occurred..."
   "Certificate is invalid..."
   ```

2. **Analysis Phase**
   - Extracts domain from error message
   - Checks current Info.plist configuration
   - Determines best fix approach

3. **User Communication**
   - Provides clear, non-technical explanation
   - Shows what the system is doing
   - Tracks if this is a repeated issue

4. **Fix Application**
   - **Option 1**: Add ATS exception to Info.plist
   - **Option 2**: Upgrade HTTP to HTTPS in code
   - **Option 3**: Implement certificate validation

5. **Intelligent Retry**
   - If first fix doesn't work, tries alternatives
   - Learns from failures
   - Provides different approaches

## Example Scenarios

### Scenario 1: HTTP Blocked by ATS
**User**: "My app crashes with 'App Transport Security has blocked a cleartext HTTP'"

**SwiftGen Response**:
```
🔒 SSL/Security Issue Detected

Your app is trying to connect to a server using HTTP (insecure) instead of HTTPS (secure).
iOS blocks insecure connections by default for security reasons.

Recommended solutions:
1. Change your API URLs from HTTP to HTTPS (most secure)
2. Add a security exception for your domain (temporary fix)

🔧 Applying fix: Add App Transport Security exception...
```

### Scenario 2: Invalid Certificate
**User**: "Getting SSL certificate error when connecting to my server"

**SwiftGen Response**:
```
🔒 SSL/Security Issue Detected

The server's SSL certificate is not trusted by iOS.
This could be because it's self-signed, expired, or from an untrusted authority.

🔧 Applying fix: Implement custom certificate validation (development mode)...
```

### Scenario 3: Repeated Issue
**User**: "Still getting the SSL error" (2nd attempt)

**SwiftGen Response**:
```
🔒 SSL/Security Issue Detected

[Previous explanation...]

I see the previous fix didn't work. Let me try a different approach (attempt #2).
🔧 Applying alternative fix: Allow all insecure loads (not recommended for production)...
```

## Configuration Examples

### Info.plist ATS Exception (Domain-specific)
```xml
<key>NSAppTransportSecurity</key>
<dict>
    <key>NSExceptionDomains</key>
    <dict>
        <key>example.com</key>
        <dict>
            <key>NSIncludesSubdomains</key>
            <true/>
            <key>NSTemporaryExceptionAllowsInsecureHTTPLoads</key>
            <true/>
        </dict>
    </dict>
</dict>
```

### Info.plist ATS Exception (Allow All - Dev Only)
```xml
<key>NSAppTransportSecurity</key>
<dict>
    <key>NSAllowsArbitraryLoads</key>
    <true/>
</dict>
```

### Certificate Validation Bypass (Dev Only)
```swift
class CertificateBypassDelegate: NSObject, URLSessionDelegate {
    func urlSession(_ session: URLSession, 
                    didReceive challenge: URLAuthenticationChallenge, 
                    completionHandler: @escaping (URLSession.AuthChallengeDisposition, URLCredential?) -> Void) {
        if challenge.protectionSpace.authenticationMethod == NSURLAuthenticationMethodServerTrust,
           let serverTrust = challenge.protectionSpace.serverTrust {
            let credential = URLCredential(trust: serverTrust)
            completionHandler(.useCredential, credential)
        } else {
            completionHandler(.performDefaultHandling, nil)
        }
    }
}
```

## Benefits

1. **User-Friendly**: No need for users to understand technical SSL details
2. **Automatic**: Fixes are applied without manual intervention
3. **Intelligent**: Learns from failures and tries alternatives
4. **Educational**: Explains what's happening and why
5. **Safe**: Warns about security implications of fixes

## Future Enhancements

1. Support for more SSL scenarios (mutual TLS, pinning)
2. Production-safe alternatives
3. Certificate installation guidance
4. Network debugging tools integration
5. SSL best practices recommendations

## Testing

Run the test suite:
```bash
python3 test_ssl_handler.py
```

This verifies:
- SSL error detection
- Issue analysis
- Fix generation
- iOS-specific fixes
- Integration with modification handler