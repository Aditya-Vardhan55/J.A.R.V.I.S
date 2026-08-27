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
  const [isSpeaking, setIsSpeaking] = useState(false);
  const chatBoxRef = useRef(null);

  useEffect(() => {
    if (chatBoxRef.current) {
      chatBoxRef.current.scrollTop = chatBoxRef.current.scrollHeight;
    }
  }, [messages, isLoading]);

  const speak = (text) => {
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.onstart = () => setIsSpeaking(true);
    utterance.onend = () => setIsSpeaking(false);
    window.speechSynthesis.speak(utterance);
  };

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    window.speechSynthesis.cancel();
    setIsSpeaking(false);

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
      window.speechSynthesis.cancel();
      setIsSpeaking(false);
      recognition.start();
      setIsListening(true);
    }
  };

  const handleStopSpeaking = () => {
    window.speechSynthesis.cancel();
    setIsSpeaking(false);
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

    const IdleOrb = ({ isListening }) => (
      <motion.div
        className='idle-orb'
        initial={{ scale: 0.8, opacity: 0}}
        animate={{ scale: 1, opacity: 1}}
        transition={{ duration: 1, repeat: Infinity, repeatType: 'reverse' }}
        style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', zIndex: 10 }}
      >
        <div className='orb-glow'></div>
        {isListening && <div className='sound-arcs'></div>}
      </motion.div>
    );
  }
  
  return (
    <div id="chat-container">
      <h1>J.A.R.V.I.S.</h1>
      {!messages.length && <IdleOrb isListening={isListening} />}
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
            {isSpeaking && msg.type === 'bot' && (
              <svg className='speaking-wave' viewBox='0 0 100 20' style={{ width: '100%', height: '20px' }}>
                <motion.path 
                  d="M0 10 Q 25 0 50 10 T 100 10"
                  stroke='#00d4ff'
                  strokeWidth="2"
                  fill="none"
                  animate={{
                    d: 'M0 10 Q${Math.random()*50} ${Math.random()*20} 50 10 T 100 10'
                  }}
                  transition={{ repeat: Infinity, duration: 0.6, ease: "easeInOut" }}
                  />
              </svg>
            )}
          </motion.div>
        ))}
        {isLoading && (
          <motion.div className='message bot-message' initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
            <strong>J.A.R.V.I.S.</strong>
            <div className='thinking-galaxy'></div>
              {/* <div className='spinner'></div> */}
          </motion.div>
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
        {isSpeaking && (
          <button id='stop-btn' onClick={handleStopSpeaking} style={{backgroundColor: '#ff851b'}}>
            ⏹️
          </button>
        )}
        <button id="send-btn" onClick={handleSend} disabled={isLoading}>
          {isLoading ? '...' : 'Send'}
        </button>
      </div>
    </div>
  );
}

export default App;