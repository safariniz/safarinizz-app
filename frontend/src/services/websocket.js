import io from 'socket.io-client';

class WebSocketService {
  constructor() {
    this.socket = null;
    this.listeners = {};
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.isConnected = false;
  }

  connect(url, roomId = 'global') {
    if (this.socket) {
      this.socket.disconnect();
    }

    const wsUrl = url.replace('/api', '');
    this.socket = io(`${wsUrl}`, {
      path: '/ws/live-css',
      transports: ['websocket', 'polling'], // Fallback to polling on mobile
      query: { room_id: roomId },
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionDelayMax: 5000,
      reconnectionAttempts: this.maxReconnectAttempts
    });

    this.socket.on('connect', () => {
      console.log('✅ WebSocket connected');
      this.isConnected = true;
      this.reconnectAttempts = 0;
      this.notifyListeners('connection_status', { connected: true });
    });

    this.socket.on('disconnect', (reason) => {
      console.log('⚠️ WebSocket disconnected:', reason);
      this.isConnected = false;
      this.notifyListeners('connection_status', { connected: false, reason });
    });

    this.socket.on('connect_error', (error) => {
      console.error('WebSocket connection error:', error);
      this.reconnectAttempts++;
      if (this.reconnectAttempts >= this.maxReconnectAttempts) {
        this.notifyListeners('connection_error', { 
          message: 'Connection failed. Please check your network.' 
        });
      }
    });

    this.socket.on('reconnect', (attemptNumber) => {
      console.log('✅ WebSocket reconnected after', attemptNumber, 'attempts');
      this.isConnected = true;
      this.notifyListeners('reconnected', { attempts: attemptNumber });
    });

    this.socket.on('message', (data) => {
      this.notifyListeners('message', data);
    });

    // Handle mobile background/foreground
    if (typeof document !== 'undefined') {
      document.addEventListener('visibilitychange', () => {
        if (document.hidden) {
          console.log('App in background');
        } else if (!this.isConnected) {
          console.log('App in foreground, reconnecting...');
          this.socket?.connect();
        }
      });
    }
  }

  notifyListeners(event, data) {
    if (this.listeners[event]) {
      this.listeners[event].forEach(callback => {
        try {
          callback(data);
        } catch (error) {
          console.error('Listener error:', error);
        }
      });
    }
  }

  on(event, callback) {
    if (!this.listeners[event]) {
      this.listeners[event] = [];
    }
    this.listeners[event].push(callback);
  }

  off(event, callback) {
    if (this.listeners[event]) {
      this.listeners[event] = this.listeners[event].filter(cb => cb !== callback);
    }
  }

  getStatus() {
    return {
      connected: this.isConnected,
      reconnectAttempts: this.reconnectAttempts
    };
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
      this.isConnected = false;
    }
  }
}

export default new WebSocketService();