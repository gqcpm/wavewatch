import React from 'react';
import styled from 'styled-components';
import { theme } from '../../styles/theme';

const StyledButton = styled.button`
  padding: ${props => {
    if (props.size === 'large') return '0.875rem 1.75rem';
    if (props.size === 'small') return '0.5rem 1rem';
    return '0.75rem 1.5rem';
  }};
  background: ${props => {
    if (props.variant === 'primary') return theme.colors.primary;
    if (props.variant === 'secondary') return theme.colors.background.secondary;
    return theme.colors.background.secondary;
  }};
  color: ${props =>
    props.variant === 'primary' ? theme.colors.white : theme.colors.text.primary};
  border: ${props =>
    props.variant === 'outline' ? `1px solid ${theme.colors.border.medium}` : 'none'};
  border-radius: ${theme.borderRadius.md};
  cursor: pointer;
  font-weight: ${theme.typography.fontWeight.semibold};
  font-size: ${theme.typography.fontSize.base};
  font-family: ${theme.typography.fontFamily};
  transition: all 0.2s ease;
  box-shadow: ${props => (props.variant === 'primary' ? theme.shadows.sm : 'none')};

  &:hover:not(:disabled) {
    background: ${props => {
      if (props.variant === 'primary') return theme.colors.secondary;
      if (props.variant === 'secondary') return theme.colors.background.tertiary;
      return theme.colors.background.tertiary;
    }};
    transform: translateY(-1px);
    box-shadow: ${props =>
      props.variant === 'primary' ? theme.shadows.md : theme.shadows.sm};
  }

  &:active:not(:disabled) {
    transform: translateY(0);
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    transform: none;
  }
`;

const Button = ({ children, variant = 'primary', size = 'medium', ...props }) => {
  return (
    <StyledButton variant={variant} size={size} {...props}>
      {children}
    </StyledButton>
  );
};

export default Button;
