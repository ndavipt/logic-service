# CLAUDE.md - Logic Service

## Architecture Context
- Part of microservice architecture: [Scraper-Service] → [PostgreSQL] → [Logic-Service] → [Frontend-Service]
- Logic-Service handles calculations, caching, and API endpoints between PostgreSQL and Frontend

## Database Connection
- PostgreSQL tables:
  - instagram_accounts (id, username, status, created_at)
  - instagram_profiles (id, account_id, follower_count, profile_pic_url, full_name, biography, checked_at)

## Build/Test Commands
- Build: `npm run build` or `yarn build`
- Start dev server: `npm run dev` or `yarn dev`
- Run all tests: `npm test` or `yarn test`
- Run single test: `npm test -- -t "test name"` or `yarn test -t "test name"`
- Lint: `npm run lint` or `yarn lint`

## Code Style Guidelines
- **Naming**: camelCase for variables/functions, PascalCase for components/classes
- **Imports**: Group by: 1) standard libraries, 2) external packages, 3) internal modules
- **Formatting**: 2-space indentation, 100 char line limit
- **Error Handling**: Use structured try/catch with proper logging
- **Types**: Use TypeScript with explicit types for function parameters and returns
- **API Design**: RESTful endpoints with consistent naming and response structures
- **Comments**: JSDoc for public APIs and complex logic only