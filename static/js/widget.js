(function() {
    'use strict';
    
    // Widget configuration
    const DEFAULT_CONFIG = {
        serverUrl: window.location.origin,
        theme: 'modern',
        position: 'bottom-right',
        title: 'AI Voice Assistant',
        enableVoice: true,
        enableScreenShare: true,
        enableChat: true,
        autoConnect: true,
        minimized: true
    };
    
    class AIVoiceWidget {
        constructor(config = {}) {
            this.config = { ...DEFAULT_CONFIG, ...config };
            this.isInitialized = false;
            this.isConnected = false;
            this.isMinimized = this.config.minimized;
            this.socket = null;
            this.webrtcClient = null;
            this.voiceAssistant = null;
            
            this.init();
        }
        
        async init() {
            if (this.isInitialized) return;
            
            try {
                await this.loadDependencies();
                this.createWidget();
                this.setupEventListeners();
                
                if (this.config.autoConnect) {
                    await this.connect();
                }
                
                this.isInitialized = true;
                console.log('AI Voice Widget initialized successfully');
            } catch (error) {
                console.error('Failed to initialize AI Voice Widget:', error);
            }
        }
        
        async loadDependencies() {
            // Load Socket.IO if not already loaded
            if (typeof io === 'undefined') {
                await this.loadScript('https://cdn.socket.io/4.7.2/socket.io.min.js');
            }
            
            // Load WebRTC client if not already loaded
            if (typeof WebRTCClient === 'undefined') {
                await this.loadScript(`${this.config.serverUrl}/static/js/webrtc-client.js`);
            }
            
            // Load Voice Assistant if not already loaded
            if (typeof VoiceAssistant === 'undefined') {
                await this.loadScript(`${this.config.serverUrl}/static/js/voice-assistant.js`);
            }
        }
        
        loadScript(src) {
            return new Promise((resolve, reject) => {
                const script = document.createElement('script');
                script.src = src;
                script.onload = resolve;
                script.onerror = reject;
                document.head.appendChild(script);
            });
        }
        
        createWidget() {
            // Create widget container
            this.widgetContainer = document.createElement('div');
            this.widgetContainer.id = 'ai-voice-widget';
            this.widgetContainer.className = `ai-widget ${this.config.theme} ${this.config.position}`;
            
            // Create widget HTML
            this.widgetContainer.innerHTML = `
                <div class="widget-header" id="widget-header">
                    <div class="widget-title">${this.config.title}</div>
                    <div class="widget-controls">
                        <button class="widget-btn minimize-btn" id="minimize-btn" title="Minimize">
                            <span class="minimize-icon">−</span>
                        </button>
                        <button class="widget-btn close-btn" id="close-btn" title="Close">
                            <span class="close-icon">×</span>
                        </button>
                    </div>
                </div>
                
                <div class="widget-body" id="widget-body" style="${this.isMinimized ? 'display: none;' : ''}">
                    <div class="connection-status" id="connection-status">
                        <span class="status-indicator" id="status-indicator"></span>
                        <span class="status-text" id="status-text">Disconnected</span>
                    </div>
                    
                    <div class="voice-controls" id="voice-controls">
                        <button class="voice-btn" id="voice-btn" title="Start Voice Chat">
                            <span class="voice-icon">🎤</span>
                            <span class="voice-text">Talk</span>
                        </button>
                        
                        <button class="screen-share-btn" id="screen-share-btn" title="Share Screen">
                            <span class="screen-icon">🖥️</span>
                        </button>
                        
                        <button class="call-btn" id="call-btn" title="Start Voice Call">
                            <span class="call-icon">📞</span>
                        </button>
                    </div>
                    
                    <div class="chat-area" id="chat-area" style="display: none;">
                        <div class="messages" id="messages"></div>
                        <div class="input-area">
                            <input type="text" id="chat-input" placeholder="Type your message..." />
                            <button id="send-btn">Send</button>
                        </div>
                    </div>
                    
                    <div class="voice-status" id="voice-status" style="display: none;">
                        <div class="listening-indicator" id="listening-indicator">
                            <div class="pulse"></div>
                            <span>Listening...</span>
                        </div>
                        <div class="processing-indicator" id="processing-indicator" style="display: none;">
                            <div class="spinner"></div>
                            <span>Processing...</span>
                        </div>
                    </div>
                </div>
            `;
            
            // Add CSS styles
            this.addStyles();
            
            // Append to body
            document.body.appendChild(this.widgetContainer);
        }
        
        addStyles() {
            if (document.getElementById('ai-widget-styles')) return;
            
            const styles = document.createElement('style');
            styles.id = 'ai-widget-styles';
            styles.textContent = `
                .ai-widget {
                    position: fixed;
                    z-index: 10000;
                    width: 320px;
                    max-height: 500px;
                    background: #ffffff;
                    border-radius: 12px;
                    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    font-size: 14px;
                    border: 1px solid #e1e5e9;
                    overflow: hidden;
                }
                
                .ai-widget.bottom-right {
                    bottom: 20px;
                    right: 20px;
                }
                
                .ai-widget.bottom-left {
                    bottom: 20px;
                    left: 20px;
                }
                
                .ai-widget.top-right {
                    top: 20px;
                    right: 20px;
                }
                
                .ai-widget.top-left {
                    top: 20px;
                    left: 20px;
                }
                
                .widget-header {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 12px 16px;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    cursor: move;
                }
                
                .widget-title {
                    font-weight: 600;
                    font-size: 16px;
                }
                
                .widget-controls {
                    display: flex;
                    gap: 8px;
                }
                
                .widget-btn {
                    background: rgba(255, 255, 255, 0.2);
                    border: none;
                    color: white;
                    width: 24px;
                    height: 24px;
                    border-radius: 4px;
                    cursor: pointer;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 16px;
                    transition: background 0.2s;
                }
                
                .widget-btn:hover {
                    background: rgba(255, 255, 255, 0.3);
                }
                
                .widget-body {
                    padding: 16px;
                    max-height: 400px;
                    overflow-y: auto;
                }
                
                .connection-status {
                    display: flex;
                    align-items: center;
                    gap: 8px;
                    margin-bottom: 16px;
                    padding: 8px 12px;
                    background: #f8f9fa;
                    border-radius: 6px;
                }
                
                .status-indicator {
                    width: 8px;
                    height: 8px;
                    border-radius: 50%;
                    background: #dc3545;
                }
                
                .status-indicator.connected {
                    background: #28a745;
                }
                
                .status-indicator.connecting {
                    background: #ffc107;
                    animation: pulse 1s infinite;
                }
                
                .voice-controls {
                    display: flex;
                    gap: 12px;
                    margin-bottom: 16px;
                    justify-content: center;
                }
                
                .voice-btn, .screen-share-btn, .call-btn {
                    background: #667eea;
                    color: white;
                    border: none;
                    padding: 12px 16px;
                    border-radius: 8px;
                    cursor: pointer;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    gap: 4px;
                    min-width: 60px;
                    transition: all 0.2s;
                }
                
                .voice-btn:hover, .screen-share-btn:hover, .call-btn:hover {
                    background: #5a6fd8;
                    transform: translateY(-1px);
                }
                
                .voice-btn.active {
                    background: #dc3545;
                    animation: pulse 1s infinite;
                }
                
                .voice-btn.processing {
                    background: #ffc107;
                }
                
                .voice-icon, .screen-icon, .call-icon {
                    font-size: 20px;
                }
                
                .voice-text {
                    font-size: 12px;
                    font-weight: 500;
                }
                
                .chat-area {
                    border-top: 1px solid #e1e5e9;
                    padding-top: 16px;
                }
                
                .messages {
                    max-height: 200px;
                    overflow-y: auto;
                    margin-bottom: 12px;
                }
                
                .message {
                    margin-bottom: 12px;
                    padding: 8px 12px;
                    border-radius: 8px;
                    max-width: 80%;
                }
                
                .message.user {
                    background: #667eea;
                    color: white;
                    margin-left: auto;
                }
                
                .message.assistant {
                    background: #f8f9fa;
                    color: #333;
                }
                
                .input-area {
                    display: flex;
                    gap: 8px;
                }
                
                .input-area input {
                    flex: 1;
                    padding: 8px 12px;
                    border: 1px solid #e1e5e9;
                    border-radius: 6px;
                    outline: none;
                }
                
                .input-area input:focus {
                    border-color: #667eea;
                }
                
                .input-area button {
                    background: #667eea;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 6px;
                    cursor: pointer;
                }
                
                .voice-status {
                    text-align: center;
                    padding: 16px;
                }
                
                .listening-indicator, .processing-indicator {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    gap: 8px;
                }
                
                .pulse {
                    width: 40px;
                    height: 40px;
                    border-radius: 50%;
                    background: #667eea;
                    animation: pulse 1.5s infinite;
                }
                
                .spinner {
                    width: 20px;
                    height: 20px;
                    border: 2px solid #f3f3f3;
                    border-top: 2px solid #667eea;
                    border-radius: 50%;
                    animation: spin 1s linear infinite;
                }
                
                @keyframes pulse {
                    0% { transform: scale(1); opacity: 1; }
                    50% { transform: scale(1.1); opacity: 0.7; }
                    100% { transform: scale(1); opacity: 1; }
                }
                
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
                
                /* Dark theme */
                .ai-widget.dark {
                    background: #2d3748;
                    color: #e2e8f0;
                    border-color: #4a5568;
                }
                
                .ai-widget.dark .widget-body {
                    background: #2d3748;
                }
                
                .ai-widget.dark .connection-status {
                    background: #4a5568;
                }
                
                .ai-widget.dark .message.assistant {
                    background: #4a5568;
                    color: #e2e8f0;
                }
                
                .ai-widget.dark .input-area input {
                    background: #4a5568;
                    border-color: #718096;
                    color: #e2e8f0;
                }
            `;
            
            document.head.appendChild(styles);
        }
        
        setupEventListeners() {
            // Minimize/Maximize
            const minimizeBtn = this.widgetContainer.querySelector('#minimize-btn');
            minimizeBtn.addEventListener('click', () => this.toggleMinimize());
            
            // Close widget
            const closeBtn = this.widgetContainer.querySelector('#close-btn');
            closeBtn.addEventListener('click', () => this.close());
            
            // Voice button
            const voiceBtn = this.widgetContainer.querySelector('#voice-btn');
            voiceBtn.addEventListener('click', () => this.toggleVoice());
            
            // Screen share button
            const screenShareBtn = this.widgetContainer.querySelector('#screen-share-btn');
            screenShareBtn.addEventListener('click', () => this.toggleScreenShare());
            
            // Call button
            const callBtn = this.widgetContainer.querySelector('#call-btn');
            callBtn.addEventListener('click', () => this.toggleCall());
            
            // Chat input
            const chatInput = this.widgetContainer.querySelector('#chat-input');
            const sendBtn = this.widgetContainer.querySelector('#send-btn');
            
            chatInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.sendChatMessage();
                }
            });
            
            sendBtn.addEventListener('click', () => this.sendChatMessage());
            
            // Make widget draggable
            this.makeDraggable();
        }
        
        makeDraggable() {
            const header = this.widgetContainer.querySelector('.widget-header');
            let isDragging = false;
            let currentX;
            let currentY;
            let initialX;
            let initialY;
            let xOffset = 0;
            let yOffset = 0;
            
            header.addEventListener('mousedown', (e) => {
                initialX = e.clientX - xOffset;
                initialY = e.clientY - yOffset;
                
                if (e.target === header || header.contains(e.target)) {
                    isDragging = true;
                }
            });
            
            document.addEventListener('mousemove', (e) => {
                if (isDragging) {
                    e.preventDefault();
                    currentX = e.clientX - initialX;
                    currentY = e.clientY - initialY;
                    
                    xOffset = currentX;
                    yOffset = currentY;
                    
                    this.widgetContainer.style.transform = `translate(${currentX}px, ${currentY}px)`;
                }
            });
            
            document.addEventListener('mouseup', () => {
                isDragging = false;
            });
        }
        
        async connect() {
            if (this.isConnected) return;
            
            try {
                this.updateConnectionStatus('connecting', 'Connecting...');
                
                // Initialize Socket.IO connection
                this.socket = io(this.config.serverUrl);
                
                this.socket.on('connect', () => {
                    this.isConnected = true;
                    this.updateConnectionStatus('connected', 'Connected');
                    this.initializeClients();
                });
                
                this.socket.on('disconnect', () => {
                    this.isConnected = false;
                    this.updateConnectionStatus('disconnected', 'Disconnected');
                });
                
                this.socket.on('error', (error) => {
                    console.error('Socket error:', error);
                    this.updateConnectionStatus('error', 'Connection Error');
                });
                
            } catch (error) {
                console.error('Connection failed:', error);
                this.updateConnectionStatus('error', 'Connection Failed');
            }
        }
        
        initializeClients() {
            // Initialize WebRTC client
            this.webrtcClient = new WebRTCClient(this.socket);
            
            // Initialize Voice Assistant
            this.voiceAssistant = new VoiceAssistant(this.socket);
            
            // Setup voice assistant callbacks
            this.voiceAssistant.onListeningStart(() => {
                this.showVoiceStatus('listening');
                this.updateVoiceButton('active');
            });
            
            this.voiceAssistant.onListeningEnd(() => {
                this.hideVoiceStatus();
                this.updateVoiceButton('normal');
            });
            
            this.voiceAssistant.onProcessingStart(() => {
                this.showVoiceStatus('processing');
                this.updateVoiceButton('processing');
            });
            
            this.voiceAssistant.onProcessingEnd(() => {
                this.hideVoiceStatus();
                this.updateVoiceButton('normal');
            });
            
            this.voiceAssistant.onResponse((data) => {
                this.addMessage('assistant', data.textResponse || 'I heard you, but I couldn\\'t generate a response.');
            });
            
            this.voiceAssistant.onError((error) => {
                this.addMessage('assistant', `Sorry, I encountered an error: ${error}`);
                this.updateVoiceButton('normal');
                this.hideVoiceStatus();
            });
        }
        
        updateConnectionStatus(status, text) {
            const indicator = this.widgetContainer.querySelector('#status-indicator');
            const statusText = this.widgetContainer.querySelector('#status-text');
            
            indicator.className = `status-indicator ${status}`;
            statusText.textContent = text;
        }
        
        toggleMinimize() {
            this.isMinimized = !this.isMinimized;
            const body = this.widgetContainer.querySelector('#widget-body');
            const minimizeBtn = this.widgetContainer.querySelector('#minimize-btn');
            
            if (this.isMinimized) {
                body.style.display = 'none';
                minimizeBtn.querySelector('.minimize-icon').textContent = '+';
            } else {
                body.style.display = 'block';
                minimizeBtn.querySelector('.minimize-icon').textContent = '−';
            }
        }
        
        close() {
            if (this.socket) {
                this.socket.disconnect();
            }
            
            if (this.webrtcClient) {
                this.webrtcClient.endCall();
            }
            
            this.widgetContainer.remove();
        }
        
        async toggleVoice() {
            if (!this.voiceAssistant) {
                this.addMessage('assistant', 'Voice assistant not available. Please check your connection.');
                return;
            }
            
            if (this.voiceAssistant.isListening) {
                this.voiceAssistant.stopListening();
            } else {
                const success = await this.voiceAssistant.startListening();
                if (!success) {
                    this.addMessage('assistant', 'Could not start voice recognition. Please check microphone permissions.');
                }
            }
        }
        
        async toggleScreenShare() {
            if (!this.webrtcClient) {
                this.addMessage('assistant', 'Screen sharing not available. Please check your connection.');
                return;
            }
            
            try {
                await this.webrtcClient.startScreenShare();
                this.addMessage('assistant', 'Screen sharing started.');
            } catch (error) {
                this.addMessage('assistant', 'Could not start screen sharing. Please check permissions.');
            }
        }
        
        async toggleCall() {
            if (!this.webrtcClient) {
                this.addMessage('assistant', 'Voice call not available. Please check your connection.');
                return;
            }
            
            if (this.webrtcClient.isConnected) {
                this.webrtcClient.endCall();
                this.addMessage('assistant', 'Call ended.');
            } else {
                try {
                    await this.webrtcClient.startCall('ai-assistant');
                    this.addMessage('assistant', 'Starting voice call...');
                } catch (error) {
                    this.addMessage('assistant', 'Could not start call. Please check permissions.');
                }
            }
        }
        
        sendChatMessage() {
            const input = this.widgetContainer.querySelector('#chat-input');
            const message = input.value.trim();
            
            if (!message) return;
            
            this.addMessage('user', message);
            input.value = '';
            
            if (this.voiceAssistant) {
                this.voiceAssistant.sendTextQuery(message);
            }
        }
        
        addMessage(sender, text) {
            const messagesContainer = this.widgetContainer.querySelector('#messages');
            const chatArea = this.widgetContainer.querySelector('#chat-area');
            
            // Show chat area if hidden
            chatArea.style.display = 'block';
            
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${sender}`;
            messageDiv.textContent = text;
            
            messagesContainer.appendChild(messageDiv);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }
        
        showVoiceStatus(type) {
            const voiceStatus = this.widgetContainer.querySelector('#voice-status');
            const listeningIndicator = this.widgetContainer.querySelector('#listening-indicator');
            const processingIndicator = this.widgetContainer.querySelector('#processing-indicator');
            
            voiceStatus.style.display = 'block';
            
            if (type === 'listening') {
                listeningIndicator.style.display = 'flex';
                processingIndicator.style.display = 'none';
            } else if (type === 'processing') {
                listeningIndicator.style.display = 'none';
                processingIndicator.style.display = 'flex';
            }
        }
        
        hideVoiceStatus() {
            const voiceStatus = this.widgetContainer.querySelector('#voice-status');
            voiceStatus.style.display = 'none';
        }
        
        updateVoiceButton(state) {
            const voiceBtn = this.widgetContainer.querySelector('#voice-btn');
            voiceBtn.className = `voice-btn ${state}`;
            
            const voiceText = voiceBtn.querySelector('.voice-text');
            switch (state) {
                case 'active':
                    voiceText.textContent = 'Listening';
                    break;
                case 'processing':
                    voiceText.textContent = 'Processing';
                    break;
                default:
                    voiceText.textContent = 'Talk';
            }
        }
    }
    
    // Auto-initialize if config is provided
    window.AIVoiceWidget = AIVoiceWidget;
    
    // Check for auto-initialization
    if (window.aiVoiceWidgetConfig) {
        new AIVoiceWidget(window.aiVoiceWidgetConfig);
    }
    
})();

