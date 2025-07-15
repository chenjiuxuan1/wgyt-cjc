import request from '@/utils/request'

/**
 * 岗位推荐
 * @param {Object} data 包含参数和权重的对象
 * @returns {Promise}
 */
export function recommendJobs(data) {
  return request({
    url: '/jobs/recommend',
    method: 'post',
    data
  })
} 