'''

David Lettier (C) 2014.

Web client that retrieves files via HTTP from an HTTP server.

Requires Python 2.7.3.

'''

import socket;
import sys;
import re;
import time;
import string;

print "\nWelcome to Web Connoisseur 9000!\n";

try:

	# Get and parse the URL from the command line.
	
	url = sys.argv[ 1 ];
	
	parse_url = "(?P<proc>\w.*://)?(?P<host>[^:/ ]+).?(?P<port>[0-9]*)(?P<file>/*\S*)";	

	url_parts = re.search( parse_url, url );
	
	# Error checking.
	
	try:

		protocol  = url_parts.group( "proc" );
		host      = url_parts.group( "host" );
		port      = url_parts.group( "port" );
		data_file = url_parts.group( "file" );
		
	except AttributeError:
	
		print "\nDid not understand the URL.";
		
		print "Format: [protocol://]hostname[:port number][/path/to/file.ext]\n";
		
		sys.exit( 1 );
		
	if ( ( protocol != None ) and ( protocol.replace( "://", "" ).lower( ) != "http" ) ):
	
		print "\nOnly HTTP allowed.";
		print "Received: " + protocol + "\n";
		
		sys.exit( 1 );
	
	if ( host == "" or host == None ):
		
		host = url.replace( "http://", "" );
	
		host = url.split( "/" )[ 0 ];
		
		host = host.split( ":" )[ 0 ];
			
	if ( port == "" or port == None ):

		port = 80;
			
	if ( data_file == "" or data_file == None ):
	
		data_file = "/";
			
	port = int( port );
	
	if ( data_file[ 0 ] != "/" ):
	
		data_file = "/" + data_file;
		
	# Print status updates.
		
	time_stamp = time.strftime('%a, %d %b %Y %H:%M:%S GMT', time.gmtime( ) );
	
	print "--" + time_stamp + "--" + " " + "http://" + host + ":" + str( port ) + data_file;
	
	print "Resolving " + host + " (" + host + ")... " + socket.getaddrinfo( host, port )[ 0 ][ 4 ][ 0 ];
		
	print "Connecting to " + host + " (" + host + ")|" + socket.getaddrinfo( host, port )[ 0 ][ 4 ][ 0 ] + "|" + str( socket.getaddrinfo( host, port )[ 0 ][ 4 ][ 1 ] ) + "...",;
		
	# Connect to the server.

	server_socket = socket.socket( socket.AF_INET, socket.SOCK_STREAM );

	server_socket.connect( ( host, port ) );
	
	print( "connected." );

	# Send request query with Host: header.

	query = "GET " + data_file + " HTTP/1.1\r\nHost: " + host + "\r\n" + "\r\n";	

	server_socket.send( query );
	
	print "HTTP request sent, awaiting response...",;

	# Read in the response.

	response = b'';
	
	response_body = b'';

	while 1:

		buffer = server_socket.recv( 1024 );

		if not buffer: 
	
			break;
		
		response = response + buffer;
		
	# Save binary data for future possible use.
		
	response_body_binary_start = response.find( "\r\n\r\n" ) + 4;
	
	response_body_binary = response[ response_body_binary_start : ];
	
	# Parse the response.
		
	response = "".join( response );
	
	response = response.split( "\r\n" );
	
	# Get the response status.
		
	response_status = response[ 0 ].replace( "HTTP/1.1 ", "" ).rstrip( "\r" );
	
	print response_status;
	
	# Something went wrong with the query?
	
	if ( response_status.find( "200" ) == -1 ):
	
		print "Server response:";
		print "----------------";
	
		for i in xrange( 0, len( response ) ):
	
			if ( all( characters in string.printable for characters in response[ i ] ) ):
		
				print response[ i ];
			
			else:
		
				print "<binary>";
			
		print "----------------";
		
		sys.exit( 0 );
		
	# Print the response.
	
	print "Server response:";
	print "----------------";
	
	for i in xrange( 0, len( response ) ):
	
		if ( all( characters in string.printable for characters in response[ i ] ) ):
		
			print response[ i ];
			
		else:
		
			print "<binary>";
			
	print "----------------";
	
	# Save the response body.
	
	i = 0;

	for line in xrange( 0, len( response ) ):
	
		# Find when the body starts.

		if ( response[ line ] == "" ):
		
			i = line;
			
			break;
			
	response_body_text = response[ i + 1 : ];
	
	if ( data_file == "/" ):
	
		# They did not specify a file so assume they meant the index.html file.
	
		try:
		
			# Do not overwrite the file.
	
			data_file_save = open( "index.html", "r" );
			
			data_file_save.close( );
			
			# File exits so make a new one with a similar name.
			
			new_data_file_save_name = str( int( round( time.time( ) * 1000 ) ) ) + "." + "index.html";
			
			print "Saving to: `" + new_data_file_save_name + "`";
			
			data_file_save = open( new_data_file_save_name, "w" );
			
			data_file_save.write( "".join( response_body_text ) );
			
			data_file_save.close( );
			
		except ( OSError, IOError ) as error:
		
			# File does not exist so proceed as normal.
		
			data_file_save = open( "index.html", "w" );
			
			print "Saving to: `" + "index.html" + "`";
			
			data_file_save.write( "".join( response_body_text ) );
			
			data_file_save.close( );
			
	else:
	
			# Detect if the file request is of the binary type (images).
			
			data_file_extension = data_file.lower( ).split( "." )[ -1 ];
			
			if ( data_file_extension == "png" or data_file_extension == "gif" or data_file_extension == "jpg" or data_file_extension == "ico" or  data_file_extension == "bmp" or  data_file_extension == "tiff" ):
			
				# Binary file.
				
				try:
				
					# Do not overwrite the file.

					data_file_local_directory = data_file.split( "/" )[ -1 ];
					
					data_file_save = open( data_file_local_directory, "rb" );
		
					data_file_save.close( );
					
					# File exits so make a new one with a similar name.
		
					new_data_file_save_name = str( int( round( time.time( ) * 1000 ) ) ) + "." + data_file_local_directory;
		
					print "Saving to: `" + new_data_file_save_name + "`";
		
					data_file_save = open( new_data_file_save_name, "wb" );			
					
					data_file_save.write( response_body_binary );
		
					data_file_save.close( );
		
				except ( OSError, IOError ) as error:
				
					data_file_local_directory = data_file.split( "/" )[ -1 ];
	
					data_file_save = open( data_file_local_directory , "wb" );
		
					print "Saving to: `" + data_file_local_directory  + "`";
					
					data_file_save.write( response_body_binary );
		
					data_file_save.close( );
			
			else:
			
				# Plain text file.
		
				try:
				
					# Do not overwrite the file.
				
					data_file_local_directory = data_file.split( "/" )[ -1 ];

					data_file_save = open( data_file_local_directory, "r" );
		
					data_file_save.close( );
					
					# File exits so make a new one with a similar name.
		
					new_data_file_save_name = str( int( round( time.time( ) * 1000 ) ) ) + "." + data_file_local_directory;
		
					print "Saving to: `" + new_data_file_save_name + "`";
		
					data_file_save = open( new_data_file_save_name, "w" );			
		
					data_file_save.write( "".join( response_body_text ) );
		
					data_file_save.close( );
		
				except ( OSError, IOError ) as error:
				
					data_file_local_directory = data_file.split( "/" )[ -1 ];
	
					data_file_save = open( data_file_local_directory, "w" );
		
					print "Saving to: `" + data_file_local_directory + "`";
		
					data_file_save.write( "".join( response_body_text ) );
		
					data_file_save.close( );
	
	# All done so close the socket.

	server_socket.close;
	
except IndexError:

	# No URL specified on the command line.

	print "\nUsage:\npython web_client.py URL\n";

