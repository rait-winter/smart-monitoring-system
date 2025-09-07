#!/usr/bin/env node
/**
 * 智能npm依赖安装脚本
 * 自动尝试多个国内源，选择最快的进行安装
 */

import { execSync } from 'child_process';
import https from 'https';
import { URL } from 'url';

// 国内npm源列表
const registries = [
  {
    name: '淘宝镜像',
    url: 'https://registry.npmmirror.com',
  },
  {
    name: '华为云镜像', 
    url: 'https://repo.huaweicloud.com/repository/npm',
  },
  {
    name: '腾讯云镜像',
    url: 'https://mirrors.cloud.tencent.com/npm',
  },
  {
    name: 'npm官方源',
    url: 'https://registry.npmjs.org',
  }
];

// 测试源的响应时间
function testRegistry(registry) {
  return new Promise((resolve) => {
    const start = Date.now();
    const url = new URL(registry.url);
    
    const req = https.request({
      hostname: url.hostname,
      port: url.port || 443,
      path: '/',
      method: 'HEAD',
      timeout: 5000
    }, (res) => {
      const time = Date.now() - start;
      resolve({ ...registry, time });
    });
    
    req.on('error', () => {
      resolve({ ...registry, time: Infinity });
    });
    
    req.on('timeout', () => {
      req.destroy();
      resolve({ ...registry, time: Infinity });
    });
    
    req.end();
  });
}

// 主函数
async function main() {
  console.log('🔍 正在测试npm源速度...\n');
  
  // 并发测试所有源
  const results = await Promise.all(
    registries.map(registry => testRegistry(registry))
  );
  
  // 按响应时间排序
  results.sort((a, b) => a.time - b.time);
  
  // 显示测试结果
  results.forEach((result, index) => {
    const status = result.time === Infinity ? '❌ 超时' : `✅ ${result.time}ms`;
    console.log(`${index + 1}. ${result.name}: ${status}`);
  });
  
  // 选择最快的源
  const fastest = results[0];
  
  if (fastest.time === Infinity) {
    console.log('\n❌ 所有源都无法访问，请检查网络连接');
    process.exit(1);
  }
  
  console.log(`\n🚀 选择最快的源: ${fastest.name} (${fastest.time}ms)`);
  console.log(`📦 开始安装依赖...\n`);
  
  try {
    // 使用最快的源安装依赖
    execSync(`npm install --registry ${fastest.url}`, {
      stdio: 'inherit',
      cwd: process.cwd()
    });
    
    console.log('\n✅ 依赖安装完成！');
  } catch (error) {
    console.error('\n❌ 安装失败:', error.message);
    process.exit(1);
  }
}

main().catch(console.error);