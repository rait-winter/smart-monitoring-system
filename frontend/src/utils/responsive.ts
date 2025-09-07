// ======== 响应式设计工具函数 ========

/**
 * 断点定义
 */
export const breakpoints = {
  xs: 480,
  sm: 768,
  md: 1024,
  lg: 1280,
  xl: 1920
} as const

export type Breakpoint = keyof typeof breakpoints

/**
 * 设备类型枚举
 */
export enum DeviceType {
  MOBILE = 'mobile',
  TABLET = 'tablet',
  DESKTOP = 'desktop'
}

/**
 * 屏幕方向枚举
 */
export enum ScreenOrientation {
  PORTRAIT = 'portrait',
  LANDSCAPE = 'landscape'
}

/**
 * 响应式配置接口
 */
export interface ResponsiveConfig {
  breakpoint: Breakpoint
  deviceType: DeviceType
  orientation: ScreenOrientation
  isMobile: boolean
  isTablet: boolean
  isDesktop: boolean
  width: number
  height: number
}

/**
 * 获取当前断点
 */
export function getCurrentBreakpoint(): Breakpoint {
  const width = window.innerWidth
  
  if (width < breakpoints.xs) return 'xs'
  if (width < breakpoints.sm) return 'sm'
  if (width < breakpoints.md) return 'md'
  if (width < breakpoints.lg) return 'lg'
  return 'xl'
}

/**
 * 获取设备类型
 */
export function getDeviceType(): DeviceType {
  const width = window.innerWidth
  
  if (width < breakpoints.sm) return DeviceType.MOBILE
  if (width < breakpoints.lg) return DeviceType.TABLET
  return DeviceType.DESKTOP
}

/**
 * 获取屏幕方向
 */
export function getScreenOrientation(): ScreenOrientation {
  return window.innerWidth > window.innerHeight 
    ? ScreenOrientation.LANDSCAPE 
    : ScreenOrientation.PORTRAIT
}

/**
 * 判断是否为移动设备
 */
export function isMobileDevice(): boolean {
  return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)
}

/**
 * 判断是否为触摸设备
 */
export function isTouchDevice(): boolean {
  return 'ontouchstart' in window || navigator.maxTouchPoints > 0
}

/**
 * 获取完整的响应式配置
 */
export function getResponsiveConfig(): ResponsiveConfig {
  const width = window.innerWidth
  const height = window.innerHeight
  const breakpoint = getCurrentBreakpoint()
  const deviceType = getDeviceType()
  const orientation = getScreenOrientation()
  
  return {
    breakpoint,
    deviceType,
    orientation,
    isMobile: deviceType === DeviceType.MOBILE,
    isTablet: deviceType === DeviceType.TABLET,
    isDesktop: deviceType === DeviceType.DESKTOP,
    width,
    height
  }
}

/**
 * 响应式断点媒体查询
 */
export function createMediaQuery(breakpoint: Breakpoint, direction: 'min' | 'max' = 'min'): string {
  const width = breakpoints[breakpoint]
  return `(${direction}-width: ${width}px)`
}

/**
 * 监听断点变化
 */
export function watchBreakpoint(
  breakpoint: Breakpoint,
  callback: (matches: boolean) => void,
  direction: 'min' | 'max' = 'min'
): () => void {
  const mediaQuery = window.matchMedia(createMediaQuery(breakpoint, direction))
  
  // 立即执行一次
  callback(mediaQuery.matches)
  
  // 监听变化
  const handler = (e: MediaQueryListEvent) => callback(e.matches)
  mediaQuery.addEventListener('change', handler)
  
  // 返回清理函数
  return () => mediaQuery.removeEventListener('change', handler)
}

/**
 * 监听设备类型变化
 */
export function watchDeviceType(callback: (deviceType: DeviceType) => void): () => void {
  let currentDeviceType = getDeviceType()
  
  const handler = () => {
    const newDeviceType = getDeviceType()
    if (newDeviceType !== currentDeviceType) {
      currentDeviceType = newDeviceType
      callback(newDeviceType)
    }
  }
  
  window.addEventListener('resize', handler)
  
  // 立即执行一次
  callback(currentDeviceType)
  
  // 返回清理函数
  return () => window.removeEventListener('resize', handler)
}

/**
 * 监听屏幕方向变化
 */
