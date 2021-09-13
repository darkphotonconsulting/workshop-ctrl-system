const http = require('http')
const express = require('express')
const cors = require('cors')
const app = express()
app.use(cors())
const fs = require('fs')
const path = require('path')
const url = require('url')
const rpio = require('rpio')

const port = 8000

const relayState = {
	0: 'LOW',
	1: 'HIGH'
}
Array.prototype.findByValueOfObject = function(key, value) {
	  return this.filter(function(item) {
		      return (item[key] === value);
		    });
}

app.get('/', (req, res) => {
  res.end('testing');
});

app.get('/ro/sys', (req, res) => {
  fs.readFile(__dirname + '/' + 'sys.json', 'utf8', (err, data) => {
    let database = JSON.parse(data)
    res.json(database)
  });
});

app.get('/ro/gpio', (req, res) => {
  fs.readFile(__dirname + '/' + 'gpio.json', 'utf8', (err, data) => {
    let database = JSON.parse(data)
    res.json(database)
  });
});

app.get('/ro/gpio/:gpio_port', (req, res) =>{
  fs.readFile(__dirname + '/' + 'gpio.json', 'utf8', (err, data) => {
	  let database = JSON.parse(data)
	  let pin = database.find(p => p.gpio_port === parseInt(req.params.gpio_port))
	  console.log(pin)
	  res.json(pin)
  });
});

app.get('/ro/gpio/:gpio_port/keys', (req, res) =>{
  fs.readFile(__dirname + '/' + 'gpio.json', 'utf8', (err, data) => {
	  let database = JSON.parse(data)
	  let pin = database.find(p => p.gpio_port === parseInt(req.params.gpio_port))
	  console.log(Object.keys(pin))
	  res.json(Object.keys(pin))
  });
});

/* 
mapping
gpio, board number, channel

*/

app.get('/rw/gpio/:gpio_port/:direction/:state', (req, res) =>{
  fs.readFile(__dirname + '/' + 'gpio.json', 'utf8', (err, data) => {
	  let database = JSON.parse(data)
	  let pin = database.find(p => p.gpio_port === parseInt(req.params.gpio_port))
	  console.log(pin)
	  rpio.open(
		  parseInt(pin.gpio_port), 
		  req.params.direction == 'INPUT' ? rpio.INPUT : rpio.OUTPUT, 
		  req.params.state == 'HIGH' ? rpio.HIGH : rpio.LOW
		);
	  let state = rpio.read(parseInt(req.params.gpio_port))
	  let ret = {}
	  ret[parseInt(req.params.gpio_port)] = state ? 'high' : 'low'
	  res.json(ret)
	  //res.end(String(val))
  });
});

app.get('/rw/relay/:channel/:direction/:state', (req, res) =>{
  fs.readFile(__dirname + '/' + 'gpio.json', 'utf8', (err, data) => {
	  let database = JSON.parse(data)
      let relaypins = database.filter(p => p.relay_channel != null )
	  console.log('relay pins: ' + relaypins)
	  let pin = relaypins.find(p => p.relay_channel === parseInt(req.params.channel))
	  console.log('selected pin gpio: ' + pin.gpio_port)
	  console.log('selected pin board: ' + pin.board_port)
	  //rpio.
	  rpio.open(
		  parseInt(pin.board_port), 
		  req.params.direction == 'INPUT' ? rpio.INPUT : rpio.OUTPUT, 
		  req.params.state == 'HIGH' ? rpio.HIGH : rpio.LOW
		);
	   let state = rpio.read(parseInt(pin.board_port))
	   let ret = {}
	   ret[parseInt(req.params.channel)] = state ? 'high' : 'low'
	   res.json(ret)
	  //res.end(String(val))
  });
});

