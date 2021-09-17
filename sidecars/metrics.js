os = require('node-os-utils')
const http = require("http");
const express = require("express");
const cors = require("cors");
const app = express();
app.use(cors());
const fs = require("fs");
const path = require("path");
const url = require("url");
const rpio = require("rpio");
const influx = require("influx")

const port = 8001

const db = new influx.InfluxDB({
    host: 'localhost',
});



app.get("/ro/databases", (req, res) => {
  db.getDatabaseNames().then(names => {
      res.json(names);  
  });

  //res.end("testing");
});

app.get("/rw/databases/:name/", (req, res) => {
  db.getDatabaseNames().then((names) => {
    res.json(names);
  });

  //res.end("testing");
});


app.listen(port, () => {
  console.log(`app listening on http://localhost:${port}`);
});