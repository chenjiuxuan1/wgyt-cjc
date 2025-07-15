const express = require('express')
const router = express.Router()
const jobsController = require('../controllers/jobs')

// 岗位推荐
router.post('/recommend', jobsController.recommendJobs)

// 岗位预警相关路由
router.post('/alert/check', jobsController.checkJobAlerts)
router.post('/alert/count', jobsController.getJobCount)

module.exports = router 