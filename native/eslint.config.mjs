import {FlatCompat} from "@eslint/eslintrc";
import {fileURLToPath} from "node:url";
import path from "node:path";
const compat=new FlatCompat({baseDirectory:path.dirname(fileURLToPath(import.meta.url))});

/**
 * Pre-existing violations in files owned by other workstreams. Each rule stays an error
 * everywhere else; these files report it as a warning until they are cleaned up, then
 * remove the entry (tracked in PR #37).
 */
const pendingCleanup=[
 {files:["components/TopBar.tsx","components/PlanCards.tsx","components/TeamPage.tsx"],rules:{"@next/next/no-html-link-for-pages":"warn"}},
 {files:["components/TeamPage.tsx","components/AccountAccess.tsx","app/history/page.tsx"],rules:{"react/no-unescaped-entities":"warn"}},
 {files:["lib/persistence/supabase.ts"],rules:{"@typescript-eslint/no-explicit-any":"warn"}},
 {files:["lib/powerRatings.ts"],rules:{"prefer-const":"warn"}}
];

const config=[
 {ignores:[".next/**","out/**","build/**","next-env.d.ts"]},
 ...compat.extends("next/core-web-vitals","next/typescript"),
 // Scheduled-function handlers receive a Request they do not use; an underscore marks that.
 {rules:{"@typescript-eslint/no-unused-vars":["warn",{argsIgnorePattern:"^_",varsIgnorePattern:"^_"}]}},
 ...pendingCleanup
];
export default config;
