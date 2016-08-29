module.exports = {
  entry : './src/index.jsx',
  output : {
    path : '../dist',
    filename : 'app.bundle.js'
  },
  module : {
    loaders : [ {
      test : /\.jsx?$/,
      loader : 'babel-loader',
      query : {
        presets : ['es2015', 'react', 'stage-1' ]
      }
    } ]
  },
  resolve : {
    extensions : [ '', '.js', '.jsx' ]
  }
};
