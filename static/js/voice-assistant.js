class VoiceAssistant {
    constructor(socketClient) {
        this.socket = socketClient;
        this.isListening = false;
        this.isProcessing = false;
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.recognition = null;
        this.synthesis = null;
        
        this.callbacks = {
            onListeningStart: null,
            onListeningEnd: null,
            onProcessingStart: null,
            onProcessingEnd: null,
            onResponse: null,
            onError: null
        };
        
        this.initializeSpeechRecognition();
        this.initializeSpeechSynthesis();
        this.setupSocketListeners();
    }
    
    initializeSpeechRecognition() {
        // Check for browser support
        if ('webkitSpeechRecognition' in window) {
            this.recognition = new webkitSpeechRecognition();
        } else if ('SpeechRecognition' in window) {
            this.recognition = new SpeechRecognition();
        }
        
        if (this.recognition) {
            this.recognition.continuous = false;
            this.recognition.interimResults = false;
            this.recognition.lang = 'en-US';
            
            this.recognition.onstart = () => {
                this.isListening = true;
                if (this.callbacks.onListeningStart) {
                    this.callbacks.onListeningStart();
                }
            };
            
            this.recognition.onend = () => {
                this.isListening = false;
                if (this.callbacks.onListeningEnd) {
                    this.callbacks.onListeningEnd();
                }
            };
            
            this.recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                this.processVoiceQuery(transcript);
            };
            
            this.recognition.onerror = (event) => {
                console.error('Speech recognition error:', event.error);
                if (this.callbacks.onError) {
                    this.callbacks.onError(event.error);
                }
            };
        }
    }
    
    initializeSpeechSynthesis() {
        if ('speechSynthesis' in window) {
            this.synthesis = window.speechSynthesis;
        }
    }
    
    setupSocketListeners() {
        this.socket.on('ai_response', (data) => {
            this.handleAIResponse(data);
        });
        
        this.socket.on('error', (data) => {
            this.isProcessing = false;
            if (this.callbacks.onProcessingEnd) {
                this.callbacks.onProcessingEnd();
            }
            if (this.callbacks.onError) {
                this.callbacks.onError(data.message);
            }
        });
    }
    
    async startListening() {
        if (this.isListening || this.isProcessing) {
            return false;
        }
        
        try {
            if (this.recognition) {
                // Use Web Speech API
                this.recognition.start();
            } else {
                // Fallback to MediaRecorder
                await this.startRecording();
            }
            return true;
        } catch (error) {
            console.error('Error starting voice recognition:', error);
            if (this.callbacks.onError) {
                this.callbacks.onError(error.message);
            }
            return false;
        }
    }
    
    stopListening() {
        if (this.recognition && this.isListening) {
            this.recognition.stop();
        }
        
        if (this.mediaRecorder && this.mediaRecorder.state === 'recording') {
            this.mediaRecorder.stop();
        }
    }
    
    async startRecording() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            this.mediaRecorder = new MediaRecorder(stream);
            this.audioChunks = [];
            
            this.mediaRecorder.ondataavailable = (event) => {
                this.audioChunks.push(event.data);
            };
            
            this.mediaRecorder.onstop = () => {
                const audioBlob = new Blob(this.audioChunks, { type: 'audio/wav' });
                this.processAudioBlob(audioBlob);
            };
            
            this.mediaRecorder.start();
            this.isListening = true;
            
            if (this.callbacks.onListeningStart) {
                this.callbacks.onListeningStart();
            }
            
        } catch (error) {
            console.error('Error starting recording:', error);
            throw error;
        }
    }
    
    async processAudioBlob(audioBlob) {
        try {
            // Convert blob to base64
            const reader = new FileReader();
            reader.onloadend = () => {
                const base64Audio = reader.result;
                this.sendVoiceQuery(base64Audio);
            };
            reader.readAsDataURL(audioBlob);
            
        } catch (error) {
            console.error('Error processing audio blob:', error);
            if (this.callbacks.onError) {
                this.callbacks.onError(error.message);
            }
        }
    }
    
    processVoiceQuery(transcript) {
        if (!transcript || transcript.trim() === '') {
            return;
        }
        
        console.log('Voice query:', transcript);
        
        // Get current screen context
        const context = this.getCurrentContext();
        
        this.isProcessing = true;
        if (this.callbacks.onProcessingStart) {
            this.callbacks.onProcessingStart();
        }
        
        // Send to server for AI processing
        this.socket.emit('voice_query', {
            query: transcript,
            context: context
        });
    }
    
    sendVoiceQuery(audioData, context = null) {
        this.isProcessing = true;
        if (this.callbacks.onProcessingStart) {
            this.callbacks.onProcessingStart();
        }
        
        this.socket.emit('voice_query', {
            audioData: audioData,
            context: context || this.getCurrentContext()
        });
    }
    
    getCurrentContext() {
        // Gather context about current page/screen
        const context = {
            url: window.location.href,
            title: document.title,
            timestamp: new Date().toISOString()
        };
        
        // Try to get visible text content
        try {
            const bodyText = document.body.innerText || '';
            context.pageText = bodyText.substring(0, 1000); // Limit to first 1000 chars
        } catch (error) {
            console.warn('Could not extract page text:', error);
        }
        
        // Try to get form elements
        try {
            const forms = Array.from(document.forms);
            context.forms = forms.map(form => ({
                id: form.id,
                name: form.name,
                action: form.action,
                method: form.method,
                elements: Array.from(form.elements).map(el => ({
                    type: el.type,
                    name: el.name,
                    id: el.id,
                    placeholder: el.placeholder,
                    required: el.required
                }))
            }));
        } catch (error) {
            console.warn('Could not extract form data:', error);
        }
        
        // Try to get visible buttons
        try {
            const buttons = Array.from(document.querySelectorAll('button, input[type=\"button\"], input[type=\"submit\"]'));
            context.buttons = buttons
                .filter(btn => btn.offsetParent !== null) // Only visible buttons
                .map(btn => ({
                    text: btn.textContent || btn.value,
                    type: btn.type,
                    id: btn.id,
                    className: btn.className
                }))
                .slice(0, 10); // Limit to first 10 buttons
        } catch (error) {
            console.warn('Could not extract button data:', error);
        }
        
        return context;
    }
    
    handleAIResponse(data) {
        this.isProcessing = false;
        
        if (this.callbacks.onProcessingEnd) {
            this.callbacks.onProcessingEnd();
        }
        
        if (this.callbacks.onResponse) {
            this.callbacks.onResponse(data);
        }
        
        // Play audio response if available
        if (data.audioResponse) {
            this.playAudioResponse(data.audioResponse);
        } else if (data.textResponse) {
            // Fallback to text-to-speech
            this.speakText(data.textResponse);
        }
    }
    
    playAudioResponse(audioData) {
        try {
            const audio = new Audio(audioData);
            audio.play().catch(error => {
                console.error('Error playing audio response:', error);
                // Fallback to text-to-speech
                if (this.callbacks.onResponse && this.callbacks.onResponse.textResponse) {
                    this.speakText(this.callbacks.onResponse.textResponse);
                }
            });
        } catch (error) {
            console.error('Error creating audio element:', error);
        }
    }
    
    speakText(text) {
        if (!this.synthesis) {
            console.warn('Speech synthesis not supported');
            return;
        }
        
        // Cancel any ongoing speech
        this.synthesis.cancel();
        
        const utterance = new SpeechSynthesisUtterance(text);
        
        // Try to find a female voice
        const voices = this.synthesis.getVoices();
        const femaleVoice = voices.find(voice => 
            voice.name.toLowerCase().includes('female') ||
            voice.name.toLowerCase().includes('woman') ||
            voice.gender === 'female'
        );
        
        if (femaleVoice) {
            utterance.voice = femaleVoice;
        } else if (voices.length > 1) {
            // Use second voice if available (often female)
            utterance.voice = voices[1];
        }
        
        utterance.rate = 0.9;
        utterance.pitch = 1.1;
        utterance.volume = 0.8;
        
        utterance.onend = () => {
            console.log('Speech synthesis completed');
        };
        
        utterance.onerror = (event) => {
            console.error('Speech synthesis error:', event.error);
        };
        
        this.synthesis.speak(utterance);
    }
    
    // Text-based query method
    async sendTextQuery(text, context = null) {
        if (!text || text.trim() === '') {
            return;
        }
        
        this.isProcessing = true;
        if (this.callbacks.onProcessingStart) {
            this.callbacks.onProcessingStart();
        }
        
        try {
            const response = await fetch('/api/ai-query', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    query: text,
                    context: context || this.getCurrentContext()
                })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                this.handleAIResponse({
                    textQuery: text,
                    textResponse: data.response,
                    audioResponse: null
                });
            } else {
                throw new Error(data.error || 'AI query failed');
            }
            
        } catch (error) {
            console.error('Error sending text query:', error);
            this.isProcessing = false;
            if (this.callbacks.onProcessingEnd) {
                this.callbacks.onProcessingEnd();
            }
            if (this.callbacks.onError) {
                this.callbacks.onError(error.message);
            }
        }
    }
    
    // Callback setters
    onListeningStart(callback) {
        this.callbacks.onListeningStart = callback;
    }
    
    onListeningEnd(callback) {
        this.callbacks.onListeningEnd = callback;
    }
    
    onProcessingStart(callback) {
        this.callbacks.onProcessingStart = callback;
    }
    
    onProcessingEnd(callback) {
        this.callbacks.onProcessingEnd = callback;
    }
    
    onResponse(callback) {
        this.callbacks.onResponse = callback;
    }
    
    onError(callback) {
        this.callbacks.onError = callback;
    }
}

