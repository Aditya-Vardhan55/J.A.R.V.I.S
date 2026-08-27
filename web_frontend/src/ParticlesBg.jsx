import { useCallback } from "react";
import Particles from 'react-tsparticles';
import { loadSlim } from 'tsparticles-slim';

const ParticlesBg = ({ children }) => {
    const particlesInit = useCallback(async (engine) => {
        await loadSlim(engine);
    }, []);

    const particlesOptions = {
        background: { color: { value: '#0a0a0a' } },
        fpsLimit: 60,
        interactivity: {
            events: { onHover: { enable: false, mode: 'repulse' }, onClick: { enable: true, mode: 'push' } },
            modes: { repulse: { distance: 100, duration: 0.4 }, push: { quantity: 2 } }
        },
        particles: {
            number: { value: 160, density: { enable: true, value_area: 800 } },
            color: { value: '#ffffff' },
            shape: { type: 'circle' },
            opacity: { value: 0.5, random: true, anim: { enable: true, speed: 1, opacity_min: 0.1 } },
            size: { value: 1, random: true },
            move: { enable: true, speed: 0.5, direction: 'none', random: false, straight: false, out_mode: 'out', bounce: false, attract: { enable: false} },

        },
        detectRetina: true,
    };

    return (
        <div style={{ position: 'relative', width: '100vw', height: '100vh', overflow: 'hidden' }}>
            <Particles id="tsparticles" init={particlesInit} options={particlesOptions} style={{ position: 'absolute', zIndex: 0 }}/>
            <div style={{ position: 'relative', zIndex: 1, height: '100%', width: '100%' }}>{children}</div>
        </div>
    );
};

export default ParticlesBg;