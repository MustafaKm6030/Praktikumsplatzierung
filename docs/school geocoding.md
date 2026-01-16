Geocoding Feature Documentation
1. Overview
The Geocoding feature is a critical data enrichment pipeline that automatically finds and saves geographic coordinates (latitude and longitude) for schools. This enables the Map View functionality, allowing administrators to visualize the geographic distribution of partner schools and make informed decisions based on location.
The system uses a Hybrid Workflow: it attempts to geocode automatically upon data import and provides a manual trigger for administrators to process or retry schools in batches, ensuring both automation efficiency and human oversight.
2. User Workflow
A. Automatic on Import:
1. An administrator imports the master Excel file containing mentor and school data.
2. For each newly created school that does not have coordinates, the system automatically sets its geocoding_status to "PENDING". It does not make any API calls during the import to ensure the process remains fast.
B. Manual Batch Processing (The Main Workflow):
1. The administrator navigates to the School Management page. In the action bar, they see a button: "Find Missing Coordinates."
2. Upon clicking, a confirmation dialog appears, warning them that the process is synchronous and may take several minutes.
3. On confirmation, a full-page loading overlay appears, the button becomes disabled, and a POST request is sent to the backend.
4. The backend synchronously processes all schools with a PENDING or FAILED status, making one API call per school with a 1.1-second delay.
5. Upon completion, the backend returns a full statistical report (e.g., { success: 66, failed: 50 }).
6. The frontend displays a success notification with the results, removes the loading overlay, re-enables the button, and automatically refreshes the school list. The map and table now show the newly found coordinates.
3. Backend Implementation
A. Data Model (schools/models.py)
The School model was extended with three fields to manage this process:
* latitude: DecimalField to store the latitude.
* longitude: DecimalField to store the longitude.
* geocoding_status: A CharField with choices (PENDING, SUCCESS, FAILED) to track the state of each school, with PENDING as the default for new entries.
B. Geocoding Service (schools/services.py)
* Core Function: A central geocode_school(school) function encapsulates the logic for a single school. It uses the geopy library with the Nominatim (OpenStreetMap) provider.
* Robustness:
o User-Agent: Sets a descriptive User-Agent (uni-passau-praktikumsamt-app/1.0) as required by Nominatim's policy.
o Error Handling: It includes try...except blocks to gracefully handle GeocoderTimedOut and other service errors, correctly setting the school's status to FAILED.
* Batch Function: A geocode_schools_batch() service iterates through a queryset of schools, calls geocode_school for each, and includes a time.sleep(1.1) to respect the API's rate limit (max 1 request/second).
C. API Endpoints (schools/views.py)
A custom action was added to the SchoolViewSet:
* Endpoint: POST /api/schools/run_geocoding_task/
* Logic:
1. It is a synchronous (blocking) endpoint.
2. It queries the database for all schools with geocoding_status of PENDING or FAILED.
3. It calls the geocode_schools_batch service and waits for it to complete.
4. It returns a 200 OK response containing the final statistics of the batch run.
o Architectural Note: A background (asynchronous) approach using threading was initially considered but discarded in favor of this simpler, more robust synchronous implementation, which provides clearer feedback to the user for this specific administrative task.
4. Frontend Implementation
A. State Management:
* A new state variable, isGeocoding (boolean), was added to the SchoolManagement page to control the UI during the process.
B. UI Components:
* ActionButtons.jsx: A new button, "Find Missing Coordinates," was added. Its disabled state is tied to isGeocoding.
* SchoolManagement.jsx: The handleRunGeocoding function manages the entire user-facing workflow: it shows the confirmation, sets isGeocoding to true, calls the API, and on success, shows a notification and triggers a refetchSchools() to update the UI.
* Loader.jsx: The main loading overlay is now also triggered by the isGeocoding state, providing clear feedback to the user that a long-running process is active.
5. Technical Decisions & Justification
* Synchronous vs. Asynchronous: We chose a synchronous (blocking) API call for simplicity and reliability. For an infrequent administrative task, guaranteeing completion and providing a clear final report is more valuable than allowing the user to navigate away while a background task runs silently.
* geopy Library: We used geopy instead of direct requests calls to abstract away the specific API details, improve error handling, and make it easy to switch to a different geocoding provider in the future.
* Status Field (geocoding_status): This field is essential. It allows the system to be fault-tolerant (failures can be retried) and efficient (successfully geocoded schools are not re-processed).

