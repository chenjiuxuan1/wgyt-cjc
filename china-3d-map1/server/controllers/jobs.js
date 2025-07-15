const db = require('../config/db');

const recommendJobs = async (req, res) => {
  try {
    const { params, weights } = req.body;
    
    console.log('Received params:', params);
    console.log('Received weights:', weights);

    // 构建基础查询
    let query = `
      SELECT 
        岗位名称 as position,
        工作地点 as city,
        岗位薪资 as salary,
        学历要求 as education,
        经验要求 as experience,
        企业名称 as company,
        企业规模 as scale,
        企业类型 as companyType,
        岗位技能需求 as skills,
        企业融资状况 as financing_status,
        岗位一级分类 as job_category_l1,
        岗位二级分类 as job_category_l2
      FROM 岗位信息
      WHERE 1=1
    `;
    
    const queryParams = [];

    // 添加筛选条件
    if (params.city) {
      query += ` AND 工作地点 LIKE ?`;
      queryParams.push(`%${params.city}%`);
    }
    if (params.salary) {
      query += ` AND 岗位薪资 = ?`;
      queryParams.push(params.salary);
    }
    if (params.education) {
      query += ` AND 学历要求 = ?`;
      queryParams.push(params.education);
    }
    if (params.experience) {
      query += ` AND 经验要求 = ?`;
      queryParams.push(params.experience);
    }
    if (params.position) {
      query += ` AND (岗位名称 LIKE ? OR 岗位一级分类 LIKE ? OR 岗位二级分类 LIKE ?)`;
      queryParams.push(`%${params.position}%`, `%${params.position}%`, `%${params.position}%`);
    }
    if (params.scale) {
      query += ` AND 企业规模 = ?`;
      queryParams.push(params.scale);
    }
    if (params.companyType) {
      query += ` AND 企业类型 LIKE ?`;
      queryParams.push(`%${params.companyType}%`);
    }

    console.log('Executing query:', query);
    console.log('Query params:', queryParams);

    // 执行查询
    const [jobs] = await db.query(query, queryParams);
    
    console.log('Query results:', jobs);

    // 计算匹配度
    const recommendedJobs = jobs.map(job => {
      let matchScore = 0;
      let totalWeight = 0;

      if (params.city && weights.city) {
        totalWeight += weights.city;
        if (job.city.includes(params.city)) matchScore += weights.city;
      }
      if (params.salary && weights.salary) {
        totalWeight += weights.salary;
        if (job.salary === params.salary) matchScore += weights.salary;
      }
      if (params.education && weights.education) {
        totalWeight += weights.education;
        if (job.education === params.education) matchScore += weights.education;
      }
      if (params.experience && weights.experience) {
        totalWeight += weights.experience;
        if (job.experience === params.experience) matchScore += weights.experience;
      }
      if (params.position && weights.position) {
        totalWeight += weights.position;
        const positionMatch = 
          job.position.includes(params.position) ||
          job.job_category_l1.includes(params.position) ||
          job.job_category_l2.includes(params.position);
        if (positionMatch) matchScore += weights.position;
      }
      if (params.scale && weights.scale) {
        totalWeight += weights.scale;
        if (job.scale === params.scale) matchScore += weights.scale;
      }
      if (params.companyType && weights.companyType) {
        totalWeight += weights.companyType;
        if (job.companyType.includes(params.companyType)) matchScore += weights.companyType;
      }

      const matchPercentage = totalWeight > 0 ? (matchScore / totalWeight) * 100 : 100;

      return {
        ...job,
        matchScore: Math.round(matchPercentage)
      };
    });

    // 按匹配度排序并只返回匹配度大于60%的结果
    const filteredJobs = recommendedJobs
      .filter(job => job.matchScore >= 60)
      .sort((a, b) => b.matchScore - a.matchScore);

    console.log('Filtered jobs:', filteredJobs);

    res.json({
      code: 200,
      data: filteredJobs,
      message: "查询成功"
    });
  } catch (error) {
    console.error('Error in recommendJobs:', error);
    res.status(500).json({
      code: 500,
      message: '查询失败，请稍后重试',
      error: error.message
    });
  }
};

/**
 * 检查岗位预警条件
 */
