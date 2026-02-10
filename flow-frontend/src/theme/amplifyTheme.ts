import { Theme } from '@aws-amplify/ui-react';

/**
 * Dark theme for Flow's login page
 *
 * Ocean colors adapted for dark background:
 * - Page bg: hsl(222, 47%, 7%)
 * - Card bg: hsl(222, 47%, 11%)
 * - Accent: teal hsl(175, 84%, 32-40%)
 * - Text: light grays
 */
export const amplifyTheme: Theme = {
  name: 'flow-dark-theme',
  tokens: {
    colors: {
      brand: {
        primary: {
          10: { value: 'hsl(175, 84%, 95%)' },
          20: { value: 'hsl(175, 84%, 80%)' },
          40: { value: 'hsl(175, 84%, 60%)' },
          60: { value: 'hsl(175, 84%, 45%)' },
          80: { value: 'hsl(175, 84%, 32%)' },   // button bg
          90: { value: 'hsl(175, 84%, 25%)' },   // hover
          100: { value: 'hsl(175, 84%, 20%)' },  // active
        },
      },
      background: {
        primary: { value: 'hsl(222, 47%, 7%)' },
        secondary: { value: 'hsl(222, 47%, 11%)' },
      },
      font: {
        primary: { value: 'hsl(210, 40%, 95%)' },
        secondary: { value: 'hsl(215, 20%, 55%)' },
        interactive: { value: 'hsl(175, 84%, 40%)' },
      },
      border: {
        primary: { value: 'rgba(255, 255, 255, 0.1)' },
        focus: { value: 'hsl(175, 84%, 40%)' },
      },
    },
    components: {
      authenticator: {
        router: {
          borderWidth: { value: '1px' },
          boxShadow: { value: '0 10px 25px -5px rgba(0, 0, 0, 0.3)' },
        },
      },
      button: {
        primary: {
          backgroundColor: { value: 'hsl(175, 84%, 32%)' },
          color: { value: 'white' },
          _hover: {
            backgroundColor: { value: 'hsl(175, 84%, 25%)' },
          },
          _focus: {
            backgroundColor: { value: 'hsl(175, 84%, 25%)' },
            boxShadow: { value: '0 0 0 2px hsl(175, 84%, 40%)' },
          },
          _active: {
            backgroundColor: { value: 'hsl(175, 84%, 20%)' },
          },
        },
        link: {
          color: { value: 'hsl(175, 84%, 40%)' },
          _hover: {
            color: { value: 'hsl(175, 84%, 50%)' },
            backgroundColor: { value: 'transparent' },
          },
        },
      },
      fieldcontrol: {
        borderColor: { value: 'rgba(255, 255, 255, 0.12)' },
        color: { value: 'hsl(210, 40%, 95%)' },
        _focus: {
          borderColor: { value: 'hsl(175, 84%, 40%)' },
          boxShadow: { value: '0 0 0 1px hsl(175, 84%, 40%)' },
        },
      },
      tabs: {
        item: {
          color: { value: 'hsl(215, 20%, 55%)' },
          _hover: {
            color: { value: 'hsl(210, 40%, 90%)' },
          },
          _active: {
            color: { value: 'hsl(210, 40%, 95%)' },
            borderColor: { value: 'hsl(175, 84%, 40%)' },
          },
        },
      },
    },
    fonts: {
      default: {
        variable: { value: "Inter, system-ui, sans-serif" },
        static: { value: "Inter, system-ui, sans-serif" },
      },
    },
    radii: {
      small: { value: '0.375rem' },
      medium: { value: '0.5rem' },
      large: { value: '0.75rem' },
    },
  },
};
