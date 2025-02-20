// pnpm add sqlite3 sqlite
import { promises as fs } from 'node:fs'
import path from 'node:path'
import process from 'node:process'
import { fileURLToPath } from 'node:url'
import { isMainThread, parentPort, Worker, workerData } from 'node:worker_threads'
import { open } from 'sqlite'
import sqlite3 from 'sqlite3'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

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
 * @returns {Promise<import('sqlite').Database>}
 */
async function initDatabase(dbPath) {
  const db = await open({
    filename: dbPath,
    driver: sqlite3.Database,
  })

  // 创建扩展表
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

  // 创建索引
  await Promise.all([
    db.exec('CREATE INDEX IF NOT EXISTS idx_extension_full_name ON extensions(extension_full_name)'),
    db.exec('CREATE INDEX IF NOT EXISTS idx_last_updated ON extensions(last_updated)'),
    db.exec('CREATE INDEX IF NOT EXISTS idx_display_name ON extensions(display_name)'),
  ])

  return db
}

/**
 * 处理单个 JSON 文件
 * @param {object} params 处理参数
 * @returns {Promise<[string, boolean, string|null]>} 处理结果
 */
async function processJsonFile({ filePath, dbPath }) {
  try {
    // 读取 JSON 文件
    const content = await fs.readFile(filePath, 'utf-8')
    const data = JSON.parse(content)

    // 过滤标签
    const filteredTags = filterTags(data.tags)

    // 准备插入的数据
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

    const db = await open({
      filename: dbPath,
      driver: sqlite3.Database,
    })

    await db.run(
      `
      INSERT OR REPLACE INTO extensions (
        extension_id,
        extension_name,
        extension_full_name,
        display_name,
        short_description,
        latest_version,
        last_updated,
        version_history,
        categories,
        tags,
        download_url,
        filename,
        marketplace_url
      ) VALUES (
        @extension_id,
        @extension_name,
        @extension_full_name,
        @display_name,
        @short_description,
        @latest_version,
        @last_updated,
        @version_history,
        @categories,
        @tags,
        @download_url,
        @filename,
        @marketplace_url
      )
    `,
      insertData,
    )

    await db.close()
    return [data.extensionFullName, true, null]
  } catch (error) {
    return [filePath, false, error.message]
  }
}

/**
 * Worker 线程处理函数
 */
async function workerProcess() {
  const result = await processJsonFile(workerData)
  parentPort.postMessage(result)
}

/**
 * 导入 JSON 文件到数据库
 * @param {string} jsonDir JSON 文件目录
 * @param {string} dbPath 数据库路径
 * @param {number} maxWorkers 最大工作线程数
 * @returns {Promise<[number, number]>}
 */
async function importJsonToDb(jsonDir, dbPath, maxWorkers = 4) {
  // 初始化数据库
  await initDatabase(dbPath)

  // 获取所有 JSON 文件
  const files = (await fs.readdir(jsonDir)).filter((file) => file.endsWith('.json')).map((file) => path.join(jsonDir, file))

  console.log(`开始使用 ${maxWorkers} 个线程处理 ${files.length} 个文件...`)

  let successCount = 0
  let failedCount = 0
  let completedCount = 0

  const processFile = async (filePath) => {
    const worker = new Worker(import.meta.url, {
      workerData: { filePath, dbPath },
    })

    return new Promise((resolve, reject) => {
      worker.on('message', ([fileName, success, error]) => {
        completedCount++
        if (success) {
          successCount++
          console.log(`已导入 [${completedCount}/${files.length}]: ${fileName}`)
        } else {
          failedCount++
          console.error(`处理失败 [${completedCount}/${files.length}] ${fileName}: ${error}`)
        }
        resolve()
      })

      worker.on('error', reject)
      worker.on('exit', (code) => {
        if (code !== 0) {
          reject(new Error(`Worker stopped with exit code ${code}`))
        }
      })
    })
  }

  // 使用 Promise.all 和 Array.slice 控制并发
  const batchProcess = async (batch) => {
    await Promise.all(batch.map((file) => processFile(file)))
  }

  // 分批处理文件
  for (let i = 0; i < files.length; i += maxWorkers) {
    const batch = files.slice(i, i + maxWorkers)
    await batchProcess(batch)
  }

  return [successCount, failedCount]
}

/**
 * 主函数
 */
async function main() {
  if (!isMainThread) {
    return workerProcess()
  }

  try {
    // 设置路径
    const baseDir = path.resolve(__dirname, '..')
    const jsonDir = path.join(baseDir, 'src', 'data')
    const dbPath = path.join(baseDir, 'src', 'data', 'extensions.db')

    // 确保目录存在
    await fs.mkdir(jsonDir, { recursive: true })

    // 设置线程数
    const maxWorkers = 4

    console.log(`开始导入数据到数据库：${dbPath}`)
    const [successCount, failedCount] = await importJsonToDb(jsonDir, dbPath, maxWorkers)

    console.log('\n导入完成统计：')
    console.log(`成功：${successCount} 个`)
    console.log(`失败：${failedCount} 个`)

    // 显示最终的数据库统计
    const db = await open({
      filename: dbPath,
      driver: sqlite3.Database,
    })
    const { count } = await db.get('SELECT COUNT(*) as count FROM extensions')
    console.log(`数据库中总共有 ${count} 个扩展`)
    await db.close()
  } catch (error) {
    console.error('程序执行出错：', error)
    process.exit(1)
  }
}

// 运行主函数
if (isMainThread) {
  main().catch(console.error)
}

export { filterTags, importJsonToDb, initDatabase, processJsonFile }
