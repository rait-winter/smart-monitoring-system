import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueJsx from '@vitejs/plugin-vue-jsx'
import { resolve } from 'path'

// 自动导入插件
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import Icons from 'unplugin-icons/vite'

// Element Plus
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'

// WindiCSS (原子化CSS)
import WindiCSS from 'vite-plugin-windicss'

// ESLint
import eslint from 'vite-plugin-eslint'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  
  return {
    plugins: [
      vue({
        script: {
          defineModel: true, // 启用defineModel
          propsDestructure: true, // 启用props解构
        },
      }),
      vueJsx(),
      
      // 自动导入Vue API
      AutoImport({
        imports: [
          'vue',
          'vue-router',
          'pinia',
          '@vueuse/core',
        ],
        resolvers: [ElementPlusResolver()],
        dts: 'src/types/auto-imports.d.ts',
        eslintrc: {
          enabled: true,
          filepath: './.eslintrc-auto-import.json',
        },
      }),
      
      // 自动导入组件
      Components({
        resolvers: [
          ElementPlusResolver(),
        ],
        dts: 'src/types/components.d.ts',
        directoryAsNamespace: true,
      }),
      
      // 图标自动导入
      Icons({
        compiler: 'vue3',
        autoInstall: true,
      }),
      
      // WindiCSS原子化CSS - 暂时禁用
      // WindiCSS(),
      
      // ESLint - 暂时禁用以解决配置问题
      // eslint({
      //   include: ['src/**/*.{vue,js,ts}'],
      //   exclude: ['node_modules', 'dist'],
      //   cache: false,
      // }),
    ],
    
    resolve: {
      alias: {
        '@': resolve(__dirname, 'src'),
        '#': resolve(__dirname, 'types'),
      },
    },
    
    css: {
      preprocessorOptions: {
        scss: {
          api: 'modern-compiler', // 使用现代Dart Sass API
          additionalData: `
            @use "@/styles/variables.scss" as *;
            @use "@/styles/mixins.scss" as *;
          `,
        },
      },
    },
    
    server: {
      host: '0.0.0.0',
      port: 3000,
      open: false,
      cors: true,
      proxy: {
        '/api': {
          target: 'http://localhost:8000',
          changeOrigin: true,
          secure: false,
          timeout: 30000,
          rewrite: (path) => {
            console.log('代理请求:', path)
            return path
          }
        },
      },
    },
    
    build: {
      target: 'esnext',
      minify: 'esbuild',
      sourcemap: mode !== 'production',
      rollupOptions: {
        output: {
          manualChunks: {
            // Vue生态系统
            'vue-vendor': ['vue', 'vue-router', 'pinia'],
            // UI库
            'ui-vendor': ['element-plus'],
            // 图表库
            'chart-vendor': ['echarts', 'vue-echarts'],
            // 工具库
            'utils-vendor': ['axios', 'lodash-es', 'dayjs'],
          },
        },
      },
      chunkSizeWarningLimit: 1500,
    },
    
    optimizeDeps: {
      include: [
        'vue',
        'vue-router',
        'pinia',
        'axios',
        'echarts',
        'vue-echarts',
        'element-plus',
        '@element-plus/icons-vue',
        'dayjs',
        'lodash-es',
        '@vueuse/core',
        'nprogress',
      ],
    },
    
    define: {
      __VUE_OPTIONS_API__: false, // 禁用Options API以减小包体积
      __VUE_PROD_DEVTOOLS__: mode !== 'production',
    },
  }
})