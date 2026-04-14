const helmet = require('helmet');
app = express();
app.use(helmet());
app.get('/', (req, res) => {
  res.send('Hello World!');
});