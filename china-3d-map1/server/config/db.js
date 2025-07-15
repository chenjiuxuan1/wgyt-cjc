const mysql = require('mysql2');

const pool = mysql.createPool({
  host: 'localhost',
  user: 'root',      // MySQL用户名
  password: '123456',      // 先尝试空密码
  database: 'zhaoping',
  waitForConnections: true,
  connectionLimit: 10,
  queueLimit: 0
});

// 将连接池转换为Promise API
const promisePool = pool.promise();

module.exports = promisePool; 