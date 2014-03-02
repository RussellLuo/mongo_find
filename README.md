mongo_find
==========

Generic find interface (support filtering, sorting and paging) for MongoDB.

1. Run it
---------

    python sites/models.py
    python manage.py runserver

2. Try it
---------

Try the following urls:

	http://127.0.0.1:8000/sites/
	http://127.0.0.1:8000/sites/?site_name=my_site
    http://127.0.0.1:8000/sites/?user_name=russell
	http://127.0.0.1:8000/sites/?pv=1&page=1
