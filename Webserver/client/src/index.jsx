import injectTapEventPlugin from 'react-tap-event-plugin';
import React from 'react';
import { render } from 'react-dom';

import App from './app.jsx';

injectTapEventPlugin();
console.log('stuff');
render((
  <App />
  ), document.getElementById('react-root')
);

