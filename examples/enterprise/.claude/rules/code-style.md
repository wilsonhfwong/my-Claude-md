<important if="working on frontend code in frontend/">

## Frontend Conventions

- Components use the `ComponentName/` directory pattern:
  - `ComponentName/index.tsx` -- component
  - `ComponentName/ComponentName.test.tsx` -- tests
  - `ComponentName/ComponentName.stories.tsx` -- Storybook story
  - `ComponentName/types.ts` -- component-specific types (if needed)

- State management: Zustand for client state, React Query for server state.
  Never mix the two. Zustand stores in `frontend/src/stores/`.

- Styling: Tailwind CSS utility classes. No inline styles, no CSS modules.
  Custom design tokens in `frontend/tailwind.config.ts`.

- API calls: all go through generated client from proto definitions.
  Import from `frontend/src/api/generated/`. Never use raw `fetch`.

- Routing: Next.js App Router. New pages go in `frontend/src/app/`.
  Use server components by default. Add `"use client"` only when needed.

- Accessibility: all interactive elements need `aria-label` or visible label.
  Run `pnpm a11y` to check.

</important>