app.get('/rw/relay/estop', (req, res) =>{
  fs.readFile(__dirname + '/' + 'gpio.json', 'utf8', (err, data) => {
	  let database = JSON.parse(data)
	  console.log('database: ' + database)
	  console.log('database type: ' + typeof(database))
	  console.log('database keys: ' + Object.keys(database))
      let relaypins = database.filter(p => p.relay_channel != null )
	  console.log('relay pins: ' + relaypins)
	  console.log('relay pins keys: ' + Object.keys(relaypins))

	  Object.entries(relaypins).forEach( entry => {
		const [k, v]  = entry ;
		console.log('relay pin keys: ' + Object.keys(v))
		console.log('relay key: ' + k + 'relay val: ' + v.relay_channel)
		rpio.open(
			parseInt(v.board_port),
			rpio.OUTPUT,
			rpio.HIGH
		)
	  });
	  //console.log('relay pins: ' + relaypins)

	  res.end('fin')
  });
});

app.get('/rw/relay/estart', (req, res) =>{
  fs.readFile(__dirname + '/' + 'gpio.json', 'utf8', (err, data) => {
	  let database = JSON.parse(data)
	  console.log('database: ' + database)
	  console.log('database type: ' + typeof(database))
	  console.log('database keys: ' + Object.keys(database))
      let relaypins = database.filter(p => p.relay_channel != null )
	  console.log('relay pins: ' + relaypins)
	  console.log('relay pins keys: ' + Object.keys(relaypins))

	  Object.entries(relaypins).forEach( entry => {
		const [k, v]  = entry ;
		console.log('relay pin keys: ' + Object.keys(v))
		console.log('relay key: ' + k + 'relay val: ' + v.relay_channel)
		rpio.open(
			parseInt(v.board_port),
			rpio.OUTPUT,
			rpio.LOW
		)
	  });
	  //console.log('relay pins: ' + relaypins)

	  res.end('fin')
  });
});




app.get('/ro/gpio/:port/:attrib', (req, res) =>{
  fs.readFile(__dirname + '/' + 'gpio.json', 'utf8', (err, data) => {
	  let database = JSON.parse(data)
	  let pin = database.find(p => p.gpio_port === parseInt(req.params.port))
	  let attrib = req.params.attrib
	  let val = pin[req.params.attrib]
	  let ret = {}
	  ret[attrib] = val
	  console.log('pin: '+ JSON.stringify(pin))
	  console.log('gpio_port: ' + req.params.port)
	  console.log('key:' + req.params.attrib)
	  console.log('attribute value:' + val)
	  console.log(typeof(val))
	  res.json(ret)
	  //res.end(String(val))
  });
});

app.get('/ro/relay', (req, res) =>{
  fs.readFile(__dirname + '/' + 'gpio.json', 'utf8', (err, data) => {
	  let database = JSON.parse(data)
	  console.log(database)
	  console.log(typeof(database))
	  let relaypins = database.filter(p => p.relay_channel != null )
	  console.log(relaypins)
	  res.json(relaypins)
  });
});

app.get('/ro/relay/:channel', (req, res) =>{
  fs.readFile(__dirname + '/' + 'gpio.json', 'utf8', (err, data) => {
	  let database = JSON.parse(data)
	  let relaypins = database.filter(p => p.relay_channel != null )
	  let pin = relaypins.find(p => p.relay_channel == req.params.channel)
	  console.log(pin)
	  res.json(pin)
  });
});

app.get('/ro/relay/:channel/:attrib', (req, res) =>{
  fs.readFile(__dirname + '/' + 'gpio.json', 'utf8', (err, data) => {
	  let database = JSON.parse(data)
	  let relaypins = database.filter(p => p.relay_channel != null )
	  let pin = relaypins.find(p => p.relay_channel == req.params.channel)
	  let attrib = req.params.attrib
	  let val = pin[attrib]
	  let ret = {}
	  ret[attrib] = val
	  console.log(ret)
	  res.json(ret)
  });
});


app.listen(port, () => {
  console.log(`app listening on http://localhost:${port}`)
})
