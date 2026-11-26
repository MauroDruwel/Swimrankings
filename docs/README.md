# SwimRankings Documentation

This directory contains the documentation website for the SwimRankings Python library, built with [Nextra](https://nextra.site/) - a modern documentation theme for Next.js.

## Features

- 🎨 **Beautiful Design**: Modern, responsive documentation theme
- 🔍 **Full-text Search**: Built-in search functionality
- 📱 **Mobile-friendly**: Responsive design that works on all devices
- 🌙 **Dark Mode**: Toggle between light and dark themes
- 📖 **Table of Contents**: Auto-generated navigation
- 💻 **Code Highlighting**: Syntax highlighting for code examples
- 🔗 **Live Links**: Direct links to GitHub repository

## Quick Start

### Prerequisites

- Node.js 18.17 or higher (for Next.js 14)
- npm

### Setup

1. **Install dependencies:**
   ```bash
   cd docs
   npm ci
   ```

2. **Start development server:**
   ```bash
   npm run dev
   ```

3. **Open in browser:**
   Visit [http://localhost:3000](http://localhost:3000)

## Development

### File Structure

```
docs/
├── pages/                   # Documentation pages
│   ├── index.mdx            # Homepage
│   ├── installation.mdx     # Installation guide
│   ├── quick-start.mdx      # Quick start guide
│   ├── examples.mdx         # Usage examples & cookbook
│   ├── reference-data.mdx   # Reference data guide
│   ├── api-reference.mdx    # Complete API reference
│   ├── error-handling.mdx   # Error handling guide
│   ├── contributing.mdx     # Contributing guide
│   └── _meta.json           # Page navigation configuration
├── theme.config.tsx         # Nextra theme configuration
├── next.config.js          # Next.js static export configuration
├── package.json            # Dependencies and scripts
└── tsconfig.json           # TypeScript configuration
```

### Adding New Pages

1. **Create a new `.mdx` file** in the `pages` directory
2. **Add the page to `_meta.json`** to include it in navigation
3. **Use Nextra components** for enhanced functionality

Example page structure:

```mdx
# Page Title

Introduction paragraph.

## Section

Content with code examples:

```python
from swimrankings import Athletes
athletes = Athletes(name="Example")
```

import { Callout } from 'nextra/components'

<Callout type="info">
  This is an info callout.
</Callout>
```

### Available Components

Nextra provides several built-in components:

```mdx
import { Callout, Cards, Card, Steps, Tabs, Tab } from 'nextra/components'

<Callout type="info" emoji="ℹ️">
  Information callout
</Callout>

<Callout type="warning" emoji="⚠️">
  Warning callout
</Callout>

<Callout type="error" emoji="🚨">
  Error callout
</Callout>

<Cards>
  <Card icon="📖" title="Guide" href="/guide" />
</Cards>

<Steps>
### Step 1
First step description.

### Step 2
Second step description.
</Steps>

<Tabs items={['Python', 'JavaScript']}>
  <Tab>
    ```python
    print("Hello from Python")
    ```
  </Tab>
  <Tab>
    ```javascript
    console.log("Hello from JavaScript")
    ```
  </Tab>
</Tabs>
```

## Configuration

### Theme Configuration

Edit `theme.config.tsx` to customize:

- Site logo and title
- Navigation links
- Footer content
- Color scheme
- Social links

### Next.js Configuration

Edit `next.config.js` for:

- Build settings
- Custom redirects
- Performance optimizations

## Building for Production

`next.config.js` configures `output: 'export'` with `distDir: 'out'`.

```bash
# Build the static site into docs/out/
npm run build

# Start production preview server
npm run start
```

## Deployment

Deploy the generated `docs/out/` directory to Cloudflare Pages, Vercel, Netlify, or GitHub Pages (`npm run build`).

## Writing Guidelines

### Code Examples

- Always include working code examples
- Use realistic data (like "Smith", "Johnson", etc.)
- Show both success and error cases
- Include imports and setup code

### Documentation Style

- Use clear, concise language
- Include practical examples
- Explain the "why" not just the "how"
- Use consistent terminology
- Add callouts for important information

### Markdown Features

- Use proper heading hierarchy (`#`, `##`, `###`)
- Include code syntax highlighting
- Add links to related sections
- Use tables for structured data
- Include images when helpful

## Maintenance

### Updating Dependencies

```bash
npm update
```

### Checking for Vulnerabilities

```bash
npm audit
npm audit fix
```

### Performance

The site is optimized for:

- Fast loading times
- SEO optimization
- Mobile responsiveness
- Accessibility

## Troubleshooting

### Common Issues

**Build fails with TypeScript errors:**
- Check `tsconfig.json` configuration
- Ensure all dependencies are installed

**Styles not loading:**
- Clear `.next` directory: `rm -rf .next`
- Rebuild: `npm run build`

**Search not working:**
- Ensure all pages have proper frontmatter
- Rebuild the search index

### Getting Help

- Check [Nextra documentation](https://nextra.site/)
- Review [Next.js documentation](https://nextjs.org/docs)
- Open an issue in the project repository

## Contributing to Documentation

1. Follow the writing guidelines above
2. Test your changes locally
3. Ensure all links work
4. Check mobile responsiveness
5. Submit a pull request

The documentation is as important as the code - thank you for helping make it better! 📚
