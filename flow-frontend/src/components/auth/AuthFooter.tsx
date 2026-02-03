import { View, Text } from '@aws-amplify/ui-react';

export function AuthFooter() {
  return (
    <View textAlign="center" padding="1rem">
      <Text
        style={{
          color: 'hsl(215, 16%, 47%)', // ocean-slate
          fontSize: '0.75rem',
        }}
      >
        Built for powerlifting athletes and coaches
      </Text>
    </View>
  );
}
