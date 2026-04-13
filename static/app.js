app.use(function (req, res, next) {
      res.header('Content-Security-Policy', "default-src 'self'; object-src 'none'");
      next();
    });