import React, { Component } from "react";
import { withStyles } from "@material-ui/core/styles";
import Grid from "@material-ui/core/Grid";
import Paper from "@material-ui/core/Paper";
import * as Colors from "@material-ui/core/colors/";
import TopBar from "./components/topbar";
import System from "./components/system";
import {
  createTheme,
  responsiveFontSizes, 
  ThemeProvider,
} from "@material-ui/core/styles";
//import { BrowserRouter as Router, Switch, Route } from "react-router-dom";


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
          <TopBar/>
        </ThemeProvider>

        <ThemeProvider theme={theme}>
          <div className={classes.root}>
            <Paper elevation={3} variant="outlined" className={classes.content}>
              <Grid container spacing={3}>
                <Grid item xs={12}>
                  {/* <System system={this.state.system} /> */}
                  Testing
                </Grid>
                <Grid item xs={12}>
                  {/* <System system={this.state.system} /> */}
                  Testing
                </Grid>
                <Grid item xs={12}>
                  {/* <System system={this.state.system} /> */}
                  Testing
                </Grid>
                <Grid item xs={12}>
                  <System system={this.state.system} />
                  
                </Grid>
              </Grid>
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

    fetch("http://headunit:8000/ro/sys/info")
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
