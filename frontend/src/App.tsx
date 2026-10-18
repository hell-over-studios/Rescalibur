import { useState, useCallback } from 'react';
import './App.css'; 
import ImageUploader from './components/ImageUploader';
import ResolutionSelector from './components/ResolutionSelector';
import ModeSelector from './components/ModeSelector';

function App() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [dimensions, setDimensions] = useState({ width: 0, height: 0 });
  const [targetHeight, setTargetHeight] = useState<number>(0);
  const [processingMode, setProcessingMode] = useState<'fast' | 'quality'>('fast');

  const handleImageReady = (file: File, width: number, height: number) => {
    setSelectedFile(file);
    setDimensions({ width, height });
  };

  const handleResolutionChange = useCallback((height: number) => {
    setTargetHeight(height);
  }, []);

  const handleModeChange = useCallback((mode: 'fast' | 'quality') => {
    setProcessingMode(mode);
  }, []);

  const handleProcess = () => {
    alert(`Listo para enviar a la API:\nArchivo: ${selectedFile?.name}\nAltura destino: ${targetHeight}p\nModo: ${processingMode}`);
  };

  return (
    <main className="main-container">
      <h1 className="title">Excalibur - Mejorador de Imágenes</h1>
      
      <ImageUploader onImageReady={handleImageReady} />

      {selectedFile && (
        <>
          <ResolutionSelector 
            originalWidth={dimensions.width} 
            originalHeight={dimensions.height}
            onResolutionChange={handleResolutionChange}
          />
          
          <ModeSelector onModeChange={handleModeChange} />

          <div className="action-container">
            <button className="btn btn-primary btn-large" onClick={handleProcess}>
              Mejorar Imagen
            </button>
          </div>
        </>
      )}
    </main>
  );
}

export default App;