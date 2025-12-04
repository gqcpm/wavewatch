import { theme } from './theme';

// Reusable styled-component mixins
export const glassCard = `
  background: ${theme.colors.background.glass};
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: ${theme.borderRadius.md};
`;

export const flexCenter = `
  display: flex;
  align-items: center;
  justify-content: center;
`;

export const textMuted = `
  color: ${theme.colors.text.muted};
  font-size: 0.9rem;
`;
