import React, { useState } from 'react';
import styled from 'styled-components';

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
      // This would connect to your backend API
      // const response = await fetch(`/api/surf/${beachName}/${selectedDate}`);
      // const data = await response.json();
      
      // For now, show placeholder
      setTimeout(() => {
        setSurfData({
          beachName: beachName,
          date: selectedDate,
          message: 'Surf data will be fetched from your backend API'
        });
        setLoading(false);
      }, 1000);
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
            <p>{surfData.message}</p>
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
