class WebRTCClient {
    constructor(socketClient, config = {}) {
        this.socket = socketClient;
        this.config = {
            iceServers: [
                { urls: 'stun:stun.l.google.com:19302' },
                { urls: 'stun:stun1.l.google.com:19302' }
            ],
            ...config
        };
        
        this.peerConnection = null;
        this.localStream = null;
        this.remoteStream = null;
        this.isInitiator = false;
        this.isConnected = false;
        this.dataChannel = null;
        
        this.callbacks = {
            onLocalStream: null,
            onRemoteStream: null,
            onConnectionStateChange: null,
            onDataChannelMessage: null,
            onError: null
        };
        
        this.setupSocketListeners();
    }
    
    setupSocketListeners() {
        this.socket.on('offer', (data) => {
            this.handleOffer(data.offer, data.fromId);
        });
        
        this.socket.on('answer', (data) => {
            this.handleAnswer(data.answer);
        });
        
        this.socket.on('ice_candidate', (data) => {
            this.handleIceCandidate(data.candidate);
        });
    }
    
    async initializePeerConnection() {
        try {
            this.peerConnection = new RTCPeerConnection(this.config);
            
            // Handle ICE candidates
            this.peerConnection.onicecandidate = (event) => {
                if (event.candidate) {
                    this.socket.emit('ice_candidate', {
                        candidate: event.candidate,
                        targetId: this.remoteUserId
                    });
                }
            };
            
            // Handle remote stream
            this.peerConnection.ontrack = (event) => {
                this.remoteStream = event.streams[0];
                if (this.callbacks.onRemoteStream) {
                    this.callbacks.onRemoteStream(this.remoteStream);
                }
            };
            
            // Handle connection state changes
            this.peerConnection.onconnectionstatechange = () => {
                const state = this.peerConnection.connectionState;
                this.isConnected = state === 'connected';
                
                if (this.callbacks.onConnectionStateChange) {
                    this.callbacks.onConnectionStateChange(state);
                }
                
                console.log('Connection state:', state);
            };
            
            // Setup data channel for text communication
            if (this.isInitiator) {
                this.setupDataChannel();
            } else {
                this.peerConnection.ondatachannel = (event) => {
                    this.dataChannel = event.channel;
                    this.setupDataChannelListeners();
                };
            }
            
            return true;
        } catch (error) {
            console.error('Error initializing peer connection:', error);
            if (this.callbacks.onError) {
                this.callbacks.onError(error);
            }
            return false;
        }
    }
    
    setupDataChannel() {
        this.dataChannel = this.peerConnection.createDataChannel('messages', {
            ordered: true
        });
        this.setupDataChannelListeners();
    }
    
    setupDataChannelListeners() {
        this.dataChannel.onopen = () => {
            console.log('Data channel opened');
        };
        
        this.dataChannel.onmessage = (event) => {
            if (this.callbacks.onDataChannelMessage) {
                this.callbacks.onDataChannelMessage(event.data);
            }
        };
        
        this.dataChannel.onerror = (error) => {
            console.error('Data channel error:', error);
        };
    }
    
    async getUserMedia(constraints = { audio: true, video: false }) {
        try {
            this.localStream = await navigator.mediaDevices.getUserMedia(constraints);
            
            if (this.callbacks.onLocalStream) {
                this.callbacks.onLocalStream(this.localStream);
            }
            
            return this.localStream;
        } catch (error) {
            console.error('Error accessing media devices:', error);
            if (this.callbacks.onError) {
                this.callbacks.onError(error);
            }
            throw error;
        }
    }
    
    async getDisplayMedia(constraints = { video: true, audio: true }) {
        try {
            const displayStream = await navigator.mediaDevices.getDisplayMedia(constraints);
            
            // Replace video track if we have an existing connection
            if (this.peerConnection && this.localStream) {
                const videoTrack = displayStream.getVideoTracks()[0];
                const sender = this.peerConnection.getSenders().find(s => 
                    s.track && s.track.kind === 'video'
                );
                
                if (sender) {
                    await sender.replaceTrack(videoTrack);
                } else {
                    this.peerConnection.addTrack(videoTrack, displayStream);
                }
                
                // Add audio track if available
                const audioTrack = displayStream.getAudioTracks()[0];
                if (audioTrack) {
                    this.peerConnection.addTrack(audioTrack, displayStream);
                }
            }
            
            // Handle screen share end
            displayStream.getVideoTracks()[0].onended = () => {
                this.stopScreenShare();
            };
            
            return displayStream;
        } catch (error) {
            console.error('Error accessing display media:', error);
            if (this.callbacks.onError) {
                this.callbacks.onError(error);
            }
            throw error;
        }
    }
    
