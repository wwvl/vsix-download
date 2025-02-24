import { useClipboard } from '@vueuse/core'

/**
 * 获取扩展的下载链接
 */
export function getDownloadUrl(extensionName: string, version: string): string {
  const [publisher, name] = extensionName.split('.')
  return `https://marketplace.visualstudio.com/_apis/public/gallery/publishers/${publisher}/vsextensions/${name}/${version}/vspackage`
}

/**
 * 扩展相关的功能 Hook
 */
export function useExtension() {
  const toast = useToast()
  const { copy } = useClipboard()

  /**
   * 复制安装命令到剪贴板
   */
  const copyInstallCommand = async (extensionId: string): Promise<void> => {
    await copy(`ext install ${extensionId}`)
    toast.add({
      title: '安装命令已复制！',
      description: `命令：ext install ${extensionId}`,
      icon: 'i-carbon-checkmark-outline',
      color: 'success',
    })
  }

  /**
   * 复制扩展 ID 到剪贴板
   */
  const copyExtensionIds = async (extensionIds: string[]): Promise<void> => {
    const ids = extensionIds.join('\n')
    await copy(ids)
    toast.add({
      title: '已复制选中的扩展 ID！',
      description: `共复制 ${extensionIds.length} 个扩展 ID`,
      icon: 'i-carbon-checkmark-outline',
      color: 'success',
    })
  }

  return {
    getDownloadUrl,
    copyInstallCommand,
    copyExtensionIds,
  }
}