const checkJobAlerts = async (req, res) => {
  try {
    const { conditions, threshold } = req.body;
    
    console.log('Checking job alerts:', conditions, threshold);

    // 构建基础查询
    let query = `
      SELECT COUNT(*) as count
      FROM 岗位信息
      WHERE DATE(创建时间) = CURDATE()
    `;
    
    const queryParams = [];

    // 添加筛选条件
    if (conditions.city) {
      query += ` AND 工作地点 LIKE ?`;
      queryParams.push(`%${conditions.city}%`);
    }
    if (conditions.salary) {
      query += ` AND 岗位薪资 = ?`;
      queryParams.push(conditions.salary);
    }
    if (conditions.education) {
      query += ` AND 学历要求 = ?`;
      queryParams.push(conditions.education);
    }
    if (conditions.experience) {
      query += ` AND 经验要求 = ?`;
      queryParams.push(conditions.experience);
    }
    if (conditions.position) {
      query += ` AND (岗位名称 LIKE ? OR 岗位一级分类 LIKE ? OR 岗位二级分类 LIKE ?)`;
      queryParams.push(`%${conditions.position}%`, `%${conditions.position}%`, `%${conditions.position}%`);
    }
    if (conditions.scale) {
      query += ` AND 企业规模 = ?`;
      queryParams.push(conditions.scale);
    }
    if (conditions.companyType) {
      query += ` AND 企业类型 LIKE ?`;
      queryParams.push(`%${conditions.companyType}%`);
    }

    console.log('Executing query:', query);
    console.log('Query params:', queryParams);

    // 执行查询
    const [result] = await db.query(query, queryParams);
    const count = result[0].count;
    
    console.log('Query result:', count);

    res.json({
      code: 200,
      data: {
        isTriggered: count >= threshold,
        count
      },
      message: "检查完成"
    });
  } catch (error) {
    console.error('Error in checkJobAlerts:', error);
    res.status(500).json({
      code: 500,
      message: '检查失败，请稍后重试',
      error: error.message
    });
  }
};

/**
 * 获取岗位数量统计
 */
const getJobCount = async (req, res) => {
  try {
    const { conditions } = req.body;
    
    console.log('Getting job count:', conditions);

    // 构建基础查询
    let query = `
      SELECT DATE(创建时间) as date, COUNT(*) as count
      FROM 岗位信息
      WHERE 创建时间 >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
    `;
    
    const queryParams = [];

    // 添加筛选条件
    if (conditions.city) {
      query += ` AND 工作地点 LIKE ?`;
      queryParams.push(`%${conditions.city}%`);
    }
    if (conditions.salary) {
      query += ` AND 岗位薪资 = ?`;
      queryParams.push(conditions.salary);
    }
    if (conditions.education) {
      query += ` AND 学历要求 = ?`;
      queryParams.push(conditions.education);
    }
    if (conditions.experience) {
      query += ` AND 经验要求 = ?`;
      queryParams.push(conditions.experience);
    }
    if (conditions.position) {
      query += ` AND (岗位名称 LIKE ? OR 岗位一级分类 LIKE ? OR 岗位二级分类 LIKE ?)`;
      queryParams.push(`%${conditions.position}%`, `%${conditions.position}%`, `%${conditions.position}%`);
    }
    if (conditions.scale) {
      query += ` AND 企业规模 = ?`;
      queryParams.push(conditions.scale);
    }
    if (conditions.companyType) {
      query += ` AND 企业类型 LIKE ?`;
      queryParams.push(`%${conditions.companyType}%`);
    }

    query += ` GROUP BY DATE(创建时间)
               ORDER BY date ASC`;

    console.log('Executing query:', query);
    console.log('Query params:', queryParams);

    // 执行查询
    const [results] = await db.query(query, queryParams);
    
    console.log('Query results:', results);

    res.json({
      code: 200,
      data: results,
      message: "查询成功"
    });
  } catch (error) {
    console.error('Error in getJobCount:', error);
    res.status(500).json({
      code: 500,
      message: '查询失败，请稍后重试',
      error: error.message
    });
  }
};

module.exports = {
  recommendJobs,
  checkJobAlerts,
  getJobCount
}; 