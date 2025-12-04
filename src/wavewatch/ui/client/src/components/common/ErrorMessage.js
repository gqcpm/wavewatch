import React from 'react';
import styled from 'styled-components';
import { theme } from '../../styles/theme';

const ErrorContainer = styled.div`
  color: ${theme.colors.accent.orange};
  text-align: center;
  font-size: ${theme.typography.fontSize.lg};
  padding: ${theme.spacing.lg};
  background: ${theme.colors.background.secondary};
  border-radius: ${theme.borderRadius.md};
  border: 1px solid ${theme.colors.accent.orange};
  font-weight: ${theme.typography.fontWeight.medium};
`;

const ErrorMessage = ({ message, children }) => {
  return <ErrorContainer>{children || (message && message)}</ErrorContainer>;
};

export default ErrorMessage;
