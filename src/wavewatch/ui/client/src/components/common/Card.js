import React from 'react';
import styled from 'styled-components';
import { theme } from '../../styles/theme';

const CardContainer = styled.div`
  background: ${theme.colors.background.primary};
  padding: ${props => props.padding || theme.spacing.lg};
  border-radius: ${theme.borderRadius.lg};
  border: 1px solid ${theme.colors.border.light};
  box-shadow: ${theme.shadows.md};
  ${props => props.marginBottom && `margin-bottom: ${props.marginBottom};`}
  transition: box-shadow 0.2s ease;

  &:hover {
    box-shadow: ${props => (props.hover ? theme.shadows.lg : theme.shadows.md)};
  }
`;

const Card = ({ children, padding, marginBottom, hover = false, ...props }) => {
  return (
    <CardContainer
      padding={padding}
      marginBottom={marginBottom}
      hover={hover}
      {...props}
    >
      {children}
    </CardContainer>
  );
};

export default Card;
