import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import styled from 'styled-components';
import Button from '../components/common/Button';
import Input from '../components/common/Input';
import Card from '../components/common/Card';
import { theme } from '../styles/theme';

const RegisterContainer = styled.div`
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

const RegisterPage = () => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
  });

  const handleChange = e => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = e => {
    e.preventDefault();
    // Handle registration logic here
  };

  return (
    <RegisterContainer>
      <Card>
        <Title>Sign Up</Title>
        <Form onSubmit={handleSubmit}>
          <Input
            type="text"
            name="username"
            placeholder="Username"
            value={formData.username}
            onChange={handleChange}
            required
          />
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
          <Input
            type="password"
            name="confirmPassword"
            placeholder="Confirm Password"
            value={formData.confirmPassword}
            onChange={handleChange}
            required
          />
          <Button type="submit">Register</Button>
        </Form>
        <LinkText>
          Already have an account? <StyledLink to="/login">Login here</StyledLink>
        </LinkText>
      </Card>
    </RegisterContainer>
  );
};

export default RegisterPage;