export function watchOrientation(callback: (orientation: ScreenOrientation) => void): () => void {
  let currentOrientation = getScreenOrientation()
  
  const handler = () => {
    const newOrientation = getScreenOrientation()
    if (newOrientation !== currentOrientation) {
      currentOrientation = newOrientation
      callback(newOrientation)
    }
  }
  
  window.addEventListener('resize', handler)
  window.addEventListener('orientationchange', handler)
  
  // 立即执行一次
  callback(currentOrientation)
  
  // 返回清理函数
  return () => {
    window.removeEventListener('resize', handler)
    window.removeEventListener('orientationchange', handler)
  }
}

/**
 * 响应式值计算器
 */
export function createResponsiveValue<T>(values: Record<Breakpoint, T>): () => T {
  return () => {
    const breakpoint = getCurrentBreakpoint()
    return values[breakpoint]
  }
}

/**
 * 响应式类名生成器
 */
export function createResponsiveClasses(
  baseClass: string,
  modifiers: Partial<Record<Breakpoint, string>>
): string[] {
  const classes = [baseClass]
  const breakpoint = getCurrentBreakpoint()
  
  // 添加当前断点的修饰类
  if (modifiers[breakpoint]) {
    classes.push(`${baseClass}--${modifiers[breakpoint]}`)
  }
  
  // 添加设备类型类
  const deviceType = getDeviceType()
  classes.push(`${baseClass}--${deviceType}`)
  
  return classes
}

/**
 * 获取响应式网格列数
 */
export function getResponsiveColumns(columns: Partial<Record<Breakpoint, number>>): number {
  const breakpoint = getCurrentBreakpoint()
  
  // 从当前断点开始向下查找
  const orderedBreakpoints: Breakpoint[] = ['xl', 'lg', 'md', 'sm', 'xs']
  const currentIndex = orderedBreakpoints.indexOf(breakpoint)
  
  for (let i = currentIndex; i < orderedBreakpoints.length; i++) {
    const bp = orderedBreakpoints[i]
    if (columns[bp] !== undefined) {
      return columns[bp]!
    }
  }
  
  return 1 // 默认单列
}

/**
 * 适配移动端的滚动条样式
 */
export function adaptScrollbarForMobile(): void {
  if (isMobileDevice()) {
    const style = document.createElement('style')
    style.textContent = `
      /* 隐藏移动端滚动条 */
      ::-webkit-scrollbar {
        display: none;
      }
      
      /* Firefox */
      * {
        scrollbar-width: none;
      }
      
      /* 移动端触摸滚动优化 */
      * {
        -webkit-overflow-scrolling: touch;
      }
    `
    document.head.appendChild(style)
  }
}

/**
 * 防止移动端双击缩放
 */
export function preventMobileZoom(): void {
  if (isMobileDevice()) {
    const viewport = document.querySelector('meta[name="viewport"]')
    if (viewport) {
      viewport.setAttribute('content', 
        'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=0'
      )
    }
  }
}

/**
 * 移动端安全区域适配
 */
export function adaptSafeArea(): void {
  if (isMobileDevice()) {
    const style = document.createElement('style')
    style.textContent = `
      /* 安全区域适配 */
      .safe-area-inset-top {
        padding-top: env(safe-area-inset-top);
      }
      
      .safe-area-inset-bottom {
        padding-bottom: env(safe-area-inset-bottom);
      }
      
      .safe-area-inset-left {
        padding-left: env(safe-area-inset-left);
      }
      
      .safe-area-inset-right {
        padding-right: env(safe-area-inset-right);
      }
      
      .safe-area-inset-all {
        padding-top: env(safe-area-inset-top);
        padding-bottom: env(safe-area-inset-bottom);
        padding-left: env(safe-area-inset-left);
        padding-right: env(safe-area-inset-right);
      }
    `
    document.head.appendChild(style)
  }
}

export default {
  breakpoints,
  DeviceType,
  ScreenOrientation,
  getCurrentBreakpoint,
  getDeviceType,
  getScreenOrientation,
  isMobileDevice,
  isTouchDevice,
  getResponsiveConfig,
  createMediaQuery,
  watchBreakpoint,
  watchDeviceType,
  watchOrientation,
  createResponsiveValue,
  createResponsiveClasses,
  getResponsiveColumns,
  adaptScrollbarForMobile,
  preventMobileZoom,
  adaptSafeArea
}