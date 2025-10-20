import React, { useState } from 'react';
import styled from 'styled-components';
import ReactMarkdown from 'react-markdown';
import surfApi from '../services/surfApi';

const SurfContainer = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
`;

const SearchSection = styled.div`
  background: rgba(255, 255, 255, 0.1);
  padding: 2rem;
  border-radius: 15px;
  margin-bottom: 2rem;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
`;

const SearchForm = styled.form`
  display: flex;
  gap: 1rem;
  align-items: center;
  flex-wrap: wrap;
`;

const Input = styled.input`
  padding: 0.8rem;
  border: none;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.9);
  color: #333;
  font-size: 1rem;
  min-width: 200px;
  
  &:focus {
    outline: none;
    box-shadow: 0 0 0 2px rgba(255, 255, 255, 0.5);
  }
`;

const Button = styled.button`
  padding: 0.8rem 1.5rem;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: bold;
  transition: all 0.3s ease;
  
  &:hover {
    background: rgba(255, 255, 255, 0.3);
    transform: translateY(-1px);
  }
`;

const ResultsSection = styled.div`
  background: rgba(255, 255, 255, 0.1);
  padding: 2rem;
  border-radius: 15px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: white;
`;

const LoadingText = styled.p`
  text-align: center;
  color: rgba(255, 255, 255, 0.8);
  font-size: 1.1rem;
`;

const ErrorText = styled.p`
  color: #ff6b6b;
  text-align: center;
  font-size: 1.1rem;
`;

const SurfPage = () => {
  const [beachName, setBeachName] = useState('');
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [surfData, setSurfData] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!beachName.trim()) return;

    setLoading(true);
    setError('');
    
    try {
          const data = await surfApi.getSurfData(beachName, selectedDate);
          console.log('DEBUG: Received surf data:', data);
          console.log('DEBUG: bestSurfTimes type:', typeof data.bestSurfTimes);
          console.log('DEBUG: bestSurfTimes value:', data.bestSurfTimes);
          setSurfData(data);
          setLoading(false);
    } catch (err) {
      setError('Failed to fetch surf data');
      setLoading(false);
    }
  };

  return (
    <SurfContainer>
      <SearchSection>
        <h2 style={{ color: 'white', marginBottom: '1rem' }}>🌊 Check Surf Conditions</h2>
        <SearchForm onSubmit={handleSubmit}>
          <Input
            type="text"
            placeholder="Enter beach name (e.g., pleasure point)"
            value={beachName}
            onChange={(e) => setBeachName(e.target.value)}
          />
          <Input
            type="date"
            value={selectedDate}
            onChange={(e) => setSelectedDate(e.target.value)}
          />
          <Button type="submit" disabled={loading}>
            {loading ? 'Loading...' : 'Get Surf Data'}
          </Button>
        </SearchForm>
      </SearchSection>

      <ResultsSection>
        {loading && <LoadingText>🌊 Fetching surf conditions...</LoadingText>}
        {error && <ErrorText>❌ {error}</ErrorText>}
                {surfData && (
                  <div>
                    <h3>🏖️ {surfData.beachName}</h3>
                    <p>📅 {surfData.date}</p>
                    <p style={{ color: '#4CAF50', fontWeight: 'bold', marginBottom: '1rem' }}>
                      ✅ Real Stormglass API Data
                    </p>
            
            {/* One Sentence Summary */}
            <div style={{ marginBottom: '2rem', padding: '1rem', background: 'rgba(255,255,255,0.1)', borderRadius: '8px' }}>
              <h4>🌊 Summary</h4>
              <p>{surfData.oneSentenceSummary}</p>
            </div>

                    {/* Current Conditions */}
                    <div style={{ marginBottom: '2rem' }}>
                      <h4>📊 Current Conditions</h4>
                      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginTop: '1rem' }}>
                        <div>Wave Height: <strong>{surfData.currentConditions.wave_height}ft</strong></div>
                        <div>Wave Period: <strong>{surfData.currentConditions.wave_period}s</strong></div>
                        <div>Wind Speed: <strong>{surfData.currentConditions.wind_speed}mph</strong></div>
                        <div>Water Temp: <strong>{surfData.currentConditions.water_temperature}°F</strong></div>
                        <div>Air Temp: <strong>{surfData.currentConditions.air_temperature}°F</strong></div>
                        <div>Tide: <strong>{surfData.currentConditions.tide}ft</strong></div>
                      </div>
                    </div>

                    {/* Best Surf Times */}
                    <div style={{ marginBottom: '2rem' }}>
                      <h4>🏄‍♂️ Best Surf Times</h4>
                      {Array.isArray(surfData.bestSurfTimes) && surfData.bestSurfTimes.length > 0 ? (
                        surfData.bestSurfTimes.map((time, index) => (
                          <div key={index} style={{ margin: '0.5rem 0', padding: '0.5rem', background: 'rgba(255,255,255,0.1)', borderRadius: '5px' }}>
                            <strong>{new Date(time.time).toLocaleTimeString()}</strong> - 
                            Wave: {time.wave_height}ft - 
                            Period: {time.wave_period}s - 
                            Wind: {time.wind_speed}mph - 
                            Score: {time.score}/50
                          </div>
                        ))
                      ) : (
                        <p style={{ opacity: 0.8, fontStyle: 'italic' }}>
                          {typeof surfData.bestSurfTimes === 'string' ? surfData.bestSurfTimes : 'No surf time data available'}
                        </p>
                      )}
                    </div>

            {/* AI Analysis */}
            <div>
              <h4>🤖 AI Analysis</h4>
              <div style={{ 
                marginTop: '1rem', 
                padding: '1rem', 
                background: 'rgba(255,255,255,0.1)', 
                borderRadius: '8px',
                lineHeight: '1.6'
              }}>
                <ReactMarkdown
                  components={{
                    h1: ({children}) => <h1 style={{color: '#4A90E2', fontSize: '1.5rem', margin: '1rem 0 0.5rem 0'}}>{children}</h1>,
                    h2: ({children}) => <h2 style={{color: '#4A90E2', fontSize: '1.3rem', margin: '1rem 0 0.5rem 0'}}>{children}</h2>,
                    h3: ({children}) => <h3 style={{color: '#4A90E2', fontSize: '1.1rem', margin: '0.8rem 0 0.4rem 0'}}>{children}</h3>,
                    p: ({children}) => <p style={{margin: '0.5rem 0', color: '#E8F4FD'}}>{children}</p>,
                    strong: ({children}) => <strong style={{color: '#7BB3F0', fontWeight: 'bold'}}>{children}</strong>,
                    ul: ({children}) => <ul style={{margin: '0.5rem 0', paddingLeft: '1.5rem', color: '#E8F4FD'}}>{children}</ul>,
                    li: ({children}) => <li style={{margin: '0.3rem 0', color: '#E8F4FD'}}>{children}</li>,
                    ol: ({children}) => <ol style={{margin: '0.5rem 0', paddingLeft: '1.5rem', color: '#E8F4FD'}}>{children}</ol>
                  }}
                >
                  {surfData.aiAnalysis}
                </ReactMarkdown>
              </div>
            </div>
          </div>
        )}
        {!loading && !error && !surfData && (
          <p style={{ textAlign: 'center', opacity: 0.8 }}>
            Enter a beach name and date to get surf conditions
          </p>
        )}
      </ResultsSection>
    </SurfContainer>
  );
};

export default SurfPage;
