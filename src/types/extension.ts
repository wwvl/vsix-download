export interface Extension {
  extensionId: string
  extensionName: string
  displayName: string
  shortDescription: string
  downloadUrl: string
  filename: string
  categories: string[]
  tags: string[]
  marketplaceUrl: string
  latest_version: {
    version: string
    lastUpdated: string
  }
  version_history: Array<{
    version: string
    lastUpdated: string
  }>
}
