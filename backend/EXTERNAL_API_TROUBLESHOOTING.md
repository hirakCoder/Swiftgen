# External API Troubleshooting Guide for SwiftGen

## Common Issues and Solutions

### 1. Generic "Failed to load" Errors

**Problem**: Apps show generic error messages without details about what actually went wrong.

**Root Causes**:
- Network timeouts
- SSL/certificate issues
- API rate limiting
- JSON parsing errors
- No internet connection

**Solution**: Implement comprehensive error handling with specific messages.

### 2. iOS App Transport Security (ATS) Issues

**Problem**: iOS blocks network requests for security reasons.

**Common Scenarios**:
- HTTP (non-secure) URLs
- Self-signed certificates
- Expired certificates
- Invalid certificate chains

**Solutions**:

#### For Production APIs (HTTPS with valid certs):
```swift
// No changes needed - should work by default
```

#### For Development/Testing (HTTP or self-signed certs):
```xml
<!-- Info.plist -->
<key>NSAppTransportSecurity</key>
<dict>
    <!-- For specific domain -->
    <key>NSExceptionDomains</key>
    <dict>
        <key>api.example.com</key>
        <dict>
            <key>NSIncludesSubdomains</key>
            <true/>
            <key>NSTemporaryExceptionAllowsInsecureHTTPLoads</key>
            <true/>
        </dict>
    </dict>
</dict>
```

### 3. Network Timeout Issues

**Problem**: Requests fail in poor network conditions.

**Solution**: Implement proper timeout and retry logic:
```swift
let config = URLSessionConfiguration.default
config.timeoutIntervalForRequest = 30
config.timeoutIntervalForResource = 60
let session = URLSession(configuration: config)
```

### 4. Enhanced Error Handling Pattern

```swift
enum NetworkError: LocalizedError {
    case noInternet
    case timeout
    case serverError(Int)
    case sslError
    case decodingError
    case unknown(Error)
    
    var errorDescription: String? {
        switch self {
        case .noInternet:
            return "No internet connection. Please check your network."
        case .timeout:
            return "Request timed out. Please try again."
        case .serverError(let code):
            return "Server error (\(code)). Please try again later."
        case .sslError:
            return "Security connection failed. Please update the app."
        case .decodingError:
            return "Invalid response format. Please contact support."
        case .unknown(let error):
            return "An error occurred: \(error.localizedDescription)"
        }
    }
}
```

### 5. Robust API Service Implementation

```swift
class RobustAPIService {
    private let session: URLSession
    private let maxRetries = 3
    
    init() {
        let config = URLSessionConfiguration.default
        config.timeoutIntervalForRequest = 30
        config.waitsForConnectivity = true
        self.session = URLSession(configuration: config)
    }
    
    func fetchWithRetry<T: Decodable>(
        from url: URL,
        type: T.Type,
        retries: Int = 0
    ) async throws -> T {
        do {
            let (data, response) = try await session.data(from: url)
            
            guard let httpResponse = response as? HTTPURLResponse else {
                throw NetworkError.unknown(URLError(.badServerResponse))
            }
            
            switch httpResponse.statusCode {
            case 200...299:
                do {
                    return try JSONDecoder().decode(type, from: data)
                } catch {
                    print("Decoding error: \(error)")
                    throw NetworkError.decodingError
                }
            case 429:
                // Rate limited - wait and retry
                if retries < maxRetries {
                    try await Task.sleep(nanoseconds: UInt64(pow(2.0, Double(retries)) * 1_000_000_000))
                    return try await fetchWithRetry(from: url, type: type, retries: retries + 1)
                }
                throw NetworkError.serverError(429)
            case 500...599:
                throw NetworkError.serverError(httpResponse.statusCode)
            default:
                throw NetworkError.serverError(httpResponse.statusCode)
            }
        } catch {
            // Network errors
            if let urlError = error as? URLError {
                switch urlError.code {
                case .notConnectedToInternet:
                    throw NetworkError.noInternet
                case .timedOut:
                    throw NetworkError.timeout
                case .secureConnectionFailed:
                    throw NetworkError.sslError
                default:
                    if retries < maxRetries {
                        try await Task.sleep(nanoseconds: UInt64(pow(2.0, Double(retries)) * 1_000_000_000))
                        return try await fetchWithRetry(from: url, type: type, retries: retries + 1)
                    }
                    throw NetworkError.unknown(error)
                }
            }
            throw error
        }
    }
}
```

### 6. Testing External APIs

#### In Simulator:
1. Check Console.app for detailed error logs
2. Use Network Link Conditioner to test poor connections
3. Test with/without internet
4. Test with VPN (may cause SSL issues)

#### Common API Issues:
- **api.quotable.io**: Generally reliable, HTTPS enabled
- **openweathermap.org**: Requires API key, rate limits
- **jsonplaceholder.typicode.com**: Good for testing, always available
- **localhost/127.0.0.1**: Requires ATS exception

### 7. SwiftGen-Specific Solutions

When users report API issues:

1. **Detect API usage pattern**:
   - Check for URLSession usage
   - Identify the API domain
   - Check for error handling

2. **Apply appropriate fixes**:
   - For SSL issues: Apply robust SSL handler
   - For timeout issues: Add retry logic
   - For ATS issues: Add Info.plist exceptions

3. **Improve error visibility**:
   - Add proper error logging
   - Implement specific error messages
   - Add network status monitoring

### 8. Currency Converter Success Story

The currency converter worked because:
- Used HTTPS API (exchangerate-api.com)
- Had proper error handling
- Included retry logic
- Clear error messages

### 9. Recommended APIs for Testing

**Always Working (HTTPS, no auth)**:
- https://api.quotable.io/random
- https://jsonplaceholder.typicode.com/posts
- https://api.ipify.org?format=json

**Require API Key**:
- OpenWeatherMap
- NewsAPI
- Currency converters

**May Have Issues**:
- Self-hosted APIs
- HTTP-only APIs
- APIs with IP restrictions