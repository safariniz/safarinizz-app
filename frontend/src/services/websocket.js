import io from 'socket.io-client';

class WebSocketService {
  constructor() {
    this.socket = null;
    this.listeners = {};
  }

  connect(url, roomId = 'global') {
    if (this.socket) {
      this.socket.disconnect();
    }

    const wsUrl = url.replace('/api', '');
    this.socket = io(`${wsUrl}`, {
      path: '/ws/live-css',
      transports: ['websocket'],
      query: { room_id: roomId }
    });

    this.socket.on('connect', () => {
      console.log('✅ WebSocket connected');
    });

    this.socket.on('disconnect', () => {
      console.log('⚠️ WebSocket disconnected');
    });

    this.socket.on('message', (data) => {
      if (this.listeners['message']) {
        this.listeners['message'].forEach(callback => callback(data));
      }
    });
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

  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
    }
  }
}

export default new WebSocketService();