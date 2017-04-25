# Introduction
API server enables programmatic read and write access to the climbing database.  For example, you can retrieve all climbing routes 30km around Dresden, Germany as follows: 

```javascript
var api_key='xyz';
var latlng='13.7372621,51.0504088'; // Dresden, Germany
var search_radius = 30000; //30km

var url ='https://api.openbeta.io/routes?api_key=' + api_key + '&latlng=' + lnglat + '&r=' + search_radius;

// Fetch data 
$.ajax({
  url: api_url,
  success: function(data, textStatus, jqXHR ) { 
    console.log(data);
    // something with the data  
  });

```

The easiest way to get started is to play with [a sample code on CodePen](http://codepen.io/openbeta/pen/vgpqwP).  Due to a [bug](https://github.com/OpenBeta/design/issues/9) you must pass `longitude,latitude` to the API even though the parameter is called `latlng`.

The project is under heavy development.  There is a [task](https://github.com/OpenBeta/design/issues/5) to autogenerate API documentation.



# API Documentation
```
GET /routes
```
Get climbing routes within a search radius

|Parameter|Required|Description|
|---------|--------|-----------|
|api_key|Yes| API access key|
|latlng|Yes| Longitude,Latitude. Example, `13.7372621,51.0504088`|
|r|Yes| Radius in meters. Example, 1200| 

```
GET /featureset
```
Get climbing routes and crags within a search radius

|Parameter|Required|Description|
|---------|--------|-----------|
|api_key|Yes| API access key|
|latlng|Yes| Longitude,Latitude. Example, `13.7372621,51.0504088`|
|r|Yes| Radius in meters. Example, `1200`| 




# Contribution
Yes please and thank you!




# Copyright & License
- Data (c) OpenStreetMap contributors, available under [CC-BY-SA](https://creativecommons.org/licenses/by-sa/4.0/)
- Source code [GPLv3](https://github.com/OpenBeta/beta/blob/master/LICENSE)

