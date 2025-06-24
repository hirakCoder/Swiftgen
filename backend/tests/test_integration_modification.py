"""
Integration tests for modification workflow
Tests the complete modification flow including verification
"""
import pytest
import asyncio
import json
import os
from unittest.mock import Mock, patch, AsyncMock, call
from fastapi.testclient import TestClient

from conftest import TEST_FILES, TEST_APP_NAME, TEST_PROJECT_ID
from utils import create_mock_modification_response


@pytest.mark.integration
class TestModificationWorkflow:
    """Integration tests for modification workflow"""
    
    @pytest.fixture
    def test_client(self):
        """Create test client"""
        from main import app
        return TestClient(app)
    
    @pytest.fixture
    def mock_project_state(self):
        """Create mock project state"""
        return {
            "project_id": TEST_PROJECT_ID,
            "app_name": TEST_APP_NAME,
            "generated_files": TEST_FILES,
            "modification_history": [],
            "status": "ready"
        }
    
    @pytest.mark.asyncio
    async def test_simple_modification_flow(self, test_client, mock_project_state):
        """Test simple modification: request -> modify -> verify -> build"""
        with patch('project_manager.ProjectManager.get_project') as mock_get_project, \
             patch('project_manager.ProjectManager.read_project_files') as mock_read_files, \
             patch('enhanced_claude_service.EnhancedClaudeService.apply_modification') as mock_modify, \
             patch('modification_verifier.ModificationVerifier.verify_modifications') as mock_verify, \
             patch('subprocess.run') as mock_subprocess:
            
            # Setup mocks
            mock_get_project.return_value = mock_project_state
            mock_read_files.return_value = TEST_FILES
            mock_modify.return_value = {
                "modified_files": [{
                    "path": "Sources/ContentView.swift",
                    "content": "struct ContentView: View {\n    var body: some View {\n        Button(\"Test\") { }\n    }\n}"
                }]
            }
            mock_verify.return_value = {
                "files_changed": 1,
                "total_files": 2,
                "changes_detected": True
            }
            mock_subprocess.return_value = Mock(returncode=0, stdout="Build succeeded")
            
            # Make modification request
            response = test_client.post("/api/modify", json={
                "project_id": TEST_PROJECT_ID,
                "modification": "Add a button to the main view"
            })
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            
            # Verify the flow
            assert mock_get_project.called
            assert mock_modify.called
            assert mock_verify.called
    
    @pytest.mark.asyncio
    async def test_modification_with_verification_failure(self, test_client, mock_project_state):
        """Test modification when verification detects no changes"""
        with patch('project_manager.ProjectManager.get_project') as mock_get_project, \
             patch('project_manager.ProjectManager.read_project_files') as mock_read_files, \
             patch('enhanced_claude_service.EnhancedClaudeService.apply_modification') as mock_modify, \
             patch('modification_verifier.ModificationVerifier.verify_modifications') as mock_verify:
            
            mock_get_project.return_value = mock_project_state
            mock_read_files.return_value = TEST_FILES
            
            # LLM returns unchanged files
            mock_modify.return_value = {"modified_files": TEST_FILES}
            
            # Verification detects no changes
            mock_verify.return_value = {
                "files_changed": 0,
                "total_files": 2,
                "changes_detected": False
            }
            
            response = test_client.post("/api/modify", json={
                "project_id": TEST_PROJECT_ID,
                "modification": "Add feature"
            })
            
            # Should handle gracefully with retry logic
            assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_dark_theme_modification(self, test_client, mock_project_state):
        """Test dark theme specific modification"""
        with patch('project_manager.ProjectManager.get_project') as mock_get_project, \
             patch('project_manager.ProjectManager.read_project_files') as mock_read_files, \
             patch('modification_handler.ModificationHandler.detect_issue_type') as mock_detect, \
             patch('modification_handler.ModificationHandler._implement_dark_theme') as mock_dark_theme, \
             patch('subprocess.run') as mock_subprocess:
            
            mock_get_project.return_value = mock_project_state
            mock_read_files.return_value = TEST_FILES
            mock_detect.return_value = ("dark_theme", {})
            mock_dark_theme.return_value = {
                "modified_files": [{
                    "path": "Sources/ContentView.swift",
                    "content": "// Dark theme implemented"
                }]
            }
            mock_subprocess.return_value = Mock(returncode=0)
            
            response = test_client.post("/api/modify", json={
                "project_id": TEST_PROJECT_ID,
                "modification": "Add dark mode toggle"
            })
            
            assert response.status_code == 200
            assert mock_dark_theme.called
    
    @pytest.mark.asyncio
    async def test_ssl_error_modification(self, test_client, mock_project_state):
        """Test SSL error fix modification"""
        with patch('project_manager.ProjectManager.get_project') as mock_get_project, \
             patch('project_manager.ProjectManager.read_project_files') as mock_read_files, \
             patch('modification_handler.ModificationHandler.detect_issue_type') as mock_detect, \
             patch('modification_handler.ModificationHandler.apply_ssl_fix') as mock_ssl_fix, \
             patch('subprocess.run') as mock_subprocess:
            
            mock_get_project.return_value = mock_project_state
            mock_read_files.return_value = TEST_FILES
            mock_detect.return_value = ("ssl_error", {"domain": "api.example.com"})
            mock_ssl_fix.return_value = {
                "fix_applied": True,
                "modified_files": TEST_FILES
            }
            mock_subprocess.return_value = Mock(returncode=0)
            
            response = test_client.post("/api/modify", json={
                "project_id": TEST_PROJECT_ID,
                "modification": "App crashes with SSL error for api.example.com"
            })
            
            assert response.status_code == 200
            assert mock_ssl_fix.called
    
    @pytest.mark.asyncio
    async def test_multiple_sequential_modifications(self, test_client, mock_project_state):
        """Test multiple modifications in sequence"""
        with patch('project_manager.ProjectManager.get_project') as mock_get_project, \
             patch('project_manager.ProjectManager.read_project_files') as mock_read_files, \
             patch('enhanced_claude_service.EnhancedClaudeService.apply_modification') as mock_modify, \
             patch('subprocess.run') as mock_subprocess:
            
            mock_get_project.return_value = mock_project_state
            mock_subprocess.return_value = Mock(returncode=0)
            
            modifications = [
                "Add a button",
                "Change button color to blue",
                "Add dark mode",
                "Fix the count bug"
            ]
            
            # Mock different responses for each modification
            mock_modify.side_effect = [
                {"modified_files": [{"path": "ContentView.swift", "content": f"// Mod {i}"}]}
                for i in range(len(modifications))
            ]
            
            # Fresh files for each modification
            mock_read_files.return_value = TEST_FILES
            
            # Apply modifications
            for i, mod in enumerate(modifications):
                response = test_client.post("/api/modify", json={
                    "project_id": TEST_PROJECT_ID,
                    "modification": mod
                })
                
                assert response.status_code == 200
                
                # Update mock state to simulate history
                mock_project_state["modification_history"].append({
                    "type": "modification",
                    "description": mod
                })
            
            # Verify all modifications were attempted
            assert mock_modify.call_count == len(modifications)
    
    @pytest.mark.asyncio
    async def test_modification_with_websocket_updates(self):
        """Test modification with real-time WebSocket updates"""
        from main import app
        from fastapi.testclient import TestClient
        
        with TestClient(app) as client:
            with patch('project_manager.ProjectManager.get_project') as mock_get_project, \
                 patch('enhanced_claude_service.EnhancedClaudeService.apply_modification') as mock_modify, \
                 patch('subprocess.run') as mock_subprocess:
                
                mock_get_project.return_value = {
                    "project_id": TEST_PROJECT_ID,
                    "app_name": TEST_APP_NAME,
                    "generated_files": TEST_FILES
                }
                mock_modify.return_value = {"modified_files": TEST_FILES}
                mock_subprocess.return_value = Mock(returncode=0)
                
                # Connect WebSocket
                with client.websocket_connect(f"/ws/{TEST_PROJECT_ID}") as websocket:
                    # Send modification via WebSocket
                    websocket.send_json({
                        "type": "modify",
                        "project_id": TEST_PROJECT_ID,
                        "modification": "Add a feature"
                    })
                    
                    # Collect messages
                    messages = []
                    try:
                        for _ in range(5):
                            message = websocket.receive_json(timeout=2)
                            messages.append(message)
                    except:
                        pass
                    
                    # Should receive status updates
                    assert any(msg.get("type") == "status" for msg in messages)
                    assert any("modif" in str(msg).lower() for msg in messages)
    
    @pytest.mark.asyncio
    async def test_modification_error_recovery(self, test_client, mock_project_state):
        """Test modification with build error recovery"""
        with patch('project_manager.ProjectManager.get_project') as mock_get_project, \
             patch('project_manager.ProjectManager.read_project_files') as mock_read_files, \
             patch('enhanced_claude_service.EnhancedClaudeService.apply_modification') as mock_modify, \
             patch('subprocess.run') as mock_subprocess, \
             patch('robust_error_recovery_system.RobustErrorRecoverySystem.recover_from_errors') as mock_recovery:
            
            mock_get_project.return_value = mock_project_state
            mock_read_files.return_value = TEST_FILES
            mock_modify.return_value = {"modified_files": TEST_FILES}
            
            # First build fails, recovery fixes, second build succeeds
            mock_subprocess.side_effect = [
                Mock(returncode=1, stderr="syntax error"),
                Mock(returncode=0, stdout="Build succeeded")
            ]
            
            mock_recovery.return_value = {
                "success": True,
                "fixed_files": TEST_FILES
            }
            
            response = test_client.post("/api/modify", json={
                "project_id": TEST_PROJECT_ID,
                "modification": "Add feature"
            })
            
            assert response.status_code == 200
            assert mock_recovery.called
            assert mock_subprocess.call_count == 2
    
    @pytest.mark.asyncio
    async def test_chat_based_modification(self, test_client, mock_project_state):
        """Test modification through chat interface"""
        with patch('project_manager.ProjectManager.get_project') as mock_get_project, \
             patch('enhanced_claude_service.EnhancedClaudeService.apply_modification') as mock_modify, \
             patch('subprocess.run') as mock_subprocess:
            
            mock_get_project.return_value = mock_project_state
            mock_modify.return_value = {"modified_files": TEST_FILES}
            mock_subprocess.return_value = Mock(returncode=0)
            
            # Send chat message for existing project
            response = test_client.post("/api/chat", json={
                "message": "Add a dark mode toggle",
                "project_id": TEST_PROJECT_ID,
                "context": {"app_name": TEST_APP_NAME}
            })
            
            assert response.status_code == 200
            data = response.json()
            
            # Should get contextual response (not "Perfect!")
            assert "dark" in data["response"].lower()
            assert TEST_APP_NAME in data["response"]
            assert data["action"] == "modify"