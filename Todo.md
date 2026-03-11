make sure team members (mainly me) know how to develop in environment and push to gihub branch 
    I did: start vscode with git link
    created python virtual environment
    imported python libraries used in django (note this can be done with requirements.txt)
    used the createsuperuser command to modify database (add movies)
    migrate and runserver to test changes
user story 1: see a map showing which movis are trending in different geographic areas (popular around me or in other regions)
"Local Popularity Page" (called geography) 

Here is info
    User story 1: 
    As a User, I want to see a map showing which movies of the GT Movie Store are trending (or most purchased) in different geographic areas, so I can discover what’s popular around me or in other regions.

    Completion Steps:
    a) Log in or register an account.

    b) Navigate to the “Local Popularity Map” page.

Add field to register called location
location is: city name, geo coordinates

load purchases 

    c) Verify that the map loads correctly with regional boundaries or markers.

    d) Confirm that movies with high purchase/view counts are displayed as trending in at least one region.

movie purchase account 

    e) Select a specific region on the map.

    f) Verify that the region’s top trending movies are listed (titles, counts, etc.).

Create an intro video and stitch my part together

Django: 
#1 make sure user is tied to city
registering account select a city
registering account saves the geolocation of that city

#3 update database upon purchase
purchasing a movie adds city to list
purchasing a movie increases its watch count

#2 integrate lookup in the geo page
create page where you can view a map with all possible locations marked
select marker and display purchase count (sorted by popularity)