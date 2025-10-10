import { useState, useEffect, useRef } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import { motion } from 'framer-motion';
import './App.css'

const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
let recognition;
if (SpeechRecognition) {
  recognition = new SpeechRecognition();
  recognition.continuous = false;
  recognition.lang = 'en-US';
  recognition.interimResults = false;
} else {
  console.log("Speech Recognition not supported by this browser.");
}

function App() {
  const [messages, setMessages] = useState([{ sender: 'J.A.R.V.I.S.', text: "Hello! How can I help you?", type: 'bot' }]);
  const [input, setInput] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const chatBoxRef = useRef(null);

  useEffect(() => {
    if (chatBoxRef.current) {
      chatBoxRef.current.scrollTop = chatBoxRef.current.scrollHeight;
    }
  }, [messages, isLoading]);

  const speak = (text) => {
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    window.speechSynthesis.speak(utterance);
  };

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage = { sender: 'You', text: input, type: 'user' };
    setMessages(prev => [...prev, userMessage]);
    const currentInput = input;
    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch('http://127.0.0.1:5000/api/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: currentInput }),
      });

      const data = await response.json();
      const botResponseText = data.response || data.error;
      const botMessage = { sender: 'J.A.R.V.I.S.', text: botResponseText, type: 'bot' };

      setMessages(prev => [...prev, botMessage]);
      speak(botResponseText);
      
    } catch (error) {
      console.error("API Error:", error);
      const errorMessageText = 'Failed to connect to the assistant.';
      const errorMessage = { sender: 'System', text: errorMessageText, type: 'bot-message' };
      setMessages(prev => [...prev, errorMessage]);
      speak(errorMessageText);
    } finally {
      setIsLoading(false);
    }
  };

  const handleListen = () => {
    if (!recognition) {
      alert("Speech Recognition is not supported by your browser.");
      return;
    }
    
    if (isListening) {
      recognition.stop();
      setIsListening(false);
    } else {
      recognition.start();
      setIsListening(true);
    }
  };

  if (recognition) {
    recognition.onresult = (event) => {
      const transcript = event.results[event.results.length - 1][0].transcript;
      setInput(transcript);
      setIsListening(false);
      setTimeout(() => document.getElementById('send-btn').click(), 50);
    };

    recognition.onerror = (event) => {
      console.error("Speech recognition error:", event.error);
      setIsListening(false);
    };
  }
  
  return (
    <div id="chat-container">
      <h1>J.A.R.V.I.S.</h1>
      <div id="chat-box" ref={chatBoxRef}>
        {messages.map((msg, index) => (
          <motion.div
            key={index}
            className={`message ${msg.type === 'user' ? 'user-message' : 'bot-message'}`}
            initial={{ opacity: 0, y: 20, x: msg.type === 'user' ? 20 : -20 }}
            animate={{ opacity: 1, y: 0, x: 0 }}
            transition={{ duration: 0.3 }}
          >
            <strong>{msg.sender}</strong>
            <p>{msg.text}</p>
          </motion.div>
        ))}
        {isLoading && (
          <div className='message bot-message'>
            <strong>J.A.R.V.I.S.</strong>
            <div className='loading-spinner'>
              <div className='spinner'></div>
            </div>
          </div>
        )}
      </div>
      <div id="input-container">
        <input
          type="text"
          id="user-input"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSend()}
          placeholder="Ask me anything..."
          disabled={isLoading}
        />
        <button
          id='mic-btn'
          onClick={handleListen}
          disabled={isLoading}
          style={{ backgroundColor: isListening ? '#ff4d4d': '#007bff' }}
        >
          🎤
          </button>
        <button id="send-btn" onClick={handleSend} disabled={isLoading}>
          {isLoading ? '...' : 'Send'}
        </button>
      </div>
    </div>
  );
}

export default App;