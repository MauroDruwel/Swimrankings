/** @type {import('next').NextConfig} */
const withNextra = require('nextra')({
  theme: 'nextra-theme-docs',
  themeConfig: './theme.config.tsx',
  defaultShowCopyCode: true
})

const isGithubActions = process.env.GITHUB_ACTIONS || false

let assetPrefix = ''
let basePath = ''

if (isGithubActions) {
  // Ex: "/my-github-repo"
  const repo = process.env.GITHUB_REPOSITORY.replace(/.*?\//, '')
  assetPrefix = `/${repo}/`
  basePath = `/${repo}`
}

module.exports = withNextra({
  // Next.js config
  reactStrictMode: true,
  swcMinify: true,
  output: 'export',
  trailingSlash: true,
  skipTrailingSlashRedirect: true,
  distDir: 'out',
  images: {
    unoptimized: true
  },
  assetPrefix: assetPrefix,
  basePath: basePath,
})
