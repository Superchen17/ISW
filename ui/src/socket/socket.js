import SocketIO from 'socket.io-client';

export const socket = SocketIO('localhost:8888')
// export const socket = SocketIO(process.env.REACT_APP_SERVER_URL);