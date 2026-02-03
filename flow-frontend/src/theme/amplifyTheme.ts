import { Theme } from '@aws-amplify/ui-react';

/**
 * Custom Amplify Authenticator theme using Flow's ocean palette
 *
 * Ocean colors:
 * - navy-dark: hsl(222, 47%, 11%) - darkest
 * - navy: hsl(212, 52%, 25%) - primary buttons
 * - teal: hsl(175, 84%, 32%) - accents, success
 * - seafoam-light: hsl(152, 76%, 90%) - light backgrounds
 * - mist: hsl(210, 40%, 96%) - page background
 * - slate: hsl(215, 16%, 47%) - muted text
 */
export const amplifyTheme: Theme = {
  name: 'flow-ocean-theme',
  tokens: {
    colors: {
      brand: {
        primary: {
          10: { value: 'hsl(152, 76%, 90%)' },  // seafoam-light
          20: { value: 'hsl(175, 84%, 80%)' },
          40: { value: 'hsl(175, 84%, 60%)' },
          60: { value: 'hsl(175, 84%, 40%)' },
          80: { value: 'hsl(175, 84%, 32%)' },  // teal
          90: { value: 'hsl(212, 52%, 25%)' },  // navy
          100: { value: 'hsl(222, 47%, 11%)' }, // navy-dark
        },
      },
      background: {
        primary: { value: 'hsl(210, 40%, 96%)' },   // mist
        secondary: { value: 'hsl(0, 0%, 100%)' },   // white
      },
      font: {
        primary: { value: 'hsl(222, 47%, 11%)' },   // navy-dark
        secondary: { value: 'hsl(215, 16%, 47%)' }, // slate
        interactive: { value: 'hsl(175, 84%, 32%)' }, // teal
      },
      border: {
        primary: { value: 'hsl(215, 20%, 85%)' },
        focus: { value: 'hsl(175, 84%, 32%)' },     // teal
      },
    },
    components: {
      authenticator: {
        router: {
          borderWidth: { value: '0' },
          boxShadow: { value: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)' },
        },
      },
      button: {
        primary: {
          backgroundColor: { value: 'hsl(212, 52%, 25%)' }, // navy
          color: { value: 'white' },
          _hover: {
            backgroundColor: { value: 'hsl(222, 47%, 11%)' }, // navy-dark
          },
          _focus: {
            backgroundColor: { value: 'hsl(222, 47%, 11%)' },
            boxShadow: { value: '0 0 0 2px hsl(175, 84%, 32%)' }, // teal ring
          },
          _active: {
            backgroundColor: { value: 'hsl(222, 47%, 15%)' },
          },
        },
        link: {
          color: { value: 'hsl(175, 84%, 32%)' }, // teal
          _hover: {
            color: { value: 'hsl(175, 84%, 25%)' },
            backgroundColor: { value: 'transparent' },
          },
        },
      },
      fieldcontrol: {
        borderColor: { value: 'hsl(215, 20%, 85%)' },
        _focus: {
          borderColor: { value: 'hsl(175, 84%, 32%)' }, // teal
          boxShadow: { value: '0 0 0 1px hsl(175, 84%, 32%)' },
        },
      },
      tabs: {
        item: {
          color: { value: 'hsl(215, 16%, 47%)' }, // slate
          _hover: {
            color: { value: 'hsl(212, 52%, 25%)' }, // navy
          },
          _active: {
            color: { value: 'hsl(212, 52%, 25%)' }, // navy
            borderColor: { value: 'hsl(175, 84%, 32%)' }, // teal
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
