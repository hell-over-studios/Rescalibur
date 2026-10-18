import { useState, useCallback } from 'react';
import './App.css'; 
import ImageUploader from './components/ImageUploader';
import ResolutionSelector from './components/ResolutionSelector';

function App() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [dimensions, setDimensions] = useState({ width: 0, height: 0 });
  const [targetHeight, setTargetHeight] = useState<number>(0);

  const handleImageReady = (file: File, width: number, height: number) => {
    setSelectedFile(file);
    setDimensions({ width, height });
  };

  const handleResolutionChange = useCallback((height: number) => {
    setTargetHeight(height);
  }, []);

  return (
    <main className="main-container">
      <h1 className="title">Excalibur - Mejorador de Imágenes</h1>
      
      <ImageUploader onImageReady={handleImageReady} />

      {selectedFile && (
        <ResolutionSelector 
          originalWidth={dimensions.width} 
          originalHeight={dimensions.height}
          onResolutionChange={handleResolutionChange}
        />
      )}
    </main>
  );
}

export default App;