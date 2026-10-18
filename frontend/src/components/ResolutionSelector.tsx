import React, { useState, useEffect } from 'react';

interface ResolutionSelectorProps {
  originalWidth: number;
  originalHeight: number;
  onResolutionChange: (height: number) => void;
}

export default function ResolutionSelector({ originalWidth, originalHeight, onResolutionChange }: ResolutionSelectorProps) {
  const targetHeights = [480, 720, 1080];
  
  const availableHeights = targetHeights.filter(h => h > originalHeight);
  
  const [selectedHeight, setSelectedHeight] = useState<number>(availableHeights[0] || 0);

  useEffect(() => {
    if (selectedHeight > 0) {
      onResolutionChange(selectedHeight);
    }
  }, [selectedHeight, onResolutionChange]);

  if (originalHeight === 0) return null;

  if (availableHeights.length === 0) {
    return (
      <div className="card">
        <h2 className="card-title">2. Resolución de destino</h2>
        <p className="error-text">La imagen ya tiene 1080p o más de altura, por lo que no es posible ampliarla.</p>
      </div>
    );
  }

  const newWidth = Math.round(originalWidth * (selectedHeight / originalHeight));

  return (
    <div className="card">
      <h2 className="card-title">2. Resolución de destino</h2>
      
      <div className="button-group">
        {availableHeights.map(h => (
          <button
            key={h}
            onClick={() => setSelectedHeight(h)}
            className={`btn ${selectedHeight === h ? 'btn-active' : 'btn-outline'}`}
          >
            {h}p
          </button>
        ))}
      </div>

      <div className="info-box">
        <strong>Dimensiones resultantes estimadas:</strong> {newWidth} x {selectedHeight} px
      </div>
    </div>
  );
}