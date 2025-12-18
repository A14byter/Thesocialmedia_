const convId = 1;  // مثال
const chatSocket = new WebSocket(
    'ws://' + window.location.host + '/ws/chat/' + convId + '/'
);

chatSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    console.log(data);
};

chatSocket.onclose = function(e) {
    console.error('Chat socket closed unexpectedly');
};
