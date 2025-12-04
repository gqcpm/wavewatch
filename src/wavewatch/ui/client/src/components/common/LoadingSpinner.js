import React from 'react';
import styled from 'styled-components';
import { theme } from '../../styles/theme';

const SpinnerContainer = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  padding: ${theme.spacing.xl};
`;

const SpinnerIcon = styled.div`
  width: 40px;
  height: 40px;
  border: 3px solid ${theme.colors.border.light};
  border-top-color: ${theme.colors.primary};
  border-radius: 50%;
  animation: spin 1s linear infinite;

  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }
`;

const SpinnerText = styled.p`
  color: ${theme.colors.text.secondary};
  font-size: ${theme.typography.fontSize.lg};
  margin-left: ${theme.spacing.md};
  font-weight: ${theme.typography.fontWeight.medium};
`;

const LoadingSpinner = ({ message = 'Loading...' }) => {
  return (
    <SpinnerContainer>
      <SpinnerIcon />
      <SpinnerText>{message}</SpinnerText>
    </SpinnerContainer>
  );
};

export default LoadingSpinner;
