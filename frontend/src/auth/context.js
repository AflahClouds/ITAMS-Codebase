import { createContext } from 'react';

// The context object lives apart from the provider component so that AuthContext.jsx
// exports a component and nothing else — React Fast Refresh cannot preserve state
// across edits in a module that mixes component and non-component exports.
export const AuthContext = createContext(null);
