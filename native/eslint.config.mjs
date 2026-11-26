import {FlatCompat} from "@eslint/eslintrc";
import {fileURLToPath} from "node:url";
import path from "node:path";
const compat=new FlatCompat({baseDirectory:path.dirname(fileURLToPath(import.meta.url))});


const config=[
 {ignores:[".next/**","out/**","build/**","next-env.d.ts"]},
 ...compat.extends("next/core-web-vitals","next/typescript"),
 // Scheduled-function handlers receive a Request they do not use; an underscore marks that.
 {rules:{"@typescript-eslint/no-unused-vars":["warn",{argsIgnorePattern:"^_",varsIgnorePattern:"^_"}]}}
];
export default config;
