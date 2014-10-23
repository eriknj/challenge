import urllib2
from bs4 import BeautifulSoup
import sys
from os import environ

script, job_id_str, scheme, loc = sys.argv
job_id = int( job_id_str )

addr = environ[ 'HTTPD_PORT_5000_TCP_ADDR' ]
port = environ[ 'HTTPD_PORT_5000_TCP_PORT' ]

result_target = "http://%s:%s/result/%s" % ( addr, port, "%d" )
status_target = "http://%s:%s/status/%s" % ( addr, port, "%d" )

opener = urllib2.build_opener( urllib2.HTTPHandler )

def do_put( target, d ) :
    request = urllib2.Request( target, data=d )
    request.add_header( 'Content-Type', 'text/plain' )
    request.add_header( 'Content-Length', len( d ) )
    request.get_method = lambda: 'PUT'
    opener.open( request )

def report_results( results ) :
    target = result_target % ( job_id )
    data = ",".join( results )
    do_put( target, data )

def report_completion() :
    target = status_target % ( job_id )
    do_put( target, loc )

def valid_url( url ) :
    return url != None and url.startswith( "http:" )

def scrape_images( soup ) :
    results = []
    for img in soup.find_all( 'img' ) :
        result = img.get( 'src' )
        if valid_url( result ) :
            results.append( result )
    if len( results ) > 0 :
        report_results( results )

if __name__ == "__main__" :
    page = "%s://%s/" % ( scheme, loc )
    html = urllib2.urlopen( page ).read()
    soup = BeautifulSoup( html )

    scrape_images( soup )

    links = soup.find_all( 'a' )
    for link in links :
        page = link.get( 'href' )
        if valid_url( page ) :
            try :
                html = urllib2.urlopen( page ).read()
                scrape_images( BeautifulSoup( html ) )
            except :
                pass

    report_completion()
    exit( 0 )
