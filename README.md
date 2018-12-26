# Item Catalog

## Introduction

> An application that provides : <br/><ol><li> A list of cities within a variety of countries.</li><li>Provide a user registration and authentication system. </li> <li>Registered users will have the ability to post, edit and delete their own added countries and cities. </li></ol>

## Code Samples

> The application has several routes:<br/>
<ol>
<li>http://localhost:500/ & http://localhost:5000/country: Show all countries.</li>
<li>http://localhost:500/country/new: to add new country.</li>
<li>http://localhost:500< int:country_id>/edit/: To edit country name.</li>
<li>http://localhost:500/country/< int:country_id>/delete/: To delete a country.</li>
<li>http://localhost:500/country/< int:country_id>/ && http://localhost:500/country/< int:country_id>/cities: To view all cities of a country.</li>
<li>http://localhost:500/country/<int:country_id >/cities/new/: To add new city.</li>
<li>http://localhost:500'/country/< int:country_id>/cities/< int:city_id>/edit: To edit a city info.</li>
<li>http://localhost:500/country/< int:country_id>/cities/<I nt:city_id>/delete: To delete a city.</li>
<li>http://localhost/gdisconnect: DISCONNECT - Revoke a current user's token and reset their login_session.</li>
<li>http://localhost:5000/country/< int:country_id >/cities/JSON:  Illustrate JSON for  Country Information.</li>
<li>http://localhost:500/country/< int:country_id>/cities/<int:city_id>/JSON: illustrate city info.</li>
<li>http://localhost:500/JSON : illustrate json for all countries. </li>
<li>http://localhost:500/disconnect: To start disconnecting a user based on the provider of log in Authentication</li>
<li>http://localhost:500/login: start a login authontication session and creating anti-forgery state token.
</li>
<li>http://localhost:500/gconnect: Validate token of a user used Google provider to log in</li>
</ol>

## Installation

>## This project uses:
<ul>
<li>virtual box.</li>
<li>vagrant.</li>
<li>database_setup.py to initiate database.</li>
<li>helper.py contains DB helper functions</li>
</ul>

> ## Python version: <br/>
Python 2.7

>## Running the Item Catalog App:
<ol>
<li> Make sure the virtual machine is running.</li>
<li>The project folder should be included in a vagrant folder to able running it on the terminal. </li>
<li>Once the VM is running, and the current directory is the project folder, Go to next step</li>
<li>Initiate the database, by running the command: python database_setup.py</li>
<li>When the database is started successfully(it should not show any error messages), we start running the main code by typing: python item_catalog.py.</li>
<li>Then on the browser address bar, type the route: http://localhost:5000, this should take you to the home page with no user logged in yet.</li>
</ol>