    async startCall(remoteUserId, constraints = { audio: true, video: false }) {
        try {
            this.remoteUserId = remoteUserId;
            this.isInitiator = true;
            
            // Get user media
            await this.getUserMedia(constraints);
            
            // Initialize peer connection
            await this.initializePeerConnection();
            
            // Add local stream to peer connection
            this.localStream.getTracks().forEach(track => {
                this.peerConnection.addTrack(track, this.localStream);
            });
            
            // Create and send offer
            const offer = await this.peerConnection.createOffer();
            await this.peerConnection.setLocalDescription(offer);
            
            this.socket.emit('offer', {
                offer: offer,
                targetId: remoteUserId
            });
            
            return true;
        } catch (error) {
            console.error('Error starting call:', error);
            if (this.callbacks.onError) {
                this.callbacks.onError(error);
            }
            return false;
        }
    }
    
    async handleOffer(offer, fromId) {
        try {
            this.remoteUserId = fromId;
            this.isInitiator = false;
            
            // Get user media
            await this.getUserMedia({ audio: true, video: false });
            
            // Initialize peer connection
            await this.initializePeerConnection();
            
            // Add local stream to peer connection
            this.localStream.getTracks().forEach(track => {
                this.peerConnection.addTrack(track, this.localStream);
            });
            
            // Set remote description and create answer
            await this.peerConnection.setRemoteDescription(offer);
            const answer = await this.peerConnection.createAnswer();
            await this.peerConnection.setLocalDescription(answer);
            
            this.socket.emit('answer', {
                answer: answer,
                targetId: fromId
            });
            
        } catch (error) {
            console.error('Error handling offer:', error);
            if (this.callbacks.onError) {
                this.callbacks.onError(error);
            }
        }
    }
    
    async handleAnswer(answer) {
        try {
            await this.peerConnection.setRemoteDescription(answer);
        } catch (error) {
            console.error('Error handling answer:', error);
            if (this.callbacks.onError) {
                this.callbacks.onError(error);
            }
        }
    }
    
    async handleIceCandidate(candidate) {
        try {
            await this.peerConnection.addIceCandidate(candidate);
        } catch (error) {
            console.error('Error handling ICE candidate:', error);
            if (this.callbacks.onError) {
                this.callbacks.onError(error);
            }
        }
    }
    
    async startScreenShare() {
        try {
            const displayStream = await this.getDisplayMedia();
            return displayStream;
        } catch (error) {
            console.error('Error starting screen share:', error);
            if (this.callbacks.onError) {
                this.callbacks.onError(error);
            }
            throw error;
        }
    }
    
    async stopScreenShare() {
        try {
            // Get camera stream back
            const cameraStream = await navigator.mediaDevices.getUserMedia({ 
                video: true, 
                audio: true 
            });
            
            // Replace video track
            const videoTrack = cameraStream.getVideoTracks()[0];
            const sender = this.peerConnection.getSenders().find(s => 
                s.track && s.track.kind === 'video'
            );
            
            if (sender && videoTrack) {
                await sender.replaceTrack(videoTrack);
            }
            
        } catch (error) {
            console.error('Error stopping screen share:', error);
        }
    }
    
    sendDataChannelMessage(message) {
        if (this.dataChannel && this.dataChannel.readyState === 'open') {
            this.dataChannel.send(message);
            return true;
        }
        return false;
    }
    
    toggleAudio() {
        if (this.localStream) {
            const audioTrack = this.localStream.getAudioTracks()[0];
            if (audioTrack) {
                audioTrack.enabled = !audioTrack.enabled;
                return audioTrack.enabled;
            }
        }
        return false;
    }
    
    toggleVideo() {
        if (this.localStream) {
            const videoTrack = this.localStream.getVideoTracks()[0];
            if (videoTrack) {
                videoTrack.enabled = !videoTrack.enabled;
                return videoTrack.enabled;
            }
        }
        return false;
    }
    
    endCall() {
        // Stop all tracks
        if (this.localStream) {
            this.localStream.getTracks().forEach(track => track.stop());
            this.localStream = null;
        }
        
        if (this.remoteStream) {
            this.remoteStream.getTracks().forEach(track => track.stop());
            this.remoteStream = null;
        }
        
        // Close data channel
        if (this.dataChannel) {
            this.dataChannel.close();
            this.dataChannel = null;
        }
        
        // Close peer connection
        if (this.peerConnection) {
            this.peerConnection.close();
            this.peerConnection = null;
        }
        
        this.isConnected = false;
        this.isInitiator = false;
        this.remoteUserId = null;
    }
    
    // Callback setters
    onLocalStream(callback) {
        this.callbacks.onLocalStream = callback;
    }
    
    onRemoteStream(callback) {
        this.callbacks.onRemoteStream = callback;
    }
    
    onConnectionStateChange(callback) {
        this.callbacks.onConnectionStateChange = callback;
    }
    
    onDataChannelMessage(callback) {
        this.callbacks.onDataChannelMessage = callback;
    }
    
    onError(callback) {
        this.callbacks.onError = callback;
    }
}

