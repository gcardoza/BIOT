import React from 'react';
import { render } from 'react-dom';
import getMuiTheme from 'material-ui/styles/getMuiTheme';
import MuiThemeProvider from 'material-ui/styles/MuiThemeProvider';

import AppBar from 'material-ui/AppBar';
import Drawer from 'material-ui/Drawer';
import MenuItem from 'material-ui/MenuItem';

export default class App extends React.Component {

  constructor(props) {
    super(props);
    this.state = {open : false};
  }

  handleToggle  = () => this.setState({open: !this.state.open});

  render() {
    return (
      <MuiThemeProvider muiTheme={getMuiTheme()}>
        <div>
          <AppBar
            title="BIOT Dashboard"
            onTouchTap={this.handleToggle}
          />
          <Drawer 
            open={this.state.open}
            docked={false}
            onRequestChange={(open) => this.setState({open})}
          >
            <MenuItem> Foo </MenuItem>
            <MenuItem> Bar </MenuItem>
          </Drawer>
        </div>
      </MuiThemeProvider>
    );
  }

}
