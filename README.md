challenge
=========

Programming challenge solution.

This solution contains two modules, httpd.py and scrape.py. They are intended to be run as docker containers with images named eriknj/httpd and eriknj/scrape respectively. 
The httpd module provides the required interface, spawns new eriknj/scrape containers, receives data from them, and removes them when they finish running. 
The scrape modules perform the actual web scraping and communicate their findings back to the eriknj/httpd container.

To start the program, execute:<br/>
<code>
docker run -d -v /var/run/docker.sock:/var/run/docker.sock -p &lt;port&gt;:5000 --name httpd eriknj/httpd
</code<br/>
Where &lt;port&gt; is the port you wish to communicate with the application on.
