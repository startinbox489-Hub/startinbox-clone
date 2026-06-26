import nextJest from 'next/jest.js';
import type { Config } from 'jest';

const createJestConfig = nextJest({
	dir: './',
});

const config: Config = {
	coverageProvider: 'v8',
	testEnvironment: 'jsdom',

	setupFilesAfterEnv: ['<rootDir>/jest.setup.ts'],

	moduleNameMapper: {
		'^@/(.*)$': '<rootDir>/$1',
		'^@common/(.*)$': '<rootDir>/src/common/$1',

		'^@components/(.*)$': '<rootDir>/src/components/$1',
	},

	testPathIgnorePatterns: [
		'<rootDir>/.next/',
		'<rootDir>/node_modules/',
		'<rootDir>/__tests__/test-config/',
	],

	collectCoverageFrom: [
		'./**/*.{ts,tsx}',
		'!./**/*.d.ts',
		'!./**/index.ts',
		'!./__tests__/test-config/**',
		'!./**/*.mock.{ts,tsx}',
	],
};

export default createJestConfig(config);
