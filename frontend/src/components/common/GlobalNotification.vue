<template>
  <div class="global-notification-container">
    <!-- 这里可以放置全局通知组件 -->
  </div>
</template>

<script setup lang="ts">
// 全局通知组件
// 可以在这里集成 Element Plus 的消息通知
// 或者自定义全局通知逻辑

// 暂时空实现，后续可以扩展
console.log('全局通知组件已初始化')
</script>

<style scoped lang="scss">
.global-notification-container {
  /* 全局通知容器样式 */
  position: fixed;
  top: 0;
  right: 0;
  z-index: 3000;
  pointer-events: none;
}
</style>