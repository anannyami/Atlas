# Atlas

**Understand any codebase before reading a single file.**

Atlas is a modern repository intelligence workspace that helps developers explore unfamiliar GitHub projects through a clean, interactive interface. Instead of navigating hundreds of files manually, Atlas organizes repository information into dedicated workspaces for architecture, dependencies, documentation, insights, and technology discovery.

Built with a strong emphasis on developer experience, smooth interactions, and scalable frontend architecture.

---

## Features

- GitHub-inspired repository explorer
- Repository workspace with dedicated analysis panels
- Repository overview dashboard
- Architecture workspace
- Dependency visualization workspace
- Documentation viewer
- Interactive file explorer
- Repository insights dashboard
- Technology stack overview
- Global repository search interface
- Dynamic right-side information panel
- Premium UI with glassmorphism and smooth animations
- Responsive layout
- Modular service-based architecture ready for backend integration

---

## Tech Stack

### Frontend

- React
- TypeScript
- Vite
- TanStack Router
- TanStack Query
- Tailwind CSS
- shadcn/ui
- Framer Motion
- Lucide React

### Architecture

- Component-based architecture
- Service layer abstraction
- Typed API interfaces
- Modular workspace design
- Reusable UI components

---

## Project Structure

```text
src/
├── components/
│   ├── ui/
│   └── workspace/
├── hooks/
├── lib/
├── routes/
├── services/
├── styles.css
└── router.tsx
```

---

## Workspace Modules

### Overview

Repository summary including metadata, repository statistics, language distribution, activity, and health indicators.

### Architecture

Visual workspace designed for repository architecture exploration and dependency understanding.

### Dependencies

Organized dependency information with package grouping and version details.

### Documentation

Integrated documentation viewer with Markdown rendering support.

### Explorer

IDE-inspired file explorer for navigating repository structure.

### Insights

Repository analysis workspace highlighting maintainability, architecture, and repository metrics.

### Tech Stack

Categorized technology overview for frontend, backend, infrastructure, testing, and tooling.

### Search

Centralized repository search experience for files, folders, components, and configuration.

### Settings

Workspace customization and user preferences.

---

## Design Philosophy

Atlas focuses on helping developers understand unfamiliar repositories quickly through:

- Clear information hierarchy
- Minimal visual clutter
- Smooth micro-interactions
- Editorial-inspired typography
- Consistent spacing
- Glassmorphism and subtle gradients
- Keyboard-friendly workflows
- Modular, scalable architecture

---

## Installation

Clone the repository

```bash
git clone https://github.com/anannyami/Atlas.git
```

Navigate into the project

```bash
cd Atlas
```

Install dependencies

```bash
npm install
```

Start the development server

```bash
npm run dev
```

---

## Future Improvements

- GitHub OAuth authentication
- Live GitHub API integration
- Repository architecture graph visualization
- Interactive dependency graph
- AI-powered repository summaries
- Static code analysis
- Repository health scoring
- Exportable analysis reports
- Team collaboration features

---

## Why Atlas?

Understanding an unfamiliar repository often requires navigating hundreds of files before identifying the project's architecture and technology stack.

Atlas aims to provide a centralized workspace where developers can quickly explore repository structure, documentation, dependencies, and key project insights before diving into implementation details.

---

## License

This project is licensed under the MIT License.