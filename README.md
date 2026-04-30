# Faiz Ghifari Haznitrama — Personal Portfolio

Built with [Astro](https://astro.build) + [Tailwind CSS](https://tailwindcss.com).

## Quick Start

```bash
npm install
npm run dev     # Local dev server at http://localhost:4321
npm run build   # Build static site to dist/
```

## Site Structure

```
src/
├── components/
│   ├── Nav.astro           # Top navigation bar
│   ├── Footer.astro        # Site footer
│   ├── SocialLinks.astro   # Social/academic profile icons
│   └── DarkModeToggle.astro # Light/dark mode toggle
├── layouts/
│   └── BaseLayout.astro    # HTML shell used by all pages
├── pages/
│   ├── index.astro         # Homepage (papers + research focus)
│   ├── about/index.astro   # About page (bio, education, skills)
│   ├── research/index.astro # Research (publications, preprints, ongoing)
│   ├── experience/index.astro # Experience + projects timeline
│   ├── blog/index.astro    # Blog listing
│   └── 404.astro           # 404 page
├── styles/
│   └── global.css          # Global styles, Tailwind config
└── content/                # (future) MDX blog posts, paper data

public/
├── profile-square.jpg      # Profile photo (400x400)
├── profile-full.jpg        # Profile photo (full size)
├── favicon.svg             # Site favicon
└── robots.txt              # Search engine directives
```

## How to Edit Content

### Homepage (Recent Papers + Research)
Edit `src/pages/index.astro` — the frontmatter (between `---` blocks) has three arrays:
- `recentPapers` — published papers shown on homepage
- `recentPreprints` — arXiv/working papers
- `ongoingResearch` — current research projects

Each paper object:
```js
{
  title: 'Paper Title',
  authors: 'Author list',
  venue: 'ACL 2025',
  year: 2025,
  links: { pdf: 'url', arxiv: 'url', acl: 'url', github: 'url' },
}
```

### About Page
Edit `src/pages/about/index.astro` — update bio text, education timeline, research interests, skills, and contact info.

### Research Page
Edit `src/pages/research/index.astro` — three data arrays: `publications`, `preprints`, `ongoing`. Same paper format as homepage.

### Experience Page
Edit `src/pages/experience/index.astro` — `experiences` array with roles and nested `projects` arrays.

### Adding Blog Posts
Coming soon — MDX content collection will be set up for easy blog writing.

### Changing Colors/Theme
- Accent color: `src/styles/global.css` (indigo-600/400)
- Dark mode colors: `dark:` variants throughout
- Tailwind config: `tailwind.config.mjs`

### Changing Profile Photo
Replace `public/profile-square.jpg` (400x400) and `public/profile-full.jpg`.

### Social Links
Edit `src/components/SocialLinks.astro` — the `socials` array.

### Navigation Links
Edit `src/components/Nav.astro` — the `navLinks` array.

## Deployment

Push to `master` branch → GitHub Actions auto-builds and deploys to https://faizghifari.github.io

```bash
git add -A
git commit -m "your changes"
git push origin master
```

## Tech Stack

- **Astro 5** — Static site generator, zero JS by default
- **Tailwind CSS** — Utility-first styling
- **Inter + JetBrains Mono** — Fonts
- **GitHub Pages** — Hosting
- **GitHub Actions** — CI/CD
