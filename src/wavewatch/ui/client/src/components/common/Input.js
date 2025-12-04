import React from 'react';
import styled from 'styled-components';
import { theme } from '../../styles/theme';

const StyledInput = styled.input`
  padding: 0.75rem 1rem;
  border: 1px solid ${theme.colors.border.light};
  border-radius: ${theme.borderRadius.md};
  background: ${theme.colors.background.primary};
  color: ${theme.colors.text.primary};
  font-size: ${theme.typography.fontSize.base};
  font-family: ${theme.typography.fontFamily};
  min-width: ${props => props.minWidth || '200px'};
  transition: all 0.2s ease;

  &:focus {
    outline: none;
    border-color: ${theme.colors.primary};
    box-shadow: 0 0 0 3px rgba(0, 102, 204, 0.1);
  }

  &::placeholder {
    color: ${theme.colors.text.muted};
  }

  &:disabled {
    background: ${theme.colors.background.secondary};
    cursor: not-allowed;
  }
`;

const Input = ({ minWidth, ...props }) => {
  return <StyledInput minWidth={minWidth} {...props} />;
};

export default Input;
