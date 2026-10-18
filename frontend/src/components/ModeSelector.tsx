import React, { useState, useEffect } from 'react';

interface ModeSelectorProps {
  onModeChange: (mode: 'fast' | 'quality') => void;
}

export default function ModeSelector({ onModeChange }: ModeSelectorProps) {
  const [mode, setMode] = useState<'fast' | 'quality'>('fast');

  useEffect(() => {
    onModeChange(mode);
  }, [mode, onModeChange]);

  return (
    <div className="card">
      <h2 className="card-title">3. Modo de procesamiento</h2>
      
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        {/* El modo rápido usa interpolación bilineal y requiere menor costo computacional */}
        <label 
          style={{ 
            display: 'flex', alignItems: 'center', gap: '1rem', padding: '1rem', 
            border: `2px solid ${mode === 'fast' ? 'var(--primary)' : 'var(--border)'}`, 
            borderRadius: 'var(--radius-md)', cursor: 'pointer',
            backgroundColor: mode === 'fast' ? 'var(--primary-light)' : 'transparent',
            transition: 'var(--transition)'
          }}
        >
          <input 
            type="radio" 
            name="mode" 
            value="fast" 
            checked={mode === 'fast'} 
            onChange={() => setMode('fast')} 
            style={{ width: '1.2rem', height: '1.2rem', accentColor: 'var(--primary)', cursor: 'pointer' }}
          />
          <div>
            <strong style={{ display: 'block', fontSize: '1.05rem', color: mode === 'fast' ? 'var(--primary)' : 'var(--text-main)' }}>
              Rápido (Bilineal)
            </strong>
            <span style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>
              Menor costo computacional, ideal para resultados veloces.
            </span>
          </div>
        </label>

        {/* El modo de alta calidad usa interpolación bicúbica para mayor precisión[cite: 2] */}
        <label 
           style={{ 
            display: 'flex', alignItems: 'center', gap: '1rem', padding: '1rem', 
            border: `2px solid ${mode === 'quality' ? 'var(--primary)' : 'var(--border)'}`, 
            borderRadius: 'var(--radius-md)', cursor: 'pointer',
            backgroundColor: mode === 'quality' ? 'var(--primary-light)' : 'transparent',
            transition: 'var(--transition)'
          }}
        >
          <input 
            type="radio" 
            name="mode" 
            value="quality" 
            checked={mode === 'quality'} 
            onChange={() => setMode('quality')} 
            style={{ width: '1.2rem', height: '1.2rem', accentColor: 'var(--primary)', cursor: 'pointer' }}
          />
          <div>
            <strong style={{ display: 'block', fontSize: '1.05rem', color: mode === 'quality' ? 'var(--primary)' : 'var(--text-main)' }}>
              Alta Calidad (Bicúbica)
            </strong>
            <span style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>
              Mayor precisión y transiciones más suaves.
            </span>
          </div>
        </label>
      </div>
    </div>
  );
}