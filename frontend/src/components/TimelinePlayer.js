import { useCallback, useEffect, useRef, useState } from 'react';
import './TimelinePlayer.css';

const TimelinePlayer = ({ years, selectedYear, onYearChange }) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [speed, setSpeed] = useState(500); // ms par année
  const intervalRef = useRef(null);

  const currentIndex = years.indexOf(selectedYear);

  const handlePlay = useCallback(() => {
    setIsPlaying(true);
  }, []);

  const handlePause = useCallback(() => {
    setIsPlaying(false);
  }, []);

  const handleStop = useCallback(() => {
    setIsPlaying(false);
    if (years.length > 0) {
      onYearChange(years[0]);
    }
  }, [years, onYearChange]);

  const handleSliderChange = useCallback((e) => {
    const index = parseInt(e.target.value, 10);
    onYearChange(years[index]);
  }, [years, onYearChange]);

  const handleSpeedChange = useCallback((e) => {
    setSpeed(parseInt(e.target.value, 10));
  }, []);

  const goToNextYear = useCallback(() => {
    const currentIdx = years.indexOf(selectedYear);
    if (currentIdx < years.length - 1) {
      onYearChange(years[currentIdx + 1]);
    } else {
      setIsPlaying(false);
    }
  }, [years, selectedYear, onYearChange]);

  const goToPrevYear = useCallback(() => {
    const currentIdx = years.indexOf(selectedYear);
    if (currentIdx > 0) {
      onYearChange(years[currentIdx - 1]);
    }
  }, [years, selectedYear, onYearChange]);

  // Animation de la timeline
  useEffect(() => {
    if (isPlaying) {
      intervalRef.current = setInterval(() => {
        goToNextYear();
      }, speed);
    } else {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [isPlaying, speed, goToNextYear]);

  if (years.length === 0) return null;

  return (
    <div className="timeline-player">
      <div className="timeline-controls">
        <button 
          className="control-btn" 
          onClick={handleStop}
          title="Retour au début"
        >
          <svg viewBox="0 0 24 24" fill="currentColor">
            <path d="M6 6h2v12H6zm3.5 6l8.5 6V6z"/>
          </svg>
        </button>
        <button 
          className="control-btn" 
          onClick={goToPrevYear}
          disabled={currentIndex === 0}
          title="Année précédente"
        >
          <svg viewBox="0 0 24 24" fill="currentColor">
            <path d="M11 18V6l-8.5 6 8.5 6zm.5-6l8.5 6V6l-8.5 6z"/>
          </svg>
        </button>
        {isPlaying ? (
          <button 
            className="control-btn play-pause" 
            onClick={handlePause}
            title="Pause"
          >
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M6 4h4v16H6V4zm8 0h4v16h-4V4z"/>
            </svg>
          </button>
        ) : (
          <button 
            className="control-btn play-pause" 
            onClick={handlePlay}
            disabled={currentIndex === years.length - 1}
            title="Lecture"
          >
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M8 5v14l11-7z"/>
            </svg>
          </button>
        )}
        <button 
          className="control-btn" 
          onClick={goToNextYear}
          disabled={currentIndex === years.length - 1}
          title="Année suivante"
        >
          <svg viewBox="0 0 24 24" fill="currentColor">
            <path d="M4 18l8.5-6L4 6v12zm9-12v12l8.5-6L13 6z"/>
          </svg>
        </button>
      </div>

      <div className="timeline-slider-container">
        <span className="timeline-year-label">{years[0]}</span>
        <div className="timeline-slider-wrapper">
          <input
            type="range"
            className="timeline-slider"
            min="0"
            max={years.length - 1}
            value={currentIndex}
            onChange={handleSliderChange}
          />
          <div className="timeline-year-display">{selectedYear}</div>
        </div>
        <span className="timeline-year-label">{years[years.length - 1]}</span>
      </div>

      <div className="timeline-speed">
        <label htmlFor="speed-control">Vitesse:</label>
        <select 
          id="speed-control"
          className="speed-selector"
          value={speed}
          onChange={handleSpeedChange}
        >
          <option value="1000">0.5x</option>
          <option value="500">1x</option>
          <option value="250">2x</option>
          <option value="125">4x</option>
        </select>
      </div>
    </div>
  );
};

export default TimelinePlayer;
