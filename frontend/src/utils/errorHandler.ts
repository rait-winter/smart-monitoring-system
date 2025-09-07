/**
 * 全局错误处理
 */

// Vue错误处理
window.addEventListener('unhandledrejection', (event) => {
  console.error('未处理的Promise错误:', event.reason)
  event.preventDefault()
})

// JavaScript错误处理
window.addEventListener('error', (event) => {
  console.error('JavaScript错误:', event.error)
})

console.log('全局错误处理已配置')