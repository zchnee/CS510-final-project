import { translate } from '@vitalets/google-translate-api'

let input = ''

process.stdin.setEncoding('utf8')

process.stdin.on('data', (chunk) => {
  input += chunk
})

process.stdin.on('end', async () => {
  try {
    const { text, to = 'en', from = 'auto' } = JSON.parse(input)
    const result = await translate(text, { from, to })

    process.stdout.write(JSON.stringify({
      text: result.text,
    }))
  } catch (error) {
    process.stderr.write(error instanceof Error ? error.message : String(error))
    process.exit(1)
  }
})
