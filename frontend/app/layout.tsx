export const metadata = {
  title: '🎯 AI Prompt Doctor - Grammarly for AI Prompts',
  description: 'Find and fix prompt problems you didn\'t know existed. Turn 3/10 prompts into 9/10 prompts in 3 seconds. Free, instant, shareable.',
  openGraph: {
    title: 'AI Prompt Doctor - Grammarly for AI Prompts',
    description: 'Find and fix prompt problems you didn\'t know existed. Turn bad prompts into great ones in 3 seconds.',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'AI Prompt Doctor',
    description: 'Find and fix prompt problems you didn\'t know existed.',
  }
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <head>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </head>
      <body style={{ margin: 0, padding: 0 }}>{children}</body>
    </html>
  )
}
