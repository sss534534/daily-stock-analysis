// 测试缓存功能的脚本
const { stockApi } = require('./dist/assets/api-V_qCs0vd.js');

async function testCache() {
  console.log('=== 开始测试缓存功能 ===');
  
  // 第一次请求（应该发起真实请求）
  console.log('第一次请求股票列表...');
  const startTime1 = Date.now();
  const data1 = await stockApi.getStocks();
  const duration1 = Date.now() - startTime1;
  console.log(`第一次请求耗时: ${duration1}ms`);
  console.log(`返回数据:`, data1);
  
  // 第二次请求（应该使用缓存）
  console.log('\n第二次请求股票列表（应该使用缓存）...');
  const startTime2 = Date.now();
  const data2 = await stockApi.getStocks();
  const duration2 = Date.now() - startTime2;
  console.log(`第二次请求耗时: ${duration2}ms`);
  console.log(`返回数据:`, data2);
  
  // 验证两次返回的数据是否相同
  console.log('\n验证两次返回数据是否相同:', JSON.stringify(data1) === JSON.stringify(data2));
  
  // 测试不同参数的请求
  console.log('\n测试不同参数的请求（应该重新请求）...');
  const startTime3 = Date.now();
  const data3 = await stockApi.getStockKline('600036');
  const duration3 = Date.now() - startTime3;
  console.log(`请求K线数据耗时: ${duration3}ms`);
  console.log(`返回数据长度:`, data3.data.length);
  
  console.log('\n=== 缓存测试完成 ===');
}

testCache().catch(console.error);