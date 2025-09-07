# 前端代码规范指南

## 📋 概述

本文档定义了智能监控预警系统前端项目的代码规范，旨在提高代码质量、可维护性和团队协作效率。

## 🛠️ 技术栈

- **框架**: Vue 3 + TypeScript
- **构建工具**: Vite
- **UI组件库**: Element Plus
- **状态管理**: Pinia
- **路由**: Vue Router
- **样式**: SCSS + CSS变量
- **图表**: ECharts 5
- **代码检查**: ESLint + Prettier
- **测试**: Vitest + Vue Test Utils

## 📁 项目结构

```
src/
├── components/          # 公共组件
│   ├── common/         # 通用组件
│   └── layout/         # 布局组件
├── views/              # 页面组件
├── stores/             # 状态管理
│   └── modules/        # 状态模块
├── services/           # API服务
├── utils/              # 工具函数
├── types/              # 类型定义
├── styles/             # 样式文件
│   ├── variables.scss  # SCSS变量
│   ├── mixins.scss     # SCSS混入
│   └── themes.scss     # 主题配置
├── router/             # 路由配置
└── assets/             # 静态资源
```

## 📝 TypeScript 规范

### 1. 基本类型定义

```typescript
// ✅ 推荐：使用接口定义对象类型
interface User {
  id: string
  username: string
  email?: string
  roles: string[]
}

// ❌ 避免：使用 any 类型
const userData: any = {}

// ✅ 推荐：使用具体类型
const userData: User = {
  id: '1',
  username: 'admin',
  roles: ['admin']
}
```

### 2. 组件Props类型

```typescript
// ✅ 推荐：使用 defineProps 配合 TypeScript
interface Props {
  title: string
  data: MetricData[]
  loading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  loading: false
})
```

### 3. API 类型定义

```typescript
// 定义请求参数类型
interface MetricQuery {
  start?: string
  end?: string
  step?: string
  query: string
}

// 定义响应数据类型
interface ApiResponse<T = any> {
  code: number
  message: string
  data: T
  success: boolean
}
```

## 🎨 Vue 组件规范

### 1. 组件命名

```typescript
// ✅ 推荐：使用 PascalCase
export default defineComponent({
  name: 'MonitorChart'
})

// 文件名使用 PascalCase
// MonitorChart.vue
// GlobalNotification.vue
```

### 2. 组件结构

```vue
<template>
  <!-- 模板内容 -->
</template>

<script setup lang="ts">
// 1. 导入依赖
import { ref, computed, onMounted } from 'vue'
import type { MetricData } from '@/types/global'

// 2. 定义 Props
interface Props {
  data: MetricData[]
}
const props = defineProps<Props>()

// 3. 定义 Emits
interface Emits {
  (e: 'update', data: MetricData[]): void
}
const emit = defineEmits<Emits>()

// 4. 响应式数据
const loading = ref(false)
const chartData = ref<MetricData[]>([])

// 5. 计算属性
const processedData = computed(() => {
  return chartData.value.map(item => ({
    ...item,
    formattedValue: formatValue(item.value)
  }))
})

// 6. 方法
const fetchData = async () => {
  loading.value = true
  try {
    // API 调用
  } finally {
    loading.value = false
  }
}

// 7. 生命周期
onMounted(() => {
  fetchData()
})

// 8. 暴露方法
defineExpose({
  fetchData
})
</script>

<style scoped lang="scss">
// 样式定义
</style>
```

### 3. 响应式数据规范

```typescript
// ✅ 推荐：明确类型定义
const userList = ref<User[]>([])
const loading = ref<boolean>(false)
const currentUser = ref<User | null>(null)

// ✅ 推荐：使用计算属性处理复杂逻辑
const filteredUsers = computed(() => {
  return userList.value.filter(user => user.active)
})

// ❌ 避免：在模板中使用复杂表达式
// <div>{{ userList.filter(u => u.active).length }}</div>

// ✅ 推荐：使用计算属性
// <div>{{ activeUserCount }}</div>
const activeUserCount = computed(() => {
  return userList.value.filter(u => u.active).length
})
```

## 🎯 状态管理规范

### 1. Store 结构

```typescript
// stores/modules/user.ts
export const useUserStore = defineStore('user', {
  state: (): UserState => ({
    user: null,
    token: null,
    permissions: []
  }),

  getters: {
    isLoggedIn: (state) => !!state.token,
    hasPermission: (state) => (permission: string) => {
      return state.permissions.includes(permission)
    }
  },

  actions: {
    async login(credentials: LoginCredentials) {
      // 登录逻辑
    },
    
    logout() {
      // 登出逻辑
    }
  },

  persist: {
    key: 'user-store',
    storage: localStorage,
    paths: ['user', 'token']
  }
})
```

