<template>
  <div class="placeholder-view">
    <el-card>
      <template #header>
        <h2>{{ title }}</h2>
      </template>
      <el-empty description="功能开发中...">
        <el-button type="primary" @click="$router.push('/')">
          返回首页
        </el-button>
      </el-empty>
    </el-card>
  </div>
</template>

<script setup lang="ts">
interface Props {
  title?: string
}

const props = withDefaults(defineProps<Props>(), {
  title: '功能页面'
})
</script>

<style scoped lang="scss">
.placeholder-view {
  padding: 20px;
}
</style>