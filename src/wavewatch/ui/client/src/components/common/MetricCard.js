import React from 'react';
import styled from 'styled-components';
import { theme } from '../../styles/theme';

const MetricContainer = styled.div`
  background: ${theme.colors.background.primary};
  border: 2px solid ${props => props.borderColor || theme.colors.border.light};
  border-radius: ${theme.borderRadius.md};
  padding: ${theme.spacing.md};
  display: flex;
  flex-direction: column;
  gap: ${theme.spacing.xs};
  transition: all 0.2s ease;
  position: relative;
  
  /* Subtle background highlight */
  ${props => props.borderColor && `
    background: linear-gradient(to bottom, 
      ${props.borderColor}08 0%, 
      ${theme.colors.background.primary} 100%
    );
  `}
  
  &:hover {
    border-color: ${props => props.borderColor || theme.colors.border.medium};
    box-shadow: ${props => props.borderColor 
      ? `0 2px 8px ${props.borderColor}20` 
      : theme.shadows.sm};
    transform: translateY(-1px);
  }
`;

const MetricLabel = styled.div`
  font-size: ${theme.typography.fontSize.sm};
  color: ${theme.colors.text.secondary};
  font-weight: ${theme.typography.fontWeight.medium};
  text-transform: uppercase;
  letter-spacing: 0.5px;
`;

const MetricValue = styled.div`
  font-size: ${props => props.size === 'large' ? theme.typography.fontSize['2xl'] : theme.typography.fontSize.xl};
  color: ${theme.colors.text.primary};
  font-weight: ${theme.typography.fontWeight.bold};
  line-height: 1.2;
`;

const MetricUnit = styled.span`
  font-size: ${theme.typography.fontSize.base};
  color: ${theme.colors.text.secondary};
  font-weight: ${theme.typography.fontWeight.normal};
  margin-left: 0.25rem;
`;

const MetricCard = ({ label, value, unit, size = 'medium', borderColor, ...props }) => {
  return (
    <MetricContainer borderColor={borderColor} {...props}>
      <MetricLabel>{label}</MetricLabel>
      <MetricValue size={size}>
        {value}
        {unit && <MetricUnit>{unit}</MetricUnit>}
      </MetricValue>
    </MetricContainer>
  );
};

export default MetricCard;

