# Convention: React Component Patterns

## Component Structure
- One component per file
- Named exports (no default exports)
- Component file: `ComponentName.tsx`
- Test file: `ComponentName.test.tsx`
- Directory per component with index.ts barrel export

## Naming
- Components: PascalCase
- Hooks: camelCase with `use` prefix
- Event handlers: `on{Action}` prop name, `handle{Action}` implementation
- State: clear noun describing the value

## Example
```typescript
// CampaignList.tsx
interface CampaignListProps {
  onSelectCampaign: (id: string) => void;
}

export function CampaignList({ onSelectCampaign }: CampaignListProps) {
  // ...
}
```

## Styling
- Use Tailwind CSS utility classes
- No inline styles
- Conditional classes use clsx or template literals
