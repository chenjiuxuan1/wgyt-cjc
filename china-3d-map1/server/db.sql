-- 创建数据库
CREATE DATABASE IF NOT EXISTS job_db;
USE job_db;

-- 创建公司表
CREATE TABLE IF NOT EXISTS companies (
  id INT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(100) NOT NULL,
  size VARCHAR(50) NOT NULL,
  type VARCHAR(50) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建职位表
CREATE TABLE IF NOT EXISTS jobs (
  id INT PRIMARY KEY AUTO_INCREMENT,
  title VARCHAR(100) NOT NULL,
  salary VARCHAR(50) NOT NULL,
  education VARCHAR(50) NOT NULL,
  experience VARCHAR(50) NOT NULL,
  city VARCHAR(50) NOT NULL,
  company_id INT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (company_id) REFERENCES companies(id)
);

-- 创建岗位预警表
CREATE TABLE IF NOT EXISTS job_alerts (
  id INT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(200) NOT NULL,
  conditions JSON NOT NULL,
  threshold INT NOT NULL,
  is_active BOOLEAN DEFAULT FALSE,
  last_count INT DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 创建岗位数量统计表
CREATE TABLE IF NOT EXISTS job_counts (
  id INT PRIMARY KEY AUTO_INCREMENT,
  date DATE NOT NULL,
  conditions JSON NOT NULL,
  count INT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY unique_date_conditions (date, conditions(100))
);

-- 插入示例公司数据
INSERT INTO companies (name, size, type) VALUES
('科技有限公司', '500+', '互联网'),
('某某科技', '200-499人', '互联网'),
('智能科技', '50-199人', '人工智能'),
('网络科技', '500+', '互联网');

-- 插入示例职位数据
INSERT INTO jobs (title, salary, education, experience, city, company_id) VALUES
('前端开发工程师', '3-5k', '本科', '3-5年', '上海', 1),
('Java开发工程师', '8-12k', '本科', '1-3年', '北京', 2),
('算法工程师', '15k+', '硕士', '1-3年', '深圳', 3),
('产品经理', '12-15k', '本科', '3-5年', '广州', 4); 