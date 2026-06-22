// Jest em ESM nativo (rodado com node --experimental-vm-modules, ver package.json "test").
export default {
  testEnvironment: 'node',
  transform: {},
  testMatch: ['**/tests/**/*.test.js'],
};
