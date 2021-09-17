import React from "react";
import { makeStyles } from "@material-ui/core/styles";
//import clsx from "clsx";


import Card from "@material-ui/core/Card";
import CardHeader from "@material-ui/core/CardHeader";
import CardMedia from "@material-ui/core/CardMedia";
import CardContent from "@material-ui/core/CardContent";
import CardActions from "@material-ui/core/CardActions";
import Avatar from "@material-ui/core/Avatar";
import IconButton from "@material-ui/core/IconButton";
//import Typography from "@material-ui/core/Typography";
//import { red, grey } from "@material-ui/core/colors";
import * as Colors from "@material-ui/core/colors/";
import ListSubheader from "@material-ui/core/ListSubheader";
import List from "@material-ui/core/List";
import ListItem from "@material-ui/core/ListItem";
import ListItemIcon from "@material-ui/core/ListItemIcon";
import ListItemText from "@material-ui/core/ListItemText";
import Collapse from "@material-ui/core/Collapse";
import ExpandLess from "@material-ui/icons/ExpandLess";
import ExpandMore from "@material-ui/icons/ExpandMore";
import StarBorder from "@material-ui/icons/StarBorder";
import Divider from "@material-ui/core/Divider";
import MoreVertIcon from "@material-ui/icons/MoreVert";
//import {ReactCompicture} from "../static/images/cards/system/test.jpg"
//import {ReactComponent as PiSvg } from "../static/images/cards/system/pi.svg"
import ComputerSVG from "../static/images/cards/system/computer.svg"
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { library } from "@fortawesome/fontawesome-svg-core";
import { fab } from "@fortawesome/free-brands-svg-icons";
import { faRaspberryPi } from "@fortawesome/free-brands-svg-icons";

import {
  faCheckSquare,
  faDigitalTachograph,
  faRandom,
  faLaptopMedical,
  faRobot,
} from "@fortawesome/free-solid-svg-icons";
library.add(fab, faCheckSquare, faRaspberryPi, faDigitalTachograph, faRandom, faLaptopMedical, faRobot);
//import {ReactComponent as Pi} from "./pi"
const useStyles = makeStyles((theme) => ({
  root: {
    //width: "100%",
    backgroundColor: theme.palette.background.paper,
    display: "flex",
    flexDirection: "row",
  },
  card: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
  },
  list: {
    width: "100%",
    backgroundColor: theme.palette.background.paper,
    justifyContent: "center",
    alignItems: "center",
  },
  nestedlist: {
    paddingLeft: theme.spacing(4),
  },
  media: {
    paddingTop: "56.25%", // 16:9
    height: 0,


  },
  expand: {
    transform: "rotate(0deg)",
    marginLeft: "auto",
    transition: theme.transitions.create("transform", {
      duration: theme.transitions.duration.shortest,
    }),
  },
  expandOpen: {
    transform: "rotate(180deg)",
  },
  avatar: {
    backgroundColor: Colors.grey[500],
  },
}));

const System = ({ system }) => {
  const classes = useStyles();
  const [expanded, setExpanded] = React.useState(false);
  const [open, setOpen] = React.useState(true);

  const handleExpandClick = () => {
    setExpanded(!expanded);
  };

  const handleClick = () => {
    setOpen(!open);
  };

  //console.log(system.keys())
  Object.keys(system).map((key, index) => (
      console.log('key: ' + key + ' index: ' + index)
  ));
  //generate accordion items for system page
  const list_items = Object.keys(system).map((key, index) => (
    <React.Fragment key={`frag-${key.toString()}`}>
      <ListItem
        button
        onClick={handleClick}
        alignItems="flex-start"
        key={`key-${key.toString()}`}
        component="li"
      >
        <ListItemText primary={key} />
        {open ? <ExpandLess /> : <ExpandMore />}
      </ListItem>
      <Collapse
        key={`collapse-${key.toString()}`}
        in={!open}
        timeout="auto"
        unmountOnExit
      >
        <List component="ul" key={`innerlist-${key.toString()}`} disablePadding>
          <ListItem
            button
            key={`ico-${key.toString()}`}
            className={classes.nestedlist}
            component="li"
          >
            <ListItemIcon key={`icon-${key.toString()}`} component="li">
              <StarBorder />
            </ListItemIcon>
            <ListItemText
              key={`val-${key.toString()}`}
              primary={system[key]}
              component="li"
            />
          </ListItem>
        </List>
      </Collapse>
      <Divider
        key={`divider-${key.toString()}`}
        variant="inset"
        component="li"
      />
    </React.Fragment>
  ));

  return (
    <Card className={classes.card}>
      <CardHeader
        avatar={
          <Avatar
            aria-label="system"
            className={classes.avatar}
            variant="rounded"
            alt={system.system}
            src={system.logo_url}
          />
        }
        action={
          <IconButton aria-label="settings">
            <MoreVertIcon />
          </IconButton>
        }
        title={system.system}
        subheader={`Model ${system.model}`}
      />
      <CardMedia
        className={classes.media}
        component="img"
        src={system.logo_url}
        title="Raspberry Pi 4 birdseye view"
      />
      <CardContent>
        {/* <Accordion
        >
          {accordion_items}
        </Accordion> */}

        <List
          component="ul"
          aria-labelledby="nested-list-subheader"
          subheader={
            <ListSubheader component="div">System Details</ListSubheader>
          }
          className={classes.list}
        >
          {list_items}
        </List>
      </CardContent>
    </Card>
  );
};

export default System;
