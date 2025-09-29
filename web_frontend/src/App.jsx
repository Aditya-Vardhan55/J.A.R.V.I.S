import { useState, useEffect, useRef } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'

const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
const recognition = new SpeechRecognition();
recognition.continuous = false;
recognition.lang = 'en-US';
recognition.interimResults = false;

function App() {
  const [messages, setMessages] = useState([{ sender: 'J.A.R.V.I.S.', text: "Hello! How can I help you?", type: 'bot-message' }]);
  const [input, setInput] = useState('');
  const [isListening, setIsListening] = useState(false);
  const chatBoxRef = useRef(null);

  useEffect(() => {
    if (chatBoxRef.current) {
      chatBoxRef.current.scrollTop = chatBoxRef.current.scrollHeight;
    }
  }, [messages]);

  const speak = (text) => {
    const utterance = new SpeechSynthesisUtterance(text);
    window.speechSynthesis.speak(utterance);
  };

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage = { sender: 'You', text: input, type: 'user-message' };
    setMessages(prev => [...prev, userMessage]);
    const currentInput = input;
    setInput('');

    try {
      const response = await fetch('http://127.0.0.1:5000/api/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: currentInput }),
      });

      const data = await response.json();
      const botResponseText = data.response || data.error;
      const botMessage = { sender: 'J.A.R.V.I.S.', text: botResponseText, type: 'bot-message' };

      setMessages(prev => [...prev, botMessage]);
      speak(botResponseText);
      
    } catch (error) {
      console.error("API Error:", error);
      const errorMessageText = 'Failed to connect to the assistant.';
      const errorMessage = { sender: 'System', text: errorMessageText, type: 'bot-message' };
      setMessages(prev => [...prev, errorMessage]);
      speak(errorMessageText);
    }
  };

  const handleListen = () => {
    if (isListening) {
      recognition.stop();
      setIsListening(false);
    } else {
      recognition.start();
      setIsListening(true);
    }
  };

  recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    setInput(transcript);
    recognition.stop();
    setIsListening(false);
  };

  recognition.onerror = (event) => {
    console.error("Speech recognition error:", event.error);
    setIsListening(false);
  };

  
  return (
    <div id='chat-container'>
      <h1>J.A.R.V.I.S.</h1>
      <div id='chat-box' ref={chatBoxRef}>
        {messages.map((msg, index) => (
          <div key={index} className={'message ${msg.type}'}>
            <strong>{msg.sender}</strong>
            <p>{msg.text}</p>
          </div>
        ))}
      </div>
      <div id='input-container'>
        <input 
          type="text" 
          id='user-input'
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSend()}
          placeholder='Ask me anything...'
        />
        <button id='mic-btn' onClick={handleListen} style={{backgroundColor: isListening ? '#ff4136' : '#007bff'}}>
          🎤
        </button>
        <button id='send-btn' onClick={handleSend}>Send</button>
      </div>
    </div>
  );
}

export default App;