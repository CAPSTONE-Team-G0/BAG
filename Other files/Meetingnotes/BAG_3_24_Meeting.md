3/24/2026 6:00PM



LOOSE AGENDA:



\* Make sure modularized ver can be run (It doesn't LOL)

\* Need better way to get app working on VSCODE, AI generated quickstart directions are not clear/inconsistent

\* 



###### Mattea method for running the app that actually works:



In VSCODE terminal:



py -m pip install -r requirements.txt

$env:FLASK\_APP="app"

py -m flask init-db

py -m flask run



press CTRL+C to stop program



New problems:

\*modularized version of app returns Internal Server Error when logging in (registering works, when logging in with registered account is what returns the error)



VSCODE terminal log during error:



127.0.0.1 - - \[24/Mar/2026 18:05:27] "GET / HTTP/1.1" 302 -

127.0.0.1 - - \[24/Mar/2026 18:05:27] "GET /login HTTP/1.1" 200 -

127.0.0.1 - - \[24/Mar/2026 18:05:27] "GET /static/style.css HTTP/1.1" 200 -

127.0.0.1 - - \[24/Mar/2026 18:05:27] "GET /favicon.ico HTTP/1.1" 404 -

127.0.0.1 - - \[24/Mar/2026 18:09:41] "GET /register HTTP/1.1" 200 -

127.0.0.1 - - \[24/Mar/2026 18:09:41] "GET /static/style.css HTTP/1.1" 304 -

127.0.0.1 - - \[24/Mar/2026 18:09:59] "POST /register HTTP/1.1" 302 -

127.0.0.1 - - \[24/Mar/2026 18:09:59] "GET /login HTTP/1.1" 200 -

127.0.0.1 - - \[24/Mar/2026 18:09:59] "GET /static/style.css HTTP/1.1" 304 -

\[2026-03-24 18:10:17,989] ERROR in app: Exception on /login \[POST]

Traceback (most recent call last):

&#x20; File "C:\\Users\\smell\\AppData\\Local\\Python\\pythoncore-3.14-64\\Lib\\site-packages\\flask\\app.py", line 1473, in wsgi\_app

&#x20;   response = self.full\_dispatch\_request()

&#x20; File "C:\\Users\\smell\\AppData\\Local\\Python\\pythoncore-3.14-64\\Lib\\site-packages\\flask\\app.py", line 882, in full\_dispatch\_request

&#x20;   rv = self.handle\_user\_exception(e)

&#x20; File "C:\\Users\\smell\\AppData\\Local\\Python\\pythoncore-3.14-64\\Lib\\site-packages\\flask\\app.py", line 880, in full\_dispatch\_request

&#x20;   rv = self.dispatch\_request()

&#x20; File "C:\\Users\\smell\\AppData\\Local\\Python\\pythoncore-3.14-64\\Lib\\site-packages\\flask\\app.py", line 865, in dispatch\_request

&#x20;   return self.ensure\_sync(self.view\_functions\[rule.endpoint])(\*\*view\_args)  # type: ignore\[no-any-return]

&#x20;          \~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~^^^^^^^^^^^^^

&#x20; File "C:\\Users\\smell\\Documents\\School\\Flask\_Bag\_modularized\\Flask\_Bag\_mod\\app\\auth.py", line 58, in login

&#x20;   return redirect(url\_for("core.dashboard"))

&#x20;                   \~\~\~\~\~\~\~^^^^^^^^^^^^^^^^^^

&#x20; File "C:\\Users\\smell\\AppData\\Local\\Python\\pythoncore-3.14-64\\Lib\\site-packages\\flask\\helpers.py", line 220, in url\_for

&#x20;   return current\_app.url\_for(

&#x20;          \~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~^

&#x20;       endpoint,

&#x20;       ^^^^^^^^^

&#x20;   ...<4 lines>...

&#x20;       \*\*values,

&#x20;       ^^^^^^^^^

&#x20;   )

&#x20;   ^

&#x20; File "C:\\Users\\smell\\AppData\\Local\\Python\\pythoncore-3.14-64\\Lib\\site-packages\\flask\\app.py", line 1084, in url\_for

&#x20;   return self.handle\_url\_build\_error(error, endpoint, values)

&#x20;          \~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~^^^^^^^^^^^^^^^^^^^^^^^^^

&#x20; File "C:\\Users\\smell\\AppData\\Local\\Python\\pythoncore-3.14-64\\Lib\\site-packages\\flask\\app.py", line 1073, in url\_for

&#x20;   rv = url\_adapter.build(  # type: ignore\[union-attr]

&#x20;       endpoint,

&#x20;   ...<3 lines>...

&#x20;       force\_external=\_external,

&#x20;   )

&#x20; File "C:\\Users\\smell\\AppData\\Local\\Python\\pythoncore-3.14-64\\Lib\\site-packages\\werkzeug\\routing\\map.py", line 924, in build

&#x20;   raise BuildError(endpoint, values, method, self)

werkzeug.routing.exceptions.BuildError: Could not build url for endpoint 'core.dashboard'. Did you mean 'dashboard.dashboard' instead?

127.0.0.1 - - \[24/Mar/2026 18:10:17] "POST /login HTTP/1.1" 500 -





Joey ran the code through ChatGPT for a solution...



https://chatgpt.com/share/69c311c6-357c-8003-a9ac-7a4cb2cb29ae

(wish there was way to download this log as a file in case it stops being hosted but this works for now)



App now runs fine



\*Cleaned up redundant test branches of unworking versions and accidentally messed some stuff up figuring out how to merge (deleted meeting notes but re-added them. Everyone's figuring GitHub nonsense out still



###### Paul check-in:



Paul now has a working password reset feature! Will demo it next meeting either virtual or in-person









