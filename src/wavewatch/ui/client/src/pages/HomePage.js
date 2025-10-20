import React from 'react';
import styled from 'styled-components';
import { Link } from 'react-router-dom';

const HomeContainer = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  text-align: center;
`;

const Hero = styled.div`
  margin: 4rem 0;
  color: white;
`;

const Title = styled.h1`
  font-size: 3rem;
  margin-bottom: 1rem;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
`;

const Subtitle = styled.p`
  font-size: 1.2rem;
  margin-bottom: 2rem;
  opacity: 0.9;
`;

const CTAButton = styled(Link)`
  display: inline-block;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  padding: 1rem 2rem;
  border-radius: 10px;
  text-decoration: none;
  font-weight: bold;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  
  &:hover {
    background: rgba(255, 255, 255, 0.3);
    transform: translateY(-2px);
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
  }
`;

const Features = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
  margin: 4rem 0;
`;

const FeatureCard = styled.div`
  background: rgba(255, 255, 255, 0.1);
  padding: 2rem;
  border-radius: 15px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
`;

const FeatureIcon = styled.div`
  font-size: 3rem;
  margin-bottom: 1rem;
`;

const FeatureTitle = styled.h3`
  color: white;
  margin-bottom: 1rem;
`;

const FeatureText = styled.p`
  color: rgba(255, 255, 255, 0.8);
  line-height: 1.6;
`;

const HomePage = () => {
  return (
    <HomeContainer>
      <Hero>
        <Title>🌊 WaveWatch</Title>
        <Subtitle>Your ultimate surf forecasting companion</Subtitle>
        <CTAButton to="/surf">Check Surf Conditions</CTAButton>
      </Hero>
      
      <Features>
        <FeatureCard>
          <FeatureIcon>📊</FeatureIcon>
          <FeatureTitle>Real-Time Data</FeatureTitle>
          <FeatureText>
            Get accurate wave height, wind conditions, and tide information 
            from trusted sources like Stormglass and NOAA.
          </FeatureText>
        </FeatureCard>
        
        <FeatureCard>
          <FeatureIcon>🤖</FeatureIcon>
          <FeatureTitle>AI Analysis</FeatureTitle>
          <FeatureText>
            Powered by Google Gemini AI to provide intelligent surf condition 
            analysis and personalized recommendations.
          </FeatureText>
        </FeatureCard>
        
        <FeatureCard>
          <FeatureIcon>🗺️</FeatureIcon>
          <FeatureTitle>Interactive Maps</FeatureTitle>
          <FeatureText>
            Visualize surf locations with directional overlays for swell 
            and wind patterns.
          </FeatureText>
        </FeatureCard>
      </Features>
    </HomeContainer>
  );
};

export default HomePage;
