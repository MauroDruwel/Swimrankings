import React from 'react'
import { DocsThemeConfig } from 'nextra-theme-docs'

const config: DocsThemeConfig = {
  logo: <span>🏊‍♀️ <strong>SwimRankings</strong></span>,
  project: {
    link: 'https://github.com/MauroDruwel/swimrankings',
  },
  docsRepositoryBase: 'https://github.com/MauroDruwel/swimrankings/tree/main/docs',
  footer: {
    text: 'SwimRankings Python Library Documentation',
  },
  head: (
    <>
      <meta name="viewport" content="width=device-width, initial-scale=1.0" />
      <meta property="og:title" content="SwimRankings Python Library" />
      <meta property="og:description" content="A modern Python library for interacting with swimrankings.net" />
    </>
  ),
  primaryHue: 200,
  primarySaturation: 100,
  sidebar: {
    titleComponent({ title, type }) {
      if (type === 'separator') {
        return <span className="cursor-default">{title}</span>
      }
      return <>{title}</>
    },
    defaultMenuCollapseLevel: 1,
    toggleButton: true
  },
  toc: {
    backToTop: true
  },
  editLink: {
    text: 'Edit this page on GitHub →'
  },
  feedback: {
    content: 'Question? Give us feedback →',
    labels: 'feedback'
  },
  search: {
    placeholder: 'Search documentation...'
  },
  useNextSeoProps() {
    return {
      titleTemplate: '%s – SwimRankings'
    }
  }
}

export default config
