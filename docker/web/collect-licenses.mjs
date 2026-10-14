import fs from 'node:fs'
const lock = JSON.parse(fs.readFileSync('package-lock.json','utf8'))
const notices = ['Bakta Web UI 1.4.0: GPL-3.0.\nFixed source: https://github.com/ag-computational-bio/bakta-web-ui/tree/3bb62efac08b7f0b14384336569d93f22f6b5728\nDependency notices from the locked build environment (includes build-only packages):\n']
for (const [path, item] of Object.entries(lock.packages)) {
  if (!path || !fs.existsSync(path)) continue
  notices.push('\n=== '+path+' '+item.version+' ('+item.license+') ===\n'+(item.resolved||'')+'\n')
  for (const name of fs.readdirSync(path).sort()) {
    if (/^(licen[sc]e|copying|notice)(\.|$)/i.test(name) && fs.statSync(path+'/'+name).isFile()) {
      notices.push(fs.readFileSync(path+'/'+name,'utf8'))
    }
  }
}
fs.writeFileSync('THIRD_PARTY_NOTICES.txt', notices.join('\n'))
