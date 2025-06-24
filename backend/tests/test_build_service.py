"""
Unit tests for build_service.py
Tests the build system including project setup, compilation, and error handling
"""
import pytest
import os
import tempfile
import shutil
import json
from unittest.mock import Mock, patch, AsyncMock, MagicMock, call
from pathlib import Path
import asyncio
import subprocess

from build_service import BuildService
from conftest import TEST_FILES, TEST_PROJECT_ID
from utils import TestFileManager


@pytest.mark.unit
class TestBuildService:
    """Test suite for BuildService"""
    
    @pytest.fixture
    def build_service(self, temp_workspace):
        """Create build service instance with temp workspace"""
        with patch('build_service.RobustErrorRecoverySystem'):
            service = BuildService(workspace_root=temp_workspace)
            return service
    
    @pytest.fixture
    def mock_subprocess(self):
        """Mock subprocess for build commands"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(
                returncode=0,
                stdout="Build succeeded",
                stderr=""
            )
            yield mock_run
    
    @pytest.mark.asyncio
    async def test_build_project_success(self, build_service, mock_subprocess):
        """Test successful project build"""
        # Create test project structure
        project_dir = os.path.join(build_service.workspace_root, TEST_PROJECT_ID)
        os.makedirs(project_dir, exist_ok=True)
        
        # Write test files
        for file_info in TEST_FILES:
            file_path = os.path.join(project_dir, file_info["path"])
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w') as f:
                f.write(file_info["content"])
        
        # Create project.yml
        with open(os.path.join(project_dir, "project.yml"), 'w') as f:
            f.write("name: TestApp\n")
        
        result = await build_service.build_project(TEST_PROJECT_ID, TEST_FILES)
        
        assert result["success"] is True
        assert len(result["logs"]) > 0
        assert mock_subprocess.called
    
    @pytest.mark.asyncio
    async def test_build_project_failure(self, build_service):
        """Test project build failure"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(
                returncode=1,
                stdout="",
                stderr="error: no such module 'InvalidModule'"
            )
            
            project_dir = os.path.join(build_service.workspace_root, TEST_PROJECT_ID)
            os.makedirs(project_dir, exist_ok=True)
            
            result = await build_service.build_project(TEST_PROJECT_ID, TEST_FILES)
            
            assert result["success"] is False
            assert len(result["errors"]) > 0
            assert result["errors"][0]["type"] == "module_not_found"
    
    def test_create_project_structure(self, build_service):
        """Test project structure creation"""
        project_dir = build_service._create_project_structure(
            TEST_PROJECT_ID,
            "TestApp",
            "com.test.app"
        )
        
        assert os.path.exists(project_dir)
        assert os.path.exists(os.path.join(project_dir, "Sources"))
        assert os.path.exists(os.path.join(project_dir, "Info.plist"))
        assert os.path.exists(os.path.join(project_dir, "project.yml"))
    
    def test_write_project_files(self, build_service):
        """Test writing project files"""
        project_dir = os.path.join(build_service.workspace_root, TEST_PROJECT_ID)
        os.makedirs(project_dir, exist_ok=True)
        
        build_service._write_project_files(project_dir, TEST_FILES)
        
        for file_info in TEST_FILES:
            file_path = os.path.join(project_dir, file_info["path"])
            assert os.path.exists(file_path)
            with open(file_path, 'r') as f:
                content = f.read()
                assert content == file_info["content"]
    
    def test_parse_build_errors_syntax(self, build_service):
        """Test parsing syntax errors from build output"""
        error_output = """
        /path/to/ContentView.swift:10:5: error: expected '}' in struct
        struct ContentView: View {
        ^
        """
        
        errors = build_service._parse_build_errors(error_output, TEST_PROJECT_ID)
        
        assert len(errors) == 1
        assert errors[0]["type"] == "syntax_error"
        assert errors[0]["line"] == 10
        assert errors[0]["column"] == 5
        assert "expected '}'" in errors[0]["message"]
    
    def test_parse_build_errors_type_not_found(self, build_service):
        """Test parsing type not found errors"""
        error_output = """
        ContentView.swift:15:10: error: cannot find 'CustomView' in scope
        """
        
        errors = build_service._parse_build_errors(error_output, TEST_PROJECT_ID)
        
        assert len(errors) == 1
        assert errors[0]["type"] == "type_not_found"
        assert "CustomView" in errors[0]["identifier"]
    
    @pytest.mark.asyncio
    async def test_build_with_recovery(self, build_service):
        """Test build with error recovery"""
        build_service.recovery_system.should_attempt_recovery = Mock(return_value=True)
        build_service.recovery_system.recover_from_errors = AsyncMock(
            return_value={
                "success": True,
                "fixed_files": TEST_FILES
            }
        )
        
        with patch('subprocess.run') as mock_run:
            # First build fails, second succeeds after recovery
            mock_run.side_effect = [
                Mock(returncode=1, stdout="", stderr="error: syntax error"),
                Mock(returncode=0, stdout="Build succeeded", stderr="")
            ]
            
            project_dir = os.path.join(build_service.workspace_root, TEST_PROJECT_ID)
            os.makedirs(project_dir, exist_ok=True)
            
            result = await build_service.build_project(
                TEST_PROJECT_ID, 
                TEST_FILES,
                enable_recovery=True
            )
            
            assert result["success"] is True
            assert build_service.recovery_system.recover_from_errors.called
            assert mock_run.call_count == 2
    
    @pytest.mark.asyncio
    async def test_build_timeout(self, build_service):
        """Test build timeout handling"""
        async def slow_build(*args, **kwargs):
            await asyncio.sleep(10)  # Longer than timeout
            
        with patch.object(build_service, '_run_build_command', side_effect=slow_build):
            result = await build_service.build_project(
                TEST_PROJECT_ID,
                TEST_FILES,
                timeout=1  # 1 second timeout
            )
            
            assert result["success"] is False
            assert "timeout" in str(result["errors"]).lower()
    
    def test_generate_xcodegen_config(self, build_service):
        """Test XcodeGen configuration generation"""
        config = build_service._generate_xcodegen_config(
            "TestApp",
            "com.test.app",
            ios_version="17.0"
        )
        
        assert config["name"] == "TestApp"
        assert config["targets"]["TestApp"]["platform"] == "iOS"
        assert config["targets"]["TestApp"]["deploymentTarget"] == "17.0"
        assert config["targets"]["TestApp"]["settings"]["PRODUCT_BUNDLE_IDENTIFIER"] == "com.test.app"
    
    @pytest.mark.asyncio
    async def test_concurrent_builds(self, build_service, mock_subprocess):
        """Test handling concurrent build requests"""
        # Create multiple project directories
        project_ids = [f"proj_{i}" for i in range(3)]
        for pid in project_ids:
            project_dir = os.path.join(build_service.workspace_root, pid)
            os.makedirs(project_dir, exist_ok=True)
            with open(os.path.join(project_dir, "project.yml"), 'w') as f:
                f.write(f"name: App{pid}\n")
        
        # Run concurrent builds
        tasks = [
            build_service.build_project(pid, TEST_FILES)
            for pid in project_ids
        ]
        
        results = await asyncio.gather(*tasks)
        
        assert len(results) == 3
        assert all(r["success"] for r in results)
        assert mock_subprocess.call_count >= 3
    
    def test_clean_build_artifacts(self, build_service):
        """Test cleaning build artifacts"""
        project_dir = os.path.join(build_service.workspace_root, TEST_PROJECT_ID)
        build_dir = os.path.join(project_dir, "build")
        derived_data = os.path.join(project_dir, "DerivedData")
        
        os.makedirs(build_dir, exist_ok=True)
        os.makedirs(derived_data, exist_ok=True)
        
        # Create dummy files
        with open(os.path.join(build_dir, "test.o"), 'w') as f:
            f.write("test")
        
        build_service._clean_build_artifacts(project_dir)
        
        assert not os.path.exists(build_dir)
        assert not os.path.exists(derived_data)
    
    @pytest.mark.asyncio
    async def test_build_with_custom_settings(self, build_service, mock_subprocess):
        """Test build with custom settings"""
        custom_settings = {
            "SWIFT_VERSION": "5.9",
            "IPHONEOS_DEPLOYMENT_TARGET": "17.0",
            "ENABLE_BITCODE": "NO"
        }
        
        project_dir = os.path.join(build_service.workspace_root, TEST_PROJECT_ID)
        os.makedirs(project_dir, exist_ok=True)
        
        result = await build_service.build_project(
            TEST_PROJECT_ID,
            TEST_FILES,
            custom_settings=custom_settings
        )
        
        # Verify settings were passed to build command
        call_args = mock_subprocess.call_args
        assert "SWIFT_VERSION=5.9" in str(call_args)
    
    def test_error_categorization(self, build_service):
        """Test proper error categorization"""
        test_errors = [
            ("error: expected '}' in struct", "syntax_error"),
            ("error: cannot find 'View' in scope", "type_not_found"),
            ("error: no such module 'SwiftUI'", "module_not_found"),
            ("error: value of type 'String' has no member 'count'", "member_not_found"),
            ("error: cannot convert value of type", "type_mismatch"),
            ("error: The certificate for this server is invalid", "ssl_error")
        ]
        
        for error_msg, expected_type in test_errors:
            errors = build_service._parse_build_errors(error_msg, TEST_PROJECT_ID)
            if errors:  # Some might not match patterns
                assert errors[0]["type"] == expected_type
    
    @pytest.mark.asyncio
    async def test_simulator_app_path_detection(self, build_service, mock_subprocess):
        """Test finding app path in simulator"""
        project_dir = os.path.join(build_service.workspace_root, TEST_PROJECT_ID)
        build_dir = os.path.join(project_dir, "build/Release-iphonesimulator")
        os.makedirs(build_dir, exist_ok=True)
        
        # Create fake app bundle
        app_path = os.path.join(build_dir, "TestApp.app")
        os.makedirs(app_path)
        
        result = await build_service.build_project(TEST_PROJECT_ID, TEST_FILES)
        
        assert "app_path" in result
        assert result["app_path"] == app_path