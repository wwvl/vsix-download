export interface Extension {
  id: number
  extension_id: string
  extension_name: string
  extension_full_name: string
  display_name: string
  short_description: string | null
  latest_version: string
  last_updated: string
  version_history: Array<{
    version: string
    lastUpdated: string
  }>
  categories: string[]
  tags: string[]
  download_url: string
  filename: string
  marketplace_url: string
}
