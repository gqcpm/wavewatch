import React from 'react';
import styled from 'styled-components';
import { Link } from 'react-router-dom';
import Button from '../components/common/Button';
import { theme } from '../styles/theme';

const HomeContainer = styled.div`
  max-width: 1400px;
  margin: 0 auto;
  padding: ${theme.spacing.xl} ${theme.spacing.lg};
`;

const Hero = styled.div`
  text-align: center;
  margin: ${theme.spacing.xxl} 0;
  color: ${theme.colors.text.primary};
`;

const Title = styled.h1`
  font-size: ${theme.typography.fontSize['4xl']};
  font-weight: ${theme.typography.fontWeight.bold};
  margin-bottom: ${theme.spacing.md};
  font-family: ${theme.typography.fontFamily};
  color: ${theme.colors.text.primary};
  line-height: 1.2;

  @media (max-width: ${theme.breakpoints.mobile}) {
    font-size: ${theme.typography.fontSize['3xl']};
  }
`;

const Subtitle = styled.p`
  font-size: ${theme.typography.fontSize.xl};
  margin-bottom: ${theme.spacing.xl};
  color: ${theme.colors.text.secondary};
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
  line-height: 1.6;
`;

const CTAButton = styled(Button)`
  font-size: ${theme.typography.fontSize.lg};
  padding: ${theme.spacing.md} ${theme.spacing.xl};
`;

const Features = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: ${theme.spacing.xl};
  margin: ${theme.spacing.xxl} 0;
`;

const FeatureCard = styled.div`
  background: ${theme.colors.background.primary};
  padding: ${theme.spacing.xl};
  border-radius: ${theme.borderRadius.lg};
  border: 1px solid ${theme.colors.border.light};
  box-shadow: ${theme.shadows.md};
  transition: all 0.2s ease;

  &:hover {
    box-shadow: ${theme.shadows.lg};
    transform: translateY(-2px);
  }
`;

const FeatureIcon = styled.div`
  font-size: 3rem;
  margin-bottom: ${theme.spacing.md};
  text-align: center;
`;

const FeatureTitle = styled.h3`
  color: ${theme.colors.text.primary};
  margin-bottom: ${theme.spacing.sm};
  font-size: ${theme.typography.fontSize.xl};
  font-weight: ${theme.typography.fontWeight.bold};
  font-family: ${theme.typography.fontFamily};
`;

const FeatureText = styled.p`
  color: ${theme.colors.text.secondary};
  line-height: 1.6;
  font-size: ${theme.typography.fontSize.base};
`;

const HomePage = () => {
  return (
    <HomeContainer>
      <Hero>
        <Title>WaveWatch</Title>
        <Subtitle>
          Professional surf forecasting powered by real-time data and AI analysis. Get
          accurate wave conditions, wind forecasts, and personalized recommendations for
          your next surf session.
        </Subtitle>
        <CTAButton as={Link} to="/surf" variant="primary" size="large">
          Check Surf Forecast
        </CTAButton>
      </Hero>

      <Features>
        <FeatureCard>
          <FeatureIcon>📊</FeatureIcon>
          <FeatureTitle>Real-Time Data</FeatureTitle>
          <FeatureText>
            Get accurate wave height, wind conditions, and tide information from trusted
            sources like Stormglass and NOAA.
          </FeatureText>
        </FeatureCard>

        <FeatureCard>
          <FeatureIcon>🤖</FeatureIcon>
          <FeatureTitle>AI Analysis</FeatureTitle>
          <FeatureText>
            Powered by Google Gemini AI to provide intelligent surf condition analysis
            and personalized recommendations.
          </FeatureText>
        </FeatureCard>

        <FeatureCard>
          <FeatureIcon>📈</FeatureIcon>
          <FeatureTitle>Detailed Forecasts</FeatureTitle>
          <FeatureText>
            Visualize surf conditions throughout the day with interactive charts and
            hourly forecasts for optimal planning.
          </FeatureText>
        </FeatureCard>
      </Features>
    </HomeContainer>
  );
};

export default HomePage;
