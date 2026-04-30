''' See Lecture 11 on databases (pg.32), they recommend using controllers.py for larger 
functions that are called by routes.py. For example, if you have a route that needs 
to query the database and do some processing before rendering a template, you can 
put that logic in a function in controllers.py and then call that function from 
your route in routes.py. This helps keep code organized and makes it easier to 
maintain as your application grows.'''
