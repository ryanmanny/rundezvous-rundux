# RundezvousRundux
Return of Rundezvous

# Installation Instructions
1. Install Django and other Python packages

   `pip install -r requirements.txt`
1. Install GeoDjango

    `https://docs.djangoproject.com/en/2.1/ref/contrib/gis/install/`
    
    - If you're not using SpatiaLite you will need to change some values in rundezvous_rundux/settings.py (I actually recommend using Postgres)
    - Don't try getting Django to work with SpatiaLite on Windows I couldn't ever get it to work
