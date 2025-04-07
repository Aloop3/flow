// src/setupTests.ts
import '@testing-library/jest-dom';

// Use node's util for TextEncoder/TextDecoder
class TextEncoderPolyfill {
    encode(str) {
      return new Uint8Array([...str].map(c => c.charCodeAt(0)));
    }
  }
  
class TextDecoderPolyfill {
    decode(bytes) {
        return String.fromCharCode(...bytes);
    }
} 

// Set up the polyfills
global.TextEncoder = TextEncoderPolyfill;
global.TextDecoder = TextDecoderPolyfill;

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(),
    removeListener: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});