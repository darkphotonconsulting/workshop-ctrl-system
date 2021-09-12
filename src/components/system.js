import React from "react";
import { makeStyles } from "@material-ui/core/styles";
import clsx from "clsx";
import Card from "@material-ui/core/Card";
import CardHeader from "@material-ui/core/CardHeader";
import CardMedia from "@material-ui/core/CardMedia";
import CardContent from "@material-ui/core/CardContent";
import CardActions from "@material-ui/core/CardActions";
import Collapse from "@material-ui/core/Collapse";
import Avatar from "@material-ui/core/Avatar";
import IconButton from "@material-ui/core/IconButton";
import Typography from "@material-ui/core/Typography";
import { red, grey } from "@material-ui/core/colors";
import FavoriteIcon from "@material-ui/icons/Favorite";
import ShareIcon from "@material-ui/icons/Share";
import ExpandMoreIcon from "@material-ui/icons/ExpandMore";
import MoreVertIcon from "@material-ui/icons/MoreVert";

const useStyles = makeStyles((theme) => ({
  root: {
    maxWidth: 745,
  },
  media: {
    // height: 1100,
    // width: 735,
    paddingTop: "56.25%", // 16:9
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
    backgroundColor: grey[500],
  },
}));

const System = ({ system }) => {
  const classes = useStyles();
  const [expanded, setExpanded] = React.useState(false);
  console.log(Object.keys(system));
  const handleExpandClick = () => {
    setExpanded(!expanded);
  };
  return (
    <Card className={classes.root}>
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
        image="https://wallpapercave.com/wp/wp1864223.jpg"
        title="Raspberry Pi 4 birdseye view"
      />
      <CardContent>
        <Typography variant="p" color="textSecondary">
          revision: {system.revision}
          SoC: {system.soc}
          Memory: {system.ram}
        </Typography>
      </CardContent>
    </Card>
  );
};

export default System;
