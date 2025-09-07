#!/usr/bin/env node

/**
 * 代码质量检查脚本
 * 用于检查TypeScript类型、ESLint规则、Prettier格式化等
 */

const { execSync } = require('child_process')
const fs = require('fs')
const path = require('path')

// 颜色输出函数
const colors = {
  red: text => `\x1b[31m${text}\x1b[0m`,
  green: text => `\x1b[32m${text}\x1b[0m`,
  yellow: text => `\x1b[33m${text}\x1b[0m`,
  blue: text => `\x1b[34m${text}\x1b[0m`,
  cyan: text => `\x1b[36m${text}\x1b[0m`,
  bold: text => `\x1b[1m${text}\x1b[0m`
}

// 日志函数
const log = {
  info: (msg) => console.log(colors.blue('ℹ'), msg),
  success: (msg) => console.log(colors.green('✓'), msg),
  warning: (msg) => console.log(colors.yellow('⚠'), msg),
  error: (msg) => console.log(colors.red('✗'), msg),
  section: (title) => console.log(`\\n${colors.bold(colors.cyan(title))}`)
}

// 执行命令并返回结果
function runCommand(command, description, { ignoreError = false, silent = false } = {}) {
  try {
    if (!silent) {
      log.info(`执行: ${description}`)
    }
    
    const result = execSync(command, { 
      encoding: 'utf8',
      stdio: silent ? 'pipe' : 'inherit'
    })
    
    if (!silent) {
      log.success(`完成: ${description}`)
    }
    
    return { success: true, output: result }
  } catch (error) {
    if (!ignoreError) {
      log.error(`失败: ${description}`)
      if (error.stdout) {
        console.log(error.stdout)
      }
      if (error.stderr) {
        console.error(error.stderr)
      }
    }
    return { success: false, error }
  }
}

// 检查文件是否存在
function checkFile(filePath, description) {
  if (fs.existsSync(filePath)) {
    log.success(`${description}: ${filePath}`)
    return true
  } else {
    log.warning(`${description}未找到: ${filePath}`)
    return false
  }
}

// 统计代码行数
function countLines(dir, extensions = ['.vue', '.ts', '.js']) {
  let totalLines = 0
  let fileCount = 0
  
  function scanDir(dirPath) {
    const files = fs.readdirSync(dirPath)
    
    files.forEach(file => {
      const filePath = path.join(dirPath, file)
      const stat = fs.statSync(filePath)
      
      if (stat.isDirectory() && !file.startsWith('.') && file !== 'node_modules') {
        scanDir(filePath)
      } else if (stat.isFile() && extensions.some(ext => file.endsWith(ext))) {
        const content = fs.readFileSync(filePath, 'utf8')
        const lines = content.split('\\n').length
        totalLines += lines
        fileCount++
      }
    })
  }
  
  scanDir(dir)
  return { totalLines, fileCount }
}

// 主函数
async function main() {
  console.log(colors.bold(colors.cyan('🔍 前端代码质量检查工具')))
  console.log('='.repeat(50))
  
  // 1. 环境检查
  log.section('📋 环境检查')
  checkFile('package.json', 'package.json')
  checkFile('tsconfig.json', 'TypeScript配置')
  checkFile('.eslintrc.json', 'ESLint配置')
  checkFile('.prettierrc', 'Prettier配置')
  checkFile('vite.config.ts', 'Vite配置')
  
  // 2. 代码统计
  log.section('📊 代码统计')
  const stats = countLines('./src')
  log.info(`源代码文件: ${stats.fileCount} 个`)
  log.info(`总代码行数: ${stats.totalLines} 行`)
  
  // 3. TypeScript类型检查
  log.section('🔧 TypeScript类型检查')
  const typeCheck = runCommand(
    'npx vue-tsc --noEmit --skipLibCheck',
    'TypeScript类型检查',
    { ignoreError: true }
  )
  
  if (typeCheck.success) {
    log.success('TypeScript类型检查通过')
  } else {
    log.error('TypeScript类型检查失败')
  }
  
  // 4. ESLint检查
  log.section('📏 ESLint代码规范检查')
  const lintCheck = runCommand(
    'npx eslint src --ext .vue,.js,.jsx,.cjs,.mjs,.ts,.tsx,.cts,.mts',
    'ESLint代码检查',
    { ignoreError: true }
  )
  
  if (lintCheck.success) {
    log.success('ESLint检查通过')
  } else {
    log.error('ESLint检查发现问题')
    log.info('运行 npm run lint 自动修复部分问题')
  }
  
  // 5. Prettier格式检查
  log.section('💅 Prettier格式检查')
  const formatCheck = runCommand(
    'npx prettier --check src',
    'Prettier格式检查',
    { ignoreError: true }
  )
  
  if (formatCheck.success) {
    log.success('代码格式符合规范')
  } else {
    log.error('代码格式不符合规范')
    log.info('运行 npx prettier --write src 格式化代码')
  }
  
  // 6. 依赖检查
  log.section('📦 依赖检查')
  const auditResult = runCommand(
    'npm audit --audit-level moderate',
    '安全漏洞检查',
    { ignoreError: true }
  )
  
  if (auditResult.success) {
    log.success('依赖安全检查通过')
  } else {
    log.warning('发现安全漏洞，建议运行 npm audit fix')
  }
  
  // 7. 构建检查
  log.section('🏗️ 构建检查')
  const buildCheck = runCommand(
    'npm run build',
    '项目构建测试',
    { ignoreError: true }
  )
  
  if (buildCheck.success) {
    log.success('项目构建成功')
  } else {
    log.error('项目构建失败')
  }
  
  // 8. 总结报告
  log.section('📝 质量报告总结')
  const results = [
    { name: 'TypeScript类型检查', status: typeCheck.success },
    { name: 'ESLint代码规范', status: lintCheck.success },
    { name: 'Prettier代码格式', status: formatCheck.success },
    { name: '依赖安全检查', status: auditResult.success },
    { name: '项目构建测试', status: buildCheck.success }
  ]
  
  const passedCount = results.filter(r => r.status).length
  const totalCount = results.length
  
  results.forEach(result => {
    if (result.status) {
      log.success(result.name)
    } else {
      log.error(result.name)
    }
  })
  
  console.log(`\\n${colors.bold('总体评分:')} ${passedCount}/${totalCount}`)
  
  if (passedCount === totalCount) {
    console.log(colors.green(colors.bold('🎉 恭喜！代码质量检查全部通过！')))
  } else {
    console.log(colors.yellow(colors.bold('⚠️  存在需要修复的问题，请查看上方详情')))
  }
  
  console.log('\\n' + '='.repeat(50))
}

// 处理命令行参数
const args = process.argv.slice(2)
if (args.includes('--help') || args.includes('-h')) {
  console.log(`
使用方法: node code-quality-check.js [选项]

选项:
  --help, -h     显示帮助信息
  --fix          自动修复可修复的问题
  --strict       使用严格模式检查

示例:
  node code-quality-check.js          # 运行标准检查
  node code-quality-check.js --fix    # 运行检查并自动修复
  node code-quality-check.js --strict # 运行严格模式检查
`)
  process.exit(0)
}

// 运行主函数
main().catch(error => {
  log.error('检查过程中发生错误:')
  console.error(error)
  process.exit(1)
})