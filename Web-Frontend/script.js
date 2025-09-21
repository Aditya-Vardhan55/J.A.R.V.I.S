document.addEventListener('DOMContentLoaded', () => {
    const chatBox = document.getElementById('chat-box');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');

    // Function to send a message
    async function sendMessage() {
        const query = userInput.value;
        if (!query) return;

        // Display user's message
        appendMessage('You', query, 'user-message');
        userInput.value = '';

        try {
            // Send the query to your Flask backend
            const response = await fetch('http://127.0.0.1:5000/api/ask', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ query: query }),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            
            // Display bot's response
            appendMessage('J.A.R.V.I.S.', data.response || data.error, 'bot-message');

        } catch (error) {
            console.error('Error:', error);
            appendMessage('System', 'Failed to connect to the assistant.', 'bot-message');
        }
    }

    // Function to add a message to the chat window
    function appendMessage(sender, text, className) {
        const messageElement = document.createElement('div');
        messageElement.className = `message ${className}`;
        messageElement.innerHTML = `<strong>${sender}:</strong><p>${text}</p>`;
        chatBox.appendChild(messageElement);
        chatBox.scrollTop = chatBox.scrollHeight; // Auto-scroll to the bottom
    }

    // Event listeners
    sendBtn.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', (event) => {
        if (event.key === 'Enter') {
            sendMessage();
        }
    });
});