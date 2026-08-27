import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import ParticlesBg from './ParticlesBg.jsx';
import './index.css'
import App from './App.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <ParticlesBg>
      <App />
    </ParticlesBg>
  </StrictMode>,
)
