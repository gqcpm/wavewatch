import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import styled from 'styled-components';
import Button from '../components/common/Button';
import Input from '../components/common/Input';
import Card from '../components/common/Card';
import { theme } from '../styles/theme';

const LoginContainer = styled.div`
  max-width: 400px;
  margin: ${theme.spacing.xl} auto;
`;

const Form = styled.form`
  display: flex;
  flex-direction: column;
  gap: ${theme.spacing.sm};
`;

const Title = styled.h2`
  color: ${theme.colors.text.primary};
  text-align: center;
  margin-bottom: ${theme.spacing.lg};
  font-size: ${theme.typography.fontSize['2xl']};
  font-weight: ${theme.typography.fontWeight.bold};
  font-family: ${theme.typography.fontFamily};
`;

const LinkText = styled.p`
  color: ${theme.colors.text.secondary};
  text-align: center;
  margin-top: ${theme.spacing.md};
  font-size: ${theme.typography.fontSize.base};
`;

const StyledLink = styled(Link)`
  color: ${theme.colors.primary};
  text-decoration: none;
  font-weight: ${theme.typography.fontWeight.semibold};

  &:hover {
    text-decoration: underline;
    color: ${theme.colors.secondary};
  }
`;

const LoginPage = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });

  const handleChange = e => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = e => {
    e.preventDefault();
    // Handle login logic here
  };

  return (
    <LoginContainer>
      <Card>
        <Title>Login</Title>
        <Form onSubmit={handleSubmit}>
          <Input
            type="email"
            name="email"
            placeholder="Email"
            value={formData.email}
            onChange={handleChange}
            required
          />
          <Input
            type="password"
            name="password"
            placeholder="Password"
            value={formData.password}
            onChange={handleChange}
            required
          />
          <Button type="submit">Login</Button>
        </Form>
        <LinkText>
          Don't have an account? <StyledLink to="/register">Register here</StyledLink>
        </LinkText>
      </Card>
    </LoginContainer>
  );
};

export default LoginPage;
