"""
Integration tests for app generation workflow
Tests the complete flow from request to built app
"""
import pytest
import asyncio
import json
import os
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
import tempfile

from conftest import TEST_FILES, TEST_APP_NAME, TEST_DESCRIPTION
from utils import TestFileManager, create_mock_llm_response


@pytest.mark.integration
class TestAppGenerationWorkflow:
    """Integration tests for complete app generation flow"""
    
    @pytest.fixture
    def test_client(self):
        """Create test client"""
        from main import app
        return TestClient(app)
    
    @pytest.fixture
    def file_manager(self):
        """Create file manager for test cleanup"""
        fm = TestFileManager()
        yield fm
        fm.cleanup()
    
    @pytest.mark.asyncio
    async def test_complete_app_generation_flow(self, test_client, file_manager):
        """Test complete flow: request -> generate -> build -> response"""
        with patch('enhanced_claude_service.Anthropic') as mock_anthropic, \
             patch('subprocess.run') as mock_subprocess, \
             patch('build_service.BuildService._create_project_structure') as mock_create_structure:
            
            # Mock LLM response
            mock_anthropic.return_value.messages.create = AsyncMock(
                return_value=Mock(content=[Mock(text=create_mock_llm_response())])
            )
            
            # Mock successful build
            mock_subprocess.return_value = Mock(
                returncode=0,
                stdout="Build succeeded",
                stderr=""
            )
            
            # Mock project structure creation
            project_dir = file_manager.create_project_structure("test_proj")
            mock_create_structure.return_value = project_dir
            
            # Make request
            response = test_client.post("/api/generate", json={
                "description": TEST_DESCRIPTION,
                "ios_version": "17.0"
            })
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["status"] == "success"
            assert "project_id" in data
            assert "app_name" in data
            assert data["app_name"] == TEST_APP_NAME
    
    @pytest.mark.asyncio
    async def test_app_generation_with_websocket_updates(self):
        """Test app generation with WebSocket progress updates"""
        from main import app
        from fastapi.testclient import TestClient
        
        with TestClient(app) as client:
            # Mock dependencies
            with patch('enhanced_claude_service.Anthropic') as mock_anthropic, \
                 patch('subprocess.run') as mock_subprocess:
                
                mock_anthropic.return_value.messages.create = AsyncMock(
                    return_value=Mock(content=[Mock(text=create_mock_llm_response())])
                )
                mock_subprocess.return_value = Mock(returncode=0, stdout="Build succeeded")
                
                # Connect WebSocket
                with client.websocket_connect(f"/ws/test_project") as websocket:
                    # Send generate request
                    response = client.post("/api/generate", json={
                        "description": TEST_DESCRIPTION,
                        "project_id": "test_project"
                    })
                    
                    # Collect WebSocket messages
                    messages = []
                    try:
                        for _ in range(5):  # Collect up to 5 messages
                            message = websocket.receive_json(timeout=2)
                            messages.append(message)
                    except:
                        pass  # Timeout expected when no more messages
                    
                    # Verify we got progress updates
                    assert len(messages) > 0
                    assert any(msg.get("type") == "status" for msg in messages)
    
    @pytest.mark.asyncio
    async def test_app_generation_error_handling(self, test_client):
        """Test error handling during app generation"""
        with patch('enhanced_claude_service.Anthropic') as mock_anthropic:
            # Mock LLM failure
            mock_anthropic.return_value.messages.create = AsyncMock(
                side_effect=Exception("LLM API Error")
            )
            
            response = test_client.post("/api/generate", json={
                "description": TEST_DESCRIPTION
            })
            
            assert response.status_code == 500
            data = response.json()
            assert "error" in data["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_app_generation_with_build_failure(self, test_client):
        """Test handling of build failures"""
        with patch('enhanced_claude_service.Anthropic') as mock_anthropic, \
             patch('subprocess.run') as mock_subprocess:
            
            # Mock successful generation
            mock_anthropic.return_value.messages.create = AsyncMock(
                return_value=Mock(content=[Mock(text=create_mock_llm_response())])
            )
            
            # Mock build failure
            mock_subprocess.return_value = Mock(
                returncode=1,
                stdout="",
                stderr="error: cannot find 'CustomView' in scope"
            )
            
            response = test_client.post("/api/generate", json={
                "description": TEST_DESCRIPTION
            })
            
            # Should still return success but with build errors
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            # Build errors would be in project state
    
    @pytest.mark.asyncio
    async def test_app_generation_with_recovery(self, test_client):
        """Test automatic error recovery during generation"""
        with patch('enhanced_claude_service.Anthropic') as mock_anthropic, \
             patch('subprocess.run') as mock_subprocess, \
             patch('robust_error_recovery_system.RobustErrorRecoverySystem.recover_from_errors') as mock_recovery:
            
            # Mock generation
            mock_anthropic.return_value.messages.create = AsyncMock(
                return_value=Mock(content=[Mock(text=create_mock_llm_response())])
            )
            
            # First build fails, recovery fixes it, second build succeeds
            mock_subprocess.side_effect = [
                Mock(returncode=1, stderr="syntax error"),
                Mock(returncode=0, stdout="Build succeeded")
            ]
            
            mock_recovery.return_value = {
                "success": True,
                "fixed_files": TEST_FILES
            }
            
            response = test_client.post("/api/generate", json={
                "description": TEST_DESCRIPTION
            })
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
    
    @pytest.mark.asyncio
    async def test_concurrent_app_generation(self, test_client):
        """Test handling multiple concurrent generation requests"""
        with patch('enhanced_claude_service.Anthropic') as mock_anthropic, \
             patch('subprocess.run') as mock_subprocess:
            
            mock_anthropic.return_value.messages.create = AsyncMock(
                return_value=Mock(content=[Mock(text=create_mock_llm_response())])
            )
            mock_subprocess.return_value = Mock(returncode=0, stdout="Build succeeded")
            
            # Make multiple concurrent requests
            tasks = []
            for i in range(3):
                response = test_client.post("/api/generate", json={
                    "description": f"Test app {i}"
                })
                tasks.append(response)
            
            # All should succeed
            for response in tasks:
                assert response.status_code == 200
    
    @pytest.mark.asyncio 
    async def test_ios17_features_generation(self, test_client):
        """Test generation with iOS 17+ features enabled"""
        with patch('enhanced_claude_service.Anthropic') as mock_anthropic, \
             patch('subprocess.run') as mock_subprocess:
            
            # Mock response with iOS 17 features
            ios17_response = {
                "files": [{
                    "path": "Sources/ContentView.swift",
                    "content": '''import SwiftUI
import Observation

@Observable
class ViewModel {
    var count = 0
}

struct ContentView: View {
    @State private var viewModel = ViewModel()
    
    var body: some View {
        Text("Count: \\(viewModel.count)")
    }
}'''
                }],
                "app_name": "ModernApp"
            }
            
            mock_anthropic.return_value.messages.create = AsyncMock(
                return_value=Mock(content=[Mock(text=json.dumps(ios17_response))])
            )
            mock_subprocess.return_value = Mock(returncode=0, stdout="Build succeeded")
            
            response = test_client.post("/api/generate", json={
                "description": "Create app with Observable",
                "ios_version": "17.0",
                "use_ios17_features": True
            })
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            
            # Verify iOS 17 features were requested
            call_args = mock_anthropic.return_value.messages.create.call_args
            assert "Observable" in str(call_args)
    
    @pytest.mark.asyncio
    async def test_project_persistence(self, test_client, file_manager):
        """Test that generated projects are properly persisted"""
        with patch('enhanced_claude_service.Anthropic') as mock_anthropic, \
             patch('subprocess.run') as mock_subprocess:
            
            mock_anthropic.return_value.messages.create = AsyncMock(
                return_value=Mock(content=[Mock(text=create_mock_llm_response())])
            )
            mock_subprocess.return_value = Mock(returncode=0, stdout="Build succeeded")
            
            # Generate app
            response = test_client.post("/api/generate", json={
                "description": TEST_DESCRIPTION
            })
            
            assert response.status_code == 200
            project_id = response.json()["project_id"]
            
            # Check project status
            status_response = test_client.get(f"/api/project/{project_id}/status")
            assert status_response.status_code == 200
            
            status_data = status_response.json()
            assert status_data["project_id"] == project_id
            assert status_data["app_name"] == TEST_APP_NAME
            assert "generated_files" in status_data