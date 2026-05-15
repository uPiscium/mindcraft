// eslint.config.js
import globals from "globals";
import pluginJs from "@eslint/js";
import noFloatingPromise from "eslint-plugin-no-floating-promise";
import tsParser from "@typescript-eslint/parser";
import tsPlugin from "@typescript-eslint/eslint-plugin";

/** @type {import('eslint').Linter.Config[]} */
export default [
  // First, import the recommended configuration
  pluginJs.configs.recommended,

  // Then override or customize specific rules
  {
    files: ["**/*.ts", "**/*.tsx"],
    languageOptions: {
      parser: tsParser,
      parserOptions: {
        ecmaVersion: 2022,
        sourceType: "module",
      },
      globals: {
        ...globals.browser,
        ...globals.node,
        Compartment: "readonly",
        lockdown: "readonly",
        harden: "readonly",
      },
    },
    plugins: {
      "@typescript-eslint": tsPlugin,
      "no-floating-promise": noFloatingPromise,
    },
    rules: {
      "no-undef": "off",
      "@typescript-eslint/no-explicit-any": "error",
    },
  },
  {
    plugins: {
      "no-floating-promise": noFloatingPromise,
    },
      languageOptions: {
        globals: {
          ...globals.browser,
          ...globals.node,
          Compartment: "readonly",
          lockdown: "readonly",
          harden: "readonly",
        },
      ecmaVersion: 2022,
      sourceType: "module",
    },
    rules: {
      "no-undef": "error",              // Disallow the use of undeclared variables or functions.
      "semi": ["error", "always"],      // Require the use of semicolons at the end of statements.
      "curly": "off",                   // Do not enforce the use of curly braces around blocks of code.
      "no-unused-vars": "off",          // Disable warnings for unused variables.
      "no-unreachable": "off",          // Disable warnings for unreachable code.
      "require-await": "error",         // Disallow async functions which have no await expression
      "no-floating-promise/no-floating-promise": "error", // Disallow Promises without error handling or awaiting
    },
  },
];
