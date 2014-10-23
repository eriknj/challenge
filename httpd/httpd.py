from flask import Flask, request, Response
from urlparse import urlparse
import docker
import thread

app = Flask( __name__ )

job_ids = []
target_ls_by_job_id = {}
result_by_job_id = {}

c = docker.Client( 
    base_url='unix://var/run/docker.sock',
    version='1.12',
    timeout=10
)

def get_next_url( args ) :
    parser = urlparse( args )
    args = parser.path[1:]
    return ( parser.scheme, parser.netloc, args )

@app.route( '/', methods=[ 'POST' ] )
def job_intake() :
    args = request.form.keys()[0]

    targets = []
    while len( args ) > 0 :
        scheme, netloc, args = get_next_url( args )
        target = {}
        target[ 'scheme' ] = scheme
        target[ 'netloc' ] = netloc
        target[ 'pending' ] = True
        targets.append( target )
    
    if len( job_ids ) == 0 :
        job_id = 1
    else :
        job_id = job_ids[ -1 ] + 1

    target_ndx = 1
    for target in targets :
        n = "scrape%d.%d" % ( job_id, target_ndx )
        target_ndx += 1 
        cmd = "%d %s %s" % ( job_id, target[ 'scheme' ], target[ 'netloc' ] )
        container = c.create_container( "eriknj/scrape", name=n, command=cmd )
        c.start( container, links=[ ( "httpd", "HTTPD" ) ] )
        target[ 'container' ] = container

    target_ls_by_job_id[ job_id ] = targets
    result_by_job_id[ job_id ] = []
    job_ids.append( job_id )

    response = Response( "Job accepted, ID assigned: %d\n" % job_id )
    response.result = str( job_id )
    response.result_code = 200

    return response

def bad_id_error_msg( job_id ) :
    return "ERROR: Job ID %d not found.\n" % job_id

@app.route( '/status/<int:job_id>', methods=[ 'GET' ] )
def get_status( job_id ) :
    if job_id in job_ids :
        pending = complete = 0
        for target in target_ls_by_job_id[ job_id ] :
            if target[ 'pending' ] :
                pending += 1
            else :
                complete += 1

        format_str = "Crawling in progress on %d URLs\nCompleted: %d\n"
        return_str = format_str % ( pending, complete )
    else :
        return_str = bad_id_error_msg( job_id )

    return return_str

def wait_and_close( container ) :
    c.wait( container )
    c.remove_container( container )

@app.route( '/status/<int:job_id>', methods=[ 'PUT' ] )
def set_status( job_id ) :
    if job_id in job_ids :
        success = False
        loc = request.data #args[ 'loc' ]

        for target in target_ls_by_job_id[ job_id ] :

            if target[ 'netloc' ] == loc and target[ 'pending' ] :
                success = True
                target[ 'pending' ] = False
                container = target[ 'container' ]
                thread.start_new_thread( wait_and_close, ( container, ) )
                break

        if success :
            return_str = "SUCCESS: Status updated for job %d\n" % job_id
        else:
            return_str = "ERROR: Job with ID %d already complete.\n" % job_id

    else :
        return_str = bad_id_error_msg( job_id )

    return return_str

@app.route( '/result/<int:job_id>', methods=[ 'GET' ] )
def get_result( job_id ) :
    if job_id in job_ids :
        return_str = "\n".join( result_by_job_id[ job_id ] )
        return_str += "\n"
    else :
        return_str = bad_id_error_msg( job_id )

    return return_str

@app.route( '/result/<int:job_id>', methods=[ 'PUT' ] )
def append_result( job_id ) :
    if job_id in job_ids :
        raw_results = request.data #args[ 'result' ]
        results = raw_results.split( ',' )
        result_by_job_id[ job_id ].extend( results )
        result_str = "SUCCESS: Results appended to job ID %d\n" % job_id
    else :
        result_str = bad_id_error_msg( job_id )
    
    return result_str

if __name__ == '__main__' :
    app.run( host='0.0.0.0', port=5000 )
