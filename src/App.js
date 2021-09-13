import React, { Component } from "react";
import { makeStyles, withStyles } from "@material-ui/core/styles";

import Paper from "@material-ui/core/Paper";
import AppBar from "@material-ui/core/AppBar";
import Toolbar from "@material-ui/core/Toolbar";
import Typography from "@material-ui/core/Typography";
import Button from "@material-ui/core/Button";
import IconButton from "@material-ui/core/IconButton";
import MenuIcon from "@material-ui/icons/Menu";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import * as Colors from "@material-ui/core/colors/";
// import TopBar from "./components/topbar";
import System from "./components/system";
import { library } from "@fortawesome/fontawesome-svg-core";
import { fab } from "@fortawesome/free-brands-svg-icons";
import {
  faCheckSquare,
  faDigitalTachograph,
  faRandom,
  faLaptopMedical,
} from "@fortawesome/free-solid-svg-icons";
import { faRaspberryPi } from "@fortawesome/free-brands-svg-icons";
import {
  createTheme,
  responsiveFontSizes, 
  ThemeProvider,
} from "@material-ui/core/styles";
import { BrowserRouter as Router, Switch, Route } from "react-router-dom";
library.add(fab, faCheckSquare, faRaspberryPi, faDigitalTachograph);


let theme = createTheme({
  palette: {
    primary: {
      main: Colors.orange[900],
    },
    secondary: {
      main: Colors.grey[900],
    },
  },
});
theme = responsiveFontSizes(theme);

const styles = (theme) => ({
  root: {
    display: "flex",
    flexWrap: "wrap",
    flexDirection: "row",
    //backgroundColor: Colors.red[900],
    justifyContent: "center",
    alignItems: "center",
    padding: 10,
  },
  content: {
    flex: 1,
    borderRadius: "15px",
    backgroundColor: Colors.grey[500],
    alignContent: "center",
    justifyContent: "center",
    alignItems: "center",
    textAlign: "center",
  },
});

//const classes = useStyles();

class App extends Component {
  render() {
    const { classes } = this.props;

    //const { accordion_items } = 
    console.log(classes)
    return (
      <React.Fragment>
        <ThemeProvider theme={theme}>
            <AppBar position="static">
              <Toolbar>
                <IconButton
                  edge="start"
                  className={classes.menuButton}
                  color="inherit"
                  aria-label="menu"
                >
                  <MenuIcon />
                </IconButton>
                <Typography variant="h6" className={classes.title}>
                  Workshop Control System
                </Typography>

                <IconButton edge="end">
                  <FontAwesomeIcon icon={faRaspberryPi} />
                </IconButton>
                <IconButton edge="end">
                  <FontAwesomeIcon icon={faDigitalTachograph} />
                </IconButton>
                <IconButton edge="end">
                  <FontAwesomeIcon icon={faRandom} />
                </IconButton>
                <IconButton edge="end">
                  <FontAwesomeIcon icon={faLaptopMedical} />
                </IconButton>
              </Toolbar>
            </AppBar>
        </ThemeProvider>
        
        <ThemeProvider theme={theme}>
          <div className={classes.root}>
          <Paper elevation={3} variant="outlined" className={classes.content}>
         
            <p>Center Me</p>
            <System system={this.state.system} />
          </Paper>
          </div>
        </ThemeProvider>
        {/* <div className={classes.root}>
          <System system={this.state.system} />
        </div> */}
      </React.Fragment>
    );
  }
  state = {
    system: [],
    gpio: [],
    relay: [],
  };
  componentDidMount() {
    fetch("http://headunit:8000/ro/sys")
      .then((res) => res.json())
      .then((data) => {
        this.setState({ system: data });
        //console.log("system state: " + this.state.system);
      })
      .catch(console.log);

    fetch("http://headunit:8000/ro/gpio")
      .then((res) => res.json())
      .then((data) => {
        this.setState({ gpio: data });
        //console.log("gpio state: " + this.state.gpio);
      })
      .catch(console.log);

    fetch("http://headunit:8000/ro/relay")
      .then((res) => res.json())
      .then((data) => {
        this.setState({ relay: data });
        //console.log("relay state: " + this.state.relay);
      })
      .catch(console.log);
  }
}

//export default App;
export default withStyles(styles, { withTheme: true })(App);
