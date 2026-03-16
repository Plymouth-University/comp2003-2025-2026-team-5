<?php

session_start();

session_destroy();

header("Location: /geofence/pages/sign_in_page.html");