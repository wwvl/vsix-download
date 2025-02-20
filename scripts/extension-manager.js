import { promises as fs } from 'node:fs'
import path from 'node:path'
import process from 'node:process'
import { fileURLToPath } from 'node:url'
import { open } from 'sqlite'
import sqlite3 from 'sqlite3'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

/**
 * 从 VS Code Marketplace 获取扩展信息
 * @param {string} publisherExtension 扩展标识符 (publisher.extension)
 * @returns {Promise<object>} 扩展信息
 */
async function fetchExtensionInfo(publisherExtension) {
  const query = {
    assetTypes: [],
    filters: [
      {
        criteria: [
          { filterType: 8, value: 'Microsoft.VisualStudio.Code' },
          { filterType: 7, value: publisherExtension },
        ],
        pageNumber: 1,
        pageSize: 2,
      },
    ],
    flags: 0x1 | 0x4, // IncludeVersions | IncludeCategoryAndTags
  }

  const response = await fetch('https://marketplace.visualstudio.com/_apis/public/gallery/extensionquery', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Accept: 'application/json;api-version=3.0-preview.1',
      'Accept-Encoding': 'gzip',
      'User-Agent': 'VS Code Build',
    },
    body: JSON.stringify(query),
  })

  const data = await response.json()
  if (!data.results?.[0]?.extensions?.[0]) {
    throw new Error('找不到扩展信息')
  }

  const extension = data.results[0].extensions[0]
  const [publisherName, extensionName] = publisherExtension.split('.')
  const latestVersion = extension.versions[0].version

  return {
    extensionId: extension.extensionId,
    extensionName: extension.extensionName,
    extensionFullName: publisherExtension,
    displayName: extension.displayName,
    shortDescription: extension.shortDescription,
    downloadUrl: `https://marketplace.visualstudio.com/_apis/public/gallery/publishers/${publisherName}/vsextensions/${extensionName}/${latestVersion}/vspackage`,
    filename: `${publisherName}.${extensionName}-${latestVersion}.vsix`,
    marketplaceUrl: `https://marketplace.visualstudio.com/items?itemName=${publisherExtension}`,
    categories: extension.categories || [],
    tags: extension.tags || [],
    latest_version: {
      version: latestVersion,
      lastUpdated: extension.versions[0].lastUpdated,
    },
    version_history: extension.versions.slice(0, 6).map((v) => ({
      version: v.version,
      lastUpdated: v.lastUpdated,
    })),
  }
}

/**
 * 过滤标签，保留以 __ 开头的标签
 * @param {string[]} tags 标签列表
 * @returns {string[]} 过滤后的标签列表
 */
function filterTags(tags) {
  return tags.filter((tag) => tag.startsWith('__'))
}

/**
 * 初始化数据库
 * @param {string} dbPath 数据库路径
 */
async function initDatabase(dbPath) {
  const db = await open({
    filename: dbPath,
    driver: sqlite3.Database,
  })

  await db.exec(`
    CREATE TABLE IF NOT EXISTS extensions (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      extension_id TEXT NOT NULL UNIQUE,
      extension_name TEXT NOT NULL,
      extension_full_name TEXT NOT NULL UNIQUE,
      display_name TEXT NOT NULL,
      short_description TEXT,
      latest_version TEXT NOT NULL,
      last_updated DATETIME NOT NULL,
      version_history TEXT NOT NULL,
      categories TEXT,
      tags TEXT,
      download_url TEXT NOT NULL,
      filename TEXT NOT NULL,
      marketplace_url TEXT NOT NULL
    )
  `)

  await Promise.all([
    db.exec('CREATE INDEX IF NOT EXISTS idx_extension_full_name ON extensions(extension_full_name)'),
    db.exec('CREATE INDEX IF NOT EXISTS idx_last_updated ON extensions(last_updated)'),
    db.exec('CREATE INDEX IF NOT EXISTS idx_display_name ON extensions(display_name)'),
  ])

  return db
}

/**
 * 处理单个扩展
 * @param {object} params 处理参数
 */
async function processExtension(extensionId, db) {
  try {
    const data = await fetchExtensionInfo(extensionId)
    const filteredTags = filterTags(data.tags)

    const insertData = {
      extension_id: data.extensionId,
      extension_name: data.extensionName,
      extension_full_name: data.extensionFullName,
      display_name: data.displayName,
      short_description: data.shortDescription,
      latest_version: data.latest_version.version,
      last_updated: data.latest_version.lastUpdated,
      version_history: JSON.stringify(data.version_history),
      categories: JSON.stringify(data.categories),
      tags: JSON.stringify(filteredTags),
      download_url: data.downloadUrl,
      filename: data.filename,
      marketplace_url: data.marketplaceUrl,
    }

    await db.run(
      `
      INSERT OR REPLACE INTO extensions (
        extension_id, extension_name, extension_full_name, display_name,
        short_description, latest_version, last_updated, version_history,
        categories, tags, download_url, filename, marketplace_url
      ) VALUES (
        @extension_id, @extension_name, @extension_full_name, @display_name,
        @short_description, @latest_version, @last_updated, @version_history,
        @categories, @tags, @download_url, @filename, @marketplace_url
      )
    `,
      insertData,
    )

    console.log(`已导入：${data.extensionFullName}`)
    return true
  } catch (error) {
    console.error(`处理失败 ${extensionId}: ${error.message}`)
    return false
  }
}

/**
 * 从文件读取扩展列表
 */
async function readExtensionsFromFile(filePath) {
  const content = await fs.readFile(filePath, 'utf-8')
  return content
    .split('\n')
    .map((line) => line.trim())
    .filter((line) => line && !line.startsWith('#'))
}

/**
 * 主函数
 */
async function main() {
  try {
    const args = process.argv.slice(2)
    if (args.length !== 1) {
      console.log('使用方法：')
      console.log('单个扩展：node extension-manager.js publisher.extension')
      console.log('批量导入：node extension-manager.js extensions.txt')
      process.exit(1)
    }

    const baseDir = path.resolve(__dirname, '..')
    const dataDir = path.join(baseDir, 'src', 'data')
    const dbPath = path.join(dataDir, 'extensions.db')
    await fs.mkdir(dataDir, { recursive: true })

    // 初始化数据库
    const db = await initDatabase(dbPath)
    console.log(`开始导入数据到数据库：${dbPath}`)

    // 处理输入参数
    const input = args[0]
    const extensions = input.endsWith('.txt') ? await readExtensionsFromFile(input) : [input]

    // 处理扩展
    let successCount = 0
    let failedCount = 0

    for (const ext of extensions) {
      const success = await processExtension(ext, db)
      if (success) successCount++
      else failedCount++
    }

    // 输出统计信息
    console.log('\n导入完成统计：')
    console.log(`成功：${successCount} 个`)
    console.log(`失败：${failedCount} 个`)

    const { count } = await db.get('SELECT COUNT(*) as count FROM extensions')
    console.log(`数据库中总共有 ${count} 个扩展`)
    await db.close()
  } catch (error) {
    console.error('程序执行出错：', error)
    process.exit(1)
  }
}

main().catch(console.error)
