import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { theme } from '../../styles/theme';
import { authApi } from '../../services/authApi';
import Button from '../common/Button';

const HeaderContainer = styled.header`
  background: ${theme.colors.background.primary};
  border-bottom: 1px solid ${theme.colors.border.light};
  padding: ${theme.spacing.md} ${theme.spacing.lg};
  box-shadow: ${theme.shadows.sm};
  position: sticky;
  top: 0;
  z-index: 100;
`;

const Nav = styled.nav`
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1400px;
  margin: 0 auto;
`;

const Logo = styled(Link)`
  font-size: ${theme.typography.fontSize['2xl']};
  font-weight: ${theme.typography.fontWeight.bold};
  color: ${theme.colors.primary};
  text-decoration: none;
  display: flex;
  align-items: center;
  gap: ${theme.spacing.xs};
  font-family: ${theme.typography.fontFamily};

  &:hover {
    color: ${theme.colors.secondary};
  }
`;

const LogoIcon = styled.span`
  font-size: ${theme.typography.fontSize['3xl']};
`;

const NavLinks = styled.div`
  display: flex;
  gap: ${theme.spacing.md};
  align-items: center;
`;

const NavLink = styled(Link)`
  color: ${theme.colors.text.primary};
  text-decoration: none;
  padding: ${theme.spacing.xs} ${theme.spacing.sm};
  border-radius: ${theme.borderRadius.md};
  transition: all 0.2s ease;
  font-weight: ${theme.typography.fontWeight.medium};
  font-size: ${theme.typography.fontSize.base};

  &:hover {
    background-color: ${theme.colors.background.secondary};
    color: ${theme.colors.primary};
  }
`;

const UserInfo = styled.div`
  display: flex;
  align-items: center;
  gap: ${theme.spacing.sm};
`;

const UserAvatar = styled.img`
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: 2px solid ${theme.colors.border.light};
`;

const UserName = styled.span`
  color: ${theme.colors.text.primary};
  font-weight: ${theme.typography.fontWeight.medium};
  font-size: ${theme.typography.fontSize.sm};
`;

const LogoutButton = styled(Button)`
  padding: ${theme.spacing.xs} ${theme.spacing.sm};
  font-size: ${theme.typography.fontSize.sm};
`;

const Header = () => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const status = await authApi.getStatus();
        if (status.authenticated) {
          setUser(status.user);
        }
      } catch (error) {
        // Silently handle auth check errors
      } finally {
        setLoading(false);
      }
    };

    checkAuth();
  }, []);

  const handleLogout = async () => {
    try {
      await authApi.logout();
      setUser(null);
      navigate('/login');
    } catch (error) {
      // Silently handle logout errors
    }
  };

  return (
    <HeaderContainer>
      <Nav>
        <Logo to="/">
          <LogoIcon>🌊</LogoIcon>
          WaveWatch
        </Logo>
        <NavLinks>
          <NavLink to="/">Home</NavLink>
          <NavLink to="/surf">Forecast</NavLink>
          {!loading && (
            <>
              {user ? (
                <UserInfo>
                  {user.picture && <UserAvatar src={user.picture} alt={user.name} />}
                  <UserName>{user.name}</UserName>
                  <LogoutButton onClick={handleLogout}>Logout</LogoutButton>
                </UserInfo>
              ) : (
                <>
                  <NavLink to="/login">Login</NavLink>
                  <NavLink to="/register">Sign Up</NavLink>
                </>
              )}
            </>
          )}
        </NavLinks>
      </Nav>
    </HeaderContainer>
  );
};

export default Header;
