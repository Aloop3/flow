import { Heading, View, useTheme } from '@aws-amplify/ui-react';

export function AuthHeader() {
  const { tokens } = useTheme();

  return (
    <View textAlign="center" padding={tokens.space.large}>
      <Heading
        level={3}
        style={{
          fontFamily: "'DM Sans', system-ui, sans-serif",
          fontWeight: 700,
          color: 'hsl(212, 52%, 25%)', // ocean-navy
          fontSize: '2rem',
          letterSpacing: '-0.02em',
        }}
      >
        Flow
      </Heading>
      <p
        style={{
          color: 'hsl(215, 16%, 47%)', // ocean-slate
          fontSize: '0.875rem',
          marginTop: '0.5rem',
        }}
      >
        Track powerlifting workouts
      </p>
    </View>
  );
}
