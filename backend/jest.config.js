// Jest em ESM nativo (rodado com node --experimental-vm-modules, ver package.json "test").
export default {
  testEnvironment: 'node',
  transform: {},
  setupFiles: ['<rootDir>/tests/setup.js'],
  testMatch: ['**/tests/**/*.test.js'],
};
