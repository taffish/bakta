// 仅本地 viewer 展示/安全补丁，不改 Bakta 注释算法或 JSON 坐标转换。
import fs from 'node:fs'

function replaceOnce(path, before, after) {
  const text = fs.readFileSync(path, 'utf8')
  if (text.split(before).length !== 2) throw new Error('upstream context mismatch: '+path)
  fs.writeFileSync(path, text.replace(before, after))
}
replaceOnce('src/components/bakta-result/BaktaStats.vue',
  '<h2 class="section-label">Runtime</h2>',
  '<h2 class="section-label">Viewer session (not analysis runtime)</h2>')
// 换文件/示例时不保留旧结果，避免无效新输入下显示上一份统计。
replaceOnce('src/pages/show-own-result-file/ShowOwnResultPage.vue',
  'function loadData(file: File) {\n  error.value = undefined',
  'function loadData(file: File) {\n  data.value = undefined\n  error.value = undefined')
replaceOnce('src/pages/show-own-result-file/ShowOwnResultPage.vue',
  "function loadExampleData(type: 'plasmid' | 'genome') {\n  loadingProgress.value.enabled = true",
  "function loadExampleData(type: 'plasmid' | 'genome') {\n  data.value = undefined\n  error.value = undefined\n  loadingProgress.value.enabled = true")
replaceOnce('src/components/bakta-result/BaktaAnnotationTable.vue',
  "              x +\n              '\">' +\n              x +",
  "              encodeURIComponent(x) +\n              '\">' +\n              escapeHtml(x) +")
replaceOnce('src/components/bakta-result/BaktaAnnotationTable.vue',
  'const table = computed(() => {',
  `function escapeHtml(value: string): string {
  return value.replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]!))
}
const table = computed(() => {`)
