// SwiftGen AI - Modern Chat Interface with Complete Features
class SwiftGenChat {
    constructor() {
        this.ws = null;
        this.currentProjectId = null;
        this.generatedFiles = [];
        this.messageHistory = [];
        this.isProcessing = false;
        this.currentContext = {
            appName: '',
            description: '',
            features: []
        };
        this.projects = [];
        this.buildLogs = [];
        this.editingFile = null;

        this.initializeEventListeners();
        this.setupTextareaAutoResize();
        this.initializeProgress();
        this.loadProjects();
    }

    initializeEventListeners() {
        // Chat form submission
        document.getElementById('chatForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleChatSubmit();
        });

        // New project button
        document.getElementById('newChatBtn').addEventListener('click', () => {
            this.startNewProject();
        });

        // Enter key handling for textarea
        document.getElementById('chatInput').addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.handleChatSubmit();
            }
        });

        // View logs button
        document.addEventListener('click', (e) => {
            if (e.target.textContent === 'View Logs') {
                this.showBuildLogs();
            }
        });
    }
    // Add this method to open the code editor
    openCodeEditor() {
        if (!this.currentProjectId) {
            this.addMessage('assistant', 'Please create or load a project first to use the code editor.');
            return;
        }

        // Open editor in new tab/window
        const editorUrl = `/editor.html?project=${this.currentProjectId}`;
        window.open(editorUrl, '_blank');
    }

    setupTextareaAutoResize() {
        const textarea = document.getElementById('chatInput');
        textarea.addEventListener('input', () => {
            textarea.style.height = 'auto';
            textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
        });
    }

    initializeProgress() {
        this.progressSteps = {
            generate: { percent: 20, text: 'Generating Swift code...', completed: false },
            create: { percent: 40, text: 'Creating project structure...', completed: false },
            build: { percent: 60, text: 'Building app...', completed: false },
            install: { percent: 80, text: 'Installing to simulator...', completed: false },
            launch: { percent: 100, text: 'Launching app...', completed: false }
        };

        // Reset progress state
        Object.keys(this.progressSteps).forEach(step => {
            this.progressSteps[step].completed = false;
        });
    }

    async loadProjects() {
        try {
            const response = await fetch('/api/projects');
            if (response.ok) {
                this.projects = await response.json();
                this.updateProjectsList();
            }
        } catch (error) {
            console.error('Failed to load projects:', error);
        }
    }

    updateProjectsList() {
        const projectInfo = document.getElementById('projectInfo');
        if (this.projects.length > 0) {
            projectInfo.innerHTML = `
                <select id="projectSelect" class="bg-dark-surface border border-dark-border rounded px-2 py-1 text-sm">
                    <option value="">Select a project</option>
                    ${this.projects.map(p => `
                        <option value="${p.project_id}">${p.app_name} - ${new Date(p.created_at).toLocaleDateString()}</option>
                    `).join('')}
                </select>
            `;

            document.getElementById('projectSelect').addEventListener('change', (e) => {
                if (e.target.value) {
                    this.loadProject(e.target.value);
                }
            });
        }
    }

    async loadProject(projectId) {
        try {
            const response = await fetch(`/api/project/${projectId}/status`);
            if (response.ok) {
                const project = await response.json();
                this.currentProjectId = projectId;
                this.currentContext = project.context || {};

                // Load project files
                const filesResponse = await fetch(`/api/project/${projectId}/files`);
                if (filesResponse.ok) {
                    const filesData = await filesResponse.json();
                    this.generatedFiles = filesData.files;
                    this.displayGeneratedCode(this.generatedFiles);
                }

                // Update UI
                document.getElementById('projectName').textContent = `Project: ${project.app_name}`;
                this.addMessage('assistant', `Loaded project: ${project.app_name}. You can now modify it or view the code.`);

                // Connect WebSocket
                this.connectWebSocket(projectId);
            }
        } catch (error) {
            console.error('Failed to load project:', error);
            this.addMessage('assistant', 'Failed to load project. Please try again.');
        }
    }

    async handleChatSubmit() {
        const input = document.getElementById('chatInput');
        const message = input.value.trim();

        if (!message || this.isProcessing) return;

        // Add user message to chat
        this.addMessage('user', message);

        // Clear input
        input.value = '';
        input.style.height = 'auto';

        // Determine intent
        const intent = this.analyzeIntent(message);

        if (intent.type === 'create_app') {
            await this.createNewApp(intent.appName, message);
        } else if (intent.type === 'modify_app' && this.currentProjectId) {
            await this.modifyExistingApp(message);
        } else if (intent.type === 'question') {
            this.handleQuestion(message);
        } else {
            this.addMessage('assistant', "I can help you create or modify iOS apps. Try describing an app you'd like to build!");
        }
    }

    analyzeIntent(message) {
        const lowerMessage = message.toLowerCase();

        // Check for app creation keywords
        const createKeywords = ['create', 'build', 'make', 'develop', 'new'];
        const hasCreateKeyword = createKeywords.some(keyword => lowerMessage.includes(keyword));

        // Check for modification keywords
        const modifyKeywords = ['add', 'change', 'modify', 'update', 'remove', 'delete', 'fix', 'edit'];
        const hasModifyKeyword = modifyKeywords.some(keyword => lowerMessage.includes(keyword));

        // Extract app name if mentioned
        let appName = 'MyApp';
        const appNameMatch = message.match(/(?:called?|named?)\s+["']?([^"']+)["']?/i);
        if (appNameMatch) {
            appName = appNameMatch[1].trim();
        }

        if (hasCreateKeyword || (!this.currentProjectId && !hasModifyKeyword)) {
            return { type: 'create_app', appName };
        } else if (hasModifyKeyword && this.currentProjectId) {
            return { type: 'modify_app' };
        } else {
            return { type: 'question' };
        }
    }

    async createNewApp(appName, description) {
        this.isProcessing = true;
        this.initializeProgress(); // Reset progress
        this.showProgress();
        this.buildLogs = []; // Clear previous logs

        // Update context
        this.currentContext = {
            appName,
            description,
            features: []
        };

        // Update project name display
        document.getElementById('projectName').textContent = `Building: ${appName}`;

        // Show initial assistant response
        this.addMessage('assistant', `Great! I'll create ${appName} for you. Let me generate the Swift code and build it...`, true);

        try {
            // Generate project ID for WebSocket
            const tempProjectId = `proj_${Date.now()}`;
            this.connectWebSocket(tempProjectId);

            // Make API request
            const response = await fetch('/api/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    app_name: appName,
                    description: description
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            this.currentProjectId = result.project_id;

            // Display generated files
            if (result.generated_files && result.generated_files.length > 0) {
                this.generatedFiles = result.generated_files;
                this.displayGeneratedCode(result.generated_files);
            }

            // Handle build results
            if (result.status === 'success') {
                this.updateProgress('launch', 100);

                let successMessage = `✅ ${appName} has been successfully created and built!`;
                if (result.simulator_launched) {
                    successMessage += '\n\n📱 The app is now running in the iOS Simulator. Check your simulator to see it in action!';
                    this.showSimulatorStatus(true);
                }
                successMessage += '\n\nYou can now:\n• Ask me to make changes to the app\n• Edit the code directly\n• View build logs\n• Export your project';

                this.addMessage('assistant', successMessage);
                this.updateStatus('ready', 'App running in simulator');

                // Reload projects list
                this.loadProjects();
            } else {
                this.addMessage('assistant', '❌ There was an error building the app. Let me check what went wrong...', false, result.build_result.errors);
                this.buildLogs = result.build_result.errors || [];
            }

        } catch (error) {
            console.error('Error:', error);
            this.addMessage('assistant', `❌ Failed to create app: ${error.message}`);
        } finally {
            this.isProcessing = false;
            setTimeout(() => this.hideProgress(), 2000);
        }
    }

    async modifyExistingApp(request) {
        this.isProcessing = true;
        this.showProgress();
        this.buildLogs = [];

        this.addMessage('assistant', "I'll modify your app based on your request. Let me update the code and rebuild...", true);

        try {
            const response = await fetch('/api/modify', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    project_id: this.currentProjectId,
                    modification: request,
                    context: this.currentContext
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();

            // Update files display
            if (result.modified_files && result.modified_files.length > 0) {
                this.generatedFiles = result.modified_files;
                this.displayGeneratedCode(result.modified_files);
            }

            if (result.status === 'success') {
                this.updateProgress('launch', 100);

                let message = `✅ I've successfully modified your app!\n\n`;
                if (result.features_added && result.features_added.length > 0) {
                    message += `New features added:\n${result.features_added.map(f => `• ${f}`).join('\n')}`;
                }
                message += '\n\nThe app has been rebuilt and relaunched in the simulator.';

                this.addMessage('assistant', message);
                this.updateStatus('ready', 'App modified and running');
            } else {
                this.addMessage('assistant', '❌ Failed to modify the app. Check the errors below.', false, result.build_result.errors);
                this.buildLogs = result.build_result.errors || [];
            }

        } catch (error) {
            console.error('Error:', error);
            this.addMessage('assistant', `❌ Failed to modify app: ${error.message}`);
        } finally {
            this.isProcessing = false;
            setTimeout(() => this.hideProgress(), 2000);
        }
    }

    handleQuestion(message) {
        // Handle general questions about SwiftGen
        const responses = {
            'help': "I can help you create iOS apps using natural language! Just describe what you want to build, and I'll generate the Swift code and launch it in the simulator.",
            'features': "I can create various types of iOS apps including:\n• Todo lists\n• Calculators\n• Weather apps\n• Timers\n• Note-taking apps\n• Chat interfaces\n\nJust describe what you want!",
            'modify': "Once your app is created, you can ask me to modify it by describing the changes you want. For example: 'Add a delete button to the todo list' or 'Change the color scheme to dark mode'.",
            'export': "You can export your project by clicking the Export button in the code preview section. This will download all your Swift files as a zip."
        };

        const lowerMessage = message.toLowerCase();
        let response = responses.help;

        if (lowerMessage.includes('feature') || lowerMessage.includes('what can')) {
            response = responses.features;
        } else if (lowerMessage.includes('modify') || lowerMessage.includes('change')) {
            response = responses.modify;
        } else if (lowerMessage.includes('export') || lowerMessage.includes('download')) {
            response = responses.export;
        }

        this.addMessage('assistant', response);
    }

    addMessage(sender, content, isTyping = false, errors = null) {
        const messagesContainer = document.getElementById('chatMessages');
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message-enter';

        const timestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

        if (sender === 'user') {
            messageDiv.innerHTML = `
                <div class="flex items-start space-x-3 justify-end">
                    <div class="flex-1 max-w-md">
                        <p class="text-sm font-medium text-gray-300 mb-1 text-right">You</p>
                        <div class="bg-gradient-to-r from-blue-500/20 to-purple-500/20 border border-blue-500/30 rounded-lg p-4">
                            <p class="text-gray-200 whitespace-pre-wrap">${this.escapeHtml(content)}</p>
                        </div>
                        <p class="text-xs text-gray-500 mt-1 text-right">${timestamp}</p>
                    </div>
                    <div class="w-8 h-8 bg-gray-600 rounded-lg flex items-center justify-center flex-shrink-0">
                        <svg class="w-5 h-5 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
                        </svg>
                    </div>
                </div>
            `;
        } else {
            let contentHtml = content.split('\n').map(line => `<p>${this.escapeHtml(line)}</p>`).join('');
            if (isTyping) {
                contentHtml = `<span class="typing-indicator">${contentHtml}</span>`;
            }

            if (errors && errors.length > 0) {
                contentHtml += `
                    <div class="mt-3 p-3 bg-red-500/10 border border-red-500/30 rounded-lg">
                        <p class="text-sm font-medium text-red-400 mb-2">Build Errors:</p>
                        <ul class="text-sm text-red-300 space-y-1">
                            ${errors.map(error => `<li>• ${this.escapeHtml(error)}</li>`).join('')}
                        </ul>
                    </div>
                `;
            }

            messageDiv.innerHTML = `
                <div class="flex items-start space-x-3">
                    <div class="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center flex-shrink-0">
                        <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
                        </svg>
                    </div>
                    <div class="flex-1 max-w-md">
                        <p class="text-sm font-medium text-gray-300 mb-1">SwiftGen AI</p>
                        <div class="bg-dark-bg rounded-lg p-4">
                            <div class="text-gray-200 space-y-1">${contentHtml}</div>
                        </div>
                        <p class="text-xs text-gray-500 mt-1">${timestamp}</p>
                    </div>
                </div>
            `;
        }

        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;

        // Store in history
        this.messageHistory.push({ sender, content, timestamp });
    }

    connectWebSocket(projectId) {
        if (this.ws) {
            this.ws.close();
        }

        const wsUrl = `ws://localhost:8000/ws/${projectId}`;
        this.ws = new WebSocket(wsUrl);

        this.ws.onopen = () => {
            console.log('WebSocket connected');
            this.updateStatus('connected', 'Connected to server');
        };

        this.ws.onmessage = (event) => {
            const message = JSON.parse(event.data);
            this.handleWebSocketMessage(message);
        };

        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.updateStatus('error', 'Connection error');
        };

        this.ws.onclose = () => {
            console.log('WebSocket disconnected');
            this.updateStatus('disconnected', 'Disconnected from server');
        };
    }

    handleWebSocketMessage(message) {
        console.log('WebSocket message:', message);

        switch (message.type) {
            case 'status':
                this.handleStatusUpdate(message.message);
                break;
            case 'complete':
                // Final completion is handled in main response
                break;
            case 'error':
                if (message.errors) {
                    this.buildLogs = message.errors;
                }
                break;
        }
    }

    handleStatusUpdate(statusMessage) {
        console.log('Status update:', statusMessage);

        // Update progress based on status message
        if (statusMessage.includes('Generating Swift code')) {
            this.updateProgress('generate');
        } else if (statusMessage.includes('Creating project structure')) {
            this.updateProgress('create');
        } else if (statusMessage.includes('Building app')) {
            this.updateProgress('build');
        } else if (statusMessage.includes('Installing')) {
            this.updateProgress('install');
        } else if (statusMessage.includes('Launching')) {
            this.updateProgress('launch');
        } else if (statusMessage.includes('Booting simulator')) {
            this.updateProgress('install', 70);
        } else if (statusMessage.includes('✅')) {
            this.updateProgress('launch', 100);
        }

        // Update status text
        document.getElementById('progressText').textContent = statusMessage;

        // Add to build logs
        this.buildLogs.push(`[${new Date().toLocaleTimeString()}] ${statusMessage}`);
    }

    showProgress() {
        const container = document.getElementById('progressContainer');
        container.classList.remove('hidden');
        this.resetProgress();
    }

    hideProgress() {
        const container = document.getElementById('progressContainer');
        container.classList.add('hidden');
    }

    resetProgress() {
        document.getElementById('progressBar').style.width = '0%';
        document.getElementById('progressPercent').textContent = '0%';

        // Reset all step indicators
        document.querySelectorAll('.step').forEach(step => {
            step.querySelector('.bg-blue-500').style.width = '0%';
        });

        // Reset progress tracking
        Object.keys(this.progressSteps).forEach(step => {
            this.progressSteps[step].completed = false;
        });
    }

    updateProgress(step, overridePercent = null) {
        const stepConfig = this.progressSteps[step];
        if (!stepConfig) return;

        // Mark step as completed
        stepConfig.completed = true;

        const percent = overridePercent || stepConfig.percent;

        // Update main progress bar
        document.getElementById('progressBar').style.width = `${percent}%`;
        document.getElementById('progressPercent').textContent = `${percent}%`;
        document.getElementById('progressText').textContent = stepConfig.text;

        // Update step indicators
        const stepElement = document.querySelector(`[data-step="${step}"]`);
        if (stepElement) {
            stepElement.querySelector('.bg-blue-500').style.width = '100%';
        }

        // Also fill previous steps
        const steps = Object.keys(this.progressSteps);
        const currentIndex = steps.indexOf(step);
        for (let i = 0; i <= currentIndex; i++) {
            const prevStep = document.querySelector(`[data-step="${steps[i]}"]`);
            if (prevStep) {
                prevStep.querySelector('.bg-blue-500').style.width = '100%';
            }
        }
    }

    displayGeneratedCode(files) {
        const codeDisplay = document.getElementById('codeDisplay');
        const noCodeMessage = document.getElementById('noCodeMessage');
        const fileTabs = document.getElementById('fileTabs');
        const fileTabsContainer = document.getElementById('fileTabsContainer');

        // Show code display, hide no-code message
        codeDisplay.classList.remove('hidden');
        noCodeMessage.classList.add('hidden');
        fileTabs.classList.remove('hidden');

        // Clear existing tabs
        fileTabsContainer.innerHTML = '';

        // Add action buttons with new Advanced Editor button
        const actionsDiv = document.createElement('div');
        actionsDiv.className = 'ml-auto flex items-center space-x-2';
        actionsDiv.innerHTML = `
        <button onclick="swiftgenChat.openCodeEditor()" class="px-3 py-1 text-xs bg-blue-600 hover:bg-blue-700 text-white rounded flex items-center space-x-1">
            <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4"></path>
            </svg>
            <span>Advanced Editor</span>
        </button>
        <button onclick="swiftgenChat.startEditMode()" class="px-3 py-1 text-xs bg-dark-surface hover:bg-dark-hover border border-dark-border rounded">
            <svg class="w-3 h-3 inline mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
            </svg>
            Quick Edit
        </button>
        <button onclick="swiftgenChat.exportProject()" class="px-3 py-1 text-xs bg-dark-surface hover:bg-dark-hover border border-dark-border rounded">
            <svg class="w-3 h-3 inline mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
            </svg>
            Export
        </button>
    `;

        // Create tab container
        const tabContainer = document.createElement('div');
        tabContainer.className = 'flex items-center space-x-2 flex-1';

        // Create tabs for each file
        files.forEach((file, index) => {
            const fileName = file.path.split('/').pop();
            const tab = document.createElement('button');
            tab.className = `px-4 py-2 text-sm font-medium transition-all ${
                index === 0
                    ? 'text-blue-400 border-b-2 border-blue-400'
                    : 'text-gray-400 hover:text-gray-200'
            }`;
            tab.textContent = fileName;
            tab.onclick = () => this.selectFile(index);
            tab.setAttribute('data-file-index', index);
            tabContainer.appendChild(tab);
        });

        fileTabsContainer.appendChild(tabContainer);
        fileTabsContainer.appendChild(actionsDiv);

        // Display first file
        if (files.length > 0) {
            this.selectFile(0);
        }
    }
    async saveFileChanges() {
        const codeContent = document.getElementById('codeContent');
        const editButton = document.querySelector('button[onclick="swiftgenChat.startEditMode()"]');

        // Get the edited content
        const newContent = codeContent.textContent;
        const file = this.generatedFiles[this.editingFile];

        // Update local file content
        file.content = newContent;

        // Exit edit mode
        codeContent.contentEditable = false;
        codeContent.className = 'text-sm text-gray-300';
        this.editingFile = null;

        editButton.innerHTML = `
            <svg class="w-3 h-3 inline mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
            </svg>
            Edit
        `;
        editButton.className = 'px-3 py-1 text-xs bg-dark-surface hover:bg-dark-hover border border-dark-border rounded';

        // Send update to backend
        try {
            const response = await fetch('/api/modify', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    project_id: this.currentProjectId,
                    modification: 'Manual code edit',
                    context: {
                        ...this.currentContext,
                        manual_edit: true,
                        edited_files: [file]
                    }
                })
            });

            if (response.ok) {
                this.addMessage('assistant', '✅ Changes saved and app rebuilt successfully!');
            } else {
                this.addMessage('assistant', '❌ Failed to save changes. Please try again.');
            }
        } catch (error) {
            console.error('Save error:', error);
            this.addMessage('assistant', '❌ Error saving changes: ' + error.message);
        }
    }

    async exportProject() {
        if (!this.currentProjectId || this.generatedFiles.length === 0) {
            this.addMessage('assistant', 'No project to export. Please create an app first.');
            return;
        }

        // Create a zip file content
        const zip = new JSZip();

        // Add all files to zip
        this.generatedFiles.forEach(file => {
            zip.file(file.path, file.content);
        });

        // Add project info
        const projectInfo = {
            app_name: this.currentContext.appName,
            description: this.currentContext.description,
            created_at: new Date().toISOString(),
            exported_at: new Date().toISOString()
        };
        zip.file('project_info.json', JSON.stringify(projectInfo, null, 2));

        // Generate and download zip
        try {
            const content = await zip.generateAsync({ type: 'blob' });
            const url = URL.createObjectURL(content);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${this.currentContext.appName || 'SwiftGenApp'}.zip`;
            a.click();
            URL.revokeObjectURL(url);

            this.addMessage('assistant', `✅ Project exported successfully as ${a.download}`);
        } catch (error) {
            console.error('Export error:', error);
            this.addMessage('assistant', '❌ Failed to export project. Please try again.');
        }
    }

    showBuildLogs() {
        if (this.buildLogs.length === 0) {
            this.addMessage('assistant', 'No build logs available yet. Create or modify an app to see logs.');
            return;
        }

        // Create a modal or expanded view for logs
        const logsHtml = this.buildLogs.map(log => `<div class="text-xs text-gray-400 font-mono">${this.escapeHtml(log)}</div>`).join('');

        this.addMessage('assistant', `<div class="mt-2 p-3 bg-dark-surface rounded-lg border border-dark-border">
            <p class="text-sm font-medium text-gray-300 mb-2">Build Logs:</p>
            <div class="space-y-1 max-h-60 overflow-y-auto">
                ${logsHtml}
            </div>
        </div>`);
    }

    showSimulatorStatus(isRunning) {
        const statusDiv = document.getElementById('simulatorStatus');
        if (isRunning) {
            statusDiv.classList.remove('hidden');
        } else {
            statusDiv.classList.add('hidden');
        }
    }

    updateStatus(type, message) {
        const indicator = document.getElementById('statusIndicator');
        const text = document.getElementById('statusText');

        const statusConfig = {
            'ready': { color: 'bg-green-500', text: 'Ready' },
            'connected': { color: 'bg-green-500', text: message },
            'processing': { color: 'bg-yellow-500', text: message },
            'error': { color: 'bg-red-500', text: message },
            'disconnected': { color: 'bg-gray-500', text: message }
        };

        const config = statusConfig[type] || statusConfig.ready;
        indicator.className = `w-2 h-2 rounded-full ${config.color}`;
        text.textContent = config.text;
    }

    startNewProject() {
        if (this.isProcessing) {
            alert('Please wait for the current process to complete.');
            return;
        }

        // Reset state
        this.currentProjectId = null;
        this.generatedFiles = [];
        this.currentContext = { appName: '', description: '', features: [] };
        this.buildLogs = [];
        this.editingFile = null;

        // Clear UI
        document.getElementById('chatMessages').innerHTML = '';
        document.getElementById('codeContent').textContent = '';
        document.getElementById('fileTabsContainer').innerHTML = '';
        document.getElementById('codeDisplay').classList.add('hidden');
        document.getElementById('noCodeMessage').classList.remove('hidden');
        document.getElementById('fileTabs').classList.add('hidden');
        document.getElementById('simulatorStatus').classList.add('hidden');
        document.getElementById('projectName').textContent = 'Start by describing your app idea';

        // Show welcome message again
        this.addMessage('assistant', "👋 Ready to create a new iOS app! What would you like to build?");

        // Focus on input
        document.getElementById('chatInput').focus();
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Add JSZip library for export functionality
const script = document.createElement('script');
script.src = 'https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js';
document.head.appendChild(script);

// Initialize the chat interface
document.addEventListener('DOMContentLoaded', () => {
    window.swiftgenChat = new SwiftGenChat();
});