### 2. 在组件中使用 Store

```typescript
// ✅ 推荐：使用 storeToRefs 保持响应性
const userStore = useUserStore()
const { user, isLoggedIn } = storeToRefs(userStore)
const { login, logout } = userStore

// ❌ 避免：直接解构（会失去响应性）
const { user, isLoggedIn } = useUserStore()
```

## 🎨 样式规范

### 1. SCSS 变量使用

```scss
// ✅ 推荐：使用预定义变量
.monitor-card {
  background: var(--bg-color);
  border-radius: var(--border-radius);
  padding: var(--spacing-md);
  box-shadow: var(--shadow-sm);
}

// ✅ 推荐：使用混入
.alert-badge {
  @include alert-badge('error');
}
```

### 2. 组件样式规范

```scss
// ✅ 推荐：使用 scoped 样式
<style scoped lang="scss">
.component-root {
  // 组件根元素样式
  
  &__header {
    // BEM 命名规范
  }
  
  &__content {
    // 内容样式
  }
  
  &--loading {
    // 修饰符样式
  }
}

// 深度选择器
:deep(.el-table) {
  // 修改 Element Plus 组件样式
}
</style>
```

## 🔧 工具函数规范

### 1. 函数定义

```typescript
// ✅ 推荐：明确的函数签名
export function formatValue(
  value: number | null | undefined,
  unit?: string,
  precision = 2
): string {
  if (value === null || value === undefined) return '-'
  
  // 实现逻辑
  return formattedValue
}

// ✅ 推荐：使用 JSDoc 注释
/**
 * 格式化数值显示
 * @param value 数值
 * @param unit 单位
 * @param precision 精度
 * @returns 格式化后的字符串
 */
export function formatValue(/* ... */) {
  // ...
}
```

### 2. 错误处理

```typescript
// ✅ 推荐：统一错误处理
export async function fetchUserData(id: string): Promise<User | null> {
  try {
    const response = await apiService.getUser(id)
    return response.data
  } catch (error) {
    globalErrorHandler.handle(error as Error, {
      type: ErrorType.API,
      source: 'fetchUserData'
    })
    return null
  }
}
```

## 📊 性能优化规范

### 1. 组件懒加载

```typescript
// ✅ 推荐：路由懒加载
const routes = [
  {
    path: '/dashboard',
    component: () => import('@/views/Dashboard.vue')
  }
]

// ✅ 推荐：组件懒加载
const AsyncChart = defineAsyncComponent(() => import('@/components/MonitorChart.vue'))
```

### 2. 大数据处理

```vue
<template>
  <!-- 虚拟滚动处理大列表 -->
  <VirtualList
    :items="largeDataList"
    :item-height="50"
    :container-height="400"
  />
</template>
```

## 🧪 测试规范

### 1. 单元测试

```typescript
// tests/components/MonitorChart.test.ts
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import MonitorChart from '@/components/MonitorChart.vue'

describe('MonitorChart', () => {
  it('should render correctly', () => {
    const wrapper = mount(MonitorChart, {
      props: {
        data: mockChartData
      }
    })
    
    expect(wrapper.exists()).toBe(true)
  })
})
```

## 📋 代码检查

### 1. 运行检查命令

```bash
# 类型检查
npm run type-check

# 代码规范检查
npm run lint

# 代码格式检查
npm run format:check

# 完整质量检查
npm run quality:check
```

### 2. Git 提交前检查

项目配置了 `lint-staged`，在提交前会自动检查和修复代码格式。

## 🚀 最佳实践

### 1. 组件设计原则

- **单一职责**：每个组件只负责一个功能
- **可复用性**：设计通用的组件接口
- **可测试性**：组件逻辑易于单元测试
- **可维护性**：代码结构清晰，注释完善

### 2. 性能考虑

- 使用 `v-memo` 优化重复渲染
- 合理使用 `shallowRef` 和 `shallowReactive`
- 避免在模板中使用复杂计算
- 使用虚拟滚动处理大数据

### 3. 安全考虑

- 避免使用 `v-html`，使用 `v-text`
- 对用户输入进行验证和转义
- 使用 HTTPS 和安全的 Cookie 设置
- 定期更新依赖包

## 📚 参考资源

- [Vue 3 官方文档](https://vuejs.org/)
- [TypeScript 官方文档](https://www.typescriptlang.org/)
- [Element Plus 文档](https://element-plus.org/)
- [Pinia 官方文档](https://pinia.vuejs.org/)
- [ESLint 规则](https://eslint.org/docs/rules/)
- [Prettier 配置](https://prettier.io/docs/en/configuration.html)

---

**注意**: 本规范是动态文档，会根据项目发展和团队反馈持续更新。如有建议或问题，请及时反馈。