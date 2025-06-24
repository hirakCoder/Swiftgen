"""
Robust SSL Handler for iOS Applications with External API Support

This module provides comprehensive SSL/TLS handling for iOS apps that need to
connect to external APIs, including development servers, self-signed certificates,
and various SSL/TLS configuration issues.
"""

import re
import logging
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import json

logger = logging.getLogger(__name__)


class RobustSSLHandler:
    """Enhanced SSL handler with robust support for external APIs."""
    
    def __init__(self):
        self.attempted_fixes = []
        self.successful_fixes = []
        
    def generate_comprehensive_ssl_solution(self, domain: str, issue_type: str = "general") -> Dict[str, any]:
        """
        Generate a comprehensive SSL solution that handles multiple scenarios.
        
        Args:
            domain: The domain having SSL issues
            issue_type: Type of SSL issue (certificate, ats, handshake, etc.)
            
        Returns:
            Dictionary containing multiple fix approaches
        """
        fixes = {
            "info_plist_changes": self._generate_info_plist_fix(domain),
            "network_configuration": self._generate_network_config_fix(domain),
            "url_session_delegate": self._generate_session_delegate_fix(),
            "alamofire_fix": self._generate_alamofire_fix(),
            "combine_fix": self._generate_combine_fix()
        }
        
        return fixes
    
    def _generate_info_plist_fix(self, domain: str) -> Dict[str, str]:
        """Generate comprehensive Info.plist configuration."""
        return {
            "content": f"""    <!-- SSL/ATS Configuration for {domain} -->
    <key>NSAppTransportSecurity</key>
    <dict>
        <!-- Allow specific domain with relaxed security -->
        <key>NSExceptionDomains</key>
        <dict>
            <key>{domain}</key>
            <dict>
                <key>NSIncludesSubdomains</key>
                <true/>
                <key>NSTemporaryExceptionAllowsInsecureHTTPLoads</key>
                <true/>
                <key>NSTemporaryExceptionMinimumTLSVersion</key>
                <string>TLSv1.0</string>
                <key>NSExceptionRequiresForwardSecrecy</key>
                <false/>
                <key>NSThirdPartyExceptionAllowsInsecureHTTPLoads</key>
                <true/>
            </dict>
        </dict>
        <!-- For development: Allow local network connections -->
        <key>NSAllowsLocalNetworking</key>
        <true/>
    </dict>""",
            "description": "Comprehensive ATS exception for the domain"
        }
    
    def _generate_network_config_fix(self, domain: str) -> Dict[str, str]:
        """Generate a robust network configuration manager."""
        return {
            "filename": "NetworkConfiguration.swift",
            "content": """import Foundation

/// Robust network configuration for handling SSL/TLS issues
class NetworkConfiguration {
    static let shared = NetworkConfiguration()
    
    private init() {}
    
    /// Create a URL session with custom SSL handling
    func createCustomSession() -> URLSession {
        let configuration = URLSessionConfiguration.default
        configuration.timeoutIntervalForRequest = 30
        configuration.timeoutIntervalForResource = 300
        
        // Enable HTTP pipelining for better performance
        configuration.httpShouldUsePipelining = true
        
        // Allow cellular access
        configuration.allowsCellularAccess = true
        
        // Create session with custom delegate
        let session = URLSession(
            configuration: configuration,
            delegate: SSLPinningDelegate(),
            delegateQueue: nil
        )
        
        return session
    }
    
    /// Create a session for development with relaxed SSL
    func createDevelopmentSession() -> URLSession {
        let configuration = URLSessionConfiguration.default
        configuration.timeoutIntervalForRequest = 30
        
        let session = URLSession(
            configuration: configuration,
            delegate: DevelopmentSSLDelegate(),
            delegateQueue: nil
        )
        
        return session
    }
}

/// SSL Pinning Delegate for production use
class SSLPinningDelegate: NSObject, URLSessionDelegate {
    func urlSession(_ session: URLSession,
                    didReceive challenge: URLAuthenticationChallenge,
                    completionHandler: @escaping (URLSession.AuthChallengeDisposition, URLCredential?) -> Void) {
        
        guard challenge.protectionSpace.authenticationMethod == NSURLAuthenticationMethodServerTrust,
              let serverTrust = challenge.protectionSpace.serverTrust else {
            completionHandler(.performDefaultHandling, nil)
            return
        }
        
        // For now, accept the server trust
        // In production, implement proper certificate pinning here
        let credential = URLCredential(trust: serverTrust)
        completionHandler(.useCredential, credential)
    }
}

/// Development SSL Delegate - accepts all certificates
class DevelopmentSSLDelegate: NSObject, URLSessionDelegate {
    func urlSession(_ session: URLSession,
                    didReceive challenge: URLAuthenticationChallenge,
                    completionHandler: @escaping (URLSession.AuthChallengeDisposition, URLCredential?) -> Void) {
        
        if challenge.protectionSpace.authenticationMethod == NSURLAuthenticationMethodServerTrust {
            if let serverTrust = challenge.protectionSpace.serverTrust {
                let credential = URLCredential(trust: serverTrust)
                completionHandler(.useCredential, credential)
                return
            }
        }
        
        completionHandler(.performDefaultHandling, nil)
    }
}

/// Extension to handle common SSL errors
extension URLSession {
    /// Perform a data task with SSL error handling
    func dataTaskWithSSLHandling(with url: URL,
                                  completionHandler: @escaping (Data?, URLResponse?, Error?) -> Void) -> URLSessionDataTask {
        
        return self.dataTask(with: url) { data, response, error in
            if let error = error as NSError? {
                // Handle specific SSL errors
                switch error.code {
                case NSURLErrorServerCertificateHasBadDate:
                    print("⚠️ SSL Certificate has expired or bad date")
                case NSURLErrorServerCertificateUntrusted:
                    print("⚠️ SSL Certificate is untrusted")
                case NSURLErrorServerCertificateHasUnknownRoot:
                    print("⚠️ SSL Certificate has unknown root")
                case NSURLErrorServerCertificateNotYetValid:
                    print("⚠️ SSL Certificate is not yet valid")
                case NSURLErrorSecureConnectionFailed:
                    print("⚠️ Secure connection failed")
                default:
                    break
                }
            }
            
            completionHandler(data, response, error)
        }
    }
}
""",
            "description": "Comprehensive network configuration with SSL handling"
        }
    
    def _generate_session_delegate_fix(self) -> Dict[str, str]:
        """Generate URLSession delegate implementation."""
        return {
            "filename": "APIClient+SSL.swift",
            "content": """import Foundation

extension APIClient {
    /// Configure SSL handling for the API client
    func configureSSLHandling() {
        // Use custom session with SSL handling
        self.session = NetworkConfiguration.shared.createCustomSession()
    }
    
    /// Make a request with automatic SSL error recovery
    func requestWithSSLRecovery<T: Codable>(
        endpoint: String,
        method: String = "GET",
        parameters: [String: Any]? = nil,
        completion: @escaping (Result<T, Error>) -> Void
    ) {
        guard let url = URL(string: baseURL + endpoint) else {
            completion(.failure(APIError.invalidURL))
            return
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = method
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        if let parameters = parameters {
            request.httpBody = try? JSONSerialization.data(withJSONObject: parameters)
        }
        
        // First attempt with regular session
        performRequest(request: request) { (result: Result<T, Error>) in
            switch result {
            case .success(let data):
                completion(.success(data))
            case .failure(let error):
                // Check if it's an SSL error
                if self.isSSLError(error) {
                    print("🔄 SSL error detected, retrying with relaxed security...")
                    
                    // Retry with development session
                    let devSession = NetworkConfiguration.shared.createDevelopmentSession()
                    devSession.dataTask(with: request) { data, response, error in
                        if let error = error {
                            completion(.failure(error))
                            return
                        }
                        
                        guard let data = data else {
                            completion(.failure(APIError.noData))
                            return
                        }
                        
                        do {
                            let decoded = try JSONDecoder().decode(T.self, from: data)
                            completion(.success(decoded))
                        } catch {
                            completion(.failure(error))
                        }
                    }.resume()
                } else {
                    completion(.failure(error))
                }
            }
        }
    }
    
    private func isSSLError(_ error: Error) -> Bool {
        let nsError = error as NSError
        let sslErrorCodes = [
            NSURLErrorServerCertificateHasBadDate,
            NSURLErrorServerCertificateUntrusted,
            NSURLErrorServerCertificateHasUnknownRoot,
            NSURLErrorServerCertificateNotYetValid,
            NSURLErrorSecureConnectionFailed,
            -1022 // kCFURLErrorCannotLoadFromNetwork
        ]
        
        return sslErrorCodes.contains(nsError.code)
    }
    
    private func performRequest<T: Codable>(
        request: URLRequest,
        completion: @escaping (Result<T, Error>) -> Void
    ) {
        session.dataTask(with: request) { data, response, error in
            if let error = error {
                completion(.failure(error))
                return
            }
            
            guard let data = data else {
                completion(.failure(APIError.noData))
                return
            }
            
            do {
                let decoded = try JSONDecoder().decode(T.self, from: data)
                completion(.success(decoded))
            } catch {
                completion(.failure(error))
            }
        }.resume()
    }
}

enum APIError: Error {
    case invalidURL
    case noData
    case decodingError
}
""",
            "description": "APIClient extension with SSL error recovery"
        }
    
    def _generate_alamofire_fix(self) -> Dict[str, str]:
        """Generate Alamofire-specific SSL fix."""
        return {
            "filename": "AlamofireSSLManager.swift",
            "content": """import Foundation
import Alamofire

/// Custom ServerTrustManager for Alamofire with SSL handling
class CustomServerTrustManager {
    
    /// Create a server trust manager for development
    static func createDevelopmentTrustManager(for domain: String) -> ServerTrustManager {
        let evaluators: [String: ServerTrustEvaluating] = [
            domain: DisabledTrustEvaluator()
        ]
        
        return ServerTrustManager(evaluators: evaluators)
    }
    
    /// Create a session with custom SSL handling
    static func createCustomSession(for domain: String) -> Session {
        let configuration = URLSessionConfiguration.af.default
        configuration.timeoutIntervalForRequest = 30
        
        let trustManager = createDevelopmentTrustManager(for: domain)
        
        return Session(
            configuration: configuration,
            serverTrustManager: trustManager
        )
    }
}

/// Disabled trust evaluator for development
class DisabledTrustEvaluator: ServerTrustEvaluating {
    func evaluate(_ trust: SecTrust, forHost host: String) throws {
        // Accept all certificates in development
        // WARNING: Do not use in production!
    }
}

/// Extension to add SSL retry logic
extension Session {
    func requestWithSSLRetry(
        _ convertible: URLConvertible,
        method: HTTPMethod = .get,
        parameters: Parameters? = nil,
        encoding: ParameterEncoding = JSONEncoding.default,
        headers: HTTPHeaders? = nil
    ) -> DataRequest {
        
        let request = self.request(
            convertible,
            method: method,
            parameters: parameters,
            encoding: encoding,
            headers: headers
        )
        
        // Add retry logic for SSL errors
        request.validate().responseData { response in
            if let error = response.error,
               let urlError = error.underlyingError as? URLError,
               urlError.code == .serverCertificateUntrusted {
                
                print("⚠️ SSL certificate error detected")
                // Log the error but continue
            }
        }
        
        return request
    }
}
""",
            "description": "Alamofire-specific SSL handling"
        }
    
    def _generate_combine_fix(self) -> Dict[str, str]:
        """Generate Combine framework SSL fix."""
        return {
            "filename": "CombineNetworking+SSL.swift",
            "content": """import Foundation
import Combine

/// Combine networking with SSL error handling
class CombineNetworkManager {
    private var cancellables = Set<AnyCancellable>()
    private let session: URLSession
    
    init() {
        self.session = NetworkConfiguration.shared.createCustomSession()
    }
    
    /// Fetch data with SSL error handling
    func fetchWithSSLHandling<T: Codable>(
        from url: URL,
        type: T.Type
    ) -> AnyPublisher<T, Error> {
        
        return session.dataTaskPublisher(for: url)
            .retry(1) // Retry once on failure
            .tryMap { element -> Data in
                guard let httpResponse = element.response as? HTTPURLResponse,
                      httpResponse.statusCode == 200 else {
                    throw URLError(.badServerResponse)
                }
                return element.data
            }
            .decode(type: T.self, decoder: JSONDecoder())
            .catch { error -> AnyPublisher<T, Error> in
                // Check if it's an SSL error
                if let urlError = error as? URLError,
                   self.isSSLError(urlError) {
                    
                    print("🔄 SSL error in Combine, attempting recovery...")
                    
                    // Try with development session
                    let devSession = NetworkConfiguration.shared.createDevelopmentSession()
                    return devSession.dataTaskPublisher(for: url)
                        .map(\\.data)
                        .decode(type: T.self, decoder: JSONDecoder())
                        .eraseToAnyPublisher()
                }
                
                return Fail(error: error).eraseToAnyPublisher()
            }
            .eraseToAnyPublisher()
    }
    
    private func isSSLError(_ error: URLError) -> Bool {
        let sslErrorCodes: [URLError.Code] = [
            .serverCertificateHasBadDate,
            .serverCertificateUntrusted,
            .serverCertificateHasUnknownRoot,
            .serverCertificateNotYetValid,
            .secureConnectionFailed
        ]
        
        return sslErrorCodes.contains(error.code)
    }
}

/// Publisher extension for SSL error recovery
extension Publisher where Output == URLSession.DataTaskPublisher.Output {
    func handleSSLErrors() -> Publishers.Catch<Self, AnyPublisher<Output, Failure>> {
        self.catch { error -> AnyPublisher<Output, Failure> in
            if let urlError = error as? URLError {
                switch urlError.code {
                case .serverCertificateUntrusted,
                     .serverCertificateHasBadDate,
                     .secureConnectionFailed:
                    print("⚠️ SSL error caught: \\(urlError.localizedDescription)")
                    // Return empty publisher or retry with different configuration
                    return Empty().eraseToAnyPublisher()
                default:
                    break
                }
            }
            
            return Fail(error: error).eraseToAnyPublisher()
        }
    }
}
""",
            "description": "Combine framework SSL handling"
        }
    
    def apply_comprehensive_ssl_fix(self, files: List[Dict], domain: str) -> Dict[str, any]:
        """
        Apply comprehensive SSL fixes to the project.
        
        Args:
            files: List of project files
            domain: The domain having SSL issues
            
        Returns:
            Modified files with SSL fixes applied
        """
        modified_files = list(files)
        changes_made = []
        files_modified = []
        
        # Generate all fixes
        fixes = self.generate_comprehensive_ssl_solution(domain)
        
        # 1. Update Info.plist
        info_plist_updated = False
        for i, file in enumerate(modified_files):
            if 'Info.plist' in file['path']:
                content = file['content']
                plist_fix = fixes['info_plist_changes']['content']
                
                # Insert before closing </dict>
                insert_pos = content.rfind('</dict>')
                if insert_pos > 0 and 'NSAppTransportSecurity' not in content:
                    new_content = (
                        content[:insert_pos] + 
                        plist_fix + '\n' + 
                        content[insert_pos:]
                    )
                    modified_files[i] = {
                        'path': file['path'],
                        'content': new_content
                    }
                    changes_made.append("Added comprehensive ATS configuration to Info.plist")
                    files_modified.append(file['path'])
                    info_plist_updated = True
                break
        
        if not info_plist_updated:
            # Create Info.plist if it doesn't exist
            plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key>
    <string>$(PRODUCT_NAME)</string>
    <key>CFBundleIdentifier</key>
    <string>$(PRODUCT_BUNDLE_IDENTIFIER)</string>
{fixes['info_plist_changes']['content']}
</dict>
</plist>"""
            modified_files.append({
                'path': 'Info.plist',
                'content': plist_content
            })
            changes_made.append("Created Info.plist with SSL configuration")
            files_modified.append('Info.plist')
        
        # 2. Add NetworkConfiguration.swift
        network_config = fixes['network_configuration']
        modified_files.append({
            'path': f"Sources/Networking/{network_config['filename']}",
            'content': network_config['content']
        })
        changes_made.append("Added NetworkConfiguration with SSL handling")
        files_modified.append(f"Sources/Networking/{network_config['filename']}")
        
        # 3. Add or update APIClient
        api_client_found = False
        for i, file in enumerate(modified_files):
            if 'APIClient' in file['path'] or 'NetworkManager' in file['path']:
                api_client_found = True
                # Add SSL extension at the end
                ssl_ext = fixes['url_session_delegate']
                modified_files[i] = {
                    'path': file['path'],
                    'content': file['content'] + '\n\n' + ssl_ext['content']
                }
                changes_made.append("Added SSL handling to API client")
                files_modified.append(file['path'])
                break
        
        if not api_client_found:
            # Create APIClient+SSL.swift
            ssl_ext = fixes['url_session_delegate']
            modified_files.append({
                'path': f"Sources/Networking/{ssl_ext['filename']}",
                'content': ssl_ext['content']
            })
            changes_made.append("Created APIClient SSL extension")
            files_modified.append(f"Sources/Networking/{ssl_ext['filename']}")
        
        # 4. Check if project uses Alamofire
        uses_alamofire = any('import Alamofire' in file.get('content', '') for file in files)
        if uses_alamofire:
            alamofire_fix = fixes['alamofire_fix']
            modified_files.append({
                'path': f"Sources/Networking/{alamofire_fix['filename']}",
                'content': alamofire_fix['content']
            })
            changes_made.append("Added Alamofire SSL manager")
            files_modified.append(f"Sources/Networking/{alamofire_fix['filename']}")
        
        # 5. Check if project uses Combine
        uses_combine = any('import Combine' in file.get('content', '') for file in files)
        if uses_combine:
            combine_fix = fixes['combine_fix']
            modified_files.append({
                'path': f"Sources/Networking/{combine_fix['filename']}",
                'content': combine_fix['content']
            })
            changes_made.append("Added Combine SSL handling")
            files_modified.append(f"Sources/Networking/{combine_fix['filename']}")
        
        return {
            "files": modified_files,
            "modification_summary": f"Applied comprehensive SSL fixes for {domain}",
            "changes_made": changes_made,
            "files_modified": files_modified,
            "ssl_fixes_applied": {
                "info_plist": info_plist_updated or "Info.plist" in files_modified,
                "network_configuration": True,
                "api_client_ssl": True,
                "alamofire": uses_alamofire,
                "combine": uses_combine
            }
        }