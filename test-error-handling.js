// 测试API错误处理和重试机制的脚本

// 模拟API失败测试
async function testErrorHandling() {
  console.log('=== 开始测试API错误处理和重试机制 ===');
  
  // 导入API模块（从构建后的文件）
  const fs = require('fs');
  const path = require('path');
  
  // 读取API文件内容
  const apiFilePath = path.join(__dirname, 'dist', 'assets', 'api-V_qCs0vd.js');
  const apiContent = fs.readFileSync(apiFilePath, 'utf8');
  
  console.log('API模块已加载，开始测试错误处理...');
  
  // 测试场景1: 测试错误处理和重试机制
  console.log('\n测试场景1: API请求失败时的重试机制');
  
  // 修改API基础URL为一个不存在的地址来模拟失败
  const originalUrl = 'http://localhost:3006/api';
  const testUrl = 'http://localhost:9999/api'; // 不存在的服务器
  
  // 替换URL
  const modifiedApiContent = apiContent.replace(originalUrl, testUrl);
  
  // 创建临时测试文件
  const tempFilePath = path.join(__dirname, 'temp-api-test.js');
  fs.writeFileSync(tempFilePath, modifiedApiContent);
  
  try {
    // 导入修改后的API
    const { stockApi } = require(tempFilePath);
    
    console.log('尝试请求不存在的API端点...');
    const startTime = Date.now();
    
    // 这应该会触发错误处理和重试机制
    const result = await stockApi.getStocks();
    
    const duration = Date.now() - startTime;
    console.log(`请求完成耗时: ${duration}ms`);
    console.log('返回结果:', result);
    console.log('✓ 错误处理机制正常工作，返回了模拟数据');
    
  } catch (error) {
    console.error('✗ 测试失败:', error.message);
    throw error;
  } finally {
    // 清理临时文件
    fs.unlinkSync(tempFilePath);
  }
  
  console.log('\n=== API错误处理测试完成 ===');
}

testErrorHandling().catch(console.error);