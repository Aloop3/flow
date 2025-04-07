/** @type {import('jest').Config} */
export default {
    preset: 'ts-jest',
    testEnvironment: 'jsdom',
    transform: {
      "^.+\\.(ts|tsx)$": ["ts-jest", { 
        useESM: true,
        tsconfig: "tsconfig.json" 
      }]
    },
    moduleNameMapper: {
      "\\.(css|less|scss|sass)$": "identity-obj-proxy",
      "\\.(jpg|jpeg|png|gif|eot|otf|webp|svg|ttf|woff|woff2|mp4|webm|wav|mp3|m4a|aac|oga)$": "<rootDir>/src/__mocks__/fileMock.js"
    },
    setupFilesAfterEnv: ["<rootDir>/src/setupTests.ts"],
    testPathIgnorePatterns: ["/node_modules/", "/dist/"]
  };