const express = require('express');
const cors = require('cors');
const jobsRouter = require('./routes/jobs');

const app = express();
const port = 5011;

app.use(cors());
app.use(express.json());

app.use('/api/jobs', jobsRouter);

app.listen(port, () => {
  console.log(`Server is running on port ${port}`);
}); 